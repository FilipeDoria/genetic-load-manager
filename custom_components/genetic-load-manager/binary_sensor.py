"""Binary Sensor platform for Genetic Load Manager."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Genetic Load Manager binary sensor platform."""
    
    # Get the optimizer instance
    optimizer = hass.data[DOMAIN].get('optimizer')
    if not optimizer:
        _LOGGER.error("Optimizer not found")
        return
    
    # Create binary sensors
    binary_sensors = [
        OptimizationRunningSensor(optimizer, config_entry),
        SystemHealthySensor(optimizer, config_entry),
        LoadsControlledSensor(optimizer, config_entry),
        AlgorithmErrorSensor(optimizer, config_entry)
    ]
    
    async_add_entities(binary_sensors, True)
    _LOGGER.info("Created %d genetic load manager binary sensors", len(binary_sensors))

class GeneticLoadManagerBinarySensor(BinarySensorEntity):
    """Base class for Genetic Load Manager binary sensors."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the binary sensor."""
        self.optimizer = optimizer
        self.config_entry = config_entry
        self._attr_should_poll = True
        self._attr_available = True

class OptimizationRunningSensor(GeneticLoadManagerBinarySensor):
    """Binary sensor for optimization running status."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Optimization Running"
        self._attr_unique_id = f"{config_entry.entry_id}_optimization_running"
        self._attr_icon = "mdi:play-circle"
        self._attr_device_class = "running"
    
    @property
    def is_on(self) -> Optional[bool]:
        """Return true if optimization is running."""
        status = self.optimizer.get_status()
        return status.get('is_running', False)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        status = self.optimizer.get_status()
        return {
            "current_generation": status.get('current_generation', 0),
            "best_fitness": status.get('best_fitness', 0.0),
            "optimization_count": status.get('optimization_count', 0)
        }

class SystemHealthySensor(GeneticLoadManagerBinarySensor):
    """Binary sensor for system health status."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager System Healthy"
        self._attr_unique_id = f"{config_entry.entry_id}_system_healthy"
        self._attr_icon = "mdi:heart-pulse"
        self._attr_device_class = "problem"
    
    @property
    def is_on(self) -> Optional[bool]:
        """Return true if system is healthy."""
        try:
            # Check if optimizer is running and has recent activity
            status = self.optimizer.get_status()
            
            if not status.get('is_running', False):
                return False
            
            # Check if there are any recent errors
            recent_logs = self.optimizer.get_logs(level='ERROR', limit=10)
            if recent_logs:
                # If there are errors in the last 10 logs, system might be unhealthy
                return False
            
            # Check if optimization is progressing
            if status.get('optimization_count', 0) == 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        try:
            status = self.optimizer.get_status()
            recent_errors = self.optimizer.get_logs(level='ERROR', limit=5)
            
            return {
                "optimization_running": status.get('is_running', False),
                "recent_errors": len(recent_errors),
                "last_optimization": status.get('last_optimization'),
                "system_status": "Healthy" if self.is_on else "Unhealthy"
            }
        except Exception:
            return {"system_status": "Unknown"}

class LoadsControlledSensor(GeneticLoadManagerBinarySensor):
    """Binary sensor for loads being controlled."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Loads Controlled"
        self._attr_unique_id = f"{config_entry.entry_id}_loads_controlled"
        self._attr_icon = "mdi:lightbulb-group"
        self._attr_device_class = "presence"
    
    @property
    def is_on(self) -> Optional[bool]:
        """Return true if loads are being controlled."""
        try:
            status = self.optimizer.get_status()
            manageable_loads = status.get('manageable_loads_count', 0)
            return manageable_loads > 0
        except Exception:
            return False
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        try:
            status = self.optimizer.get_status()
            return {
                "manageable_loads_count": status.get('manageable_loads_count', 0),
                "loads_available": self.is_on
            }
        except Exception:
            return {"loads_available": False}

class AlgorithmErrorSensor(GeneticLoadManagerBinarySensor):
    """Binary sensor for algorithm errors."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Algorithm Errors"
        self._attr_unique_id = f"{config_entry.entry_id}_algorithm_errors"
        self._attr_icon = "mdi:alert-circle"
        self._attr_device_class = "problem"
    
    @property
    def is_on(self) -> Optional[bool]:
        """Return true if there are algorithm errors."""
        try:
            recent_errors = self.optimizer.get_logs(level='ERROR', limit=5)
            return len(recent_errors) > 0
        except Exception:
            return False
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        try:
            recent_errors = self.optimizer.get_logs(level='ERROR', limit=5)
            error_summary = []
            
            for error in recent_errors:
                error_summary.append(f"{error['timestamp']}: {error['message']}")
            
            return {
                "error_count": len(recent_errors),
                "recent_errors": error_summary,
                "last_error": recent_errors[-1]['timestamp'] if recent_errors else None
            }
        except Exception:
            return {"error_count": 0} 