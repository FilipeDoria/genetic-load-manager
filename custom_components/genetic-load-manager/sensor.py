"""Sensor platform for Genetic Load Manager integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.helpers.event import async_track_time_interval
from datetime import datetime, timedelta
import numpy as np
import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "genetic_load_manager"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigType, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType = None):
    """Set up the sensor platform for the genetic load manager."""
    async_add_entities([LoadForecastSensor(hass, entry.data)])

class LoadForecastSensor(SensorEntity):
    """Sensor entity for generating a 24-hour load forecast in 15-minute intervals based on last 24 hours of data."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the load forecast sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_load_forecast"
        self._attr_name = "Load Forecast"
        self._attr_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_device_class = "energy"
        self._load_sensor_entity = config.get("load_sensor_entity")
        self._forecast = []
        self._state = None

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
        async_track_time_interval(self.hass, self.async_update, timedelta(minutes=15))
        await self.async_update()

    async def async_update(self):
        """Update the sensor with a new 24-hour load forecast based on last 24 hours of data."""
        if not self._load_sensor_entity:
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
            history = await get_significant_states(
                self.hass,
                start_time,
                end_time,
                [self._load_sensor_entity],
                significant_changes_only=True
            )
            return history.get(self._load_sensor_entity, [])
        except Exception as e:
            _LOGGER.error(f"Error fetching last 24h data for {self._load_sensor_entity}: {e}")
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