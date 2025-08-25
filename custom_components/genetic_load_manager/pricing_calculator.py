"""Indexed tariff pricing calculator for Genetic Load Manager."""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN, CONF_MARKET_PRICE, CONF_FIXED_PERCENTAGE, CONF_QUALITY_COMPONENT,
    CONF_TRANSMISSION_TARIFF, CONF_MFRR, CONF_VAT, CONF_CURRENCY_CONVERSION,
    CONF_PEAK_HOURS, CONF_OFF_PEAK_HOURS, CONF_PEAK_MULTIPLIER, CONF_OFF_PEAK_MULTIPLIER,
    CONF_SHOULDER_MULTIPLIER, CONF_SUMMER_MONTHS, CONF_SUMMER_ADJUSTMENT,
    CONF_WINTER_ADJUSTMENT, DEFAULT_ENTITIES
)

_LOGGER = logging.getLogger(__name__)

class IndexedTariffCalculator:
    """Calculator for electricity retailer pricing with indexed tariff components."""
    
    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        """Initialize the pricing calculator."""
        self.hass = hass
        
        # Use configured entity or default
        self.market_price_entity = config.get(CONF_MARKET_PRICE, DEFAULT_ENTITIES["market_price"])
        
        # Track if we've shown the warning
        self._warning_shown = False
        
        # Fixed tariff components (in €/MWh or local currency)
        self.mfrr = config.get("mfrr", 1.94)  # Frequency Restoration Reserve
        self.q = config.get("q", 30.0)  # Quality component
        self.fp = config.get("fp", 1.1674)  # Fixed percentage/multiplier
        self.tae = config.get("tae", 60.0)  # Transmission and distribution tariff
        self.vat = config.get("vat", 1.23)  # VAT (23%)
        
        # Optional time-of-use modifiers
        self.peak_multiplier = config.get("peak_multiplier", 1.0)
        self.off_peak_multiplier = config.get("off_peak_multiplier", 1.0)
        self.shoulder_multiplier = config.get("shoulder_multiplier", 1.0)
        
        # Time periods (24-hour format)
        self.peak_hours = config.get("peak_hours", [18, 19, 20, 21])  # 6-9 PM
        self.off_peak_hours = config.get("off_peak_hours", [0, 1, 2, 3, 4, 5, 6, 23])  # Night hours
        
        # Seasonal adjustments
        self.summer_adjustment = config.get("summer_adjustment", 1.0)
        self.winter_adjustment = config.get("winter_adjustment", 1.0)
        self.summer_months = config.get("summer_months", [6, 7, 8, 9])  # June-September
        
        # Currency conversion (if needed)
        self.currency_conversion = config.get("currency_conversion", 1.0)
        
        # Caching for performance
        self._cached_prices = {}
        self._last_update = None
        self._cache_duration = timedelta(minutes=15)
        
    async def get_current_market_price(self) -> float:
        """Get current market price from configured entity."""
        if not self.market_price_entity:
            if not self._warning_shown:
                _LOGGER.warning("No market price entity configured, using default price")
                self._warning_shown = True
            return 50.0  # Default fallback price in €/MWh
            
        # Fetch market price data
        if self.market_price_entity:
            state = await self.hass.async_add_executor_job(
                self.hass.states.get, self.market_price_entity
            )
            if state and state.state not in ['unknown', 'unavailable']:
                try:
                    hourly_prices = state.attributes.get("Today hours", {})
                    if hourly_prices:
                        prices = []
                        # Get current date for the hour keys
                        current_date = datetime.now().strftime("%Y-%m-%d")
                        
                        for hour in range(24):
                            hour_key = f"{current_date}T{hour:02d}:00:00+01:00"
                            price = hourly_prices.get(hour_key, 0.1)
                            if price is None:
                                price = 0.1
                            # Convert from MWh to kWh (divide by 1000)
                            prices.append(float(price) / 1000.0)
                        
                        if len(prices) == 24:
                            self.market_prices = prices
                            _LOGGER.info(f"Loaded {len(prices)} hourly market prices from {self.market_price_entity}")
                            return prices
                        else:
                            _LOGGER.warning(f"Expected 24 hourly prices, got {len(prices)}")
                    else:
                        _LOGGER.warning(f"No hourly prices found in {self.market_price_entity} attributes")
                        _LOGGER.debug(f"Available attributes: {list(state.attributes.keys())}")
                        if "Today hours" in state.attributes:
                            _LOGGER.debug(f"Today hours content: {state.attributes['Today hours']}")
                except (ValueError, TypeError, KeyError) as e:
                    _LOGGER.error(f"Error parsing market price data: {e}")
                    _LOGGER.debug(f"State attributes: {state.attributes}")
            else:
                _LOGGER.warning(f"Market price entity unavailable: {self.market_price_entity}")
        else:
            _LOGGER.warning("No market price entity configured")
    
    def calculate_indexed_price(self, market_price: float, timestamp: datetime = None) -> float:
        """
        Calculate the indexed tariff price based on the formula:
        TOTAL = (PM * FP + Q + TAE + MFRR) * VAT
        Final price = TOTAL / 1000 (convert from €/MWh to €/kWh)
        
        Args:
            market_price: Market price (PM) in €/MWh
            timestamp: Optional timestamp for time-of-use calculations
            
        Returns:
            Final electricity price in €/kWh
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        # Base calculation: (PM * FP + Q + TAE + MFRR) * VAT
        base_price = (market_price * self.fp + self.q + self.tae + self.mfrr) * self.vat
        
        # Apply time-of-use multiplier
        tou_multiplier = self._get_time_of_use_multiplier(timestamp)
        
        # Apply seasonal adjustment
        seasonal_multiplier = self._get_seasonal_multiplier(timestamp)
        
        # Final price calculation
        final_price = base_price * tou_multiplier * seasonal_multiplier
        
        # Convert from €/MWh to €/kWh and apply currency conversion
        final_price_kwh = (final_price / 1000) * self.currency_conversion
        
        return round(final_price_kwh, 6)
    
    def _get_time_of_use_multiplier(self, timestamp: datetime) -> float:
        """Get time-of-use multiplier based on hour of day."""
        hour = timestamp.hour
        
        if hour in self.peak_hours:
            return self.peak_multiplier
        elif hour in self.off_peak_hours:
            return self.off_peak_multiplier
        else:
            return self.shoulder_multiplier
    
    def _get_seasonal_multiplier(self, timestamp: datetime) -> float:
        """Get seasonal multiplier based on month."""
        month = timestamp.month
        
        if month in self.summer_months:
            return self.summer_adjustment
        else:
            return self.winter_adjustment
    
    async def get_24h_price_forecast(self, start_time: datetime = None) -> List[float]:
        """
        Generate 24-hour price forecast in 15-minute intervals (96 slots).
        
        Args:
            start_time: Starting time for forecast (default: now)
            
        Returns:
            Array of 96 price values for 15-minute intervals
        """
        if start_time is None:
            start_time = datetime.now().replace(second=0, microsecond=0)
        
        # Check cache
        cache_key = start_time.strftime("%Y-%m-%d-%H")
        if (cache_key in self._cached_prices and 
            self._last_update and 
            datetime.now() - self._last_update < self._cache_duration):
            return self._cached_prices[cache_key]
        
        # Get current market price
        current_market_price = await self.get_current_market_price()
        
        # Generate 96 price points (24 hours * 4 quarters)
        prices = [0.0] * 96
        
        for i in range(96):
            slot_time = start_time + timedelta(minutes=15 * i)
            
            # For now, use current market price for all slots
            # In a real implementation, you might have hourly market price forecasts
            market_price = current_market_price
            
            # Add some realistic variation based on typical daily patterns
            market_price = self._apply_daily_market_variation(market_price, slot_time)
            
            # Calculate indexed price for this time slot
            prices[i] = self.calculate_indexed_price(market_price, slot_time)
        
        # Cache the result
        self._cached_prices[cache_key] = prices
        self._last_update = datetime.now()
        
        _LOGGER.debug(f"Generated 24h price forecast: min={min(prices):.4f}, max={max(prices):.4f}, avg={sum(prices)/len(prices):.4f}")
        
        return prices
    
    def _apply_daily_market_variation(self, base_price: float, timestamp: datetime) -> float:
        """Apply realistic daily market price variations."""
        hour = timestamp.hour
        
        # Typical daily market price pattern (simplified)
        if 6 <= hour <= 9:  # Morning peak
            variation = 1.2
        elif 18 <= hour <= 21:  # Evening peak
            variation = 1.3
        elif 0 <= hour <= 6:  # Night
            variation = 0.8
        elif 22 <= hour <= 23:  # Late evening
            variation = 0.9
        else:  # Day hours
            variation = 1.0
        
        return base_price * variation
    
    async def get_current_price(self) -> float:
        """Get current electricity price."""
        market_price = await self.get_current_market_price()
        return self.calculate_indexed_price(market_price)
    
    def get_pricing_components(self, market_price: float) -> Dict[str, float]:
        """
        Get breakdown of pricing components for transparency.
        
        Args:
            market_price: Current market price
            
        Returns:
            Dictionary with component breakdown
        """
        pm_component = market_price * self.fp
        base_total = pm_component + self.q + self.tae + self.mfrr
        with_vat = base_total * self.vat
        final_price = with_vat / 1000
        
        return {
            "market_price": market_price,
            "market_price_adjusted": pm_component,
            "quality_component": self.q,
            "transmission_tariff": self.tae,
            "frequency_reserve": self.mfrr,
            "subtotal": base_total,
            "vat_amount": base_total * (self.vat - 1),
            "total_with_vat": with_vat,
            "final_price_kwh": final_price
        }
    
    def update_config(self, config: Dict[str, Any]):
        """Update calculator configuration."""
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
                _LOGGER.info(f"Updated pricing config: {key} = {value}")
        
        # Clear cache when config changes
        self._cached_prices.clear()
        self._last_update = None
