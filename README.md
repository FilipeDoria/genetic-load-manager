# 🧬 **Genetic Load Manager - Advanced HACS Integration**

A sophisticated Home Assistant integration for **intelligent load management** using **genetic algorithms** to optimize energy consumption, reduce costs, and maximize solar power utilization.

## 📁 Project Structure

```
genetic-load-manager/
├── custom_components/genetic_load_manager/  # 🏠 Final Home Assistant Integration
│   ├── __init__.py                          # Main integration entry point
│   ├── genetic_algorithm.py                 # Core genetic algorithm engine
│   ├── pricing_calculator.py                # Indexed tariff pricing calculator
│   ├── sensor.py                            # Optimization status sensors
│   ├── switch.py                            # Device control switches
│   ├── binary_sensor.py                     # Binary status sensors
│   ├── dashboard.py                         # Optimization dashboard
│   ├── control_panel.py                     # Interactive control panel
│   ├── analytics.py                         # Cost and performance analytics
│   ├── config_flow.py                       # Configuration flow
│   ├── const.py                             # Constants and configuration
│   ├── services.yaml                        # Custom services
│   ├── manifest.json                        # Integration manifest
│   └── translations/                        # Multi-language support
│
├── development/                              # 🔬 Development & Testing Environment
│   ├── testing/                             # Test scripts and mock data
│   │   ├── test_*.py                        # Unit and integration tests
│   │   ├── ems_testing_integration.py       # EMS testing framework
│   │   ├── data_creation.py                 # Test data generation
│   │   └── *.png                            # Test result visualizations
│   │
│   ├── documentation/                       # Development documentation
│   │   ├── ADDING_SENSORS_GUIDE.md          # Sensor integration guide
│   │   ├── INDEXED_PRICING_GUIDE.md         # Pricing system guide
│   │   ├── ALGORITHM_IMPROVEMENTS.md        # Algorithm development notes
│   │   ├── REAL_ENTITY_TESTING_SUMMARY.md   # Testing results
│   │   └── entity_analysis_summary.md       # Entity analysis
│   │
│   ├── research/                            # Research and analysis
│   ├── inputs.txt                           # Test input parameters
│   ├── schedules.png                        # Test schedule visualizations
│   └── venv/                                # Python virtual environment
│
├── .vscode/                                 # VS Code configuration
├── lovelace_cards.yaml                      # Lovelace dashboard templates (copy to your HA)
├── advanced_dashboard.yaml                  # Advanced dashboard templates (copy to your HA)
└── README.md                                # This file
```

## 🚀 Quick Start

### For Home Assistant Users (Final Integration)

1. **Install via HACS** (recommended):

   - Add this repository to HACS
   - Install the integration
   - Configure via Home Assistant UI

2. **Manual Installation**:
   - Copy `custom_components/genetic_load_manager/` to your Home Assistant `custom_components/` folder
   - Restart Home Assistant
   - Add integration via Configuration → Integrations

### For Developers

1. **Setup Development Environment**:

   ```bash
   cd development
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Tests**:

   ```bash
   cd development/testing
   python test_basic_functionality.py
   python test_sensor_integration.py
   python test_solcast_integration.py
   ```

3. **Development Workflow**:
   - Make changes in `custom_components/genetic_load_manager/`
   - Test in `development/testing/`
   - Update documentation in `development/documentation/`
   - Commit and push changes

## 🔧 Configuration

### Core Settings

```yaml
genetic_load_manager:
  # Algorithm Parameters
  population_size: 100
  generations: 200
  mutation_rate: 0.05
  crossover_rate: 0.8

  # Device Configuration
  num_devices: 2
  device_priorities: [1.0, 0.8]

  # Energy Sources
  pv_forecast_entity: sensor.solcast_pv_forecast
  pv_forecast_tomorrow_entity: sensor.solcast_pv_forecast_tomorrow
  load_forecast_entity: sensor.load_forecast

  # Battery Management
  battery_soc_entity: sensor.battery_soc
  battery_capacity: 10.0
  max_charge_rate: 2.0
  max_discharge_rate: 2.0

  # Pricing
  use_indexed_pricing: true
  dynamic_pricing_entity: sensor.dynamic_pricing
```

## 🧪 Testing

The development environment includes comprehensive testing:

- **Unit Tests**: Core algorithm functionality
- **Integration Tests**: Home Assistant entity integration
- **Mock Tests**: Simulated data testing
- **Real Entity Tests**: Live Home Assistant testing

## 📚 Documentation

- **README.md** - Project overview and quick start
- **PROJECT_STRUCTURE.md** - Project organization guide
- **DEPLOYMENT.md** - Installation and configuration guide
- **TROUBLESHOOTING.md** - Complete troubleshooting guide
- **DEVELOPMENT.md** - Development environment and workflow

## 📊 Features

- **Genetic Algorithm Optimization**: Multi-objective optimization for energy management
- **Solar Integration**: PV forecast integration with Solcast
- **Dynamic Pricing**: Support for indexed tariffs and real-time pricing
- **Battery Management**: Intelligent battery charging/discharging
- **Device Priority**: Configurable device importance levels
- **Real-time Monitoring**: Live optimization status and metrics
- **Cost Analytics**: Detailed cost analysis and savings tracking
- **Interactive Dashboard**: Lovelace cards for monitoring and control

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions on GitHub
- **Documentation**: Check the project documentation files for detailed guides
- **Troubleshooting**: See `TROUBLESHOOTING.md` for common issues and solutions

## 🔄 Version History

- **v1.3.5**: Enhanced error handling and performance optimizations
- **v1.3.4**: Added indexed pricing calculator
- **v1.3.3**: Improved battery management algorithms
- **v1.3.2**: Enhanced solar forecast integration
- **v1.3.1**: Initial public release

---

**Note**: This integration is designed for advanced Home Assistant users with solar installations and dynamic pricing. Ensure you have the required entities and data sources configured before installation.
