"""Sensor platform for Genetic Load Manager integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.const import UnitOfEnergy
from homeassistant.helpers.event import async_track_time_interval
from datetime import datetime, timedelta

import logging
import math

_LOGGER = logging.getLogger(__name__)
from .const import (
    DOMAIN, CONF_OPTIMIZATION_MODE, CONF_UPDATE_INTERVAL, CONF_PV_FORECAST_TODAY,
    CONF_PV_FORECAST_TOMORROW, CONF_LOAD_FORECAST, CONF_LOAD_SENSOR, CONF_BATTERY_SOC, 
    CONF_GRID_POWER, CONF_DEMAND_RESPONSE, CONF_CARBON_INTENSITY, CONF_WEATHER,
    CONF_EV_CHARGER, CONF_SMART_THERMOSTAT, CONF_SMART_PLUG, CONF_LIGHTING, CONF_MEDIA_PLAYER,
    DEFAULT_OPTIMIZATION_MODE, DEFAULT_UPDATE_INTERVAL, DEFAULT_ENTITIES
)

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
    """Sensor entity for 24-hour load forecasting."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the load forecast sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_load_forecast"
        self._attr_name = "Load Forecast"
        self._attr_unit_of_measurement = "kWh"
        self._attr_device_class = "energy"
        self._attr_state_class = "measurement"
        self._async_unsub_track_time = None
        
        # Use configured entity or default
        self.load_sensor_entity = config.get(CONF_LOAD_SENSOR, DEFAULT_ENTITIES["load_sensor"])
        
        # Initialize with default values to avoid warnings
        self._forecast = [0.1] * 96  # 96 x 15-minute slots
        self._state = 9.6  # Total energy in kWh (96 * 0.1)
        
        # Track if we've shown the warning
        self._warning_shown = False

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
        """Update the sensor."""
        _LOGGER.debug(f"=== Updating LoadForecastSensor ===")
        
        try:
            if self.load_sensor_entity:
                _LOGGER.debug(f"Fetching load data from entity: {self.load_sensor_entity}")
                
                try:
                    load_state = await self.hass.async_add_executor_job(
                        self.hass.states.get, self.load_sensor_entity
                    )
                    
                    if not load_state:
                        _LOGGER.error(f"Load sensor entity not found: {self.load_sensor_entity}")
                        _LOGGER.error("This entity may not exist or may be misconfigured")
                        if not self._warning_shown:
                            _LOGGER.error("Using default load forecast values")
                            self._warning_shown = True
                        return
                    
                    if load_state.state in ['unknown', 'unavailable']:
                        _LOGGER.error(f"Load sensor entity unavailable: {self.load_sensor_entity}")
                        _LOGGER.error(f"Entity state: {load_state.state}")
                        if not self._warning_shown:
                            _LOGGER.error("Using default load forecast values")
                            self._warning_shown = True
                        return
                    
                    _LOGGER.debug(f"Load sensor state: {load_state.state}")
                    _LOGGER.debug(f"Available attributes: {list(load_state.attributes.keys())}")
                    
                    try:
                        # Try to get forecast data from attributes
                        forecast_data = load_state.attributes.get("forecast", None)
                        
                        if forecast_data is None:
                            _LOGGER.warning(f"No 'forecast' attribute found in {self.load_sensor_entity}")
                            _LOGGER.warning("Available attributes: " + str(list(load_state.attributes.keys())))
                            
                            # Try alternative attribute names
                            alternative_attrs = ['load_forecast', 'energy_forecast', 'consumption_forecast']
                            for alt_attr in alternative_attrs:
                                if alt_attr in load_state.attributes:
                                    forecast_data = load_state.attributes[alt_attr]
                                    _LOGGER.info(f"Using alternative attribute '{alt_attr}' for forecast data")
                                    break
                            
                            if forecast_data is None:
                                _LOGGER.warning("No forecast data found, using default values")
                                forecast_data = [0.1] * 96  # 96 x 15-minute slots
                        
                        _LOGGER.debug(f"Raw forecast data: {len(forecast_data)} items")
                        _LOGGER.debug(f"Sample data: {forecast_data[:5] if forecast_data else 'None'}")
                        
                        # Validate and convert forecast data
                        if isinstance(forecast_data, list):
                            try:
                                self._forecast = []
                                for i, value in enumerate(forecast_data):
                                    try:
                                        if value is None:
                                            _LOGGER.debug(f"None value at index {i}, using default")
                                            self._forecast.append(0.1)
                                        else:
                                            float_val = float(value)
                                            if not math.isfinite(float_val):
                                                _LOGGER.warning(f"Non-finite value at index {i}: {value}, using default")
                                                self._forecast.append(0.1)
                                            else:
                                                self._forecast.append(float_val)
                                    except (ValueError, TypeError) as e:
                                        _LOGGER.warning(f"Invalid value at index {i}: {value}, error: {e}, using default")
                                        self._forecast.append(0.1)
                                
                                # Ensure we have the right number of time slots
                                if len(self._forecast) != 96:
                                    _LOGGER.warning(f"Forecast length mismatch: got {len(self._forecast)}, expected 96")
                                    if len(self._forecast) < 96:
                                        # Extend with default values
                                        self._forecast.extend([0.1] * (96 - len(self._forecast)))
                                        _LOGGER.info(f"Extended forecast to 96 slots")
                                    else:
                                        # Truncate to 96 slots
                                        self._forecast = self._forecast[:96]
                                        _LOGGER.info(f"Truncated forecast to 96 slots")
                                
                                # Calculate total energy
                                self._state = sum(self._forecast)
                                
                                _LOGGER.info(f"Successfully updated load forecast: {len(self._forecast)} slots, total: {self._state:.3f} kWh")
                                _LOGGER.debug(f"Forecast range: {min(self._forecast):.3f} to {max(self._forecast):.3f} kWh")
                                
                            except Exception as e:
                                _LOGGER.error(f"Error processing forecast data: {e}")
                                _LOGGER.error(f"Exception type: {type(e).__name__}")
                                _LOGGER.error(f"Raw forecast data: {forecast_data}")
                                # Use default values
                                self._forecast = [0.1] * 96
                                self._state = 9.6
                                
                        else:
                            _LOGGER.warning(f"Forecast data is not a list: {type(forecast_data)}")
                            _LOGGER.warning("Using default load forecast values")
                            self._forecast = [0.1] * 96
                            self._state = 9.6
                            
                    except (ValueError, TypeError) as e:
                        _LOGGER.error(f"Error parsing load forecast data: {e}")
                        _LOGGER.error(f"Exception type: {type(e).__name__}")
                        _LOGGER.error(f"Raw forecast data: {forecast_data}")
                        # Use default values
                        self._forecast = [0.1] * 96
                        self._state = 9.6
                        
                except Exception as e:
                    _LOGGER.error(f"Exception while fetching load sensor data: {e}")
                    _LOGGER.error(f"Exception type: {type(e).__name__}")
                    if not self._warning_shown:
                        _LOGGER.error("Using default load forecast values")
                        self._warning_shown = True
                    return
                    
            else:
                _LOGGER.warning("No load sensor entity configured")
                if not self._warning_shown:
                    _LOGGER.warning("Using default load forecast values")
                    self._warning_shown = True
                    
        except Exception as e:
            _LOGGER.error(f"Unexpected error in LoadForecastSensor update: {e}")
            _LOGGER.error(f"Exception type: {type(e).__name__}")
            import traceback
            _LOGGER.error(f"Traceback: {traceback.format_exc()}")
            # Use default values as fallback
            self._forecast = [0.1] * 96
            self._state = 9.6

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
        forecast = [0.0] * 96
        
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
        
        _LOGGER.debug(f"Generated 24h forecast from last 24h data: total={sum(forecast):.2f} kWh")
        return forecast

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

    async def async_update(self, now=None):
        """Update the sensor with current pricing information."""
        try:
            # Get current price
            current_price = await self.pricing_calculator.get_current_price()
            self._state = round(current_price, 6)
            
            # Get current market price for component breakdown
            market_price = await self.pricing_calculator.get_current_market_price()
            
            # Ensure market_price is not None before using it
            if market_price is not None:
                self._pricing_components = self.pricing_calculator.get_pricing_components(market_price)
            else:
                _LOGGER.warning("Market price is None, using default pricing components")
                self._pricing_components = {
                    "market_price": 50.0,
                    "fp": 1.0,
                    "q": 0.0,
                    "tae": 0.0,
                    "mfrr": 0.0,
                    "vat": 1.23,
                    "final_price": 0.0615
                }
            
            # Get 24-hour forecast (sample every hour for attributes)
            forecast_96 = await self.pricing_calculator.get_24h_price_forecast()
            # Ensure forecast_96 is not None and has the expected length
            if forecast_96 and len(forecast_96) == 96:
                # Sample every 4th value (hourly instead of 15-minute intervals) for attributes
                self._forecast = [round(forecast_96[i], 6) for i in range(0, 96, 4)]
            else:
                _LOGGER.warning("Invalid forecast data, using default forecast")
                self._forecast = [0.1] * 24  # 24 hourly values
            
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

    async def async_update(self, now=None):
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

class ScheduleVisualizationSensor(SensorEntity):
    """Sensor entity for genetic algorithm schedule visualization."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the schedule visualization sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_schedule_visualization"
        self._attr_name = "Schedule Visualization"
        self._attr_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = None
        self._state = "No schedule available"
        self._schedule_data = {}
        self._last_update = None

    def _get_schedule_summary(self):
        """Get a concise summary of the schedule data."""
        if not hasattr(self, '_schedule_data') or not self._schedule_data:
            return {
                "status": "No schedule data available",
                "last_updated": "Never",
                "total_devices": 0,
                "optimization_status": "Not running"
            }
        
        try:
            # Extract key information for summary
            schedule = self._schedule_data.get("predicted_schedule", [])
            if not schedule:
                return {
                    "status": "Empty schedule",
                    "last_updated": self._schedule_data.get("last_updated", "Unknown"),
                    "total_devices": 0,
                    "optimization_status": "No data"
                }
            
            # Count active time slots per device (handle compressed format)
            device_summary = []
            total_active_slots = 0
            
            if schedule and isinstance(schedule[0], dict) and "d" in schedule[0]:
                # Compressed format with shortened keys
                num_devices = len(schedule[0]["d"]) if schedule else 0
                for device_id in range(num_devices):
                    device_key = f"d{device_id}"
                    active_slots = sum(1 for slot in schedule if slot.get("d", {}).get(device_key, 0) > 0.1)
                    total_active_slots += active_slots
                    device_summary.append({
                        "device_id": device_id,
                        "active_slots": active_slots,
                        "total_slots": len(schedule)
                    })
            else:
                # Legacy format
                for i, device_schedule in enumerate(schedule):
                    if isinstance(device_schedule, dict) and "devices" in device_schedule:
                        active_slots = sum(1 for val in device_schedule["devices"].values() if val > 0.1)
                        device_summary.append({
                            "device_id": i,
                            "active_slots": active_slots,
                            "total_slots": len(device_schedule["devices"])
                        })
                    elif isinstance(device_schedule, list):
                        active_slots = sum(1 for val in device_schedule if val > 0.1)
                        device_summary.append({
                            "device_id": i,
                            "active_slots": active_slots,
                            "total_slots": len(device_schedule)
                        })
            
            return {
                "status": "Schedule available",
                "last_updated": self._schedule_data.get("last_updated", "Unknown"),
                "total_devices": len(device_summary),
                "device_summary": device_summary,
                "total_active_slots": total_active_slots,
                "optimization_status": self._schedule_data.get("optimization_status", "Unknown"),
                "cost_estimate": self._schedule_data.get("cost_estimate", 0),
                "data_format": "compressed" if schedule and isinstance(schedule[0], dict) and "h" in schedule[0] else "legacy"
            }
        except Exception as e:
            _LOGGER.error(f"Error creating schedule summary: {e}")
            return {
                "status": "Error creating summary",
                "error": str(e),
                "last_updated": "Unknown"
            }

    def _expand_compressed_schedule(self):
        """Expand compressed schedule data to full format for external use."""
        if not hasattr(self, '_schedule_data') or not self._schedule_data:
            return {}
        
        try:
            schedule = self._schedule_data.get("predicted_schedule", [])
            if not schedule or not isinstance(schedule[0], dict) or "h" not in schedule[0]:
                return self._schedule_data  # Return as-is if not compressed
            
            # Expand compressed data
            expanded = {}
            expanded_schedule = []
            
            for slot in schedule:
                hour = slot.get("h", 0)
                time_str = f"{hour:02d}:00"
                
                expanded_slot = {
                    "slot": hour,
                    "time": time_str,
                    "price": slot.get("p", 0.1),
                    "devices": {f"device_{k[1:]}": v for k, v in slot.get("d", {}).items()},
                    "total_load": slot.get("l", 0),
                    "solar_forecast": slot.get("s", 0)
                }
                expanded_schedule.append(expanded_slot)
            
            expanded["predicted_schedule"] = expanded_schedule
            expanded["last_updated"] = self._schedule_data.get("last_updated", "Unknown")
            expanded["optimization_status"] = self._schedule_data.get("optimization_status", "Unknown")
            expanded["cost_estimate"] = self._schedule_data.get("cost_estimate", 0)
            expanded["data_format"] = "expanded"
            
            return expanded
            
        except Exception as e:
            _LOGGER.error(f"Error expanding compressed schedule: {e}")
            return {"error": f"Expansion failed: {str(e)}"}

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        if not hasattr(self, '_schedule_data') or not self._schedule_data:
            return {}
        
        # Always include the summary (it's small and useful)
        attributes = {
            "summary": self._get_schedule_summary()
        }
        
        # Check data size and include appropriate level of detail
        try:
            # Convert schedule data to string to check size
            schedule_str = str(self._schedule_data)
            if len(schedule_str) < 8000:  # Conservative limit well under 16KB
                attributes["schedule_data"] = self._schedule_data
                _LOGGER.debug("Including full schedule data in attributes")
            else:
                # Data is too large, provide compressed version and expansion method
                _LOGGER.warning("Schedule data too large for attributes, providing compressed version")
                attributes["compressed_schedule"] = self._schedule_data
                attributes["note"] = "Data is compressed. Use services to access expanded format."
                attributes["expansion_available"] = True
                
        except Exception as e:
            _LOGGER.error(f"Error processing schedule attributes: {e}")
            attributes["error"] = f"Failed to process schedule data: {str(e)}"
        
        return attributes