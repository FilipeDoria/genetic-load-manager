"""Sensor platform for Genetic Load Manager integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.const import UnitOfEnergy
from homeassistant.helpers.event import async_track_time_interval
from datetime import datetime, timedelta
import numpy as np
import logging

_LOGGER = logging.getLogger(__name__)
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType = None):
    """Set up the sensor platform for the genetic load manager."""
    sensors = [LoadForecastSensor(hass, entry.data)]
    
    # Add pricing sensor if indexed pricing is enabled
    if entry.data.get("use_indexed_pricing", True):
        sensors.append(IndexedPricingSensor(hass, entry.data))
    
    # Add status sensor
    sensors.append(GeneticAlgorithmStatusSensor(hass, entry.data))
    
    # Add dashboard sensors
    from .dashboard import OptimizationDashboardSensor, ScheduleVisualizationSensor
    from .control_panel import ControlPanelSensor
    from .analytics import CostAnalyticsSensor
    
    sensors.extend([
        OptimizationDashboardSensor(hass, entry.data),
        ScheduleVisualizationSensor(hass, entry.data),
        ControlPanelSensor(hass, entry.data),
        CostAnalyticsSensor(hass, entry.data)
    ])
    
    async_add_entities(sensors)

class LoadForecastSensor(SensorEntity):
    """Sensor entity for generating a 24-hour load forecast in 15-minute intervals based on last 24 hours of data."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the load forecast sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_load_forecast"
        self._attr_name = "Load Forecast"
        self._attr_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = "energy"
        self._state = None
        self._attributes = {}
        self.load_sensor_entity = config.get("load_sensor_entity")
        self._async_unsub_track_time = None  # Track the time interval unsub function

    @property
    def state(self):
        """Return the state of the sensor (total forecasted energy in kWh)."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the forecast array as an attribute."""
        return {"forecast": self._forecast}

    async def async_added_to_hass(self):
        """Set up periodic updates for the sensor."""
        self._async_unsub_track_time = async_track_time_interval(
            self.hass, self.async_update, timedelta(minutes=15)
        )
        await self.async_update()

    async def async_will_remove_from_hass(self):
        """Clean up when removing entity."""
        if self._async_unsub_track_time:
            self._async_unsub_track_time()
            self._async_unsub_track_time = None

    async def async_update(self):
        """Update the sensor with a new 24-hour load forecast based on last 24 hours of data."""
        if not self.load_sensor_entity:
            _LOGGER.warning("No load sensor entity specified, setting forecast to zeros")
            self._forecast = [0.0] * 96
            self._state = 0.0
            return

        # Fetch last 24 hours of historical data
        history = await self._get_last_24h_data()
        if not history:
            _LOGGER.warning("No historical data available for last 24 hours, setting forecast to defaults")
            self._forecast = [0.1] * 96  # Default to small non-zero values
            self._state = 9.6  # 96 * 0.1 kWh
            return

        # Generate forecast based on last 24 hours
        self._forecast = await self._generate_forecast_from_last_24h(history)
        self._state = round(sum(self._forecast), 2)  # Total energy in kWh

    async def _get_last_24h_data(self):
        """Fetch historical load data for the last 24 hours."""
        from homeassistant.components.recorder.history import get_significant_states
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        try:
            history = await self.hass.async_add_executor_job(
                get_significant_states,
                self.hass,
                start_time,
                end_time,
                [self.load_sensor_entity],
                None,  # end_time_param
                True   # significant_changes_only
            )
            return history.get(self.load_sensor_entity, [])
        except Exception as e:
            _LOGGER.error(f"Error fetching last 24h data for {self.load_sensor_entity}: {e}")
            return []

    async def _generate_forecast_from_last_24h(self, history):
        """Generate a 96-slot forecast based on the last 24 hours of load data."""
        current_time = datetime.now()
        forecast = np.zeros(96)
        
        # Create time slots for the next 24 hours (96 x 15-minute intervals)
        time_slots = []
        for i in range(96):
            slot_time = current_time + timedelta(minutes=15 * i)
            time_slots.append(slot_time)
        
        # Map historical data to time slots
        slot_data = {i: [] for i in range(96)}
        
        for state in history:
            try:
                timestamp = state.last_updated
                value = float(state.state)
                
                # Find the corresponding time slot (same time of day)
                slot_idx = self._get_time_slot_index(timestamp)
                if slot_idx is not None:
                    slot_data[slot_idx].append(value)
                    
            except (ValueError, TypeError) as e:
                _LOGGER.debug(f"Skipping invalid state: {e}")
                continue
        
        # Fill forecast array with historical data or defaults
        for i in range(96):
            if slot_data[i]:
                # Use the most recent value for this time slot
                forecast[i] = slot_data[i][-1]
            else:
                # No data for this time slot, use default
                forecast[i] = 0.1
        
        _LOGGER.debug(f"Generated 24h forecast from last 24h data: total={np.sum(forecast):.2f} kWh")
        return forecast.tolist()

    def _get_time_slot_index(self, timestamp):
        """Get the time slot index (0-95) for a given timestamp based on time of day."""
        # Extract time of day (hour and minute)
        hour = timestamp.hour
        minute = timestamp.minute
        
        # Calculate slot index (0-95) based on time of day
        # Slot 0 = 00:00-00:14, Slot 1 = 00:15-00:29, etc.
        slot_idx = hour * 4 + minute // 15
        
        # Ensure slot index is within bounds
        if 0 <= slot_idx < 96:
            return slot_idx
        else:
            _LOGGER.warning(f"Timestamp {timestamp} maps to invalid slot index: {slot_idx}")
            return None

    async def _get_historical_data(self):
        """Legacy method - kept for compatibility but not used."""
        # This method is kept for backward compatibility but the new implementation
        # uses _get_last_24h_data instead
        return await self._get_last_24h_data()

    async def _generate_forecast(self, history):
        """Legacy method - kept for compatibility but not used."""
        # This method is kept for backward compatibility but the new implementation
        # uses _generate_forecast_from_last_24h instead
        return await self._generate_forecast_from_last_24h(history)


class IndexedPricingSensor(SensorEntity):
    """Sensor entity for indexed tariff electricity pricing."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the indexed pricing sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_indexed_pricing"
        self._attr_name = "Indexed Electricity Price"
        self._attr_unit_of_measurement = "€/kWh"
        self._attr_device_class = "monetary"
        self._attr_state_class = "measurement"
        self._state = None
        self._pricing_components = {}
        self._forecast = []
        
        # Import here to avoid circular imports
        from .pricing_calculator import IndexedTariffCalculator
        self.pricing_calculator = IndexedTariffCalculator(hass, config)

    @property
    def state(self):
        """Return the current electricity price."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return detailed pricing information as attributes."""
        attrs = {
            "pricing_components": self._pricing_components,
            "24h_forecast": self._forecast,
            "pricing_method": "indexed_tariff",
            "last_updated": datetime.now().isoformat()
        }
        
        # Add configuration details
        attrs.update({
            "mfrr": self.pricing_calculator.mfrr,
            "quality_component": self.pricing_calculator.q,
            "fixed_percentage": self.pricing_calculator.fp,
            "transmission_tariff": self.pricing_calculator.tae,
            "vat": self.pricing_calculator.vat,
            "peak_multiplier": self.pricing_calculator.peak_multiplier,
            "off_peak_multiplier": self.pricing_calculator.off_peak_multiplier
        })
        
        return attrs

    async def async_added_to_hass(self):
        """Set up periodic updates for the sensor."""
        async_track_time_interval(self.hass, self.async_update, timedelta(minutes=5))
        await self.async_update()

    async def async_update(self):
        """Update the sensor with current pricing information."""
        try:
            # Get current price
            current_price = await self.pricing_calculator.get_current_price()
            self._state = round(current_price, 6)
            
            # Get current market price for component breakdown
            market_price = await self.pricing_calculator.get_current_market_price()
            self._pricing_components = self.pricing_calculator.get_pricing_components(market_price)
            
            # Get 24-hour forecast (sample every hour for attributes)
            forecast_96 = await self.pricing_calculator.get_24h_price_forecast()
            # Sample every 4th value (hourly instead of 15-minute intervals) for attributes
            self._forecast = [round(forecast_96[i], 6) for i in range(0, 96, 4)]
            
            _LOGGER.debug(f"Updated indexed pricing: {self._state} €/kWh (market: {market_price} €/MWh)")
            
        except Exception as e:
            _LOGGER.error(f"Error updating indexed pricing sensor: {e}")
            if self._state is None:
                self._state = 0.1  # Fallback price


class GeneticAlgorithmStatusSensor(SensorEntity):
    """Sensor entity for genetic algorithm status and metrics."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the genetic algorithm status sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_genetic_algorithm_status"
        self._attr_name = "Genetic Algorithm Status"
        self._attr_unit_of_measurement = None
        self._attr_device_class = None
        self._state = "idle"
        self._attributes = {}

    @property
    def state(self):
        """Return the current status of the genetic algorithm."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return detailed status information as attributes."""
        return self._attributes

    async def async_added_to_hass(self):
        """Set up the sensor."""
        await self.async_update()

    async def async_update(self):
        """Update the sensor status."""
        try:
            # Get genetic algorithm instance from hass data
            genetic_algo = self.hass.data.get(DOMAIN, {}).get('genetic_algorithm')
            
            if genetic_algo:
                # Update status based on genetic algorithm state
                if hasattr(genetic_algo, 'is_running') and genetic_algo.is_running:
                    self._state = "running"
                elif hasattr(genetic_algo, 'is_optimizing') and genetic_algo.is_optimizing:
                    self._state = "optimizing"
                else:
                    self._state = "idle"
                
                # Update attributes
                self._attributes = {
                    "last_updated": datetime.now().isoformat(),
                    "population_size": getattr(genetic_algo, 'population_size', 100),
                    "generations": getattr(genetic_algo, 'generations', 200),
                    "mutation_rate": getattr(genetic_algo, 'mutation_rate', 0.05),
                    "crossover_rate": getattr(genetic_algo, 'crossover_rate', 0.8),
                    "best_fitness": getattr(genetic_algo, 'best_fitness', None),
                    "current_generation": getattr(genetic_algo, 'best_fitness', None),
                    "optimization_count": getattr(genetic_algo, 'optimization_count', 0)
                }
            else:
                self._state = "not_initialized"
                self._attributes = {
                    "last_updated": datetime.now().isoformat(),
                    "error": "Genetic algorithm not available"
                }
                
        except Exception as e:
            _LOGGER.error(f"Error updating genetic algorithm status sensor: {e}")
            self._state = "error"
            self._attributes = {
                "last_updated": datetime.now().isoformat(),
                "error": str(e)
            }