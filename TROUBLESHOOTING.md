# Troubleshooting Guide - Genetic Load Manager

## Quick Fix for Common Warnings

### 1. **"No PV tomorrow forecast entity configured"**
**Problem**: The integration can't find solar forecast data
**Quick Fix**: Add this to your `configuration.yaml`:
```yaml
genetic_load_manager:
  pv_forecast_today: "sensor.solcast_pv_forecast_today"
  pv_forecast_tomorrow: "sensor.solcast_pv_forecast_tomorrow"
```
**Alternative**: Create placeholder entities:
```yaml
sensor:
  - platform: template
    sensors:
      solcast_pv_forecast_today:
        friendly_name: "PV Forecast Today"
        value_template: "0"
        attributes:
          DetailedForecast: []
      solcast_pv_forecast_tomorrow:
        friendly_name: "PV Forecast Tomorrow"
        value_template: "0"
        attributes:
          DetailedForecast: []
```

### 2. **"No Solcast PV forecast data available, using zeros"**
**Problem**: PV forecast entities exist but have no data
**Quick Fix**: Check if your Solcast integration is working
**Alternative**: Use OpenWeatherMap for basic solar data:
```yaml
sensor:
  - platform: openweathermap
    api_key: YOUR_API_KEY
    monitored_conditions:
      - solar_radiation
```

### 3. **"No load forecast entity configured"**
**Problem**: Missing load consumption prediction
**Quick Fix**: Add this to your `configuration.yaml`:
```yaml
genetic_load_manager:
  load_forecast: "sensor.load_forecast"
```
**Alternative**: Create a simple load forecast:
```yaml
sensor:
  - platform: template
    sensors:
      load_forecast:
        friendly_name: "Load Forecast"
        value_template: "{{ 0.5 }}"
        attributes:
          forecast: "{{ [0.5] * 96 }}"
```

### 4. **"No load sensor entity specified, setting forecast to zeros"**
**Problem**: Missing historical load data source
**Quick Fix**: Configure a load sensor:
```yaml
genetic_load_manager:
  load_sensor: "sensor.power_consumption"
```
**Alternative**: Use any power sensor you have:
```yaml
genetic_load_manager:
  load_sensor: "sensor.smart_meter_power"  # or any power sensor
```

### 5. **"No market price entity configured, using default"**
**Problem**: Missing electricity pricing data
**Quick Fix**: Add this to your `configuration.yaml`:
```yaml
genetic_load_manager:
  market_price: "sensor.omie_electricity_price"
```
**Alternative**: Create a simple price sensor:
```yaml
sensor:
  - platform: template
    sensors:
      omie_electricity_price:
        friendly_name: "Electricity Price"
        value_template: "{{ 50 }}"  # Default price
        unit_of_measurement: "€/MWh"
```

### 6. **"State attributes exceed maximum size of 16384 bytes"**
**Problem**: Too much data stored in sensor attributes
**Quick Fix**: The integration automatically handles this now
**Alternative**: Check your logs for detailed data instead of attributes

## Complete Minimal Configuration

To eliminate ALL warnings, use this minimal configuration:

```yaml
# configuration.yaml
genetic_load_manager:
  optimization_mode: "cost_savings"
  update_interval: 15
  
  # Required entities (will use defaults if not specified)
  pv_forecast_today: "sensor.solcast_pv_forecast_today"
  pv_forecast_tomorrow: "sensor.solcast_pv_forecast_tomorrow"
  load_forecast: "sensor.load_forecast"
  battery_soc: "sensor.battery_soc"
  market_price: "sensor.omie_electricity_price"
```

## Entity Creation Commands

Run these commands in Home Assistant to create required entities:

### 1. Create PV Forecast Sensors
```yaml
# Developer Tools > YAML
sensor:
  - platform: template
    sensors:
      solcast_pv_forecast_today:
        friendly_name: "PV Forecast Today"
        value_template: "0"
        attributes:
          DetailedForecast: []
      solcast_pv_forecast_tomorrow:
        friendly_name: "PV Forecast Tomorrow"
        value_template: "0"
        attributes:
          DetailedForecast: []
```

### 2. Create Load Forecast Sensor
```yaml
# Developer Tools > YAML
sensor:
  - platform: template
    sensors:
      load_forecast:
        friendly_name: "Load Forecast"
        value_template: "{{ 0.5 }}"
        attributes:
          forecast: "{{ [0.5] * 96 }}"
```

### 3. Create Battery Sensor
```yaml
# Developer Tools > YAML
sensor:
  - platform: template
    sensors:
      battery_soc:
        friendly_name: "Battery Level"
        value_template: "{{ 50 }}"
        unit_of_measurement: "%"
```

### 4. Create Market Price Sensor
```yaml
# Developer Tools > YAML
sensor:
  - platform: template
    sensors:
      omie_electricity_price:
        friendly_name: "Electricity Price"
        value_template: "{{ 50 }}"
        unit_of_measurement: "€/MWh"
```

## Testing Your Configuration

### 1. Check Entity Status
```yaml
# Developer Tools > States
# Search for: solcast_pv_forecast_today, load_forecast, battery_soc, omie_electricity_price
```

### 2. Test Entity Values
```yaml
# Developer Tools > Templates
{{ states('sensor.solcast_pv_forecast_today') }}
{{ state_attr('sensor.load_forecast', 'forecast') }}
{{ states('sensor.battery_soc') }}
{{ states('sensor.omie_electricity_price') }}
```

### 3. Check Integration Logs
```yaml
# Configuration > Logs
# Look for: genetic_load_manager
# Should see: "Integration loaded successfully" instead of warnings
```

## Performance Optimization

### 1. Reduce Update Frequency
```yaml
genetic_load_manager:
  update_interval: 30  # Update every 30 minutes instead of 15
```

### 2. Use Simple Entity Types
- Prefer `sensor` over complex integrations
- Use `template` sensors for simple data
- Avoid storing large datasets in attributes

### 3. Limit Genetic Algorithm Complexity
```yaml
genetic_load_manager:
  population_size: 50   # Smaller population
  generations: 100      # Fewer generations
```

## Common Mistakes to Avoid

1. **Missing Entity IDs**: Always verify entities exist before configuring
2. **Wrong Data Format**: Ensure entities return expected data types
3. **Too Many Updates**: Don't set update_interval too low
4. **Complex Templates**: Keep sensor templates simple
5. **Large Attributes**: Don't store big datasets in entity attributes

## Still Getting Warnings?

If you still see warnings after following this guide:

1. **Check Entity Names**: Ensure exact spelling and case
2. **Verify Data Types**: Numbers should be numeric, not strings
3. **Test Templates**: Use Developer Tools to test your sensor templates
4. **Check Permissions**: Ensure entities are accessible
5. **Restart Home Assistant**: After configuration changes

## Emergency Configuration

If nothing else works, use this ultra-minimal configuration:

```yaml
# configuration.yaml
genetic_load_manager:
  optimization_mode: "cost_savings"
  update_interval: 60  # Update every hour
```

This will use all default values and should eliminate warnings, though with limited functionality.

## Getting Help

1. **Check Logs**: Look for specific error messages
2. **Verify Configuration**: Use YAML validation tools
3. **Test Entities**: Use Developer Tools to verify entity data
4. **Simplify**: Start with minimal configuration and add complexity gradually
5. **Report Issues**: Include logs, configuration, and entity states
