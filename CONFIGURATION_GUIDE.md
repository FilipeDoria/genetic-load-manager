# Genetic Load Manager - Configuration Guide

## Overview
This guide helps you configure the Genetic Load Manager integration to avoid common warnings and errors. The integration will work with default values, but for optimal performance, you should configure the required entities.

## Quick Start - Minimal Configuration
The integration will work with just these basic settings:
```yaml
# configuration.yaml
genetic_load_manager:
  optimization_mode: "cost_savings"  # or "carbon_reduction", "grid_stability"
  update_interval: 15  # minutes
```

## Required Entities Configuration

### 1. PV Forecast Entities (Solar Generation)
**Purpose**: Predict solar energy generation for optimization
**Default**: `sensor.solcast_pv_forecast_today` and `sensor.solcast_pv_forecast_tomorrow`

**Recommended Integrations**:
- **Solcast**: Provides detailed 15-minute PV forecasts
- **OpenWeatherMap**: Basic solar radiation data
- **Custom**: Your own solar forecasting system

**Configuration**:
```yaml
genetic_load_manager:
  pv_forecast_today: "sensor.solcast_pv_forecast_today"
  pv_forecast_tomorrow: "sensor.solcast_pv_forecast_tomorrow"
```

**Entity Structure**:
```yaml
# Example Solcast entity attributes
sensor.solcast_pv_forecast_today:
  DetailedForecast:
    - period_start: "2024-01-15T00:00:00Z"
      pv_estimate: 0.0
    - period_start: "2024-01-15T00:15:00Z"
      pv_estimate: 0.1
    # ... 96 entries for 24 hours
```

### 2. Load Forecast Entity
**Purpose**: Predict household energy consumption
**Default**: `sensor.load_forecast`

**Recommended Integrations**:
- **Energy Dashboard**: Historical consumption patterns
- **Custom Load Prediction**: ML-based forecasting
- **Simple Historical**: Last 24 hours average

**Configuration**:
```yaml
genetic_load_manager:
  load_forecast: "sensor.load_forecast"
```

**Entity Structure**:
```yaml
# Example load forecast entity
sensor.load_forecast:
  forecast: [0.5, 0.6, 0.4, ...]  # 96 values for 15-minute slots
  unit_of_measurement: "kWh"
```

### 3. Battery State of Charge
**Purpose**: Monitor battery storage level
**Default**: `sensor.battery_soc`

**Recommended Integrations**:
- **Tesla Powerwall**: `sensor.powerwall_charge`
- **Generic Battery**: `sensor.battery_level`
- **Custom Battery**: Your own battery monitoring

**Configuration**:
```yaml
genetic_load_manager:
  battery_soc: "sensor.battery_soc"
```

**Entity Structure**:
```yaml
# Example battery entity
sensor.battery_soc:
  state: "75.5"  # Percentage (0-100)
  unit_of_measurement: "%"
```

### 4. Market Price Entity
**Purpose**: Real-time electricity pricing
**Default**: `sensor.omie_electricity_price`

**Recommended Integrations**:
- **OMIE Spain**: Iberian electricity market
- **Nord Pool**: European electricity prices
- **Custom API**: Your energy retailer's pricing

**Configuration**:
```yaml
genetic_load_manager:
  market_price: "sensor.omie_electricity_price"
```

**Entity Structure**:
```yaml
# Example market price entity
sensor.omie_electricity_price:
  state: "45.67"  # Price in €/MWh
  unit_of_measurement: "€/MWh"
```

## Optional Entities

### 5. Grid Export Limit
**Purpose**: Maximum power you can export to grid
**Default**: `sensor.grid_export_limit`

### 6. Demand Response
**Purpose**: Grid stability signals
**Default**: `binary_sensor.demand_response_active`

### 7. Carbon Intensity
**Purpose**: Environmental impact optimization
**Default**: `sensor.carbon_intensity`

### 8. Weather
**Purpose**: Weather-based load prediction
**Default**: `weather.home`

### 9. Smart Devices
**Purpose**: Controllable loads for optimization
**Defaults**:
- EV Charger: `switch.ev_charger`
- Thermostat: `climate.home_thermostat`
- Smart Plug: `switch.smart_plug`
- Lighting: `light.living_room`
- Media Player: `media_player.tv`

## Complete Configuration Example

```yaml
# configuration.yaml
genetic_load_manager:
  # Basic settings
  optimization_mode: "cost_savings"
  update_interval: 15
  
  # Required entities
  pv_forecast_today: "sensor.solcast_pv_forecast_today"
  pv_forecast_tomorrow: "sensor.solcast_pv_forecast_tomorrow"
  load_forecast: "sensor.load_forecast"
  battery_soc: "sensor.powerwall_charge"
  market_price: "sensor.omie_electricity_price"
  
  # Optional entities
  grid_export_limit: "sensor.grid_export_limit"
  demand_response: "binary_sensor.demand_response_active"
  carbon_intensity: "sensor.carbon_intensity"
  weather: "weather.home"
  
  # Controllable devices
  ev_charger: "switch.ev_charger"
  smart_thermostat: "climate.home_thermostat"
  smart_plug: "switch.smart_plug"
  lighting: "light.living_room"
  media_player: "media_player.tv"
  
  # Advanced settings
  population_size: 100
  generations: 200
  mutation_rate: 0.1
  crossover_rate: 0.8
```

## Entity Creation Examples

### Create a Simple Load Forecast Sensor
```yaml
# configuration.yaml
sensor:
  - platform: template
    sensors:
      load_forecast:
        friendly_name: "Load Forecast"
        value_template: "{{ states('sensor.power_consumption') | float * 0.25 }}"
        unit_of_measurement: "kWh"
        attributes:
          forecast: "{{ [0.5] * 96 }}"
```

### Create a Market Price Sensor
```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: "OMIE Electricity Price"
    resource: "https://api.omie.es/electricity/price"
    value_template: "{{ value_json.price }}"
    unit_of_measurement: "€/MWh"
    scan_interval: 300  # 5 minutes
```

## Troubleshooting Common Issues

### 1. "No PV forecast entity configured"
**Solution**: Configure `pv_forecast_today` and `pv_forecast_tomorrow` entities
**Alternative**: The integration will use zero values (no solar generation)

### 2. "No load forecast entity configured"
**Solution**: Configure `load_forecast` entity or use historical data
**Alternative**: The integration will use default values (0.1 kWh per 15-minute slot)

### 3. "No market price entity configured"
**Solution**: Configure `market_price` entity
**Alternative**: The integration will use default price (50 €/MWh)

### 4. "State attributes exceed maximum size"
**Solution**: The integration automatically limits attribute size
**Alternative**: Check logs for detailed data

### 5. "Entity not found" warnings
**Solution**: Ensure entities exist before configuring
**Alternative**: Use default entity IDs or create placeholder entities

## Performance Optimization

### 1. Reduce Update Frequency
```yaml
genetic_load_manager:
  update_interval: 30  # Update every 30 minutes instead of 15
```

### 2. Limit Genetic Algorithm Complexity
```yaml
genetic_load_manager:
  population_size: 50   # Smaller population (default: 100)
  generations: 100      # Fewer generations (default: 200)
```

### 3. Use Efficient Entity Types
- Prefer `sensor` over `input_text` for numerical data
- Use `binary_sensor` for on/off states
- Avoid storing large datasets in entity attributes

## Testing Your Configuration

### 1. Check Entity Availability
```yaml
# Developer Tools > States
# Search for your configured entities
```

### 2. Verify Data Quality
```yaml
# Developer Tools > Templates
# Test entity values:
{{ states('sensor.pv_forecast_today') }}
{{ state_attr('sensor.pv_forecast_today', 'DetailedForecast') }}
```

### 3. Monitor Integration Logs
```yaml
# Configuration > Logs
# Look for genetic_load_manager entries
```

## Best Practices

1. **Start Simple**: Begin with basic configuration and add complexity gradually
2. **Use Defaults**: The integration works with default values
3. **Monitor Performance**: Watch for high CPU usage or memory consumption
4. **Regular Updates**: Keep entity data fresh and accurate
5. **Backup Configuration**: Save working configurations for reference

## Support

If you continue to experience issues:
1. Check the integration logs for specific error messages
2. Verify all configured entities exist and are accessible
3. Ensure entity data formats match expected structures
4. Consider using the default configuration temporarily
5. Report issues with detailed logs and configuration
