# Indexed Tariff Pricing System

The Genetic Load Manager now includes a comprehensive indexed tariff pricing calculator that implements the formula you provided:

```
TOTAL = (PM * FP + Q + TAE + MFRR) * VAT
Final Price = TOTAL / 1000 (€/kWh)
```

## Components

### Market Price (PM)
- **Source**: Configurable entity (e.g., `sensor.omie_spot_price_pt`)
- **Unit**: €/MWh
- **Description**: Real-time wholesale electricity market price

### Fixed Components
- **MFRR**: Frequency Restoration Reserve (default: 1.94 €/MWh)
- **Q**: Quality component (default: 30.0 €/MWh)  
- **FP**: Fixed percentage multiplier (default: 1.1674)
- **TAE**: Transmission and distribution tariff (default: 60.0 €/MWh)
- **VAT**: Value Added Tax multiplier (default: 1.23 = 23%)

## Configuration

### Basic Setup
```yaml
# Configuration example
use_indexed_pricing: true
market_price_entity: "sensor.omie_spot_price_pt"
mfrr: 1.94
q: 30.0
fp: 1.1674
tae: 60.0
vat: 1.23
```

### Advanced Features

#### Time-of-Use Pricing
```yaml
peak_multiplier: 1.2        # 20% increase during peak hours
off_peak_multiplier: 0.8    # 20% decrease during off-peak hours
peak_hours: [18, 19, 20, 21]  # 6-9 PM
off_peak_hours: [0, 1, 2, 3, 4, 5, 6, 23]  # Night hours
```

#### Seasonal Adjustments
```yaml
summer_adjustment: 1.1      # 10% increase in summer
winter_adjustment: 0.95     # 5% decrease in winter
summer_months: [6, 7, 8, 9] # June-September
```

## Sensors Created

### 1. Indexed Electricity Price Sensor
- **Entity ID**: `sensor.genetic_load_manager_indexed_pricing`
- **State**: Current electricity price in €/kWh
- **Attributes**:
  - `pricing_components`: Detailed breakdown of all components
  - `24h_forecast`: Hourly price forecast for next 24 hours
  - `pricing_method`: "indexed_tariff"
  - Configuration parameters (mfrr, q, fp, tae, vat, etc.)

### Example Sensor Output
```yaml
state: 0.1234  # €/kWh
attributes:
  pricing_components:
    market_price: 45.67          # €/MWh
    market_price_adjusted: 53.31 # PM * FP
    quality_component: 30.0      # Q
    transmission_tariff: 60.0    # TAE
    frequency_reserve: 1.94      # MFRR
    subtotal: 145.25             # Sum before VAT
    vat_amount: 33.41            # VAT amount
    total_with_vat: 178.66       # With VAT
    final_price_kwh: 0.1787      # Final price in €/kWh
  24h_forecast: [0.1234, 0.1456, ...]
  mfrr: 1.94
  q: 30.0
  # ... other config parameters
```

## Services

### Update Pricing Parameters
Use the `genetic_load_manager.update_pricing_parameters` service to modify pricing components in real-time:

```yaml
service: genetic_load_manager.update_pricing_parameters
data:
  mfrr: 2.1
  q: 35.0
  vat: 1.25
  peak_multiplier: 1.3
```

## Integration with Genetic Algorithm

The pricing calculator is automatically integrated with the genetic algorithm:

1. **Real-time Pricing**: Gets current market prices every 15 minutes
2. **24-hour Forecast**: Generates 96 price points (15-minute intervals)
3. **Cost Optimization**: Uses indexed prices for fitness function calculations
4. **Fallback Support**: Falls back to simple pricing if indexed pricing fails

## Usage Examples

### Home Assistant Automation
```yaml
automation:
  - alias: "Update electricity pricing for peak hours"
    trigger:
      platform: time
      at: "17:30:00"  # Before peak hours
    action:
      service: genetic_load_manager.update_pricing_parameters
      data:
        peak_multiplier: 1.5  # Increase peak multiplier
```

### Template Sensor for Current Cost
```yaml
template:
  - sensor:
      - name: "Current Electricity Cost"
        state: >
          {{ states('sensor.genetic_load_manager_indexed_pricing') | float | round(4) }}
        unit_of_measurement: "€/kWh"
        device_class: monetary
```

### Lovelace Card Example
```yaml
type: entities
title: "Electricity Pricing"
entities:
  - entity: sensor.genetic_load_manager_indexed_pricing
    name: "Current Price"
  - type: attribute
    entity: sensor.genetic_load_manager_indexed_pricing
    attribute: pricing_components
    name: "Price Breakdown"
```

## Troubleshooting

### Common Issues

1. **Market Price Entity Not Available**
   - Check that `market_price_entity` exists and is accessible
   - Verify entity has numeric state (not 'unknown' or 'unavailable')
   - System will use fallback price of 50.0 €/MWh if entity is unavailable

2. **Pricing Calculation Errors**
   - Check logs for detailed error messages
   - Verify all pricing parameters are within valid ranges
   - Use service call to test parameter updates

3. **Performance Issues**
   - Pricing calculations are cached for 15 minutes
   - Reduce update frequency if needed
   - Monitor system resources during optimization

### Debug Information

Enable debug logging to see detailed pricing calculations:

```yaml
logger:
  logs:
    custom_components.genetic_load_manager.pricing_calculator: debug
```

## Advanced Configuration

### Custom Time Periods
```yaml
# Define custom peak/off-peak hours
peak_hours: [7, 8, 18, 19, 20, 21]  # Morning and evening peaks
off_peak_hours: [0, 1, 2, 3, 4, 5, 6, 22, 23]  # Night hours
shoulder_multiplier: 1.0  # Normal hours multiplier
```

### Currency Conversion
```yaml
currency_conversion: 0.85  # Convert €/kWh to $/kWh (example rate)
```

### Validation Ranges
All pricing parameters have built-in validation:
- MFRR: 0.0 - 10.0 €/MWh
- Q: 0.0 - 100.0 €/MWh  
- FP: 1.0 - 2.0
- TAE: 0.0 - 200.0 €/MWh
- VAT: 1.0 - 1.5
- Time-of-use multipliers: 0.5 - 2.0

## Benefits

1. **Accurate Cost Calculation**: Uses real market prices and regulatory components
2. **Dynamic Optimization**: Genetic algorithm optimizes based on actual tariff structure
3. **Transparency**: Full breakdown of pricing components available
4. **Flexibility**: All parameters can be updated without restart
5. **Reliability**: Fallback mechanisms ensure continuous operation
6. **Performance**: Efficient caching and calculation methods

This indexed pricing system provides a realistic and comprehensive approach to electricity cost optimization, taking into account all the regulatory and market components that make up your actual electricity bill.
