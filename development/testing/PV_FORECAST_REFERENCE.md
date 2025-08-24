# Solcast PV Forecast Entity Reference

## Entity Details

**Entity ID**: `sensor.solcast_pv_forecast_previsao_para_hoje`  
**Type**: Sensor  
**Platform**: Solcast  
**Purpose**: PV production forecasting for energy optimization

## Key Attributes

### **Daily Estimates**
- `Estimate`: **28.88 kWh** - Expected daily production
- `Estimate10`: **25.66 kWh** - Conservative estimate (10% confidence)
- `Estimate90`: **30.01 kWh** - Optimistic estimate (90% confidence)

### **Metadata**
- `Dayname`: **Wednesday** - Day of forecast
- `DataCorrect`: **true** - Data quality indicator

### **Forecast Data**
- `DetailedForecast`: 30-minute interval forecasts
- `DetailedHourly`: **Hourly forecasts** (what we use for optimization)

## DetailedHourly Structure

```yaml
DetailedHourly:
  - period_start: '2025-08-20T12:00:00+01:00'
    pv_estimate: 3.4304      # Expected production (kW)
    pv_estimate10: 3.1322    # Conservative (10%)
    pv_estimate90: 3.5546    # Optimistic (90%)
```

## Data Extraction Example

```python
def extract_pv_forecast(entity):
    """Extract PV forecast data from Solcast entity"""
    
    # Get hourly forecast
    detailed_hourly = entity.attributes.get('DetailedHourly', [])
    
    # Extract current hour forecast
    current_hour = datetime.now().hour
    current_forecast = None
    
    for hour_data in detailed_hourly:
        try:
            period_start = datetime.fromisoformat(
                hour_data['period_start'].replace('+01:00', '+00:00')
            )
            if period_start.hour == current_hour:
                current_forecast = hour_data
                break
        except:
            continue
    
    return {
        'daily_estimate': entity.attributes.get('Estimate', 0.0),
        'current_hour': current_forecast.get('pv_estimate', 0.0) if current_forecast else 0.0,
        'hourly_forecast': detailed_hourly,
        'data_quality': entity.attributes.get('DataCorrect', False)
    }
```

## Optimization Usage

### **1. Current Hour Planning**
```python
current_pv = extract_pv_forecast(entity)['current_hour']
if current_pv > 2.0:  # Good solar production
    # Charge battery, run high-power devices
elif current_pv < 0.5:  # Low solar production
    # Minimize loads, use battery power
```

### **2. Daily Planning**
```python
daily_estimate = extract_pv_forecast(entity)['daily_estimate']
if daily_estimate > 25.0:  # Sunny day expected
    # Plan for high solar production
    # Schedule energy-intensive tasks during peak hours
```

### **3. Risk Assessment**
```python
hourly_forecast = extract_pv_forecast(entity)['hourly_forecast']

# Conservative planning (worst case)
conservative_power = sum(h['pv_estimate10'] for h in hourly_forecast)

# Optimistic planning (best case)
optimistic_power = sum(h['pv_estimate90'] for h in hourly_forecast)

# Use conservative for critical planning
# Use optimistic for opportunity planning
```

### **4. Peak Production Timing**
```python
hourly_forecast = extract_pv_forecast(entity)['hourly_forecast']

# Find peak production hour
peak_hour = max(hourly_forecast, key=lambda x: x['pv_estimate'])
peak_time = peak_hour['period_start']
peak_power = peak_hour['pv_estimate']

print(f"Peak production: {peak_power:.3f} kW at {peak_time}")
```

## Integration with EMS

### **Energy Flow Calculation**
```python
def calculate_energy_flow(pv_forecast, current_load, battery_soc):
    """Calculate optimal energy flow using PV forecast"""
    
    current_pv = pv_forecast['current_hour']
    
    # Calculate net energy
    net_energy = current_pv - current_load
    
    if net_energy > 0:  # Surplus solar
        # Charge battery or export to grid
        battery_charge = min(net_energy, battery_charge_capacity)
        grid_export = net_energy - battery_charge
    else:  # Solar deficit
        # Use battery or import from grid
        battery_discharge = min(abs(net_energy), battery_discharge_capacity)
        grid_import = abs(net_energy) - battery_discharge
    
    return {
        'battery_charge': battery_charge,
        'battery_discharge': battery_discharge,
        'grid_export': grid_export,
        'grid_import': grid_import
    }
```

### **Load Scheduling**
```python
def optimize_load_schedule(pv_forecast, loads):
    """Schedule loads based on PV forecast"""
    
    hourly_forecast = pv_forecast['hourly_forecast']
    
    # Sort loads by priority and power requirement
    sorted_loads = sorted(loads, key=lambda x: (x['priority'], x['power']))
    
    schedule = {}
    
    for hour_data in hourly_forecast:
        hour = hour_data['period_start']
        available_pv = hour_data['pv_estimate']
        
        # Schedule loads that can run on available PV
        scheduled_loads = []
        for load in sorted_loads:
            if load['power'] <= available_pv and load['priority'] == 'high':
                scheduled_loads.append(load)
                available_pv -= load['power']
        
        schedule[hour] = scheduled_loads
    
    return schedule
```

## Data Quality Considerations

### **Check Data Validity**
```python
def validate_pv_forecast(entity):
    """Validate PV forecast data quality"""
    
    # Check if data is marked as correct
    data_correct = entity.attributes.get('DataCorrect', False)
    
    # Check if we have hourly forecasts
    detailed_hourly = entity.attributes.get('DetailedHourly', [])
    has_forecasts = len(detailed_hourly) > 0
    
    # Check if current hour forecast is reasonable
    current_hour = datetime.now().hour
    current_forecast = None
    
    for hour_data in detailed_hourly:
        try:
            period_start = datetime.fromisoformat(
                hour_data['period_start'].replace('+01:00', '+00:00')
            )
            if period_start.hour == current_hour:
                current_forecast = hour_data['pv_estimate']
                break
        except:
            continue
    
    # Validate forecast value
    forecast_reasonable = 0 <= current_forecast <= 10.0  # Max 10 kW
    
    return {
        'data_correct': data_correct,
        'has_forecasts': has_forecasts,
        'forecast_reasonable': forecast_reasonable,
        'overall_quality': data_correct and has_forecasts and forecast_reasonable
    }
```

### **Fallback Strategy**
```python
def get_pv_forecast_with_fallback(entity):
    """Get PV forecast with fallback to historical data"""
    
    # Try to get current forecast
    forecast_data = extract_pv_forecast(entity)
    
    # Validate data quality
    quality = validate_pv_forecast(entity)
    
    if not quality['overall_quality']:
        # Use fallback: historical average for this hour
        current_hour = datetime.now().hour
        fallback_power = get_historical_average(current_hour)
        
        return {
            'current_hour': fallback_power,
            'daily_estimate': 20.0,  # Conservative fallback
            'hourly_forecast': [],
            'data_quality': False,
            'fallback_used': True
        }
    
    return forecast_data
```

## Best Practices

### **1. Always Validate Data**
- Check `DataCorrect` flag
- Validate forecast values are reasonable
- Handle missing or corrupted data gracefully

### **2. Use Conservative Estimates for Critical Planning**
- Use `pv_estimate10` for worst-case scenarios
- Use `pv_estimate` for normal planning
- Use `pv_estimate90` for opportunity planning

### **3. Update Forecasts Regularly**
- Check for new forecast data every hour
- Handle timezone differences properly
- Cache forecasts to avoid repeated API calls

### **4. Monitor Data Quality**
- Log when fallbacks are used
- Track forecast accuracy over time
- Alert on persistent data quality issues

## Common Issues and Solutions

### **Issue: Missing DetailedHourly Data**
```python
# Solution: Check if attribute exists
detailed_hourly = entity.attributes.get('DetailedHourly', [])
if not detailed_hourly:
    # Fallback to current state or historical data
    current_pv = float(entity.state) if entity.state != 'unavailable' else 0.0
```

### **Issue: Timezone Mismatch**
```python
# Solution: Handle timezone conversion
period_start = hour_data['period_start']
# Remove timezone info and parse as local time
local_time = datetime.fromisoformat(period_start.replace('+01:00', ''))
```

### **Issue: Invalid Forecast Values**
```python
# Solution: Validate and clamp values
pv_estimate = hour_data.get('pv_estimate', 0.0)
if not isinstance(pv_estimate, (int, float)) or pv_estimate < 0:
    pv_estimate = 0.0
pv_estimate = min(pv_estimate, 10.0)  # Clamp to reasonable maximum
```
