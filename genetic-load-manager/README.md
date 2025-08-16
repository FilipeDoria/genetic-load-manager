# GA Load Manager HA Add-on

An intelligent load management system for Home Assistant that uses genetic algorithms to optimize household energy consumption based on photovoltaic production, battery status, and electricity market prices.

## Overview

This add-on implements a sophisticated load management system that runs in the background as a service, continuously optimizing the scheduling of manageable loads every 15 minutes. It uses genetic algorithms to find optimal load schedules that minimize energy costs while maximizing the utilization of renewable energy sources.

## Features

- **Genetic Algorithm Optimization**: Advanced optimization engine that evolves load schedules over multiple generations
- **Real-time Monitoring**: Continuous monitoring of PV production, battery state of charge, and electricity prices
- **Intelligent Scheduling**: 15-minute interval optimization for precise load control
- **Web Interface**: Modern, responsive web UI for configuration and monitoring
- **Background Service**: Runs continuously without user intervention
- **Configurable Parameters**: Adjustable genetic algorithm parameters for fine-tuning
- **Comprehensive Logging**: Detailed logs of all optimization runs and system events

## Research Context

This add-on is developed as part of thesis research on intelligent load management systems. It demonstrates the practical application of genetic algorithms in residential energy management, providing a foundation for research into:

- Multi-objective optimization in energy systems
- Real-time decision making for load scheduling
- Integration of renewable energy sources with conventional loads
- Economic optimization of household energy consumption

## Dependencies

### System Requirements
- Home Assistant Core 2023.8.0 or later
- Home Assistant Supervisor
- Add-on Store support

### Python Dependencies
- Flask 2.3.3 - Web framework for the UI
- NumPy 1.24.3 - Numerical computing
- DEAP 1.4.1 - Distributed Evolutionary Algorithms in Python
- APScheduler 3.10.4 - Task scheduling
- Requests 2.31.0 - HTTP library
- Pandas 2.0.3 - Data manipulation
- SciPy 1.11.1 - Scientific computing

## Installation

### 1. Add the Repository

1. In Home Assistant, go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the three dots menu (⋮) in the top right
3. Select **Repositories**
4. Add the repository URL: `https://github.com/filipe0doria/genetic-load-manager`
5. Click **Add**

### 2. Install the Add-on

1. Find "GA Load Manager HA Add-on" in the Add-on Store
2. Click on it and then click **Install**
3. Wait for the installation to complete

### 3. Configuration

1. Click **Start** to begin the add-on
2. Go to the **Configuration** tab
3. Configure the following entities:
   - **PV Power Entity**: Entity ID for photovoltaic power production
   - **Forecast Entity**: Entity ID for PV production forecasts
   - **Battery SOC Entity**: Entity ID for battery state of charge
   - **Price Entity**: Entity ID for electricity market price
4. Adjust genetic algorithm parameters if needed
5. Click **Save Configuration**

### 4. Select Manageable Loads

1. Go to the **Manage Loads** tab
2. Check the loads you want the system to manage
3. Click **Save Loads**

### 5. Access the Web Interface

#### Option A: Through Home Assistant (Recommended)
1. In Home Assistant, go to **Settings** → **Add-ons**
2. Find "GA Load Manager HA Add-on"
3. Click **Open Web UI**

#### Option B: Direct Access
1. Ensure `enable_external_access: true` in add-on options
2. Access directly at: `http://your-ha-ip:8123/`
3. The add-on must be running for direct access to work

## Configuration

### Entity IDs

The add-on requires several Home Assistant entities to function properly:

- **PV Power Entity**: Real-time photovoltaic power production (e.g., `sensor.pv_power`)
- **Forecast Entity**: PV production forecasts for the next 24 hours (e.g., `sensor.pv_forecast`)
- **Battery SOC Entity**: Current battery state of charge percentage (e.g., `sensor.battery_soc`)
- **Price Entity**: Current electricity market price (e.g., `sensor.electricity_price`)

### Genetic Algorithm Parameters

- **Population Size**: Number of individuals in each generation (default: 50)
- **Generations**: Number of evolution generations (default: 100)
- **Mutation Rate**: Probability of genetic mutation (default: 0.1)
- **Crossover Rate**: Probability of genetic crossover (default: 0.8)

### Optimization Interval

Set how often the system should run optimization (default: 15 minutes). Lower intervals provide more responsive control but increase computational load.

### Access Control

- **Enable External Access**: Set to `true` to allow direct access to the web UI (default: `true`)
- **External Port**: Port number for direct access (default: `8123`)
- **Note**: When external access is enabled, the web UI is accessible both through Home Assistant and directly via the external port

## Access Methods

The add-on provides **two ways** to access the web interface:

### 1. **Through Home Assistant (Recommended)**
- **URL**: `http://your-ha-ip:8123/addons/genetic_load_manager/`
- **Benefits**: 
  - Integrated with Home Assistant
  - Uses HA authentication and security
  - Appears in HA sidebar
  - Secure access through HA's ingress system
- **How to access**: 
  1. Go to **Settings** → **Add-ons** in Home Assistant
  2. Find "GA Load Manager HA Add-on"
  3. Click **Open Web UI**

### 2. **Direct External Access**
- **URL**: `http://your-ha-ip:8123/` (when add-on is running)
- **Benefits**: 
  - Direct access from any device
  - Can bookmark the URL
  - Works independently of HA interface
  - Useful for mobile apps or external monitoring
- **Configuration**: 
  - Set `enable_external_access: true` in add-on options
  - Configure `external_port` if needed

## Usage

### Dashboard

The main dashboard displays:
- Current system status (PV power, battery SOC, electricity price)
- List of manageable loads
- Current optimization schedule
- Manual optimization trigger button

### Configuration

Access all add-on settings including:
- Entity ID configuration
- Genetic algorithm parameters
- Optimization timing

### Load Management

Select which loads should be managed by the genetic algorithm. Only checked loads will be included in optimization calculations.

### Logs

View detailed logs of:
- Optimization runs
- System events
- Error messages
- Performance metrics

## How It Works

### 1. Data Collection

The system continuously monitors:
- Current PV production
- Battery state of charge
- Electricity market prices
- Load status and power consumption

### 2. Optimization Process

Every 15 minutes (or configured interval), the system:
1. Collects current system state
2. Generates initial population of load schedules
3. Evolves schedules using genetic algorithms
4. Evaluates fitness based on multiple objectives:
   - Energy cost minimization
   - PV utilization maximization
   - Battery efficiency optimization
   - Load balancing

### 3. Schedule Application

The best schedule is applied to Home Assistant entities, controlling:
- Load switching
- Power consumption timing
- Battery charging/discharging
- Grid energy usage

## API Endpoints

The add-on provides several REST API endpoints:

- `GET /` - Main dashboard
- `GET /config` - Configuration interface
- `GET /loads` - Load management interface
- `GET /logs` - Log viewing interface
- `POST /api/optimize` - Trigger manual optimization
- `GET /health` - Health check endpoint

## Troubleshooting

### Common Issues

1. **Entity Not Found**: Ensure all configured entity IDs exist in Home Assistant
2. **Optimization Fails**: Check logs for specific error messages
3. **High CPU Usage**: Reduce population size or generations in genetic algorithm settings
4. **Scheduling Issues**: Verify optimization interval is appropriate for your system
5. **Docker Build Errors**: If you encounter build issues, try these solutions:
   - **Use `Dockerfile.python313`** (recommended for Python 3.13+ systems)
   - **Use `Dockerfile.pure-python`** (pure Python, no compilation needed)
   - Use `Dockerfile.modern` for the latest Python 3.11+ approach
   - Use `Dockerfile.minimal` for a lighter build
   - Ensure you're using Python 3.13+ (the main Dockerfile now supports this)
   - Check that all system dependencies are properly installed

6. **Web UI Access Issues**: If you can't access the web interface:
   - Ensure the add-on is running
   - Check that `enable_external_access: true` in add-on options
   - Try accessing through Home Assistant first (Settings → Add-ons → Open Web UI)
   - Verify the external port (default: 8123) is not blocked by firewall
   - Check add-on logs for any startup errors

### Log Analysis

Check the logs tab for:
- Error messages with timestamps
- Optimization performance metrics
- System health indicators

### Performance Tuning

For better performance:
- Reduce genetic algorithm complexity for faster optimization
- Increase optimization interval for less frequent updates
- Monitor system resources during operation

## Development

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables for Home Assistant access
4. Run: `python app.py`

### Docker Build Issues

If you encounter build issues during Docker builds, you can:

1. **Use the Python 3.13 Dockerfile** (recommended for Python 3.13+ systems)
2. **Use the pure Python Dockerfile** (pure Python, no compilation needed)
3. **Use the main Dockerfile** (for modern systems with Python 3.11+)
4. **Use the modern Dockerfile**: Rename `Dockerfile.modern` to `Dockerfile` for the latest approach
5. **Use the minimal Dockerfile**: Rename `Dockerfile.minimal` to `Dockerfile` for a lighter build
6. **Use the alternative Dockerfile**: Rename `Dockerfile.alternative` to `Dockerfile` for Alpine-based systems
7. **Ensure Python 3.13+ compatibility**: The add-on now supports Python 3.13 with pure Python packages

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is developed for research purposes. Please contact the author for licensing information.

## Support

For support and questions:
- Check the logs for error messages
- Review the configuration settings
- Consult the Home Assistant community forums
- Open an issue on the GitHub repository

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version information.

---

**Note**: This add-on is designed for research and educational purposes. Always test thoroughly in your environment before relying on it for critical load management. 