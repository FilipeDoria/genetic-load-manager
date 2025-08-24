# Adding Sensors and Entities to Genetic Load Manager

## 🎯 **Overview**
This guide explains how to add new sensors, binary sensors, and entities to the Genetic Load Manager integration.

## 📁 **File Structure for Entities**
```
custom_components/genetic-load-manager/
├── __init__.py              # Main integration setup
├── sensor.py               # Sensor entities
├── binary_sensor.py        # Binary sensor entities  
├── switch.py              # Switch entities
├── dashboard.py           # Dashboard sensors
├── control_panel.py       # Control panel sensors
├── analytics.py           # Analytics sensors
└── const.py              # Constants
```

## 🔧 **Method 1: Add to Existing Platform (Recommended)**

### **Adding a New Sensor**

1. **Create the Sensor Class** in `sensor.py`:
```python
class MyNewSensor(SensorEntity):
    """My new custom sensor."""
    
    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the sensor."""
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_my_new_sensor"
        self._attr_name = "My New Sensor"
        self._attr_unit_of_measurement = "units"
        self._attr_device_class = "measurement"  # or appropriate class
        self._state = None
        
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
        
    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "custom_attribute": "value",
            "last_updated": datetime.now().isoformat()
        }
        
    async def async_added_to_hass(self):
        """Set up periodic updates."""
        async_track_time_interval(self.hass, self.async_update, timedelta(minutes=5))
        await self.async_update()
        
    async def async_update(self):
        """Update sensor state."""
        try:
            # Your sensor logic here
            self._state = self._calculate_sensor_value()
        except Exception as e:
            _LOGGER.error(f"Error updating sensor: {e}")
            
    def _calculate_sensor_value(self):
        """Calculate the sensor value."""
        # Your calculation logic
        return 42
```

2. **Register the Sensor** in `async_setup_entry()`:
```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigType, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType = None):
    """Set up the sensor platform."""
    sensors = [
        LoadForecastSensor(hass, entry.data),
        MyNewSensor(hass, entry.data),  # Add your new sensor here
    ]
    
    # Add conditional sensors
    if entry.data.get("use_indexed_pricing", True):
        sensors.append(IndexedPricingSensor(hass, entry.data))
    
    async_add_entities(sensors)
```

### **Adding a New Binary Sensor**

1. **Create the Binary Sensor Class** in `binary_sensor.py`:
```python
class MyNewBinarySensor(GeneticLoadManagerBinarySensor):
    """My new binary sensor."""
    
    def __init__(self, genetic_algo, config_entry: ConfigEntry):
        """Initialize the binary sensor."""
        super().__init__(genetic_algo, config_entry)
        self._attr_name = "My New Binary Sensor"
        self._attr_unique_id = f"{config_entry.entry_id}_my_new_binary"
        self._attr_icon = "mdi:check-circle"
        self._attr_device_class = "connectivity"  # or appropriate class
    
    @property
    def is_on(self) -> Optional[bool]:
        """Return true if condition is met."""
        try:
            # Your binary logic here
            return self._check_condition()
        except Exception:
            return False
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "condition_details": self._get_condition_details(),
            "last_check": datetime.now().isoformat()
        }
        
    def _check_condition(self) -> bool:
        """Check the binary condition."""
        # Your condition logic
        return True
        
    def _get_condition_details(self) -> str:
        """Get details about the condition."""
        return "Condition is met"
```

2. **Register the Binary Sensor**:
```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType = None):
    """Set up binary sensors."""
    binary_sensors = [
        OptimizationRunningSensor(genetic_algo, entry),
        SystemHealthySensor(genetic_algo, entry),
        LoadsControlledSensor(genetic_algo, entry),
        AlgorithmErrorSensor(genetic_algo, entry),
        MyNewBinarySensor(genetic_algo, entry),  # Add here
    ]
    
    async_add_entities(binary_sensors, True)
```

## 🔧 **Method 2: Create New Platform File**

### **1. Create New Platform File** (e.g., `number.py`):
```python
"""Number platform for Genetic Load Manager integration."""
import logging
from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up number entities."""
    numbers = [
        PopulationSizeNumber(hass, entry),
        GenerationsNumber(hass, entry),
        MutationRateNumber(hass, entry),
    ]
    
    async_add_entities(numbers)

class PopulationSizeNumber(NumberEntity):
    """Number entity for population size."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self._attr_unique_id = f"{DOMAIN}_population_size"
        self._attr_name = "Population Size"
        self._attr_min_value = 50
        self._attr_max_value = 500
        self._attr_step = 10
        self._attr_icon = "mdi:account-group"
        self._value = 100
        
    @property
    def value(self) -> float:
        return self._value
        
    async def async_set_value(self, value: float) -> None:
        """Set the population size."""
        self._value = int(value)
        
        # Update genetic algorithm
        genetic_algo = self.hass.data[DOMAIN].get('genetic_algorithm')
        if genetic_algo:
            genetic_algo.population_size = self._value
            
        self.async_write_ha_state()
```

### **2. Register New Platform** in `__init__.py`:
```python
PLATFORMS = ["sensor", "binary_sensor", "switch", "number"]  # Add your platform
```

## 🔧 **Method 3: Dynamic Entity Creation**

### **Create Entities Based on Configuration**:
```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up sensors dynamically."""
    sensors = []
    
    # Always create base sensors
    sensors.append(LoadForecastSensor(hass, entry.data))
    
    # Create device-specific sensors
    num_devices = entry.data.get("num_devices", 2)
    for device_id in range(num_devices):
        sensors.append(DeviceEfficiencySensor(hass, entry.data, device_id))
        sensors.append(DeviceCostSensor(hass, entry.data, device_id))
    
    # Create optional sensors based on config
    if entry.data.get("enable_weather_integration"):
        sensors.append(WeatherOptimizationSensor(hass, entry.data))
    
    if entry.data.get("enable_grid_monitoring"):
        sensors.append(GridStabilitySensor(hass, entry.data))
    
    async_add_entities(sensors)
```

## 📊 **Common Sensor Types to Add**

### **Performance Monitoring Sensors**:
- **Algorithm Performance**: Convergence rate, execution time
- **Device Efficiency**: Individual device optimization scores
- **Energy Flow**: Import/export tracking, self-consumption
- **Cost Breakdown**: Real-time cost per device, tariff components

### **Diagnostic Sensors**:
- **System Health**: Component status, error counts
- **Data Quality**: Forecast accuracy, sensor availability
- **Communication**: API response times, connection status

### **User Interface Sensors**:
- **Quick Stats**: Summary metrics for dashboards
- **Trend Analysis**: Historical performance trends
- **Predictions**: Future cost/savings forecasts

## 🎛️ **Adding Control Entities**

### **Input Number for Parameters**:
```python
class ParameterInputNumber(NumberEntity):
    """Input number for GA parameters."""
    
    async def async_set_value(self, value: float) -> None:
        """Update parameter and trigger recalculation."""
        self._value = value
        
        # Trigger parameter update service
        await self.hass.services.async_call(
            DOMAIN, "update_parameters",
            {self._parameter_name: value}
        )
```

### **Select for Mode Switching**:
```python
class ModeSelectEntity(SelectEntity):
    """Select entity for optimization mode."""
    
    @property
    def options(self) -> list[str]:
        return ["genetic", "rule-based", "manual", "eco", "comfort"]
    
    async def async_select_option(self, option: str) -> None:
        """Change optimization mode."""
        await self.hass.services.async_call(
            DOMAIN, "set_mode", {"mode": option}
        )
```

## 🔄 **Update Patterns**

### **Real-time Updates** (Every 1-2 minutes):
- System status, current pricing, active schedules

### **Periodic Updates** (Every 5-15 minutes):
- Performance metrics, cost analysis, forecasts

### **Event-driven Updates**:
- Optimization completion, error states, user actions

## 📝 **Best Practices**

1. **Use Unique IDs**: Always include domain and descriptive identifier
2. **Error Handling**: Wrap update logic in try/catch blocks
3. **Efficient Updates**: Don't update unnecessarily, use caching
4. **Meaningful Attributes**: Provide rich attribute data for dashboards
5. **Device Classes**: Use appropriate device classes for proper UI display
6. **State Classes**: Use measurement/total/total_increasing as appropriate

## 🧪 **Testing New Entities**

1. **Check Logs**: Monitor Home Assistant logs for errors
2. **Developer Tools**: Use States tab to verify entity creation
3. **Lovelace Cards**: Test entity display in dashboards
4. **Services**: Verify service calls work correctly
5. **Restart Testing**: Ensure entities survive HA restarts

## 📚 **Useful Entity Types**

- **Sensor**: Numeric values with units (temperature, power, cost)
- **Binary Sensor**: On/off states (running, healthy, error)
- **Switch**: Controllable on/off entities
- **Number**: Adjustable numeric parameters
- **Select**: Choose from predefined options
- **Button**: Trigger actions/services
- **Text**: Display or input text values

This comprehensive approach allows you to extend the Genetic Load Manager with any sensors or entities you need for monitoring, control, or visualization!
