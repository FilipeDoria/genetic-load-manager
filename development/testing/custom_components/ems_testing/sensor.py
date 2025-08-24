"""EMS Testing sensors for Home Assistant."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    DOMAIN,
    SENSOR_OPTIMIZATION_STATUS,
    SENSOR_NEXT_ACTION,
    SENSOR_ESTIMATED_SAVINGS,
    SENSOR_BATTERY_SCHEDULE,
    SENSOR_DEVICE_SCHEDULE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EMS Testing sensors."""
    _LOGGER.info("Setting up EMS Testing sensors")
    
    # Get the integration instance
    ems_integration = hass.data[DOMAIN][config_entry.entry_id]
    
    # Create sensor entities
    sensors = [
        EMSOptimizationStatusSensor(ems_integration),
        EMSNextActionSensor(ems_integration),
        EMSEstimatedSavingsSensor(ems_integration),
        EMSBatteryScheduleSensor(ems_integration),
        EMSDeviceScheduleSensor(ems_integration),
    ]
    
    async_add_entities(sensors)

class EMSBaseSensor(SensorEntity):
    """Base class for EMS Testing sensors."""
    
    def __init__(self, ems_integration):
        """Initialize the sensor."""
        self.ems_integration = ems_integration
        self._attr_should_poll = True
        self._attr_available = True
    
    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "ems_testing")},
            "name": "EMS Testing Integration",
            "manufacturer": "Custom",
            "model": "EMS Testing v1.0",
        }

class EMSOptimizationStatusSensor(EMSBaseSensor):
    """Sensor for EMS optimization status."""
    
    _attr_name = "EMS Optimization Status"
    _attr_unique_id = SENSOR_OPTIMIZATION_STATUS
    _attr_icon = "mdi:chart-line"
    
    def update(self) -> None:
        """Update the sensor."""
        results = self.ems_integration.get_optimization_results()
        if results:
            timestamp = results.get('timestamp')
            if timestamp:
                self._attr_native_value = f"Last optimized: {timestamp.strftime('%H:%M:%S')}"
                self._attr_available = True
            else:
                self._attr_native_value = "No optimization data"
                self._attr_available = False
        else:
            self._attr_native_value = "No optimization data"
            self._attr_available = False

class EMSNextActionSensor(EMSBaseSensor):
    """Sensor for next EMS action."""
    
    _attr_name = "EMS Next Action"
    _attr_unique_id = SENSOR_NEXT_ACTION
    _attr_icon = "mdi:calendar-clock"
    
    def update(self) -> None:
        """Update the sensor."""
        results = self.ems_integration.get_optimization_results()
        if results:
            next_action = results.get('next_action', 'No actions planned')
            self._attr_native_value = next_action
            self._attr_available = True
        else:
            self._attr_native_value = "No actions planned"
            self._attr_available = False

class EMSEstimatedSavingsSensor(EMSBaseSensor):
    """Sensor for estimated daily cost."""
    
    _attr_name = "EMS Estimated Daily Cost"
    _attr_unique_id = SENSOR_ESTIMATED_SAVINGS
    _attr_icon = "mdi:currency-eur"
    _attr_native_unit_of_measurement = "EUR"
    _attr_device_class = "monetary"
    
    def update(self) -> None:
        """Update the sensor."""
        results = self.ems_integration.get_optimization_results()
        if results:
            cost = results.get('cost', 0)
            self._attr_native_value = round(cost, 2)
            self._attr_available = True
        else:
            self._attr_native_value = 0
            self._attr_available = False

class EMSBatteryScheduleSensor(EMSBaseSensor):
    """Sensor for battery schedule summary."""
    
    _attr_name = "EMS Battery Schedule"
    _attr_unique_id = SENSOR_BATTERY_SCHEDULE
    _attr_icon = "mdi:battery"
    
    def update(self) -> None:
        """Update the sensor."""
        results = self.ems_integration.get_optimization_results()
        if results:
            schedule = results.get('schedule', {})
            battery_sched = schedule.get('battery', [])
            
            # Count actions
            charge_actions = sum(1 for action in battery_sched if action > 0)
            discharge_actions = sum(1 for action in battery_sched if action < 0)
            
            if charge_actions > 0 or discharge_actions > 0:
                self._attr_native_value = f"Charge: {charge_actions}, Discharge: {discharge_actions}"
            else:
                self._attr_native_value = "No battery actions planned"
            
            self._attr_available = True
        else:
            self._attr_native_value = "No schedule data"
            self._attr_available = False

class EMSDeviceScheduleSensor(EMSBaseSensor):
    """Sensor for device schedule summary."""
    
    _attr_name = "EMS Device Schedule"
    _attr_unique_id = SENSOR_DEVICE_SCHEDULE
    _attr_icon = "mdi:devices"
    
    def update(self) -> None:
        """Update the sensor."""
        results = self.ems_integration.get_optimization_results()
        if results:
            schedule = results.get('schedule', {})
            
            # Count device actions
            total_actions = 0
            for device_name, device_sched in schedule.items():
                if device_name != 'battery':
                    actions = sum(1 for power in device_sched if power > 0)
                    total_actions += actions
            
            if total_actions > 0:
                self._attr_native_value = f"{total_actions} device actions planned"
            else:
                self._attr_native_value = "No device actions planned"
            
            self._attr_available = True
        else:
            self._attr_native_value = "No schedule data"
            self._attr_available = False
