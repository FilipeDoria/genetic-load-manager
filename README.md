# 🧬 **Genetic Load Manager - Advanced HACS Integration - version: 1.3.1**

A sophisticated Home Assistant integration for **intelligent load management** using **genetic algorithms** to optimize energy consumption, reduce costs, and maximize solar power utilization.

## 🚀 **Key Features**

### **🧬 Genetic Algorithm Engine**
- **Advanced optimization** using genetic algorithms
- **Configurable parameters** (population size, generations, mutation rate)
- **Real-time adaptation** to changing conditions
- **15-minute optimization cycles** for continuous improvement

### **📊 Comprehensive Monitoring**
- **12+ specialized sensors** for optimization metrics
- **Real-time status monitoring** of all components
- **Performance analytics** and efficiency tracking
- **Cost optimization** and solar utilization metrics

### **🎛️ Load Control System**
- **Automatic load scheduling** based on optimization results
- **Manual load control** through switch entities
- **Priority-based load management** (1-5 priority levels)
- **Flexible load configuration** for different device types

### **🔍 System Health Monitoring**
- **Binary sensors** for system status
- **Error detection** and logging
- **Performance metrics** and health indicators
- **Comprehensive logging** system

## 📁 **Repository Structure**

```
genetic-load-manager/
├── custom_components/                        ← REQUIRED by HACS
│   └── genetic-load-manager/                ← Integration directory
│       ├── __init__.py              ✅ (1.2KB)  - Main integration setup
│       ├── const.py                 ✅ (0.3KB)  - Constants
│       ├── manifest.json            ✅ (0.3KB)  - Integration metadata
│       ├── config_flow.py           ✅ (1.3KB)  - Configuration wizard
│       ├── genetic_algorithm.py     ✅ (14.7KB) - Core GA engine
│       ├── sensor.py                ✅ (15.1KB) - 12 monitoring sensors
│       ├── switch.py                ✅ (12.4KB) - Load control switches
│       ├── binary_sensor.py         ✅ (12.0KB) - System health sensors
│       ├── services.yaml            ✅ (6.7KB)  - 15+ control services
│       └── translations/
│           └── en.json              ✅ (4.7KB)  - User interface text
├── hacs.json                    ✅ (0.2KB) - HACS configuration
└── README.md                    ✅ (8.1KB) - This documentation
```

## 🔧 **Installation**

### **1. Add Custom Repository to HACS**
```
Repository: filipe0doria/genetic-load-manager
Category: Integration
```

### **2. Install via HACS**
- Find "Genetic Load Manager" in HACS
- Click **Download**
- Restart Home Assistant

### **3. Add Integration**
- Go to **Settings** → **Devices & Services**
- Click **Add Integration**
- Search for "Genetic Load Manager"
- Configure required entities

## ⚙️ **Configuration**

### **Required Entities**
- **PV Power Entity ID** - Solar production monitoring
- **Forecast Entity ID** - Weather/solar forecast
- **Battery SOC Entity ID** - Battery state of charge
- **Electricity Price Entity ID** - Energy pricing data

### **Optional Parameters**
- **Population Size** - GA population (10-200, default: 50)
- **Generations** - GA iterations (10-500, default: 100)
- **Mutation Rate** - Genetic mutation (0.01-0.5, default: 0.1)
- **Crossover Rate** - Genetic crossover (0.1-1.0, default: 0.8)

## 📊 **Sensors & Monitoring**

### **🔍 Optimization Sensors**
- **Optimization Status** - Running/Stopped state
- **Last Optimization** - Timestamp of last run
- **Next Optimization** - Scheduled next run
- **Optimization Count** - Total runs completed
- **Best Fitness** - Current best optimization score
- **Current Generation** - Active GA generation

### **📈 Performance Sensors**
- **System Efficiency** - Overall optimization efficiency
- **Energy Cost** - Current energy cost optimization
- **Solar Utilization** - Solar power usage percentage
- **Load Control Status** - Load management status
- **Algorithm Logs** - Optimization log entries

### **🎛️ Control Sensors**
- **Manageable Loads** - Count of controllable devices

## 🎛️ **Switches & Load Control**

### **Automatic Control**
- **Genetic algorithm** automatically schedules loads
- **15-minute optimization** cycles
- **Cost-aware scheduling** based on electricity prices
- **Solar optimization** to maximize renewable usage

### **Manual Control**
- **Direct load control** through switch entities
- **Priority-based management** (1-5 priority levels)
- **Flexible scheduling** for different load types
- **Real-time status** monitoring

## 🔍 **Binary Sensors & Health Monitoring**

### **System Health**
- **Optimization Running** - GA service status
- **System Healthy** - Overall system health
- **Loads Controlled** - Load management status
- **Algorithm Errors** - Error detection and logging

### **Health Indicators**
- **Performance metrics** and efficiency tracking
- **Error detection** and logging
- **System status** monitoring
- **Health alerts** and notifications

## 🛠️ **Services & Control**

### **Optimization Services**
- **`optimize_loads`** - Manual optimization trigger
- **`apply_schedule`** - Apply optimized schedule
- **`reset_optimization`** - Reset optimization data
- **`start_optimization`** - Start GA service
- **`stop_optimization`** - Stop GA service

### **Load Control Services**
- **`control_load`** - Direct load control
- **`update_manageable_loads`** - Scan for new loads
- **`set_optimization_parameters`** - Update GA parameters

### **Monitoring Services**
- **`get_optimization_status`** - Get current status
- **`get_algorithm_logs`** - Retrieve optimization logs
- **`export_schedule`** - Export current schedule

## 🧬 **Genetic Algorithm Details**

### **Core Algorithm**
- **Population-based optimization** with configurable size
- **Tournament selection** for parent selection
- **Single-point crossover** for genetic recombination
- **Random mutation** with configurable rates
- **Fitness evaluation** based on cost and efficiency

### **Optimization Criteria**
- **Energy cost minimization** based on electricity prices
- **Solar power maximization** during peak production
- **Peak hour penalty** to avoid high-demand periods
- **Load priority management** for critical devices
- **Flexibility constraints** for different load types

### **Adaptive Features**
- **Real-time system state** monitoring
- **Dynamic parameter adjustment** based on performance
- **Continuous learning** from optimization results
- **Error handling** and recovery mechanisms

## 📊 **Performance & Monitoring**

### **Real-time Metrics**
- **Optimization progress** tracking
- **Fitness score evolution** over generations
- **System efficiency** measurements
- **Cost savings** calculations
- **Solar utilization** percentages

### **Logging & Debugging**
- **Comprehensive logging** system
- **Error tracking** and reporting
- **Performance metrics** collection
- **Debug information** for troubleshooting
- **Historical data** retention

## 🔄 **Optimization Cycle**

### **15-Minute Intervals**
1. **System State Analysis** - Current conditions
2. **Genetic Algorithm Execution** - Population evolution
3. **Schedule Optimization** - Best solution selection
4. **Load Control Application** - Schedule implementation
5. **Performance Monitoring** - Results tracking
6. **Parameter Adjustment** - Continuous improvement

### **Continuous Learning**
- **Performance feedback** integration
- **Parameter optimization** based on results
- **Load behavior** pattern recognition
- **Cost efficiency** improvement
- **Solar utilization** optimization

## 🚨 **Troubleshooting**

### **Common Issues**
- **Integration not loading** - Check entity IDs
- **Optimization errors** - Verify system state
- **Load control issues** - Check switch permissions
- **Performance problems** - Adjust GA parameters

### **Debug Steps**
1. **Check Home Assistant logs** for errors
2. **Verify entity availability** and permissions
3. **Monitor optimization status** sensors
4. **Review algorithm logs** for issues
5. **Test load control** manually

## 🔮 **Future Enhancements**

### **Planned Features**
- **Machine learning** integration for better predictions
- **Advanced scheduling** algorithms
- **Weather integration** for solar forecasting
- **Battery optimization** strategies
- **Grid demand response** integration

### **Extensibility**
- **Custom fitness functions** for specific needs
- **Plugin architecture** for additional algorithms
- **API integration** with external systems
- **Advanced analytics** and reporting
- **Mobile app** for remote control

## 📚 **Technical Details**

### **Requirements**
- **Home Assistant** 2023.8.0 or later
- **Python 3.9+** compatibility
- **Async/await** support
- **Entity state** access permissions
- **Service call** permissions

### **Architecture**
- **Modular design** for easy extension
- **Async operations** for performance
- **Error handling** and recovery
- **State management** and persistence
- **Service integration** with HA

## 🤝 **Contributing**

### **Development Setup**
1. **Fork the repository**
2. **Create feature branch**
3. **Implement changes**
4. **Add tests** and documentation
5. **Submit pull request**

### **Code Standards**
- **Python PEP 8** compliance
- **Type hints** for all functions
- **Comprehensive docstrings**
- **Error handling** best practices
- **Performance optimization**

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 **Acknowledgments**

- **Home Assistant Community** for the excellent platform
- **HACS** for the integration management system
- **Genetic Algorithm research** community
- **Energy optimization** researchers and practitioners

---

## 🎯 **Quick Start**

1. **Install via HACS** - Add custom repository
2. **Configure entities** - Set up required sensors
3. **Start optimization** - Begin genetic algorithm
4. **Monitor progress** - Watch optimization sensors
5. **Control loads** - Use generated switches
6. **Optimize further** - Adjust parameters as needed

**The Genetic Load Manager will automatically optimize your home's energy consumption using advanced genetic algorithms, reducing costs and maximizing solar power utilization!** 🚀 