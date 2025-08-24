# 🚀 Deployment Guide

This guide explains how to deploy the Genetic Load Manager integration to your Home Assistant instance.

## 📋 Prerequisites

Before deploying, ensure you have:

- **Home Assistant Core** version 2023.8.0 or newer
- **HACS (Home Assistant Community Store)** installed (recommended)
- **Required integrations** configured (see Configuration section)
- **Required entities** available in your system

## 🔧 Installation Methods

### Method 1: HACS Installation (Recommended)

1. **Install HACS** (if not already installed):
   - Follow the [HACS installation guide](https://hacs.xyz/docs/installation/installation/)
   - Restart Home Assistant

2. **Add this repository**:
   - Go to HACS → Integrations
   - Click the "+" button
   - Search for "Genetic Load Manager"
   - Click "Download"

3. **Install the integration**:
   - Click "Download" in HACS
   - Restart Home Assistant
   - Go to Configuration → Integrations
   - Click "+ Add Integration"
   - Search for "Genetic Load Manager"

### Method 2: Manual Installation

1. **Download the integration**:
   ```bash
   git clone https://github.com/yourusername/genetic-load-manager.git
   cd genetic-load-manager
   ```

2. **Copy to Home Assistant**:
   ```bash
   # Copy the integration folder
   cp -r custom_components/genetic_load_manager /path/to/homeassistant/config/custom_components/
   ```

3. **Restart Home Assistant**:
   - Go to Configuration → System → Restart
   - Or restart the service manually

4. **Add the integration**:
   - Go to Configuration → Integrations
   - Click "+ Add Integration"
   - Search for "Genetic Load Manager"

## ⚙️ Configuration

### Required Entities

The integration requires these entities to be available:

#### Solar Forecast
```yaml
# Solcast PV forecast entities
pv_forecast_entity: sensor.solcast_pv_forecast
pv_forecast_tomorrow_entity: sensor.solcast_pv_forecast_tomorrow
```

#### Load Forecast
```yaml
# Load consumption forecast
load_forecast_entity: sensor.load_forecast
```

#### Battery Management
```yaml
# Battery state of charge
battery_soc_entity: sensor.battery_soc
```

#### Dynamic Pricing
```yaml
# Dynamic electricity pricing
dynamic_pricing_entity: sensor.dynamic_pricing
```

### Configuration Options

```yaml
genetic_load_manager:
  # Algorithm Parameters
  population_size: 100          # Genetic algorithm population size
  generations: 200              # Number of generations to run
  mutation_rate: 0.05          # Mutation probability
  crossover_rate: 0.8          # Crossover probability
  
  # Device Configuration
  num_devices: 2               # Number of manageable devices
  device_priorities: [1.0, 0.8] # Device priority weights
  
  # Battery Configuration
  battery_capacity: 10.0       # Battery capacity in kWh
  max_charge_rate: 2.0         # Maximum charge rate in kW
  max_discharge_rate: 2.0      # Maximum discharge rate in kW
  
  # Control Options
  binary_control: false        # Use binary (on/off) control
  use_indexed_pricing: true   # Use indexed tariff pricing
```

## 🔍 Verification

### 1. Check Integration Status

After installation, verify:
- Integration appears in Configuration → Integrations
- Status shows "Configured" or "Running"
- No error messages in logs

### 2. Check Entities

Verify these entities are created:
- `sensor.genetic_algorithm_status`
- `sensor.optimization_dashboard`
- `sensor.cost_analytics`
- `binary_sensor.genetic_load_manager_status`
- `switch.device_0_schedule` (and more based on num_devices)

### 3. Check Services

Verify these services are available:
- `genetic_load_manager.run_optimization`
- `genetic_load_manager.start_optimization`
- `genetic_load_manager.stop_optimization`
- `genetic_load_manager.toggle_scheduler`

## 🧪 Testing

### 1. Manual Optimization

Test the integration manually:
```yaml
# In Developer Tools → Services
service: genetic_load_manager.run_optimization
```

### 2. Check Logs

Monitor the logs for:
- Successful optimization runs
- No error messages
- Proper data fetching

### 3. Verify Results

Check that:
- Device schedules are updated
- Optimization metrics are calculated
- Cost savings are tracked

## 🚨 Troubleshooting

### Common Issues

#### 1. Integration Not Found
- **Solution**: Restart Home Assistant after copying files
- **Check**: Verify files are in correct location

#### 2. Missing Entities
- **Solution**: Ensure required entities exist and are available
- **Check**: Verify entity names in configuration

#### 3. Optimization Errors
- **Solution**: Check log files for specific error messages
- **Check**: Verify forecast data availability

#### 4. Performance Issues
- **Solution**: Reduce population_size or generations
- **Check**: Monitor system resources during optimization

### Debug Mode

Enable debug logging:
```yaml
# In configuration.yaml
logger:
  default: info
  logs:
    custom_components.genetic_load_manager: debug
```

### Log Analysis

Common log locations:
- Home Assistant logs: Configuration → System → Logs
- File logs: `/config/home-assistant.log`
- Docker logs: `docker logs homeassistant`

## 📊 Monitoring

### Dashboard Integration

Add to your Lovelace dashboard:
```yaml
# Example dashboard card
type: custom:genetic-load-manager-dashboard
title: Genetic Load Manager
show_optimization_status: true
show_cost_analytics: true
show_device_schedules: true
```

### Automation Examples

```yaml
# Run optimization daily at 6 AM
automation:
  - alias: "Daily Genetic Optimization"
    trigger:
      platform: time
      at: "06:00:00"
    action:
      service: genetic_load_manager.run_optimization

# Monitor optimization status
automation:
  - alias: "Optimization Complete Notification"
    trigger:
      platform: state
      entity_id: sensor.genetic_algorithm_status
      to: "completed"
    action:
      service: notify.mobile_app
      data:
        title: "Optimization Complete"
        message: "Genetic algorithm optimization completed successfully"
```

## 🔄 Updates

### Updating via HACS

1. Go to HACS → Integrations
2. Find "Genetic Load Manager"
3. Click "Update" if available
4. Restart Home Assistant

### Manual Updates

1. Download new version
2. Replace existing files
3. Restart Home Assistant
4. Check for configuration changes

## 📞 Support

### Getting Help

1. **Check Documentation**: Review this guide and README files
2. **Search Issues**: Look for similar problems on GitHub
3. **Create Issue**: Report bugs with detailed information
4. **Community**: Ask questions in Home Assistant community

### Issue Reporting

When reporting issues, include:
- Home Assistant version
- Integration version
- Configuration (without sensitive data)
- Error logs
- Steps to reproduce

### Feature Requests

For new features:
- Describe the use case
- Explain expected behavior
- Provide examples if possible

---

**Note**: This integration is designed for advanced users. Ensure you understand the implications of automated load management before deployment.
