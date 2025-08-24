# Dashboard Troubleshooting Guide - Genetic Load Manager

## Common Dashboard Errors and Solutions

### 1. **ApexCharts Configuration Errors**

#### Error: `value.chart_type is not a ChartCardChartType`
**Problem**: Invalid chart type specified
**Solution**: Use only these valid chart types:
- `line` - Line charts
- `scatter` - Scatter plots  
- `pie` - Pie charts
- `donut` - Donut charts
- `radialBar` - Radial bar charts
- `column` - Column charts
- `bar` - Bar charts

**Fixed Example**:
```yaml
# ❌ WRONG - 'area' is not valid
chart_type: area

# ✅ CORRECT - 'line' is valid
chart_type: line
```

#### Error: `value.height is extraneous`
**Problem**: `height` property is not supported in newer ApexCharts versions
**Solution**: Remove all `height` properties from chart configurations

**Fixed Example**:
```yaml
# ❌ WRONG - height property not supported
- type: custom:apexcharts-card
  chart_type: line
  height: 200  # Remove this line
  series: [...]

# ✅ CORRECT - no height property
- type: custom:apexcharts-card
  chart_type: line
  series: [...]
```

#### Error: `value.xaxis is extraneous`
**Problem**: `xaxis` property structure has changed
**Solution**: Update xaxis configuration format

**Fixed Example**:
```yaml
# ❌ WRONG - old format
xaxis:
  - categories:
      - "00:00"
      - "01:00"

# ✅ CORRECT - new format
xaxis:
  categories:
    - "00:00"
    - "01:00"
```

### 2. **Data Generator Issues**

#### Problem: JavaScript syntax errors in data_generator
**Solution**: Use proper JavaScript syntax and remove comments

**Fixed Example**:
```yaml
# ❌ WRONG - JavaScript comments cause issues
data_generator: |
  return entity.attributes.schedule_data.predicted_schedule.map(slot => ({
    x: slot.time,
    y: slot.devices.device_0 * 1000  // Convert to watts
  }));

# ✅ CORRECT - no comments, clean syntax
data_generator: |
  return entity.attributes.schedule_data.predicted_schedule.map(slot => ({
    x: slot.time,
    y: slot.devices.device_0 * 1000
  }));
```

### 3. **Entity Reference Issues**

#### Problem: Entities don't exist yet
**Solution**: Create placeholder entities or use existing ones

**Quick Fix**: Replace non-existent entities with working ones:
```yaml
# ❌ WRONG - entity doesn't exist
entity: sensor.genetic_load_manager_dashboard

# ✅ CORRECT - use existing entity or create placeholder
entity: sensor.system_health
```

## Working Dashboard Templates

### Option 1: Simple Dashboard (Recommended)
Use `simple_dashboard.yaml` - it avoids complex ApexCharts configurations and uses:
- `mini-graph-card` for simple charts
- Standard Lovelace cards
- No complex data generators

### Option 2: Fixed Advanced Dashboard
The `advanced_dashboard.yaml` has been fixed but requires:
- ApexCharts v2.2.3+ installed
- All referenced entities to exist
- Proper data structure in entity attributes

## Step-by-Step Dashboard Setup

### 1. Install Required Custom Cards
```yaml
# HACS > Frontend > Add Repository
# Add these custom cards:
- button-card
- mini-graph-card
- apexcharts-card (optional, for advanced charts)
```

### 2. Create Required Entities
```yaml
# Developer Tools > YAML
sensor:
  - platform: template
    sensors:
      system_health:
        friendly_name: "System Health"
        value_template: "{{ 85 }}"
        unit_of_measurement: "%"
      
      cost_analytics:
        friendly_name: "Cost Analytics"
        value_template: "{{ 12.50 }}"
        unit_of_measurement: "€"
      
      genetic_algorithm_status:
        friendly_name: "Genetic Algorithm Status"
        value_template: "{{ 'idle' }}"
```

### 3. Test Dashboard
1. Copy dashboard YAML to Lovelace
2. Check for configuration errors
3. Verify all entities exist
4. Test chart functionality

## Alternative Chart Solutions

### If ApexCharts Doesn't Work

#### Use Mini-Graph-Card Instead:
```yaml
# Simple, reliable charts
- type: custom:mini-graph-card
  name: "Pricing Trend"
  entity: sensor.genetic_load_manager_indexed_pricing
  line_color: "#FF9800"
  hours_to_show: 24
  animate: true
```

#### Use Standard Lovelace Charts:
```yaml
# Built-in chart support
- type: history-graph
  name: "24-Hour Pricing"
  entities:
    - entity: sensor.genetic_load_manager_indexed_pricing
      color: "#FF9800"
  hours_to_show: 24
```

## Dashboard Validation

### Check Your Configuration:
1. **YAML Syntax**: Use YAML validator
2. **Entity Existence**: Verify all entities exist
3. **Card Compatibility**: Ensure custom cards are installed
4. **Data Structure**: Check entity attribute formats

### Common Validation Commands:
```yaml
# Developer Tools > Templates
{{ states('sensor.system_health') }}
{{ state_attr('sensor.cost_analytics', 'chart_data') }}

# Developer Tools > States
# Search for your entities
```

## Emergency Dashboard

If nothing works, use this minimal dashboard:
```yaml
title: "Genetic Load Manager - Basic"
path: genetic-load-manager-basic
cards:
  - type: entities
    title: "System Status"
    entities:
      - entity: sensor.system_health
        name: "Health"
      - entity: sensor.genetic_load_manager_indexed_pricing
        name: "Price"
  
  - type: custom:button-card
    name: "Run Optimization"
    tap_action:
      action: call-service
      service: genetic_load_manager.run_optimization
```

## Getting Help

### 1. Check Logs
```yaml
# Configuration > Logs
# Look for: lovelace, frontend, custom_cards
```

### 2. Verify Custom Cards
```yaml
# HACS > Frontend
# Check if custom cards are properly installed
```

### 3. Test Individual Cards
```yaml
# Create single card first
# Test in isolation before building full dashboard
```

### 4. Use Working Examples
- Start with `simple_dashboard.yaml`
- Gradually add complexity
- Test each addition before proceeding

## Best Practices

1. **Start Simple**: Begin with basic cards, add charts later
2. **Test Incrementally**: Add one card at a time
3. **Use Validators**: Check YAML syntax before loading
4. **Backup Working Configs**: Save working dashboard configurations
5. **Monitor Performance**: Complex dashboards can impact system performance
