"""Sensor platform for Genetic Load Manager."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_NAME,
    CONF_ENTITY_ID,
    ATTR_DEVICE_CLASS,
    ATTR_UNIT_OF_MEASUREMENT,
)

from .const import (
    DOMAIN,
    ATTR_OPTIMIZATION_STATUS,
    ATTR_LAST_OPTIMIZATION,
    ATTR_NEXT_OPTIMIZATION,
    ATTR_OPTIMIZATION_COUNT,
    ATTR_BEST_FITNESS,
    ATTR_CURRENT_SCHEDULE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Genetic Load Manager sensor platform."""
    
    # Get the optimizer instance
    optimizer = hass.data[DOMAIN].get('optimizer')
    if not optimizer:
        _LOGGER.error("Optimizer not found")
        return
    
    # Create sensors
    sensors = [
        OptimizationStatusSensor(optimizer, config_entry),
        LastOptimizationSensor(optimizer, config_entry),
        NextOptimizationSensor(optimizer, config_entry),
        OptimizationCountSensor(optimizer, config_entry),
        BestFitnessSensor(optimizer, config_entry),
    ]
    
    async_add_entities(sensors, True)

class GeneticLoadManagerSensor(SensorEntity):
    """Base class for Genetic Load Manager sensors."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        self.optimizer = optimizer
        self.config_entry = config_entry
        self._attr_attribution = "Genetic Load Manager"
        self._attr_should_poll = True
        self._attr_available = True

class OptimizationStatusSensor(GeneticLoadManagerSensor):
    """Sensor for optimization status."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Status"
        self._attr_unique_id = f"{config_entry.entry_id}_status"
        self._attr_icon = "mdi:lightning-bolt"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        return status.get(ATTR_OPTIMIZATION_STATUS, "unknown")
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_ATTRIBUTION: "Genetic Load Manager",
        }

class LastOptimizationSensor(GeneticLoadManagerSensor):
    """Sensor for last optimization time."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Last Optimization"
        self._attr_unique_id = f"{config_entry.entry_id}_last_optimization"
        self._attr_icon = "mdi:clock-outline"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        last_opt = status.get(ATTR_LAST_OPTIMIZATION)
        if last_opt:
            return datetime.fromisoformat(last_opt).strftime("%Y-%m-%d %H:%M:%S")
        return "Never"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_ATTRIBUTION: "Genetic Load Manager",
        }

class NextOptimizationSensor(GeneticLoadManagerSensor):
    """Sensor for next optimization time."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Next Optimization"
        self._attr_unique_id = f"{config_entry.entry_id}_next_optimization"
        self._attr_icon = "mdi:clock-alert-outline"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        next_opt = status.get(ATTR_NEXT_OPTIMIZATION)
        if next_opt:
            return datetime.fromisoformat(next_opt).strftime("%Y-%m-%d %H:%M:%S")
        return "Unknown"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_ATTRIBUTION: "Genetic Load Manager",
        }

class OptimizationCountSensor(GeneticLoadManagerSensor):
    """Sensor for optimization count."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Optimization Count"
        self._attr_unique_id = f"{config_entry.entry_id}_optimization_count"
        self._attr_icon = "mdi:counter"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        return status.get(ATTR_OPTIMIZATION_COUNT, 0)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_ATTRIBUTION: "Genetic Load Manager",
        }

class BestFitnessSensor(GeneticLoadManagerSensor):
    """Sensor for best fitness score."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Best Fitness"
        self._attr_unique_id = f"{config_entry.entry_id}_best_fitness"
        self._attr_icon = "mdi:chart-line"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        return round(status.get(ATTR_BEST_FITNESS, 0.0), 4)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_ATTRIBUTION: "Genetic Load Manager",
        } 