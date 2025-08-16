"""Enhanced sensor platform for Genetic Load Manager."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    PERCENTAGE,
    POWER_WATT,
    ENERGY_KILO_WATT_HOUR,
    CURRENCY_EURO
)

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
    
    # Create all sensors
    sensors = [
        OptimizationStatusSensor(optimizer, config_entry),
        LastOptimizationSensor(optimizer, config_entry),
        NextOptimizationSensor(optimizer, config_entry),
        OptimizationCountSensor(optimizer, config_entry),
        BestFitnessSensor(optimizer, config_entry),
        CurrentGenerationSensor(optimizer, config_entry),
        ManageableLoadsSensor(optimizer, config_entry),
        SystemEfficiencySensor(optimizer, config_entry),
        EnergyCostSensor(optimizer, config_entry),
        SolarUtilizationSensor(optimizer, config_entry),
        LoadControlStatusSensor(optimizer, config_entry),
        AlgorithmLogsSensor(optimizer, config_entry)
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
        return "Running" if status.get('is_running', False) else "Stopped"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        status = self.optimizer.get_status()
        return {
            ATTR_ATTRIBUTION: "Genetic Load Manager",
            "optimization_count": status.get('optimization_count', 0),
            "manageable_loads": status.get('manageable_loads_count', 0),
            "log_entries": status.get('log_entries_count', 0)
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
        last_opt = status.get('last_optimization')
        if last_opt:
            return datetime.fromisoformat(last_opt).strftime("%Y-%m-%d %H:%M:%S")
        return "Never"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

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
        next_opt = status.get('next_optimization')
        if next_opt:
            return datetime.fromisoformat(next_opt).strftime("%Y-%m-%d %H:%M:%S")
        return "Unknown"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

class OptimizationCountSensor(GeneticLoadManagerSensor):
    """Sensor for optimization count."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Optimization Count"
        self._attr_unique_id = f"{config_entry.entry_id}_optimization_count"
        self._attr_icon = "mdi:counter"
        self._attr_state_class = SensorStateClass.TOTAL
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        return status.get('optimization_count', 0)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

class BestFitnessSensor(GeneticLoadManagerSensor):
    """Sensor for best fitness score."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Best Fitness"
        self._attr_unique_id = f"{config_entry.entry_id}_best_fitness"
        self._attr_icon = "mdi:chart-line"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "fitness"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        return round(status.get('best_fitness', 0.0), 4)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

class CurrentGenerationSensor(GeneticLoadManagerSensor):
    """Sensor for current generation."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Current Generation"
        self._attr_unique_id = f"{config_entry.entry_id}_current_generation"
        self._attr_icon = "mdi:genetic"
        self._attr_state_class = SensorStateClass.MEASUREMENT
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        return status.get('current_generation', 0)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

class ManageableLoadsSensor(GeneticLoadManagerSensor):
    """Sensor for manageable loads count."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Manageable Loads"
        self._attr_unique_id = f"{config_entry.entry_id}_manageable_loads"
        self._attr_icon = "mdi:lightbulb-group"
        self._attr_state_class = SensorStateClass.MEASUREMENT
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        return status.get('manageable_loads_count', 0)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

class SystemEfficiencySensor(GeneticLoadManagerSensor):
    """Sensor for system efficiency."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager System Efficiency"
        self._attr_unique_id = f"{config_entry.entry_id}_system_efficiency"
        self._attr_icon = "mdi:gauge"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        best_fitness = status.get('best_fitness', 0.0)
        # Convert fitness to efficiency percentage (0-100%)
        efficiency = min(100.0, max(0.0, (best_fitness / 1000.0) * 100))
        return round(efficiency, 1)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

class EnergyCostSensor(GeneticLoadManagerSensor):
    """Sensor for energy cost optimization."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Energy Cost"
        self._attr_unique_id = f"{config_entry.entry_id}_energy_cost"
        self._attr_icon = "mdi:currency-eur"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = CURRENCY_EURO
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        # This would be calculated based on the current schedule and electricity prices
        # For now, return a placeholder value
        return 0.0
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

class SolarUtilizationSensor(GeneticLoadManagerSensor):
    """Sensor for solar power utilization."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Solar Utilization"
        self._attr_unique_id = f"{config_entry.entry_id}_solar_utilization"
        self._attr_icon = "mdi:solar-power"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        # This would be calculated based on solar production and load consumption
        # For now, return a placeholder value
        return 75.0
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

class LoadControlStatusSensor(GeneticLoadManagerSensor):
    """Sensor for load control status."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Load Control Status"
        self._attr_unique_id = f"{config_entry.entry_id}_load_control_status"
        self._attr_icon = "mdi:power-plug"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        # This would show the current load control status
        return "Active"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {ATTR_ATTRIBUTION: "Genetic Load Manager"}

class AlgorithmLogsSensor(GeneticLoadManagerSensor):
    """Sensor for algorithm logs."""
    
    def __init__(self, optimizer, config_entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(optimizer, config_entry)
        self._attr_name = "Genetic Load Manager Algorithm Logs"
        self._attr_unique_id = f"{config_entry.entry_id}_algorithm_logs"
        self._attr_icon = "mdi:file-document"
    
    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        status = self.optimizer.get_status()
        return f"{status.get('log_entries_count', 0)} log entries"
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        # Get recent logs
        recent_logs = self.optimizer.get_logs(limit=10)
        log_summary = []
        
        for log in recent_logs:
            log_summary.append(f"{log['timestamp']} [{log['level']}]: {log['message']}")
        
        return {
            ATTR_ATTRIBUTION: "Genetic Load Manager",
            "recent_logs": log_summary,
            "total_logs": len(recent_logs)
        } 