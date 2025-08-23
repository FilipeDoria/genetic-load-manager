"""Binary sensor platform for Genetic Load Manager integration."""
import logging
from typing import Any, Dict, Optional
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType = None):
    """Set up the Genetic Load Manager binary sensor platform."""
    
    # Get the genetic algorithm instance
    genetic_algo = hass.data[DOMAIN].get('genetic_algorithm')
    if not genetic_algo:
        _LOGGER.error("Genetic algorithm not found")
        return
    
    # Create binary sensors
    binary_sensors = [
        OptimizationRunningSensor(genetic_algo, entry),
        SystemHealthySensor(genetic_algo, entry),
        LoadsControlledSensor(genetic_algo, entry),
        AlgorithmErrorSensor(genetic_algo, entry)
    ]
    
    async_add_entities(binary_sensors, True)
    _LOGGER.info("Created %d genetic load manager binary sensors", len(binary_sensors))

class GeneticLoadManagerBinarySensor(BinarySensorEntity):
    """Base class for Genetic Load Manager binary sensors."""
    
    def __init__(self, genetic_algo, config_entry: ConfigEntry):
        """Initialize the binary sensor."""
        self.genetic_algo = genetic_algo
        self.config_entry = config_entry
        self._attr_should_poll = True
        self._attr_available = True

class OptimizationRunningSensor(GeneticLoadManagerBinarySensor):
    """Binary sensor for optimization running status."""
    
    def __init__(self, genetic_algo, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(genetic_algo, config_entry)
        self._attr_name = "Genetic Load Manager Optimization Running"
        self._attr_unique_id = f"{config_entry.entry_id}_optimization_running"
        self._attr_icon = "mdi:play-circle"
        self._attr_device_class = "running"
    
    @property
    def is_on(self) -> Optional[bool]:
        """Return true if optimization is running."""
        return self.genetic_algo.is_running
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "is_running": self.genetic_algo.is_running,
            "population_size": getattr(self.genetic_algo, 'population_size', 0),
            "generations": getattr(self.genetic_algo, 'generations', 0),
            "num_devices": getattr(self.genetic_algo, 'num_devices', 0)
        }

class SystemHealthySensor(GeneticLoadManagerBinarySensor):
    """Binary sensor for system health status."""
    
    def __init__(self, genetic_algo, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(genetic_algo, config_entry)
        self._attr_name = "Genetic Load Manager System Healthy"
        self._attr_unique_id = f"{config_entry.entry_id}_system_healthy"
        self._attr_icon = "mdi:heart-pulse"
        self._attr_device_class = "problem"
    
    @property
    def is_on(self) -> Optional[bool]:
        """Return true if system is healthy."""
        try:
            # Check if genetic algorithm is running
            if not self.genetic_algo.is_running:
                return False
            
            # Check if we have forecast data
            if not hasattr(self.genetic_algo, 'pv_forecast') or self.genetic_algo.pv_forecast is None:
                return False
            
            if not hasattr(self.genetic_algo, 'load_forecast') or self.genetic_algo.load_forecast is None:
                return False
            
            return True
            
        except Exception:
            return False
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        try:
            return {
                "optimization_running": self.genetic_algo.is_running,
                "pv_forecast_available": hasattr(self.genetic_algo, 'pv_forecast') and self.genetic_algo.pv_forecast is not None,
                "load_forecast_available": hasattr(self.genetic_algo, 'load_forecast') and self.genetic_algo.load_forecast is not None,
                "battery_soc_available": hasattr(self.genetic_algo, 'battery_soc_entity') and self.genetic_algo.battery_soc_entity is not None
            }
        except Exception:
            return {"error": "Unable to get system status"}

class LoadsControlledSensor(GeneticLoadManagerBinarySensor):
    """Binary sensor for loads controlled status."""
    
    def __init__(self, genetic_algo, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(genetic_algo, config_entry)
        self._attr_name = "Genetic Load Manager Loads Controlled"
        self._attr_unique_id = f"{config_entry.entry_id}_loads_controlled"
        self._attr_icon = "mdi:lightning-bolt"
        self._attr_device_class = "power"
    
    @property
    def is_on(self) -> Optional[bool]:
        """Return true if loads are being controlled."""
        try:
            # Check if we have manageable loads
            if not hasattr(self.genetic_algo, 'num_devices'):
                return False
            
            return self.genetic_algo.num_devices > 0
            
        except Exception:
            return False
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        try:
            return {
                "num_devices": getattr(self.genetic_algo, 'num_devices', 0),
                "device_priorities": getattr(self.genetic_algo, 'device_priorities', []),
                "battery_capacity": getattr(self.genetic_algo, 'battery_capacity', 0.0)
            }
        except Exception:
            return {"error": "Unable to get loads status"}

class AlgorithmErrorSensor(GeneticLoadManagerBinarySensor):
    """Binary sensor for algorithm error status."""
    
    def __init__(self, genetic_algo, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(genetic_algo, config_entry)
        self._attr_name = "Genetic Load Manager Algorithm Error"
        self._attr_unique_id = f"{config_entry.entry_id}_algorithm_error"
        self._attr_icon = "mdi:alert-circle"
        self._attr_device_class = "problem"
    
    @property
    def is_on(self) -> Optional[bool]:
        """Return true if there are algorithm errors."""
        try:
            # For now, we'll consider it an error if the genetic algorithm is not running
            # when it should be, or if critical attributes are missing
            if not self.genetic_algo.is_running:
                return True
            
            # Check for critical missing attributes
            critical_attrs = ['pv_forecast_entity', 'load_forecast_entity', 'battery_soc_entity']
            for attr in critical_attrs:
                if not hasattr(self.genetic_algo, attr) or getattr(self.genetic_algo, attr) is None:
                    return True
            
            return False
            
        except Exception:
            return True
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        try:
            return {
                "is_running": self.genetic_algo.is_running,
                "pv_forecast_entity": getattr(self.genetic_algo, 'pv_forecast_entity', None),
                "load_forecast_entity": getattr(self.genetic_algo, 'load_forecast_entity', None),
                "battery_soc_entity": getattr(self.genetic_algo, 'battery_soc_entity', None),
                "dynamic_pricing_entity": getattr(self.genetic_algo, 'dynamic_pricing_entity', None)
            }
        except Exception:
            return {"error": "Unable to get error status"} 