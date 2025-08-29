import random
import math
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
import logging
from .const import (
    DOMAIN, CONF_OPTIMIZATION_MODE, CONF_UPDATE_INTERVAL, CONF_PV_FORECAST_TODAY,
    CONF_PV_FORECAST_TOMORROW, CONF_LOAD_FORECAST, CONF_BATTERY_SOC, CONF_GRID_POWER,
    CONF_DEMAND_RESPONSE, CONF_CARBON_INTENSITY, CONF_WEATHER, CONF_EV_CHARGER,
    CONF_SMART_THERMOSTAT, CONF_SMART_PLUG, CONF_LIGHTING, CONF_MEDIA_PLAYER,
    DEFAULT_OPTIMIZATION_MODE, DEFAULT_UPDATE_INTERVAL, DEFAULT_ENTITIES
)
from .pricing_calculator import IndexedTariffCalculator
import asyncio

_LOGGER = logging.getLogger(__name__)

class GeneticLoadOptimizer:
    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the genetic algorithm optimizer."""
        self.hass = hass
        self.config = config
        
        # Load configuration with defaults
        self.optimization_mode = config.get(CONF_OPTIMIZATION_MODE, DEFAULT_OPTIMIZATION_MODE)
        self.update_interval = config.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        
        # Entity configuration with fallbacks to defaults
        self.pv_forecast_today_entity = config.get(CONF_PV_FORECAST_TODAY, DEFAULT_ENTITIES["pv_forecast_today"])
        self.pv_forecast_tomorrow_entity = config.get(CONF_PV_FORECAST_TOMORROW, DEFAULT_ENTITIES["pv_forecast_tomorrow"])
        self.load_forecast_entity = config.get(CONF_LOAD_FORECAST, DEFAULT_ENTITIES["load_forecast"])
        self.battery_soc_entity = config.get(CONF_BATTERY_SOC, DEFAULT_ENTITIES["battery_soc"])
        self.grid_power_entity = config.get(CONF_GRID_POWER, DEFAULT_ENTITIES["grid_power"])
        self.demand_response_entity = config.get(CONF_DEMAND_RESPONSE, DEFAULT_ENTITIES["demand_response"])
        self.carbon_intensity_entity = config.get(CONF_CARBON_INTENSITY, DEFAULT_ENTITIES["carbon_intensity"])
        self.weather_entity = config.get(CONF_WEATHER, DEFAULT_ENTITIES["weather"])
        self.ev_charger_entity = config.get(CONF_EV_CHARGER, DEFAULT_ENTITIES["ev_charger"])
        self.smart_thermostat_entity = config.get(CONF_SMART_THERMOSTAT, DEFAULT_ENTITIES["smart_thermostat"])
        self.smart_plug_entity = config.get(CONF_SMART_PLUG, DEFAULT_ENTITIES["smart_plug"])
        self.lighting_entity = config.get(CONF_LIGHTING, DEFAULT_ENTITIES["lighting"])
        self.media_player_entity = config.get(CONF_MEDIA_PLAYER, DEFAULT_ENTITIES["media_player"])

        self.population_size = config.get("population_size", 100)
        self.generations = config.get("generations", 200)
        self.mutation_rate = config.get("mutation_rate", 0.05)
        self.crossover_rate = config.get("crossover_rate", 0.8)
        self.num_devices = config.get("num_devices", 2)
        self.time_slots = 96
        self.pv_forecast = None
        self.load_forecast = None
        self.battery_capacity = config.get("battery_capacity", 10.0)
        self.max_charge_rate = config.get("max_charge_rate", 2.0)
        self.max_discharge_rate = config.get("max_discharge_rate", 2.0)
        self.binary_control = config.get("binary_control", False)
        
        # Initialize device priorities (default: all devices have equal priority)
        self.device_priorities = config.get("device_priorities", [1.0] * self.num_devices)
        if len(self.device_priorities) != self.num_devices:
            # Extend or truncate to match num_devices
            if len(self.device_priorities) < self.num_devices:
                self.device_priorities.extend([1.0] * (self.num_devices - len(self.device_priorities)))
            else:
                self.device_priorities = self.device_priorities[:self.num_devices]
        
        # Initialize pricing calculator
        self.pricing_calculator = IndexedTariffCalculator(hass, config)
        self.use_indexed_pricing = config.get("use_indexed_pricing", True)
        
        # Initialize pricing-related attributes
        self.dynamic_pricing_entity = config.get("dynamic_pricing_entity", "sensor.dynamic_electricity_price")
        self.pricing = None  # Will be populated during forecast data fetch
        
        # Initialize optimization tracking attributes
        self.best_fitness = float("-inf")
        self.best_solution = None
        self.current_generation = 0
        self._async_unsub_track_time = None  # Track the time interval unsub function

    async def fetch_forecast_data(self):
        """Fetch and process Solcast PV, load, battery, and pricing data for a 24-hour horizon."""
        _LOGGER.info("=== Starting forecast data fetch ===")
        current_time = datetime.now().replace(second=0, microsecond=0)
        # Make current_time timezone-aware to match Solcast data
        try:
            from datetime import timezone
            # Use local timezone (+01:00) to match your Solcast data
            current_time = current_time.replace(tzinfo=timezone(timedelta(hours=1)))
            _LOGGER.debug(f"Using timezone-aware current_time: {current_time}")
        except ImportError:
            # Fallback for older Python versions
            current_time = current_time.replace(tzinfo=None)
            _LOGGER.debug(f"Using timezone-naive current_time: {current_time}")
            
        slot_duration = timedelta(minutes=15)
        forecast_horizon = timedelta(hours=24)
        end_time = current_time + forecast_horizon
        pv_forecast = [0.0] * self.time_slots

        # Fetch today's and tomorrow's Solcast forecasts
        pv_today_state = None
        pv_tomorrow_state = None
        
        _LOGGER.info(f"Fetching PV forecast data from entities:")
        _LOGGER.info(f"  Today: {self.pv_forecast_today_entity}")
        _LOGGER.info(f"  Tomorrow: {self.pv_forecast_tomorrow_entity}")
        
        if self.pv_forecast_today_entity:
            try:
                pv_today_state = await self.hass.async_add_executor_job(
                    self.hass.states.get, self.pv_forecast_today_entity
                )
                if not pv_today_state:
                    _LOGGER.error(f"PV forecast entity not found: {self.pv_forecast_today_entity}")
                    _LOGGER.error("This entity may not exist or may be misconfigured")
                else:
                    _LOGGER.info(f"Successfully fetched PV today entity: {self.pv_forecast_today_entity}")
                    _LOGGER.debug(f"PV today state: {pv_today_state.state}")
                    _LOGGER.debug(f"PV today attributes: {list(pv_today_state.attributes.keys())}")
            except Exception as e:
                _LOGGER.error(f"Exception while fetching PV today entity {self.pv_forecast_today_entity}: {e}")
                _LOGGER.error(f"Exception type: {type(e).__name__}")
                pv_today_state = None
        else:
            _LOGGER.warning("No PV forecast entity configured")
            
        if self.pv_forecast_tomorrow_entity:
            try:
                pv_tomorrow_state = await self.hass.async_add_executor_job(
                    self.hass.states.get, self.pv_forecast_tomorrow_entity
                )
                if not pv_tomorrow_state:
                    _LOGGER.error(f"PV tomorrow forecast entity not found: {self.pv_forecast_tomorrow_entity}")
                    _LOGGER.error("This entity may not exist or may be misconfigured")
                else:
                    _LOGGER.info(f"Successfully fetched PV tomorrow entity: {self.pv_forecast_tomorrow_entity}")
                    _LOGGER.debug(f"PV tomorrow state: {pv_tomorrow_state.state}")
                    _LOGGER.debug(f"PV tomorrow attributes: {list(pv_tomorrow_state.attributes.keys())}")
            except Exception as e:
                _LOGGER.error(f"Exception while fetching PV tomorrow entity {self.pv_forecast_tomorrow_entity}: {e}")
                _LOGGER.error(f"Exception type: {type(e).__name__}")
                pv_tomorrow_state = None
        
        # Try to get DetailedForecast first (30-minute intervals), fallback to DetailedHourly (1-hour intervals)
        pv_today_raw = []
        pv_tomorrow_raw = []
        
        if pv_today_state:
            try:
                pv_today_raw = pv_today_state.attributes.get("DetailedForecast", [])
                if not pv_today_raw:
                    pv_today_raw = pv_today_state.attributes.get("DetailedHourly", [])
                    _LOGGER.debug("Using DetailedHourly for today's forecast")
                else:
                    _LOGGER.debug("Using DetailedForecast for today's forecast")
                _LOGGER.debug(f"Today's forecast data: {len(pv_today_raw)} items")
                if pv_today_raw:
                    _LOGGER.debug(f"First item structure: {pv_today_raw[0]}")
                    _LOGGER.debug(f"First item keys: {list(pv_today_raw[0].keys()) if isinstance(pv_today_raw[0], dict) else 'Not a dict'}")
                    _LOGGER.debug(f"Sample data points: {pv_today_raw[:3]}")
                else:
                    _LOGGER.warning("Today's forecast data is empty")
            except Exception as e:
                _LOGGER.error(f"Error accessing today's forecast attributes: {e}")
                _LOGGER.error(f"Available attributes: {list(pv_today_state.attributes.keys()) if pv_today_state.attributes else 'None'}")
                pv_today_raw = []
                
        if pv_tomorrow_state:
            try:
                pv_tomorrow_raw = pv_tomorrow_state.attributes.get("DetailedForecast", [])
                if not pv_tomorrow_raw:
                    pv_tomorrow_raw = pv_tomorrow_state.attributes.get("DetailedHourly", [])
                    _LOGGER.debug("Using DetailedHourly for tomorrow's forecast")
                else:
                    _LOGGER.debug("Using DetailedForecast for tomorrow's forecast")
                _LOGGER.debug(f"Tomorrow's forecast data: {len(pv_tomorrow_raw)} items")
                if pv_tomorrow_raw:
                    _LOGGER.debug(f"First item structure: {pv_tomorrow_raw[0]}")
                    _LOGGER.debug(f"First item keys: {list(pv_tomorrow_raw[0].keys()) if isinstance(pv_tomorrow_raw[0], dict) else 'Not a dict'}")
                    _LOGGER.debug(f"Sample data points: {pv_tomorrow_raw[:3]}")
                else:
                    _LOGGER.warning("Tomorrow's forecast data is empty")
            except Exception as e:
                _LOGGER.error(f"Error accessing tomorrow's forecast attributes: {e}")
                _LOGGER.error(f"Available attributes: {list(pv_tomorrow_state.attributes.keys()) if pv_tomorrow_state.attributes else 'None'}")
                pv_tomorrow_raw = []

        if not pv_today_raw and not pv_tomorrow_raw:
            _LOGGER.error("No Solcast PV forecast data available from either entity")
            _LOGGER.error("This will result in zero PV generation forecast")
            _LOGGER.error("Check entity configuration and data availability")
            self.pv_forecast = pv_forecast
        else:
            # Combine forecasts
            times = []
            values = []
            
            _LOGGER.info(f"Processing PV forecasts - Today: {len(pv_today_raw)} items, Tomorrow: {len(pv_tomorrow_raw)} items")
            
            for forecast_name, forecast in [("today", pv_today_raw), ("tomorrow", pv_tomorrow_raw)]:
                if not forecast:
                    _LOGGER.debug(f"No {forecast_name} forecast data")
                    continue
                    
                _LOGGER.debug(f"Processing {forecast_name} forecast with {len(forecast)} items")
                
                for i, item in enumerate(forecast):
                    try:
                        # Handle both DetailedForecast and DetailedHourly structures
                        if isinstance(item, dict) and "period_start" in item and "pv_estimate" in item:
                            period_start = item["period_start"]
                            pv_estimate = item["pv_estimate"]
                            
                            _LOGGER.debug(f"Processing item {i}: period_start={period_start}, pv_estimate={pv_estimate}")
                            
                            # Parse the period_start string (handle timezone info)
                            try:
                                period_time = datetime.fromisoformat(period_start)
                                pv_value = float(pv_estimate)
                                
                                # Handle timezone comparison - make both timezone-aware
                                if period_time.tzinfo is None:
                                    # If period_time is timezone-naive, assume it's in local time (+01:00)
                                    period_time = period_time.replace(tzinfo=timezone(timedelta(hours=1)))
                                    _LOGGER.debug(f"Made period_time timezone-aware: {period_time}")
                                
                                if current_time.tzinfo is None:
                                    # If current_time is timezone-naive, make it timezone-aware
                                    current_time = current_time.replace(tzinfo=period_time.tzinfo)
                                    _LOGGER.debug(f"Made current_time timezone-aware: {current_time}")
                                
                                # For PV forecasts, include all data for the next 48 hours regardless of current time
                                # This ensures we get both today and tomorrow's data even if it's currently night
                                time_diff = period_time - current_time
                                hours_ahead = time_diff.total_seconds() / 3600
                                
                                # Include data up to 48 hours in the future
                                if hours_ahead >= -2 and hours_ahead <= 48:  # Allow 2 hours in the past for safety
                                    times.append(period_time)
                                    values.append(pv_value)
                                    _LOGGER.debug(f"Added forecast: {period_time} -> {pv_value} kW (hours ahead: {hours_ahead:.1f})")
                                else:
                                    _LOGGER.debug(f"Skipping time: {period_time} (hours ahead: {hours_ahead:.1f})")
                                    
                            except ValueError as e:
                                _LOGGER.warning(f"Could not parse time '{period_start}' for item {i}: {e}")
                                # Try alternative timezone handling
                                try:
                                    # Remove timezone info and try parsing
                                    clean_time = period_start.split('+')[0].split('Z')[0]
                                    period_time = datetime.fromisoformat(clean_time)
                                    pv_value = float(pv_estimate)
                                    
                                    # Make both timezone-naive for comparison
                                    if current_time.tzinfo is not None:
                                        current_time_naive = current_time.replace(tzinfo=None)
                                    else:
                                        current_time_naive = current_time
                                    
                                    time_diff = period_time - current_time_naive
                                    hours_ahead = time_diff.total_seconds() / 3600
                                    
                                    # Include data up to 48 hours in the future
                                    if hours_ahead >= -2 and hours_ahead <= 48:
                                        times.append(period_time)
                                        values.append(pv_value)
                                        _LOGGER.debug(f"Added forecast (clean time): {period_time} -> {pv_value} kW (hours ahead: {hours_ahead:.1f})")
                                    else:
                                        _LOGGER.debug(f"Skipping time (clean): {period_time} (hours ahead: {hours_ahead:.1f})")
                                except ValueError as e2:
                                    _LOGGER.warning(f"Could not parse clean time '{clean_time}' for item {i}: {e2}")
                                    continue
                        else:
                            _LOGGER.warning(f"Item {i} does not have required keys: {item}")
                            _LOGGER.warning(f"Expected dict with 'period_start' and 'pv_estimate', got: {type(item)}")
                                
                    except (KeyError, ValueError, TypeError) as e:
                        _LOGGER.error(f"Error parsing Solcast forecast item {i}: {e}")
                        _LOGGER.error(f"Item data: {item}")
                        _LOGGER.error(f"Item type: {type(item)}")
                        continue

            _LOGGER.info(f"Total parsed forecast points: {len(times)}")
            if times:
                _LOGGER.debug(f"Time range: {min(times)} to {max(times)}")
                _LOGGER.debug(f"Value range: {min(values)} to {max(values)} kW")
            else:
                _LOGGER.error("No forecast times were parsed - this indicates a problem with the time filtering logic")
                _LOGGER.error(f"Current time: {current_time}")
                _LOGGER.error(f"Today raw data sample: {pv_today_raw[:2] if pv_today_raw else 'None'}")
                _LOGGER.error(f"Tomorrow raw data sample: {pv_tomorrow_raw[:2] if pv_tomorrow_raw else 'None'}")

            if times:
                # Sort by time to ensure chronological order
                sorted_pairs = sorted(zip(times, values), key=lambda x: x[0])
                times, values = zip(*sorted_pairs)
                times = list(times)
                values = list(values)

                _LOGGER.info(f"Successfully parsed {len(times)} PV forecast data points from {times[0]} to {times[-1]}")
                
                # Create the final forecast array
                self.pv_forecast = self._interpolate_forecast(times, values)
                _LOGGER.info(f"PV forecast set from interpolation: {len(self.pv_forecast)} slots, max: {max(self.pv_forecast):.3f} kW")
            else:
                _LOGGER.error("No valid forecast times found, using fallback zero forecast")
                _LOGGER.error("This will result in zero PV generation forecast")
                self.pv_forecast = pv_forecast
                _LOGGER.warning(f"PV forecast set to fallback: {len(self.pv_forecast)} slots (all zeros)")

        # Fetch load forecast
        _LOGGER.info(f"Fetching load forecast from entity: {self.load_forecast_entity}")
        if self.load_forecast_entity:
            try:
                load_state = await self.hass.async_add_executor_job(
                    self.hass.states.get, self.load_forecast_entity
                )
                if load_state and load_state.state not in ['unknown', 'unavailable']:
                    try:
                        forecast_data = load_state.attributes.get("forecast", [0.1] * self.time_slots)
                        _LOGGER.debug(f"Load forecast data: {len(forecast_data)} items")
                        _LOGGER.debug(f"Sample data: {forecast_data[:5] if forecast_data else 'None'}")
                        
                        self.load_forecast = [float(x) for x in forecast_data]
                        if len(self.load_forecast) != self.time_slots:
                            _LOGGER.warning(f"Load forecast size mismatch: got {len(self.load_forecast)}, expected {self.time_slots}")
                            # Resize to match time slots
                            if len(self.load_forecast) < self.time_slots:
                                self.load_forecast.extend([0.1] * (self.time_slots - len(self.load_forecast)))
                                _LOGGER.info(f"Extended load forecast to {len(self.load_forecast)} slots")
                            elif len(self.load_forecast) > self.time_slots:
                                self.load_forecast = self.load_forecast[:self.time_slots]
                                _LOGGER.info(f"Truncated load forecast to {len(self.load_forecast)} slots")
                        _LOGGER.info(f"Successfully loaded load forecast: {len(self.load_forecast)} slots")
                    except (ValueError, TypeError) as e:
                        _LOGGER.error(f"Error parsing load forecast data: {e}")
                        _LOGGER.error(f"Raw forecast data: {forecast_data}")
                        self.load_forecast = [0.1] * self.time_slots
                else:
                    _LOGGER.error(f"Load forecast entity unavailable: {self.load_forecast_entity}")
                    _LOGGER.error(f"Entity state: {load_state.state if load_state else 'None'}")
                    self.load_forecast = [0.1] * self.time_slots
            except Exception as e:
                _LOGGER.error(f"Exception while fetching load forecast: {e}")
                _LOGGER.error(f"Exception type: {type(e).__name__}")
                self.load_forecast = [0.1] * self.time_slots
        else:
            _LOGGER.warning("No load forecast entity configured")
            self.load_forecast = [0.1] * self.time_slots

        # Fetch battery state and pricing
        _LOGGER.info(f"Fetching battery SOC from entity: {self.battery_soc_entity}")
        if self.battery_soc_entity:
            try:
                battery_state = await self.hass.async_add_executor_job(
                    self.hass.states.get, self.battery_soc_entity
                )
                if battery_state and battery_state.state not in ['unknown', 'unavailable']:
                    try:
                        self.battery_soc = float(battery_state.state)
                        _LOGGER.debug(f"Battery SOC raw value: {battery_state.state}")
                        _LOGGER.debug(f"Battery SOC parsed value: {self.battery_soc}")
                        
                        # Validate battery SOC is within reasonable range (0-100%)
                        if not (0 <= self.battery_soc <= 100):
                            _LOGGER.warning(f"Battery SOC out of range: {self.battery_soc}%, using 50%")
                            self.battery_soc = 50.0
                        else:
                            _LOGGER.info(f"Battery SOC: {self.battery_soc}%")
                    except (ValueError, TypeError) as e:
                        _LOGGER.error(f"Error parsing battery SOC: {e}")
                        _LOGGER.error(f"Raw battery state: {battery_state.state}")
                        self.battery_soc = 50.0  # Default to 50%
                else:
                    _LOGGER.error(f"Battery SOC entity unavailable: {self.battery_soc_entity}")
                    _LOGGER.error(f"Entity state: {battery_state.state if battery_state else 'None'}")
                    self.battery_soc = 50.0
            except Exception as e:
                _LOGGER.error(f"Exception while fetching battery SOC: {e}")
                _LOGGER.error(f"Exception type: {type(e).__name__}")
                self.battery_soc = 50.0
        else:
            _LOGGER.warning("No battery SOC entity configured")
            self.battery_soc = 50.0
        
        # Use indexed pricing calculator or fallback to simple pricing
        _LOGGER.info(f"Fetching pricing data (indexed: {self.use_indexed_pricing})")
        if self.use_indexed_pricing:
            try:
                pricing_forecast = await self.pricing_calculator.get_24h_price_forecast(current_time)
                if pricing_forecast and len(pricing_forecast) == self.time_slots:
                    self.pricing = pricing_forecast
                    _LOGGER.info("Using indexed tariff pricing with 96 time slots")
                    _LOGGER.debug(f"Pricing range: {min(pricing_forecast):.4f} to {max(pricing_forecast):.4f} €/kWh")
                else:
                    _LOGGER.warning(f"Indexed pricing returned invalid data: {pricing_forecast}")
                    _LOGGER.warning(f"Expected {self.time_slots} slots, got {len(pricing_forecast) if pricing_forecast else 'None'}")
                    _LOGGER.warning("Falling back to simple pricing")
                    self.use_indexed_pricing = False
            except Exception as e:
                _LOGGER.error(f"Error getting indexed pricing: {e}")
                _LOGGER.error(f"Exception type: {type(e).__name__}")
                _LOGGER.error("Falling back to simple pricing")
                self.use_indexed_pricing = False
        
        if not self.use_indexed_pricing:
            # Fallback to market price entity directly
            _LOGGER.info("Using fallback market price pricing")
            try:
                # Use the market price entity from pricing calculator instead of fallback
                market_prices = await self.pricing_calculator.get_current_market_price()
                _LOGGER.debug(f"Market prices: {market_prices}")
                _LOGGER.debug(f"Market prices type: {type(market_prices)}")
                
                if isinstance(market_prices, list) and len(market_prices) == 24:
                    # Convert 24 hourly prices to 96 time slots (15-minute intervals)
                    self.pricing = []
                    for hour_price in market_prices:
                        # Repeat the hourly price for 4 time slots (15-minute intervals)
                        for _ in range(4):
                            self.pricing.append(float(hour_price))
                    _LOGGER.info("Using market price entity with 96 time slots")
                    _LOGGER.debug(f"Pricing range: {min(self.pricing):.4f} to {max(self.pricing):.4f} €/kWh")
                else:
                    # Single price, repeat for all time slots
                    single_price = float(market_prices) if isinstance(market_prices, (int, float)) else 0.1
                    self.pricing = [single_price] * self.time_slots
                    _LOGGER.info("Using single market price repeated for 96 time slots")
                    _LOGGER.debug(f"Single price: {single_price} €/kWh")
            except Exception as e:
                _LOGGER.error(f"Error getting market pricing: {e}")
                _LOGGER.error(f"Exception type: {type(e).__name__}")
                self.pricing = [0.1] * self.time_slots
        
        # Ensure pricing is initialized even if both methods fail
        if not hasattr(self, 'pricing') or self.pricing is None or len(self.pricing) != self.time_slots:
            _LOGGER.error("Both indexed and dynamic pricing failed, using default pricing")
            _LOGGER.error("This will result in uniform pricing across all time slots")
            self.pricing = [0.1] * self.time_slots  # Default 0.1 €/kWh
        
        # Final validation
        if len(self.pricing) != self.time_slots:
            _LOGGER.warning(f"Pricing array size mismatch: got {len(self.pricing)}, expected {self.time_slots}")
            # Resize to match time slots
            if len(self.pricing) < self.time_slots:
                self.pricing.extend([0.1] * (self.time_slots - len(self.pricing)))
                _LOGGER.info(f"Extended pricing to {len(self.pricing)} slots")
            elif len(self.pricing) > self.time_slots:
                self.pricing = self.pricing[:self.time_slots]
                _LOGGER.info(f"Truncated pricing to {len(self.pricing)} slots")
        
        _LOGGER.debug(f"Final pricing array: {len(self.pricing)} slots, sample values: {self.pricing[:5]}")
        # Note: self.pv_forecast is already set correctly above from interpolation or fallback
        _LOGGER.debug(f"PV forecast (96 slots): {self.pv_forecast}")
        
        # Final validation: Ensure PV forecast was not overwritten and contains valid data
        if not hasattr(self, 'pv_forecast') or self.pv_forecast is None:
            _LOGGER.error("CRITICAL ERROR: PV forecast is None after processing!")
            self.pv_forecast = [0.0] * self.time_slots
        elif len(self.pv_forecast) != self.time_slots:
            _LOGGER.error(f"CRITICAL ERROR: PV forecast size mismatch: {len(self.pv_forecast)} != {self.time_slots}")
            self.pv_forecast = [0.0] * self.time_slots
        elif all(x == 0.0 for x in self.pv_forecast):
            _LOGGER.warning("PV forecast contains all zeros - this may indicate a data processing issue")
        else:
            _LOGGER.info(f"PV forecast validation passed: {len(self.pv_forecast)} slots, max: {max(self.pv_forecast):.3f} kW")
        
        _LOGGER.info("=== Forecast data fetch completed ===")
        _LOGGER.info(f"PV forecast: {len(self.pv_forecast)} slots, max: {max(self.pv_forecast):.3f} kW")
        _LOGGER.info(f"Load forecast: {len(self.load_forecast)} slots, max: {max(self.load_forecast):.3f} kW")
        _LOGGER.info(f"Battery SOC: {self.battery_soc:.1f}%")
        _LOGGER.info(f"Pricing: {len(self.pricing)} slots, range: {min(self.pricing):.4f}-{max(self.pricing):.4f} €/kWh")

    async def initialize_population(self):
        # Initialize population with random values
        self.population = []
        for _ in range(self.population_size):
            device_schedule = []
            for _ in range(self.num_devices):
                time_schedule = [random.uniform(0, 1) for _ in range(self.time_slots)]
                device_schedule.append(time_schedule)
            self.population.append(device_schedule)
        for i in range(self.population_size):
            for d in range(self.num_devices):
                if self.binary_control:
                    # Convert to binary (0 or 1)
                    for t in range(self.time_slots):
                        self.population[i][d][t] = 1.0 if self.population[i][d][t] > 0.5 else 0.0

    async def fitness_function(self, chromosome):
        try:
            _LOGGER.debug("=== Starting fitness calculation ===")
            
            # Validate inputs
            if self.pv_forecast is None or self.pricing is None:
                _LOGGER.error("Missing forecast data in fitness function")
                _LOGGER.error(f"PV forecast: {self.pv_forecast is None}")
                _LOGGER.error(f"Pricing: {self.pricing is None}")
                return -1000.0  # Heavy penalty for missing data
            
            if len(self.pv_forecast) != self.time_slots or len(self.pricing) != self.time_slots:
                _LOGGER.error(f"Forecast data size mismatch: PV={len(self.pv_forecast)}, Pricing={len(self.pricing)}, Expected={self.time_slots}")
                _LOGGER.error("This indicates a data initialization problem")
                return -1000.0
            
            # Check for zero PV forecast (indicates data processing failure)
            if all(x == 0.0 for x in self.pv_forecast):
                _LOGGER.error("CRITICAL ERROR: PV forecast contains all zeros - solar optimization will be ineffective!")
                _LOGGER.error("This indicates the PV forecast data was not properly processed or was overwritten")
                return -1000.0  # Heavy penalty for invalid PV data
            
            # Validate chromosome structure
            if not isinstance(chromosome, list) or len(chromosome) != self.num_devices:
                _LOGGER.error(f"Invalid chromosome structure: expected {self.num_devices} devices, got {len(chromosome) if isinstance(chromosome, list) else 'not a list'}")
                return -1000.0
            
            for d, device_schedule in enumerate(chromosome):
                if not isinstance(device_schedule, list) or len(device_schedule) != self.time_slots:
                    _LOGGER.error(f"Invalid device {d} schedule: expected {self.time_slots} time slots, got {len(device_schedule) if isinstance(device_schedule, list) else 'not a list'}")
                    return -1000.0
                
                # Validate numeric values
                for t, value in enumerate(device_schedule):
                    if not isinstance(value, (int, float)) or not math.isfinite(value):
                        _LOGGER.error(f"Invalid value at device {d}, time {t}: {value} (type: {type(value)})")
                        return -1000.0
            
            _LOGGER.debug(f"Chromosome validation passed: {self.num_devices} devices, {self.time_slots} time slots")
            
            cost = 0.0
            solar_utilization = 0.0
            battery_penalty = 0.0
            priority_penalty = 0.0
            battery_soc = self.battery_soc if hasattr(self, 'battery_soc') and self.battery_soc is not None else 0.0
            
            _LOGGER.debug(f"Starting fitness calculation with battery SOC: {battery_soc}%")
            
            for t in range(self.time_slots):
                try:
                    # Calculate total load for this time slot
                    total_load = sum(chromosome[d][t] for d in range(len(chromosome)))
                    
                    # Validate PV forecast value
                    if not isinstance(self.pv_forecast[t], (int, float)) or not math.isfinite(self.pv_forecast[t]):
                        _LOGGER.error(f"Invalid PV forecast at time {t}: {self.pv_forecast[t]}")
                        return -1000.0
                    
                    # Validate pricing value
                    if not isinstance(self.pricing[t], (int, float)) or not math.isfinite(self.pricing[t]):
                        _LOGGER.error(f"Invalid pricing at time {t}: {self.pricing[t]}")
                        return -1000.0
                    
                    net_load = total_load - self.pv_forecast[t]
                    grid_energy = max(0, net_load)
                    cost += grid_energy * self.pricing[t]
                    
                    # Calculate solar utilization (avoid division by zero)
                    if self.pv_forecast[t] > 0:
                        solar_utilization += min(self.pv_forecast[t], total_load) / self.pv_forecast[t]
                    else:
                        solar_utilization += 0.0
                    
                    # Battery management
                    battery_change = 0
                    if net_load < 0:
                        battery_change = min(-net_load, self.max_charge_rate)
                    elif net_load > 0:
                        battery_change = -min(net_load, self.max_discharge_rate)
                    
                    battery_soc += battery_change
                    
                    # Battery constraint penalty
                    if battery_soc < 0 or battery_soc > self.battery_capacity:
                        battery_penalty += abs(battery_soc - self.battery_capacity / 2) * 100
                        _LOGGER.debug(f"Time {t}: Battery SOC {battery_soc:.1f}% out of bounds, penalty: {battery_penalty:.2f}")
                    
                    battery_soc = max(0, min(battery_soc, self.battery_capacity))
                    
                    # Device priority penalty
                    for d in range(self.num_devices):
                        if d < len(self.device_priorities):
                            priority_penalty += (1 - chromosome[d][t]) * self.device_priorities[d]
                        else:
                            _LOGGER.warning(f"Device {d} priority not defined, using default 1.0")
                            priority_penalty += (1 - chromosome[d][t]) * 1.0
                            
                except Exception as e:
                    _LOGGER.error(f"Error calculating fitness for time slot {t}: {e}")
                    _LOGGER.error(f"Exception type: {type(e).__name__}")
                    return -1000.0
            
            # Calculate final fitness components
            solar_efficiency = solar_utilization / self.time_slots if self.time_slots > 0 else 0.0
            
            # Validate all components are finite
            if not all(math.isfinite(x) for x in [cost, battery_penalty, priority_penalty, solar_efficiency]):
                _LOGGER.error("Non-finite values in fitness components")
                _LOGGER.error(f"Cost: {cost}, Battery penalty: {battery_penalty}, Priority penalty: {priority_penalty}, Solar efficiency: {solar_efficiency}")
                return -1000.0
            
            fitness = -(0.5 * cost + 0.3 * battery_penalty + 0.1 * priority_penalty - 0.1 * solar_efficiency)
            
            # Ensure finite result
            if not math.isfinite(fitness):
                _LOGGER.error("Non-finite fitness value calculated")
                _LOGGER.error(f"Fitness components: cost={cost}, battery_penalty={battery_penalty}, priority_penalty={priority_penalty}, solar_efficiency={solar_efficiency}")
                return -1000.0
            
            _LOGGER.debug(f"Fitness calculation completed: {fitness:.4f}")
            _LOGGER.debug(f"Components: cost={cost:.4f}, battery_penalty={battery_penalty:.4f}, priority_penalty={priority_penalty:.4f}, solar_efficiency={solar_efficiency:.4f}")
            
            return fitness
            
        except Exception as e:
            _LOGGER.error(f"Unexpected error in fitness function: {e}")
            _LOGGER.error(f"Exception type: {type(e).__name__}")
            _LOGGER.error(f"Exception details: {str(e)}")
            import traceback
            _LOGGER.error(f"Traceback: {traceback.format_exc()}")
            return -1000.0  # Heavy penalty for errors

    async def optimize(self):
        """Run the genetic algorithm optimization."""
        _LOGGER.info("=== Starting genetic algorithm optimization ===")
        
        try:
            # Fetch forecast data first
            _LOGGER.info("Fetching forecast data...")
            await self.fetch_forecast_data()
            
            # Validate data before proceeding
            if not self._validate_optimization_data():
                _LOGGER.error("Data validation failed, cannot proceed with optimization")
                return None
            
            # Initialize population
            _LOGGER.info("Initializing population...")
            await self.initialize_population()
            
            if not hasattr(self, 'population') or not self.population:
                _LOGGER.error("Population initialization failed")
                return None
            
            _LOGGER.info(f"Population initialized: {len(self.population)} individuals, {self.num_devices} devices, {self.time_slots} time slots")
            
            # Run CPU-intensive optimization in executor to prevent blocking
            _LOGGER.info("Starting genetic algorithm execution...")
            best_solution = await self.hass.async_add_executor_job(
                self._run_genetic_optimization
            )
            
            if best_solution is not None:
                _LOGGER.info("Optimization completed successfully")
                _LOGGER.info(f"Best fitness: {self.best_fitness:.4f}")
                _LOGGER.debug(f"Best solution shape: {len(best_solution)} devices x {len(best_solution[0]) if best_solution[0] else 0} time slots")
            else:
                _LOGGER.error("Optimization returned no solution")
            
            return best_solution
            
        except Exception as e:
            _LOGGER.error(f"Error in optimize method: {e}")
            _LOGGER.error(f"Exception type: {type(e).__name__}")
            import traceback
            _LOGGER.error(f"Traceback: {traceback.format_exc()}")
            return None

    def _validate_optimization_data(self):
        """Validate that all required data is available for optimization."""
        _LOGGER.info("Validating optimization data...")
        
        try:
            # Check PV forecast
            if self.pv_forecast is None:
                _LOGGER.error("PV forecast is None")
                return False
            if len(self.pv_forecast) != self.time_slots:
                _LOGGER.error(f"PV forecast length mismatch: {len(self.pv_forecast)} != {self.time_slots}")
                return False
            if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in self.pv_forecast):
                _LOGGER.error("PV forecast contains invalid values")
                return False
            
            # Check load forecast
            if self.load_forecast is None:
                _LOGGER.error("Load forecast is None")
                return False
            if len(self.load_forecast) != self.time_slots:
                _LOGGER.error(f"Load forecast length mismatch: {len(self.load_forecast)} != {self.time_slots}")
                return False
            if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in self.load_forecast):
                _LOGGER.error("Load forecast contains invalid values")
                return False
            
            # Check pricing
            if self.pricing is None:
                _LOGGER.error("Pricing is None")
                return False
            if len(self.pricing) != self.time_slots:
                _LOGGER.error(f"Pricing length mismatch: {len(self.pricing)} != {self.time_slots}")
                return False
            if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in self.pricing):
                _LOGGER.error("Pricing contains invalid values")
                return False
            
            # Check battery SOC
            if not hasattr(self, 'battery_soc') or self.battery_soc is None:
                _LOGGER.error("Battery SOC is None")
                return False
            if not isinstance(self.battery_soc, (int, float)) or not math.isfinite(self.battery_soc):
                _LOGGER.error(f"Battery SOC is invalid: {self.battery_soc}")
                return False
            
            # Check device priorities
            if not hasattr(self, 'device_priorities') or not self.device_priorities:
                _LOGGER.error("Device priorities not initialized")
                return False
            if len(self.device_priorities) < self.num_devices:
                _LOGGER.error(f"Device priorities length mismatch: {len(self.device_priorities)} < {self.num_devices}")
                return False
            
            _LOGGER.info("Data validation passed successfully")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error during data validation: {e}")
            _LOGGER.error(f"Exception type: {type(e).__name__}")
            return False

    def _run_genetic_optimization(self):
        """Run the genetic algorithm optimization in executor thread."""
        _LOGGER.info("=== Starting genetic algorithm execution ===")
        
        try:
            best_solution = None
            best_fitness = float("-inf")
            
            _LOGGER.info(f"Optimization parameters: {self.population_size} individuals, {self.generations} generations")
            _LOGGER.info(f"Mutation rate: {self.mutation_rate}, Crossover rate: {self.crossover_rate}")
            
            for generation in range(self.generations):
                try:
                    # Calculate fitness scores synchronously in executor
                    _LOGGER.debug(f"Generation {generation}: Calculating fitness scores...")
                    fitness_scores = []
                    
                    for i, individual in enumerate(self.population):
                        try:
                            fitness = self._fitness_function_sync(individual)
                            fitness_scores.append(fitness)
                        except Exception as e:
                            _LOGGER.error(f"Error calculating fitness for individual {i}: {e}")
                            fitness_scores.append(-1000.0)  # Heavy penalty for errors
                    
                    if not fitness_scores:
                        _LOGGER.error("No fitness scores calculated, aborting optimization")
                        break
                    
                    # Find best fitness for this generation
                    max_fitness = max(fitness_scores)
                    if max_fitness > best_fitness:
                        best_fitness = max_fitness
                        best_idx = fitness_scores.index(max_fitness)
                        best_solution = [row[:] for row in self.population[best_idx]]
                        _LOGGER.info(f"Generation {generation}: New best fitness = {best_fitness:.4f}")
                    
                    # Create new population
                    _LOGGER.debug(f"Generation {generation}: Creating new population...")
                    new_population = []
                    
                    for _ in range(self.population_size // 2):
                        try:
                            parent1 = self._tournament_selection_sync(fitness_scores)
                            parent2 = self._tournament_selection_sync(fitness_scores)
                            child1, child2 = self._crossover_sync(parent1, parent2)
                            child1 = self._mutate_sync(child1, generation)
                            child2 = self._mutate_sync(child2, generation)
                            new_population.extend([child1, child2])
                        except Exception as e:
                            _LOGGER.error(f"Error creating offspring in generation {generation}: {e}")
                            # Add parents as fallback
                            new_population.extend([parent1, parent2])
                    
                    if new_population:
                        self.population = new_population
                    else:
                        _LOGGER.error(f"Failed to create new population for generation {generation}")
                        break
                    
                    # Log progress every 50 generations
                    if generation % 50 == 0:
                        _LOGGER.info(f"Generation {generation}: Best fitness = {best_fitness:.4f}, Population size = {len(self.population)}")
                    
                except Exception as e:
                    _LOGGER.error(f"Error in generation {generation}: {e}")
                    _LOGGER.error(f"Exception type: {type(e).__name__}")
                    continue
            
            self.best_fitness = best_fitness
            self.best_solution = best_solution
            
            _LOGGER.info("=== Genetic algorithm execution completed ===")
            _LOGGER.info(f"Final best fitness: {best_fitness:.4f}")
            _LOGGER.info(f"Best solution available: {best_solution is not None}")
            
            return best_solution
            
        except Exception as e:
            _LOGGER.error(f"Unexpected error in genetic algorithm execution: {e}")
            _LOGGER.error(f"Exception type: {type(e).__name__}")
            import traceback
            _LOGGER.error(f"Traceback: {traceback.format_exc()}")
            return None

    def _fitness_function_sync(self, chromosome):
        """Synchronous version of fitness function for executor."""
        # This is the CPU-intensive calculation moved to executor thread
        cost = 0.0
        solar_utilization = 0.0
        battery_usage = 0.0
        
        for t in range(self.time_slots):
            device_consumption = sum(chromosome[d][t] for d in range(len(chromosome)))
            net_load = self.load_forecast[t] + device_consumption - self.pv_forecast[t]
            
            if hasattr(self, 'pricing') and self.pricing is not None:
                cost += net_load * self.pricing[t] / 1000.0
            else:
                cost += net_load * 0.1  # Fallback price
            
            solar_utilization += min(self.pv_forecast[t], self.load_forecast[t] + device_consumption)
            battery_usage += abs(net_load) * 0.1
        
        fitness = -(cost + battery_usage * 0.01) + solar_utilization * 0.02
        return fitness

    def _tournament_selection_sync(self, fitness_scores):
        """Synchronous tournament selection for executor."""
        tournament_size = 5
        selection = random.sample(range(self.population_size), tournament_size)
        best_idx = selection[[fitness_scores[i] for i in selection].index(max([fitness_scores[i] for i in selection]))]
        return self.population[best_idx]

    def _crossover_sync(self, parent1, parent2):
        """Synchronous crossover for executor."""
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.time_slots - 1)
            # Swap the time segments after the crossover point
            for d in range(len(parent1)):
                parent1[d][point:], parent2[d][point:] = parent2[d][point:][:], parent1[d][point:][:]
        # Deep copy the parents
        parent1_copy = [[val for val in device] for device in parent1]
        parent2_copy = [[val for val in device] for device in parent2]
        return parent1_copy, parent2_copy

    def _mutate_sync(self, chromosome, generation):
        """Synchronous mutation for executor."""
        adaptive_rate = self.mutation_rate * (1 - generation / self.generations)
        # Apply mutation to random positions
        for d in range(len(chromosome)):
            for t in range(len(chromosome[d])):
                if random.random() < adaptive_rate:
                    chromosome[d][t] = random.random()
        if self.binary_control:
            # Convert to binary (0 or 1)
            for d in range(len(chromosome)):
                for t in range(len(chromosome[d])):
                    chromosome[d][t] = 1.0 if chromosome[d][t] > 0.5 else 0.0
        return chromosome

    def _interpolate_forecast(self, times, values):
        """Interpolate forecast data to 15-minute time slots."""
        from datetime import timedelta
        
        if not times or not values:
            _LOGGER.warning("No times or values provided for interpolation")
            return [0.0] * self.time_slots
        
        # Create 15-minute slot duration
        slot_duration = timedelta(minutes=15)
        current_time = datetime.now()
        
        # Initialize forecast array with zeros
        pv_forecast = [0.0] * self.time_slots
        
        _LOGGER.debug(f"Interpolating {len(times)} data points to {self.time_slots} time slots")
        _LOGGER.debug(f"Time range: {times[0]} to {times[-1]}")
        _LOGGER.debug(f"Current time: {current_time}")
        
        # Interpolate to 15-minute slots
        for t in range(self.time_slots):
            slot_time = current_time + t * slot_duration
            
            if slot_time < times[0] or slot_time >= times[-1]:
                pv_forecast[t] = 0.0
                continue
                
            # Find bracketing times for interpolation
            for i in range(len(times) - 1):
                if times[i] <= slot_time < times[i + 1]:
                    # Linear interpolation
                    time_diff = (times[i + 1] - times[i]).total_seconds()
                    slot_diff = (slot_time - times[i]).total_seconds()
                    weight = slot_diff / time_diff
                    pv_forecast[t] = values[i] * (1 - weight) + values[i + 1] * weight
                    break
        
        _LOGGER.info(f"Generated PV forecast with {len(pv_forecast)} slots, max value: {max(pv_forecast):.3f} kW")
        return pv_forecast

    async def tournament_selection(self, fitness_scores):
        tournament_size = 5
        selection = random.sample(range(self.population_size), tournament_size)
        # Use pre-calculated fitness scores instead of recalculating
        tournament_fitness = [fitness_scores[i] for i in selection]
        best_idx = selection[tournament_fitness.index(max(tournament_fitness))]
        return self.population[best_idx]

    async def crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.time_slots - 1)
            # Create children by combining parent schedules
            child1 = []
            child2 = []
            for d in range(len(parent1)):
                child1_device = parent1[d][:point] + parent2[d][point:]
                child2_device = parent2[d][:point] + parent1[d][point:]
                child1.append(child1_device)
                child2.append(child2_device)
            return child1, child2
        # Deep copy the parents
        parent1_copy = [[val for val in device] for device in parent1]
        parent2_copy = [[val for val in device] for device in parent2]
        return parent1_copy, parent2_copy

    async def mutate(self, chromosome, generation):
        adaptive_rate = self.mutation_rate * (1 - generation / self.generations)
        # Apply mutation to random positions
        for d in range(len(chromosome)):
            for t in range(len(chromosome[d])):
                if random.random() < adaptive_rate:
                    if self.binary_control:
                        chromosome[d][t] = 1 - chromosome[d][t]
                    else:
                        chromosome[d][t] = random.uniform(0, 1)
        return chromosome

    async def schedule_optimization(self):
        async def periodic_optimization(now):
            _LOGGER.info("=== Starting periodic optimization ===")
            _LOGGER.info(f"Current time: {now}")
            
            try:
                # Check if genetic algorithm is properly initialized
                if not hasattr(self, 'population') or not self.population:
                    _LOGGER.error("Genetic algorithm not properly initialized")
                    _LOGGER.error("Attempting to reinitialize...")
                    
                    try:
                        await self.initialize_population()
                        if not hasattr(self, 'population') or not self.population:
                            _LOGGER.error("Failed to reinitialize population")
                            return
                        _LOGGER.info("Population reinitialized successfully")
                    except Exception as e:
                        _LOGGER.error(f"Error reinitializing population: {e}")
                        _LOGGER.error(f"Exception type: {type(e).__name__}")
                        return
                
                # Run optimization
                _LOGGER.info("Running genetic algorithm optimization...")
                solution = await self.optimize()
                
                if solution is not None:
                    _LOGGER.info("Optimization completed successfully")
                    _LOGGER.info(f"Solution shape: {len(solution)} devices x {len(solution[0]) if solution[0] else 0} time slots")
                    
                    # Update device schedules
                    for d in range(self.num_devices):
                        try:
                            if d < len(solution):
                                device_schedule = solution[d]
                                if isinstance(device_schedule, list) and len(device_schedule) > 0:
                                    # Use proper Home Assistant state setting method
                                    entity_id = f"switch.device_{d}_schedule"
                                    state = "on" if device_schedule[0] > 0.5 else "off"
                                    
                                    # Convert schedule to list if it's a numpy array
                                    if hasattr(device_schedule, 'tolist'):
                                        schedule_list = device_schedule.tolist()
                                    else:
                                        schedule_list = list(device_schedule)
                                    
                                    attributes = {"schedule": schedule_list}
                                    
                                    _LOGGER.debug(f"Updating device {d} schedule: {entity_id}")
                                    _LOGGER.debug(f"State: {state}, Schedule length: {len(schedule_list)}")
                                    
                                    # Set state using the proper Home Assistant method
                                    self.hass.states.async_set(entity_id, state, attributes)
                                    _LOGGER.info(f"Successfully updated device {d} schedule")
                                else:
                                    _LOGGER.warning(f"Invalid device {d} schedule: {device_schedule}")
                            else:
                                _LOGGER.warning(f"Device {d} index out of range for solution")
                                
                        except Exception as e:
                            _LOGGER.error(f"Error updating device {d} schedule: {e}")
                            _LOGGER.error(f"Exception type: {type(e).__name__}")
                            _LOGGER.error(f"Device schedule data: {solution[d] if d < len(solution) else 'Index out of range'}")
                            continue
                    
                    _LOGGER.info("Periodic optimization completed successfully")
                else:
                    _LOGGER.error("Optimization returned no solution")
                    _LOGGER.error("This indicates a problem with the genetic algorithm")
                    
                    # Try to get rule-based schedule as fallback
                    _LOGGER.info("Attempting to generate rule-based schedule as fallback...")
                    try:
                        fallback_schedule = await self.rule_based_schedule()
                        if fallback_schedule:
                            _LOGGER.info("Using rule-based schedule as fallback")
                            # Update device schedules with fallback
                            for d in range(self.num_devices):
                                try:
                                    entity_id = f"switch.device_{d}_schedule"
                                    state = "on" if fallback_schedule[d][0] > 0.5 else "off"
                                    attributes = {"schedule": fallback_schedule[d]}
                                    self.hass.states.async_set(entity_id, state, attributes)
                                    _LOGGER.info(f"Updated device {d} with fallback schedule")
                                except Exception as e:
                                    _LOGGER.error(f"Error updating device {d} with fallback schedule: {e}")
                        else:
                            _LOGGER.error("Fallback rule-based schedule also failed")
                    except Exception as e:
                        _LOGGER.error(f"Error generating fallback schedule: {e}")
                        _LOGGER.error(f"Exception type: {type(e).__name__}")
                        
            except Exception as e:
                _LOGGER.error(f"Unexpected error in periodic optimization: {e}")
                _LOGGER.error(f"Exception type: {type(e).__name__}")
                import traceback
                _LOGGER.error(f"Traceback: {traceback.format_exc()}")
                
                # Try to recover by reinitializing
                _LOGGER.info("Attempting to recover from error...")
                try:
                    await self.fetch_forecast_data()
                    await self.initialize_population()
                    _LOGGER.info("Recovery successful")
                except Exception as recovery_error:
                    _LOGGER.error(f"Recovery failed: {recovery_error}")
                    _LOGGER.error(f"Recovery exception type: {type(recovery_error).__name__}")
        
        # Run initial optimization
        _LOGGER.info("Running initial optimization...")
        await periodic_optimization(datetime.now())
        
        # Schedule periodic optimizations
        _LOGGER.info("Scheduling periodic optimizations every 15 minutes")
        self._async_unsub_track_time = async_track_time_interval(self.hass, periodic_optimization, timedelta(minutes=15))
        return self._async_unsub_track_time

    async def get_manageable_loads(self):
        """Get list of manageable loads for switch creation."""
        loads = []
        for i in range(self.num_devices):
            load_info = {
                'entity_id': f"switch.device_{i}",
                'name': f"Device {i}",
                'power_consumption': 1000,  # Default 1kW
                'priority': self.device_priorities[i] if i < len(self.device_priorities) else 1.0,
                'flexible': True
            }
            loads.append(load_info)
        return loads

    @property
    def is_running(self):
        """Check if the genetic algorithm is currently running."""
        return hasattr(self, 'population') and self.population is not None

    async def start(self):
        """Start the genetic algorithm optimizer."""
        await self.fetch_forecast_data()
        await self.initialize_population()
        return True

    async def stop(self):
        """Stop the genetic algorithm optimizer."""
        # Clean up time interval tracker
        if self._async_unsub_track_time:
            self._async_unsub_track_time()
            self._async_unsub_track_time = None
        return True

    async def run_optimization(self):
        """Run a single optimization cycle."""
        return await self.optimize()

    async def rule_based_schedule(self):
        """Generate a rule-based schedule as fallback."""
        # Ensure forecast data is available
        if not hasattr(self, 'pv_forecast') or self.pv_forecast is None:
            await self.fetch_forecast_data()
        
        # Simple rule-based scheduling based on PV forecast and pricing
        schedule = [[0.0 for _ in range(self.time_slots)] for _ in range(self.num_devices)]
        
        # Safety check for forecast data
        if hasattr(self, 'pv_forecast') and hasattr(self, 'pricing') and self.pv_forecast is not None and self.pricing is not None:
            for t in range(self.time_slots):
                # Turn on devices when PV generation is high and prices are low
                if self.pv_forecast[t] > 0.5 and self.pricing[t] < sum(self.pricing) / len(self.pricing):
                    for d in range(self.num_devices):
                        schedule[d][t] = 1.0
        
        return schedule

    def _log_event(self, level, message):
        """Log an event with the specified level."""
        if level == "INFO":
            _LOGGER.info(message)
        elif level == "WARNING":
            _LOGGER.warning(message)
        elif level == "ERROR":
            _LOGGER.error(message)
        else:
            _LOGGER.debug(message)