# Genetic Load Manager - Comprehensive Debugging Guide

This guide provides detailed information on how to troubleshoot and debug issues with the Genetic Load Manager integration using the enhanced logging and debugging capabilities.

## Table of Contents

1. [Overview](#overview)
2. [Enhanced Logging](#enhanced-logging)
3. [Debug Services](#debug-services)
4. [Common Issues and Solutions](#common-issues-and-solutions)
5. [Troubleshooting Steps](#troubleshooting-steps)
6. [Log Analysis](#log-analysis)
7. [Performance Monitoring](#performance-monitoring)

## Overview

The Genetic Load Manager integration has been enhanced with comprehensive logging and debugging capabilities to help identify and resolve optimization issues. The system now provides:

- **Detailed logging** at every step of the optimization process
- **Debug services** for troubleshooting
- **Data validation** and quality checks
- **Error tracking** with full context
- **Comprehensive reports** for analysis

## Enhanced Logging

### Log Levels

The integration uses different log levels to provide appropriate detail:

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about operations
- **WARNING**: Potential issues that don't stop operation
- **ERROR**: Issues that prevent normal operation
- **CRITICAL**: Severe issues that require immediate attention

### Log Files

Logs are automatically saved to:
- `~/.homeassistant/logs/genetic_load_manager/` - Main log files
- `~/.homeassistant/logs/genetic_load_manager/debug/` - Debug reports

### Key Logging Areas

#### 1. Forecast Data Fetching
```
=== Starting forecast data fetch ===
Fetching PV forecast data from entities:
  Today: sensor.solcast_pv_forecast_today
  Tomorrow: sensor.solcast_pv_forecast_tomorrow
Successfully fetched PV today entity: sensor.solcast_pv_forecast_today
```

#### 2. Data Validation
```
Data validation passed successfully
PV forecast: 96 slots, max: 3.245 kW
Load forecast: 96 slots, max: 2.100 kW
Battery SOC: 75.0%
Pricing: 96 slots, range: 0.0500-0.1200 €/kWh
```

#### 3. Optimization Process
```
=== Starting genetic algorithm optimization ===
Population initialized: 100 individuals, 2 devices, 96 time slots
Generation 0: Best fitness = -45.2341
Generation 50: Best fitness = -23.4567
```

## Debug Services

The integration provides several debug services that can be called from Home Assistant:

### 1. debug_optimization

Comprehensive step-by-step debugging of the optimization process.

**Service Call:**
```yaml
service: genetic_load_manager.debug_optimization
```

**What it does:**
- Checks genetic algorithm state
- Validates configuration
- Checks entity availability
- Tests data fetching
- Validates data quality
- Tests optimization readiness

**Output:**
```
=== Starting optimization debug ===
Step 1: Checking genetic algorithm state...
Step 2: Validating configuration...
Step 3: Checking entity availability...
Step 4: Testing data fetching...
Step 5: Validating data quality...
Step 6: Testing optimization...
=== Optimization debug completed ===
```

### 2. generate_debug_report

Generates a comprehensive debug report and saves it to a file.

**Service Call:**
```yaml
service: genetic_load_manager.generate_debug_report
```

**Report Contents:**
- System information
- Integration configuration
- Entity status
- Data summary
- Recent errors
- Debug data

### 3. validate_entities

Validates the status of all configured entities.

**Service Call:**
```yaml
service: genetic_load_manager.validate_entities
data:
  entities:
    - sensor.solcast_pv_forecast_today
    - sensor.load_forecast
```

### 4. test_data_fetch

Tests data fetching for all configured entities.

**Service Call:**
```yaml
service: genetic_load_manager.test_data_fetch
```

### 5. reset_optimizer

Resets the genetic algorithm optimizer to a clean state.

**Service Call:**
```yaml
service: genetic_load_manager.reset_optimizer
```

## Common Issues and Solutions

### 1. Entity Not Found Errors

**Symptoms:**
```
ERROR: PV forecast entity not found: sensor.solcast_pv_forecast_today
ERROR: This entity may not exist or may be misconfigured
```

**Solutions:**
- Check entity ID spelling
- Verify entity exists in Home Assistant
- Check entity configuration in YAML
- Ensure entity is not disabled

### 2. Data Format Issues

**Symptoms:**
```
ERROR: No Solcast PV forecast data available from either entity
ERROR: This will result in zero PV generation forecast
```

**Solutions:**
- Check entity attributes for forecast data
- Verify data structure matches expected format
- Check entity state and attributes
- Use debug services to validate data

### 3. Optimization Failures

**Symptoms:**
```
ERROR: Data validation failed, cannot proceed with optimization
ERROR: Optimization returned no solution
```

**Solutions:**
- Run `debug_optimization` service
- Check data quality with `test_data_fetch`
- Validate entities with `validate_entities`
- Reset optimizer with `reset_optimizer`

### 4. Performance Issues

**Symptoms:**
- Slow optimization
- High CPU usage
- Memory issues

**Solutions:**
- Reduce population size
- Reduce number of generations
- Check data quality
- Monitor system resources

## Troubleshooting Steps

### Step 1: Check Basic Configuration

1. Verify integration is loaded:
   ```yaml
   # Check configuration.yaml
   genetic_load_manager:
     pv_forecast_today: sensor.solcast_pv_forecast_today
     pv_forecast_tomorrow: sensor.solcast_pv_forecast_tomorrow
     load_forecast: sensor.load_forecast
     battery_soc: sensor.battery_soc
   ```

2. Check entity availability:
   ```yaml
   service: genetic_load_manager.validate_entities
   ```

### Step 2: Test Data Fetching

1. Run data fetch test:
   ```yaml
   service: genetic_load_manager.test_data_fetch
   ```

2. Check log output for data quality issues

### Step 3: Debug Optimization

1. Run comprehensive debug:
   ```yaml
   service: genetic_load_manager.debug_optimization
   ```

2. Analyze output for specific issues

### Step 4: Generate Debug Report

1. Create comprehensive report:
   ```yaml
   service: genetic_load_manager.generate_debug_report
   ```

2. Review saved report file

### Step 5: Reset and Retry

1. Reset optimizer:
   ```yaml
   service: genetic_load_manager.reset_optimizer
   ```

2. Monitor logs for improvement

## Log Analysis

### Key Log Patterns

#### Successful Operation
```
INFO: === Starting forecast data fetch ===
INFO: Successfully fetched PV today entity
INFO: Data validation passed successfully
INFO: === Starting genetic algorithm optimization ===
INFO: Optimization completed successfully
```

#### Data Issues
```
ERROR: PV forecast entity not found
WARNING: Load forecast size mismatch: got 48, expected 96
ERROR: No Solcast PV forecast data available
```

#### Optimization Issues
```
ERROR: Data validation failed, cannot proceed with optimization
ERROR: Population initialization failed
ERROR: Fitness calculation returned invalid value
```

### Log Search Commands

Search for errors:
```bash
grep "ERROR" ~/.homeassistant/logs/genetic_load_manager/*.log
```

Search for specific issues:
```bash
grep "entity not found" ~/.homeassistant/logs/genetic_load_manager/*.log
grep "data validation failed" ~/.homeassistant/logs/genetic_load_manager/*.log
```

## Performance Monitoring

### Key Metrics to Monitor

1. **Data Fetch Time**: How long it takes to fetch forecast data
2. **Optimization Time**: How long the genetic algorithm runs
3. **Memory Usage**: Memory consumption during optimization
4. **CPU Usage**: CPU utilization during optimization
5. **Error Frequency**: How often errors occur

### Performance Optimization

1. **Reduce Population Size**: Smaller populations run faster
2. **Reduce Generations**: Fewer generations complete faster
3. **Optimize Data Fetching**: Cache data when possible
4. **Monitor Resource Usage**: Watch for memory leaks

## Advanced Debugging

### Custom Logging

You can add custom logging to your configuration:

```yaml
logger:
  custom_components.genetic_load_manager: debug
  custom_components.genetic_load_manager.genetic_algorithm: debug
  custom_components.genetic_load_manager.pricing_calculator: debug
```

### Debug Mode

Enable debug mode for more verbose logging:

```yaml
genetic_load_manager:
  debug_mode: true
  log_level: DEBUG
```

### Manual Testing

Test individual components manually:

```python
# Test entity access
state = hass.states.get("sensor.solcast_pv_forecast_today")
print(f"Entity state: {state.state}")
print(f"Attributes: {state.attributes}")

# Test data processing
from custom_components.genetic_load_manager.genetic_algorithm import GeneticLoadOptimizer
ga = GeneticLoadOptimizer(hass, config)
await ga.fetch_forecast_data()
```

## Getting Help

If you continue to experience issues:

1. **Generate Debug Report**: Use the `generate_debug_report` service
2. **Check Logs**: Review recent log files for errors
3. **Validate Configuration**: Ensure all required entities are configured
4. **Test Components**: Use debug services to isolate issues
5. **Community Support**: Share debug reports and logs for assistance

## Conclusion

The enhanced logging and debugging capabilities provide comprehensive visibility into the Genetic Load Manager integration's operation. By following this guide and using the available debug services, you can quickly identify and resolve optimization issues, ensuring reliable and efficient load management.

Remember to:
- Monitor logs regularly
- Use debug services when issues arise
- Validate data quality
- Test components individually
- Generate debug reports for complex issues

This systematic approach will help maintain optimal performance and quickly resolve any problems that may arise.