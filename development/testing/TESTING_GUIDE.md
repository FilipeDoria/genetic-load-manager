# 🧪 Local Testing Guide for Genetic Load Manager

This guide explains how to test your Genetic Load Manager integration locally without needing a full Home Assistant installation.

## 🚀 **Quick Start Testing**

### **1. Run All Tests (Recommended)**
```bash
cd development/testing
python run_tests.py
```

This will run all test suites and provide a comprehensive summary.

### **2. Individual Test Scripts**
```bash
# Test integration components
python test_integration_local.py

# Test real HA entities simulation
python test_real_ha_entities.py

# Test algorithm functionality
python quick_algorithm_test.py
```

## 📋 **What Each Test Does**

### **`test_integration_local.py`**
- ✅ **Constants validation** - Checks all configuration constants
- ✅ **Pricing calculator** - Tests indexed tariff calculations
- ✅ **Genetic algorithm** - Tests core optimization engine
- ✅ **Entity processing** - Tests Home Assistant entity handling
- ✅ **Configuration validation** - Tests parameter constraints
- ✅ **Services** - Validates service definitions
- ✅ **Translations** - Checks translation files
- ✅ **Performance** - Runs algorithm performance tests

### **`test_real_ha_entities.py`**
- ✅ **Mock entity creation** - Creates realistic HA entities
- ✅ **Data extraction** - Tests entity data processing
- ✅ **Real-time simulation** - Simulates live data updates
- ✅ **Optimization data** - Creates optimization-ready data structures
- ✅ **PV forecast usage** - Demonstrates solar forecast handling
- ✅ **OMIE pricing usage** - Shows electricity price optimization

### **`quick_algorithm_test.py`**
- ✅ **Basic algorithm** - Tests core genetic algorithm
- ✅ **Quick optimization** - Runs fast optimization test
- ✅ **Constraints** - Validates parameter limits

## 🔧 **Testing Prerequisites**

### **Required Python Packages**
```bash
pip install numpy scipy matplotlib
```

### **Directory Structure**
```
genetic-load-manager/
├── custom_components/
│   └── genetic_load_manager/
│       ├── __init__.py
│       ├── genetic_algorithm.py
│       ├── pricing_calculator.py
│       ├── const.py
│       └── ...
└── development/
    └── testing/
        ├── test_integration_local.py
        ├── test_real_ha_entities.py
        ├── quick_algorithm_test.py
        └── run_tests.py
```

## 🧪 **Testing Approaches**

### **1. Unit Testing (Fastest)**
```bash
python quick_algorithm_test.py
```
- **Duration**: 10-30 seconds
- **Purpose**: Verify core algorithm functionality
- **Best for**: Development and debugging

### **2. Integration Testing (Comprehensive)**
```bash
python test_integration_local.py
```
- **Duration**: 1-5 minutes
- **Purpose**: Test all integration components
- **Best for**: Pre-deployment validation

### **3. Full Test Suite (Complete)**
```bash
python run_tests.py
```
- **Duration**: 2-10 minutes
- **Purpose**: Test everything end-to-end
- **Best for**: Final validation before HACS submission

## 🔍 **Understanding Test Results**

### **✅ PASS Indicators**
- All constants properly defined
- Algorithm creates and runs successfully
- Entity data processing works correctly
- Configuration validation passes
- Services and translations load properly

### **❌ FAIL Indicators**
- Missing dependencies or imports
- Algorithm crashes or errors
- Configuration validation fails
- File loading errors
- Performance issues

### **⚠️ WARNING Indicators**
- Tests complete but with issues
- Performance below expectations
- Missing optional features
- Deprecated functionality usage

## 🚨 **Common Issues and Solutions**

### **Import Errors**
```bash
❌ Import Error: No module named 'genetic_load_manager'
```
**Solution**: Ensure you're running from the correct directory and the path is set correctly.

### **Missing Dependencies**
```bash
❌ ModuleNotFoundError: No module named 'numpy'
```
**Solution**: Install required packages: `pip install numpy scipy matplotlib`

### **File Not Found**
```bash
❌ Services file not found
```
**Solution**: Check that all integration files are in the correct locations.

### **Algorithm Crashes**
```bash
❌ Genetic algorithm test failed
```
**Solution**: Check the genetic algorithm implementation for errors or missing methods.

## 📊 **Performance Benchmarks**

### **Expected Test Times**
- **Quick test**: 10-30 seconds
- **Integration test**: 1-5 minutes
- **Full suite**: 2-10 minutes
- **Performance test**: 1-2 minutes

### **Performance Indicators**
- **Generations/second**: > 1.0 (good), > 2.0 (excellent)
- **Memory usage**: < 100MB for small tests
- **CPU usage**: < 80% during optimization

## 🔄 **Continuous Testing**

### **Development Workflow**
1. **Make changes** to integration code
2. **Run quick test** to verify basic functionality
3. **Run integration test** to check components
4. **Fix any issues** that arise
5. **Repeat** until all tests pass

### **Pre-commit Testing**
```bash
# Before committing changes
python quick_algorithm_test.py
python test_integration_local.py
```

### **Pre-deployment Testing**
```bash
# Before HACS submission
python run_tests.py
```

## 🌐 **Advanced Testing Scenarios**

### **Custom Entity Testing**
```python
# In test_real_ha_entities.py
def test_custom_entities():
    # Add your custom entity types here
    custom_entity = MockHAEntity(
        'sensor.custom_sensor',
        '42.0',
        {'custom_attribute': 'custom_value'}
    )
    # Test processing...
```

### **Performance Profiling**
```python
# Add to any test script
import cProfile
import pstats

def profile_optimization():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run optimization...
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### **Memory Testing**
```python
# Add to performance tests
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / 1024 / 1024  # MB
    
    # Run test...
    
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Memory usage: {memory_after - memory_before:.1f} MB")
```

## 📝 **Test Output Examples**

### **Successful Test Run**
```
🧬 Genetic Load Manager - Local Integration Testing
============================================================

==================== Constants ====================
✅ DOMAIN: genetic_load_manager
✅ CONF_POPULATION_SIZE: population_size
✅ CONF_GENERATIONS: generations
...

==================== Genetic Algorithm ====================
✅ Successfully imported integration modules
✅ Optimizer created with config: {...}
✅ Fitness calculation: -1234.5678
🔄 Running single optimization...
✅ Optimization completed in 2.34 seconds
   Best fitness: -987.6543
   Generations: 20

============================================================
📊 TEST SUMMARY
============================================================
✅ PASS Constants
✅ PASS Pricing Calculator
✅ PASS Genetic Algorithm
...

Overall: 8/8 tests passed (100.0%)
🎉 All tests passed! Integration is ready for deployment.
```

### **Failed Test Run**
```
❌ FAIL Genetic Algorithm
❌ Genetic algorithm test failed: 'GeneticLoadOptimizer' object has no attribute 'calculate_fitness'

============================================================
📊 TEST SUMMARY
============================================================
✅ PASS Constants
❌ FAIL Genetic Algorithm
...

Overall: 7/8 tests passed (87.5%)
⚠️  Some tests failed. Please review the errors above.
```

## 🎯 **Next Steps After Testing**

### **All Tests Pass**
1. ✅ **Integration is ready** for Home Assistant testing
2. 🚀 **Deploy to development HA instance**
3. 📤 **Submit to HACS** for community testing

### **Some Tests Fail**
1. 🔍 **Review error messages** and stack traces
2. 🐛 **Fix identified issues** in the code
3. 🔄 **Re-run tests** to verify fixes
4. 📝 **Document any limitations** or known issues

### **Critical Failures**
1. 🚨 **Stop development** until core issues are resolved
2. 🔧 **Focus on fixing** fundamental problems first
3. 🧪 **Simplify tests** to isolate specific issues
4. 📚 **Review documentation** and examples

## 📚 **Additional Resources**

### **Home Assistant Development**
- [Custom Integration Development](https://developers.home-assistant.io/docs/creating_integration)
- [Testing Custom Integrations](https://developers.home-assistant.io/docs/development_environment)
- [Mock Objects for Testing](https://developers.home-assistant.io/docs/development_environment#mocking)

### **Genetic Algorithm Resources**
- [NumPy Documentation](https://numpy.org/doc/)
- [SciPy Optimization](https://docs.scipy.org/doc/scipy/reference/optimize.html)
- [Genetic Algorithm Theory](https://en.wikipedia.org/wiki/Genetic_algorithm)

### **Testing Best Practices**
- [Python Testing with pytest](https://docs.pytest.org/)
- [Unit Testing Guidelines](https://realpython.com/python-testing/)
- [Performance Testing](https://realpython.com/python-performance-testing/)

---

**Happy Testing! 🧪✨**

Your Genetic Load Manager integration is now ready for comprehensive local testing. Run the tests, fix any issues, and get ready for HACS deployment! 🚀
