# 🧪 **Genetic Load Manager - Testing Guide**

## 🎯 **How to Check if the Project is Functioning**

This guide provides multiple levels of testing to verify that your Genetic Load Manager integration is working correctly.

## 📁 **1. File Structure Verification**

### **✅ Check File Presence**
```bash
# Verify all required files exist
Get-ChildItem -Recurse | Select-Object Name, Length
```

**Expected Result:**
- All files should be present with appropriate sizes
- No missing or 0-byte files
- Proper directory structure maintained

### **✅ Verify HACS Compliance**
```
genetic-load-manager/
├── custom_components/                        ← REQUIRED by HACS
│   └── genetic-load-manager/                ← Integration directory
│       ├── __init__.py              ✅ (2.6KB)  - Main integration
│       ├── const.py                 ✅ (0.3KB)  - Constants
│       ├── manifest.json            ✅ (0.3KB)  - Metadata
│       ├── config_flow.py           ✅ (1.3KB)  - Configuration
│       ├── genetic_algorithm.py     ✅ (17.3KB) - GA engine
│       ├── sensor.py                ✅ (2.2KB)  - Sensors
│       ├── switch.py                ✅ (6.2KB)  - Switches
│       ├── binary_sensor.py         ✅ (7.7KB)  - Binary sensors
│       ├── services.yaml            ✅ (5.8KB)  - Services
│       └── translations/
│           └── en.json              ✅ (0.5KB)  - UI text
├── hacs.json                    ✅ (0.2KB) - HACS config
└── README.md                    ✅ (10.7KB) - Documentation
```

## 🔍 **2. Python Syntax Validation**

### **✅ Check Python Syntax**
```bash
# Test Python syntax for each file
python -m py_compile custom_components/genetic-load-manager/__init__.py
python -m py_compile custom_components/genetic-load-manager/sensor.py
python -m py_compile custom_components/genetic-load-manager/config_flow.py
python -m py_compile custom_components/genetic-load-manager/const.py
```

**Expected Result:**
- No syntax errors
- All files compile successfully
- No import errors

### **✅ Verify Import Dependencies**
```python
# Test basic imports
try:
    from homeassistant.components.sensor import SensorEntity
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
```

## 🏠 **3. Home Assistant Integration Testing**

### **✅ Basic Integration Test**
1. **Add Custom Repository to HACS**
   - Repository: `filipe0doria/genetic-load-manager`
   - Category: **Integration**

2. **Install via HACS**
   - Find "Genetic Load Manager" in HACS
   - Click **Download**
   - Restart Home Assistant

3. **Add Integration**
   - Go to **Settings** → **Devices & Services**
   - Click **Add Integration**
   - Search for "Genetic Load Manager"
   - Configure required entities

### **✅ Expected Results**
- **No setup errors** - Integration loads without errors
- **Sensors appear** - Status sensor visible in HA
- **Mock data displays** - Shows "Running" status
- **No platform errors** - All platforms load correctly

## 📊 **4. Sensor Functionality Testing**

### **✅ Verify Sensor Creation**
```yaml
# Check if sensors appear in Home Assistant
# Go to Developer Tools → States
# Search for: "genetic_load_manager"

# Expected sensors:
- sensor.genetic_load_manager_status
```

### **✅ Test Sensor Values**
```yaml
# Check sensor state and attributes
# Expected state: "Running" or "Stopped"
# Expected attributes:
- integration: "Genetic Load Manager"
- status: "Active"
- optimization_count: 5
```

### **✅ Monitor Sensor Updates**
- **Check sensor updates** - Values should refresh
- **Verify error handling** - No crashes on errors
- **Test mock data** - Should display test values

## 🎛️ **5. Configuration Flow Testing**

### **✅ Test Configuration Wizard**
1. **Start configuration** - Click "Add Integration"
2. **Fill required fields**:
   - PV Power Entity ID: `sensor.pv_power`
   - Forecast Entity ID: `sensor.solar_forecast`
   - Battery SOC Entity ID: `sensor.battery_level`
   - Electricity Price Entity ID: `sensor.electricity_price`
3. **Submit configuration** - Should create config entry

### **✅ Expected Results**
- **Configuration form** displays correctly
- **Entity validation** works properly
- **Config entry** created successfully
- **Integration appears** in devices list

## 🔧 **6. Mock Optimizer Testing**

### **✅ Verify Mock Data**
```python
# Check mock optimizer functionality
# The mock optimizer should provide:
- is_running: True
- current_generation: 25
- best_fitness: 750.0
- optimization_count: 5
- manageable_loads_count: 3
```

### **✅ Test Error Handling**
- **Simulate errors** - Mock optimizer should handle gracefully
- **Fallback values** - Should provide default values
- **No crashes** - Integration should remain stable

## 📝 **7. Log Analysis**

### **✅ Check Home Assistant Logs**
```yaml
# Go to Developer Tools → Logs
# Look for:
✅ "Genetic Load Manager integration setup completed successfully"
✅ "Genetic Load Manager sensor platform setup completed"
❌ No error messages
❌ No import errors
❌ No platform errors
```

### **✅ Monitor Integration Logs**
```yaml
# Check for these log entries:
- Integration setup messages
- Sensor creation messages
- Mock optimizer messages
- No error or warning messages
```

## 🚀 **8. Advanced Feature Testing**

### **✅ Enable Genetic Algorithm**
1. **Replace mock optimizer** with real GA
2. **Test optimization cycles** - Should run every 15 minutes
3. **Monitor performance** - Check fitness scores
4. **Verify load control** - Test switch functionality

### **✅ Test Load Control**
1. **Enable switch platform** - Add to PLATFORMS list
2. **Verify switches appear** - Load control entities
3. **Test manual control** - Turn loads on/off
4. **Check automation** - GA-based scheduling

### **✅ Test Binary Sensors**
1. **Enable binary sensor platform** - Add to PLATFORMS list
2. **Verify health sensors** - System status monitoring
3. **Test error detection** - System health indicators
4. **Monitor alerts** - Health status changes

## 🧪 **9. Automated Testing**

### **✅ Create Test Script**
```python
# test_integration.py
import asyncio
from unittest.mock import Mock, patch

async def test_basic_functionality():
    """Test basic integration functionality."""
    # Mock Home Assistant
    mock_hass = Mock()
    mock_entry = Mock()
    
    # Test integration setup
    from custom_components.genetic_load_manager import async_setup_entry
    result = await async_setup_entry(mock_hass, mock_entry)
    
    assert result == True
    print("✅ Basic functionality test passed")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
```

### **✅ Run Tests**
```bash
# Execute test script
python test_integration.py
```

## 🔍 **10. Troubleshooting Checklist**

### **❌ Common Issues & Solutions**

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Import Error** | `ModuleNotFoundError` | Check Python version compatibility |
| **Platform Error** | `Platform not found` | Verify sensor.py exists and has content |
| **Config Error** | `Config entry failed` | Check entity IDs and permissions |
| **Sensor Error** | `Sensor not updating` | Verify optimizer is working |
| **HACS Error** | `Repository not compliant` | Check directory structure |

### **✅ Health Check Commands**
```bash
# 1. File structure
tree /f

# 2. File sizes
Get-ChildItem -Recurse | Select-Object Name, Length

# 3. Python syntax
python -m py_compile custom_components/genetic-load-manager/*.py

# 4. Import test
python -c "import custom_components.genetic_load_manager"
```

## 🎯 **11. Success Criteria**

### **✅ Integration Successfully Working When:**
- **No setup errors** - Integration loads cleanly
- **Sensors visible** - All sensors appear in HA
- **Mock data displays** - Test values show correctly
- **No crashes** - Integration remains stable
- **Logs clean** - No error messages
- **HACS compliant** - Repository structure correct

### **✅ Ready for Production When:**
- **Basic functionality** tested and working
- **Error handling** robust and tested
- **Performance** acceptable and stable
- **Documentation** complete and accurate
- **User experience** smooth and intuitive

## 🚀 **12. Next Steps After Testing**

### **1. Basic Testing Complete**
- ✅ File structure verified
- ✅ Python syntax validated
- ✅ Integration loads without errors
- ✅ Sensors display correctly
- ✅ Mock data works

### **2. Enable Advanced Features**
- 🔄 Replace mock optimizer with real GA
- 🔄 Enable switch and binary sensor platforms
- 🔄 Test load control functionality
- 🔄 Configure real system entities

### **3. Production Deployment**
- 🔄 Test with real Home Assistant data
- 🔄 Monitor performance and stability
- 🔄 Gather user feedback
- 🔄 Iterate and improve

---

## 🎉 **Summary**

**To check if your Genetic Load Manager project is functioning:**

1. **✅ Verify file structure** - All files present and correct
2. **✅ Test Python syntax** - No compilation errors
3. **✅ Install in Home Assistant** - Integration loads without errors
4. **✅ Verify sensors appear** - Status sensor visible and working
5. **✅ Check mock data** - Test values display correctly
6. **✅ Monitor logs** - No error messages
7. **✅ Test configuration** - Setup wizard works properly

**The project is working correctly when all these tests pass!** 🚀

**Start with basic testing and gradually enable advanced features as you verify each component works properly.** 