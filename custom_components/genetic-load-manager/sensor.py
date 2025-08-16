"""Sensor platform for Genetic Load Manager."""
import logging

from homeassistant.components.sensor import SensorEntity
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
    """Set up the Genetic Load Manager sensor platform."""
    
    # Get the optimizer instance
    optimizer = hass.data[DOMAIN].get('optimizer')
    if not optimizer:
        _LOGGER.error("Optimizer not found")
        return
    
    # Create sensors
    sensors = [
        GeneticLoadManagerStatusSensor(optimizer, config_entry),
        GeneticLoadManagerOptimizationSensor(optimizer, config_entry),
        GeneticLoadManagerFitnessSensor(optimizer, config_entry)
    ]
    
    async_add_entities(sensors, True)

class GeneticLoadManagerStatusSensor(SensorEntity):
    """Sensor for Genetic Load Manager status."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        self.optimizer = optimizer
        self.config_entry = config_entry
        self._attr_name = "Genetic Load Manager Status"
        self._attr_unique_id = f"{config_entry.entry_id}_status"
        self._attr_icon = "mdi:lightning-bolt"
        self._attr_should_poll = False
    
    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            status = self.optimizer.get_status()
            return "Running" if status.get('is_running', False) else "Stopped"
        except Exception:
            return "Unknown"
    
    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        try:
            status = self.optimizer.get_status()
            return {
                "integration": "Genetic Load Manager",
                "status": "Active" if status.get('is_running', False) else "Inactive",
                "optimization_count": status.get('optimization_count', 0),
                "last_optimization": status.get('last_optimization'),
                "next_optimization": status.get('next_optimization')
            }
        except Exception:
            return {
                "integration": "Genetic Load Manager",
                "status": "Unknown"
            }

class GeneticLoadManagerOptimizationSensor(SensorEntity):
    """Sensor for optimization progress."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        self.optimizer = optimizer
        self.config_entry = config_entry
        self._attr_name = "Genetic Load Manager Optimization Progress"
        self._attr_unique_id = f"{config_entry.entry_id}_progress"
        self._attr_icon = "mdi:chart-line"
        self._attr_should_poll = False
    
    @property
    def native_value(self):
        """Return the current generation."""
        try:
            status = self.optimizer.get_status()
            return status.get('current_generation', 0)
        except Exception:
            return 0
    
    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        try:
            status = self.optimizer.get_status()
            return {
                "total_generations": self.optimizer.generations,
                "population_size": self.optimizer.population_size,
                "mutation_rate": self.optimizer.mutation_rate,
                "crossover_rate": self.optimizer.crossover_rate
            }
        except Exception:
            return {}

class GeneticLoadManagerFitnessSensor(SensorEntity):
    """Sensor for best fitness score."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        self.optimizer = optimizer
        self.config_entry = config_entry
        self._attr_name = "Genetic Load Manager Best Fitness"
        self._attr_unique_id = f"{config_entry.entry_id}_fitness"
        self._attr_icon = "mdi:trophy"
        self._attr_should_poll = False
        self._attr_native_unit_of_measurement = "fitness"
    
    @property
    def native_value(self):
        """Return the best fitness score."""
        try:
            status = self.optimizer.get_status()
            return status.get('best_fitness', 0.0)
        except Exception:
            return 0.0
    
    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        try:
            status = self.optimizer.get_status()
            return {
                "manageable_loads_count": status.get('manageable_loads_count', 0),
                "log_entries_count": status.get('log_entries_count', 0)
            }
        except Exception:
            return {}