# Genetic Load Manager - HACS Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintainer](https://img.shields.io/badge/maintainer-%40filipe0doria-blue.svg)](https://github.com/filipe0doria)

An intelligent load management system for Home Assistant that uses genetic algorithms to optimize household energy consumption based on photovoltaic production, battery status, and electricity market prices.

## 🎯 Features

- **Genetic Algorithm Optimization**: Advanced optimization engine that evolves load schedules
- **Real-time Monitoring**: Continuous monitoring of PV, battery, and price entities
- **Automatic Scheduling**: Configurable optimization intervals (default: 15 minutes)
- **Home Assistant Integration**: Native integration with sensors, services, and events
- **Configurable Parameters**: Adjustable genetic algorithm settings
- **Event-driven**: Fires events for automation and monitoring

## 🚀 Installation

### Prerequisites

- [Home Assistant](https://www.home-assistant.io/) 2023.8.0 or later
- [HACS](https://hacs.xyz/) (Home Assistant Community Store)

### HACS Installation

1. **Add Custom Repository to HACS:**
   - Open HACS in Home Assistant
   - Go to **Integrations**
   - Click the three dots menu (⋮)
   - Select **Custom repositories**
   - Add: `filipe0doria/genetic-load-manager-hacs`
   - Category: **Integration**

2. **Install the Integration:**
   - Find "Genetic Load Manager" in HACS
   - Click **Download**
   - Restart Home Assistant

3. **Add Integration:**
   - Go to **Settings** → **Devices & Services**
   - Click **Add Integration**
   - Search for "Genetic Load Manager"
   - Click **Configure**

## ⚙️ Configuration

### Required Configuration

- **PV Power Entity ID**: Entity for photovoltaic power production
- **Forecast Entity ID**: Entity for PV production forecasts
- **Battery SOC Entity ID**: Entity for battery state of charge
- **Price Entity ID**: Entity for electricity market price

### Optional Configuration

- **Optimization Interval**: How often to run optimization (5-60 minutes)
- **Population Size**: Genetic algorithm population size (10-200)
- **Generations**: Number of evolution generations (10-500)
- **Mutation Rate**: Probability of genetic mutation (0.01-0.5)
- **Crossover Rate**: Probability of genetic crossover (0.1-1.0)

### Example Configuration

```yaml
# Example entities (replace with your actual entity IDs)
pv_entity_id: "sensor.pv_power"
forecast_entity_id: "sensor.pv_forecast"
battery_soc_entity_id: "sensor.battery_soc"
price_entity_id: "sensor.electricity_price"

# Genetic algorithm parameters
optimization_interval: 15
population_size: 50
generations: 100
mutation_rate: 0.1
crossover_rate: 0.8
```

## 📊 Sensors

The integration creates several sensors to monitor the optimization process:

- **Genetic Load Manager Status**: Current optimization status
- **Last Optimization**: Timestamp of last optimization run
- **Next Optimization**: Scheduled time for next optimization
- **Optimization Count**: Total number of optimizations completed
- **Best Fitness Score**: Best fitness score achieved

## 🔧 Services

### `genetic_load_manager.optimize_loads`

Trigger manual load optimization.

```yaml
service: genetic_load_manager.optimize_loads
data:
  force: false  # Force optimization even if recently run
```

### `genetic_load_manager.apply_schedule`

Apply the current optimized schedule.

```yaml
service: genetic_load_manager.apply_schedule
data:
  schedule_id: "current"  # ID of schedule to apply
```

### `genetic_load_manager.reset_optimization`

Reset optimization statistics and schedule.

```yaml
service: genetic_load_manager.reset_optimization
data: {}
```

## 📡 Events

The integration fires several events for automation:

### `genetic_load_manager_optimization_started`

Fired when optimization begins.

```yaml
automation:
  - alias: "Log Optimization Start"
    trigger:
      platform: event
      event_type: genetic_load_manager_optimization_started
    action:
      - service: persistent_notification.create
        data:
          message: "Load optimization started"
```

### `genetic_load_manager_optimization_completed`

Fired when optimization completes.

```yaml
automation:
  - alias: "Log Optimization Complete"
    trigger:
      platform: event
      event_type: genetic_load_manager_optimization_completed
    action:
      - service: persistent_notification.create
        data:
          message: >
            Optimization completed!
            Count: {{ trigger.event.data.optimization_count }}
            Best Fitness: {{ trigger.event.data.best_fitness }}
```

### `genetic_load_manager_schedule_applied`

Fired when a schedule is applied.

```yaml
automation:
  - alias: "Log Schedule Applied"
    trigger:
      platform: event
      event_type: genetic_load_manager_schedule_applied
    action:
      - service: persistent_notification.create
        data:
          message: "Load schedule applied at {{ trigger.event.data.timestamp }}"
```

## 🧬 How It Works

### 1. **Data Collection**
- Monitors PV production, battery SOC, and electricity prices
- Collects load status and power consumption data

### 2. **Genetic Algorithm Optimization**
- Creates population of load schedules
- Evolves schedules over multiple generations
- Evaluates fitness based on multiple objectives:
  - Energy cost minimization
  - PV utilization maximization
  - Battery efficiency optimization
  - Load balancing

### 3. **Schedule Application**
- Applies best schedule to Home Assistant entities
- Controls load switching and power consumption timing
- Monitors and adjusts based on real-time conditions

## 🔍 Troubleshooting

### Common Issues

1. **Entity Not Found**: Ensure all configured entity IDs exist
2. **Optimization Fails**: Check logs for specific error messages
3. **High CPU Usage**: Reduce population size or generations
4. **Scheduling Issues**: Verify optimization interval is appropriate

### Log Analysis

Check Home Assistant logs for:
- Integration startup messages
- Optimization progress
- Error messages
- Performance metrics

### Performance Tuning

For better performance:
- Reduce genetic algorithm complexity
- Increase optimization interval
- Monitor system resources
- Adjust population size and generations

## 📚 Advanced Configuration

### Custom Load Selection

The integration automatically detects manageable loads from your entity registry. To customize:

1. **Create a custom component** that extends the base integration
2. **Override the `_get_manageable_loads` method**
3. **Implement your own load selection logic**

### Custom Fitness Functions

To customize the optimization objectives:

1. **Extend the `GeneticLoadOptimizer` class**
2. **Override the `_evaluate_fitness` method**
3. **Implement your own fitness calculation**

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is developed for research purposes. Please contact the author for licensing information.

## 🙏 Acknowledgments

- Home Assistant community for the excellent platform
- HACS team for the custom integration framework
- Research community for genetic algorithm applications in energy management

---

**Note**: This integration is designed for research and educational purposes. Always test thoroughly in your environment before relying on it for critical load management. 