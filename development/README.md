# 🔬 Development Environment

This directory contains the development and testing environment for the Genetic Load Manager project.

## 📁 Structure

```
development/
├── testing/                    # Test scripts and mock data
├── documentation/              # Development documentation
├── research/                   # Research and analysis files
├── inputs.txt                  # Test input parameters
├── schedules.png               # Test schedule visualizations
├── venv/                       # Python virtual environment
└── README.md                   # This file
```

## 🚀 Getting Started

### 1. Setup Virtual Environment

```bash
cd development
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install numpy pandas matplotlib homeassistant pytest
```

### 3. Run Tests

```bash
cd testing

# Basic functionality tests
python test_basic_functionality.py

# Sensor integration tests
python test_sensor_integration.py

# Solcast integration tests
python test_solcast_integration.py

# Mock sensor tests
python test_sensor_mock.py
```

## 🧪 Testing Framework

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test Home Assistant entity integration
- **Mock Tests**: Test with simulated data
- **Real Entity Tests**: Test with live Home Assistant instances

### Running Specific Tests

```bash
# Run all tests in a file
python test_basic_functionality.py

# Run with verbose output
python -v test_sensor_integration.py

# Run with custom test data
python test_solcast_integration.py --data-file custom_data.json
```

## 🔧 Development Workflow

### 1. Make Changes

1. Edit files in `custom_components/genetic_load_manager/`
2. Test changes in `development/testing/`
3. Update documentation in `development/documentation/`

### 2. Testing Cycle

```bash
# 1. Run basic tests
python test_basic_functionality.py

# 2. Run integration tests
python test_sensor_integration.py

# 3. Run mock tests
python test_sensor_mock.py

# 4. If all pass, test in real Home Assistant
```

### 3. Documentation Updates

- Update relevant `.md` files in `development/documentation/`
- Update main `README.md` if needed
- Update inline code comments

## 📊 Test Data

### Input Parameters (`inputs.txt`)

Contains test configuration parameters:
- Algorithm settings
- Device configurations
- Pricing parameters
- Battery settings

### Generated Visualizations

- `schedules.png`: Optimization schedule results
- `*.png` in testing/: Test result charts and graphs

## 🐛 Debugging

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Path Issues**: Check relative paths from development directory
3. **Dependency Issues**: Verify all required packages are installed

### Debug Mode

```bash
# Run tests with debug output
python -v test_basic_functionality.py

# Enable logging
export PYTHONPATH="${PYTHONPATH}:../custom_components"
python test_sensor_integration.py
```

## 📝 Contributing

### Before Submitting

1. ✅ All tests pass
2. ✅ Documentation updated
3. ✅ Code follows project style
4. ✅ No merge conflicts
5. ✅ Integration tested in real Home Assistant

### Code Style

- Follow PEP 8 guidelines
- Use descriptive variable names
- Add type hints where possible
- Include docstrings for functions

## 🔍 Research & Analysis

The `research/` directory contains:
- Algorithm performance analysis
- Optimization results
- Cost-benefit analysis
- Integration research

## 📚 Documentation

### Guides

- `ADDING_SENSORS_GUIDE.md`: How to add new sensors
- `INDEXED_PRICING_GUIDE.md`: Pricing system implementation
- `ALGORITHM_IMPROVEMENTS.md`: Algorithm development notes

### Analysis

- `REAL_ENTITY_TESTING_SUMMARY.md`: Testing results summary
- `entity_analysis_summary.md`: Entity analysis results

## 🚨 Important Notes

- **Never commit test data** to the main repository
- **Always test** changes before committing
- **Update documentation** when adding new features
- **Follow the testing workflow** for all changes

## 🆘 Getting Help

- Check existing documentation in `development/documentation/`
- Review test examples in `development/testing/`
- Check the main project `README.md`
- Open an issue on GitHub for bugs
- Start a discussion for questions
