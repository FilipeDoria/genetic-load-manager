# 🚨 **Genetic Load Manager - Complete Troubleshooting Guide**

## 📋 **Table of Contents**

1. [🚨 **Common Issues & Quick Fixes**](#-common-issues--quick-fixes)
2. [🔍 **Step-by-Step Debugging**](#-step-by-step-debugging)
3. [🧪 **Local Testing & Error Reproduction**](#-local-testing--error-reproduction)
4. [⚡ **Performance Optimization**](#-performance-optimization)
5. [📱 **Dashboard Issues**](#-dashboard-issues)
6. [🔧 **Advanced Debugging**](#-advanced-debugging)
7. [❓ **FAQ & Support**](#-faq--support)

---

## 🚨 **Common Issues & Quick Fixes**

### **1. "No PV forecast data available"**

**Problem**: The integration can't find solar forecast data
**Quick Fix**: Add this to your `configuration.yaml`:

```yaml
genetic_load_manager:
  pv_forecast_today: "sensor.solcast_pv_forecast_today"
  pv_forecast_tomorrow: "sensor.solcast_pv_forecast_tomorrow"
```

**Alternative**: Create placeholder entities:

```yaml
sensor:
  - platform: template
    sensors:
      solcast_pv_forecast_today:
        friendly_name: "PV Forecast Today"
        value_template: "0"
        attributes:
          DetailedForecast: []
      solcast_pv_forecast_tomorrow:
        friendly_name: "PV Forecast Tomorrow"
        value_template: "0"
        attributes:
          DetailedForecast: []
```

### **2. "No hourly prices found in OMIE entity"**

**Problem**: Missing electricity pricing data
**Quick Fix**: Add this to your `configuration.yaml`:

```yaml
genetic_load_manager:
  market_price: "sensor.omie_electricity_price"
```

**Alternative**: Create a simple price sensor:

```yaml
sensor:
  - platform: template
    sensors:
      omie_electricity_price:
        friendly_name: "Electricity Price"
        value_template: "{{ 50 }}" # Default price
        unit_of_measurement: "€/MWh"
```

### **3. "Failed to start optimizer"**

**Problem**: Genetic algorithm doesn't start
**Quick Fix**: Check required configuration:

```yaml
genetic_load_manager:
  # Required entities
  pv_forecast_today: "sensor.solcast_pv_forecast_today"
  pv_forecast_tomorrow: "sensor.solcast_pv_forecast_tomorrow"
  load_forecast: "sensor.load_forecast"
  battery_soc: "sensor.battery_soc"
  market_price: "sensor.omie_electricity_price"
```

### **4. "State attributes exceed maximum size"**

**Problem**: Too much data stored in sensor attributes
**Quick Fix**: The integration automatically handles this now
**Alternative**: Check your logs for detailed data instead of attributes

### **5. "Integration won't load"**

**Problem**: Integration fails to load after installation
**Quick Fix**:

1. Restart Home Assistant completely
2. Check file permissions
3. Verify Python version compatibility (3.8+)
4. Check Home Assistant logs for specific errors

---

## 🔍 **Step-by-Step Debugging**

### **Phase 1: Enable Detailed Logging**

```yaml
# In configuration.yaml or Developer Tools > YAML
logger:
  default: info
  logs:
    custom_components.genetic_load_manager: debug
    custom_components.genetic_load_manager.genetic_algorithm: debug
    custom_components.genetic_load_manager.pricing_calculator: debug
    custom_components.genetic_load_manager.sensor: debug
```

### **Phase 2: Check Integration Status**

1. Go to **Settings > Devices & Services**
2. Find your integration
3. Check status (should show "Running")
4. Look for any error messages
5. Click on the integration to see details

**Look for:**

- ✅ **Running** - Integration is working
- ❌ **Failed to load** - Configuration error
- ⚠️ **Not loaded** - Missing dependencies

### **Phase 3: Monitor Real-Time Logs**

**Option A: Home Assistant Logs**

1. Go to **Settings > System > Logs**
2. Look for entries with `custom_components.genetic_load_manager`
3. Filter by your integration name

**Option B: Developer Tools > Logs (Real-time)**

1. Go to **Developer Tools > Logs**
2. Filter by integration name
3. Watch logs as you interact with the integration

### **Phase 4: Test Individual Services**

In **Developer Tools > Services**, test each service:

```yaml
# Test 1: Basic Optimization
service: genetic_load_manager.run_optimization
data:
  population_size: 50
  generations: 100

# Test 2: Pricing Update
service: genetic_load_manager.update_pricing_parameters

# Test 3: Scheduler Toggle
service: genetic_load_manager.toggle_scheduler
data:
  mode: "rule-based"
```

**Watch the logs** for each service call to see:

- ✅ Service executed successfully
- ❌ Service failed with error
- ⚠️ Service completed with warnings

### **Phase 5: Check Entity States**

In **Developer Tools > States**, search for your entities:

```bash
# Search for these entities:
sensor.genetic_load_manager_dashboard
sensor.genetic_load_manager_indexed_pricing
switch.device_0_schedule
switch.device_1_schedule
```

**For each entity, check:**

- **State value** - Current status
- **Attributes** - Detailed data
- **Last updated** - When data was refreshed
- **Availability** - Entity status

### **Phase 6: Monitor Algorithm Execution**

**Watch for these log patterns:**

```bash
# ✅ Successful execution
INFO - Starting genetic algorithm optimization
INFO - PV forecast data fetched: 24 hours
INFO - Pricing data fetched: 24 hours
INFO - Optimization completed in 2.3 seconds

# ❌ Common failures
ERROR - No PV forecast data available
ERROR - No hourly prices found in OMIE entity
ERROR - Failed to start optimizer
WARNING - State attributes exceed maximum size
```

---

## 🧪 **Local Testing & Error Reproduction**

### **Quick Debug Commands**

```bash
# Enable debug logging
logger:
  custom_components.genetic_load_manager: debug

# Check entity states
# In Developer Tools > States, search for:
sensor.genetic_load_manager_dashboard
sensor.genetic_load_manager_indexed_pricing
switch.device_0_schedule
switch.device_1_schedule

# Test services
# In Developer Tools > Services
service: genetic_load_manager.run_optimization
data:
  population_size: 50
  generations: 100

# Monitor logs
# In Developer Tools > Logs, filter by:
custom_components.genetic_load_manager
```

### **Local Testing Environment**

The project includes a sophisticated local testing system that allows development without full Home Assistant installation:

```bash
# Run error reproduction script
python local_error_reproduction.py

# Test specific error modes
optimizer.set_error_mode("no_pv_data")
optimizer.set_error_mode("pricing_parsing_error")
optimizer.set_error_mode("startup_failure")
```

### **Test Categories**

| Test Type            | Purpose             | Duration | Coverage               |
| -------------------- | ------------------- | -------- | ---------------------- |
| **Quick Test**       | Basic validation    | 10-30s   | Core files, constants  |
| **Integration Test** | Component testing   | 1-5min   | All integration parts  |
| **Real Entity Test** | Mock simulation     | 2-10min  | Full entity processing |
| **Full Suite**       | Complete validation | 2-10min  | Everything end-to-end  |

### **Debug Checklist**

#### **Before Starting:**

- [ ] Integration is installed
- [ ] Detailed logging is enabled
- [ ] You have access to Home Assistant logs
- [ ] You understand the expected behavior

#### **During Debugging:**

- [ ] Monitor logs in real-time
- [ ] Test individual services
- [ ] Check entity states
- [ ] Note error patterns
- [ ] Document failure scenarios

#### **After Fixing:**

- [ ] Test the fix in Home Assistant
- [ ] Verify error is resolved
- [ ] Test related functionality
- [ ] Update documentation
- [ ] Consider adding tests

---

## ⚡ **Performance Optimization**

### **Algorithm Parameters**

```yaml
# For faster optimization (less accurate)
population_size: 50
generations: 100
mutation_rate: 0.1

# For better results (slower)
population_size: 200
generations: 500
mutation_rate: 0.03
```

### **Update Intervals**

```yaml
# Frequent updates (more responsive)
update_interval: 300  # 5 minutes

# Less frequent updates (better performance)
update_interval: 900  # 15 minutes
```

### **Entity Filtering**

```yaml
# Only essential entities
essential_entities_only: true

# All available entities
essential_entities_only: false
```

### **Performance Monitoring**

```yaml
# Enable performance monitoring
genetic_load_manager:
  performance_monitoring: true
  benchmark_mode: true
```

---

## 📱 **Dashboard Issues**

### **Common Dashboard Problems**

#### **❌ Problem: Dashboard Won't Load**

**Symptoms:**

- Dashboard shows "Error loading dashboard"
- Blank white screen
- "Invalid YAML" errors

**Solutions:**

1. **Use the Basic Dashboard**: Start with `basic_dashboard.yaml` - it uses only standard components
2. **Check YAML Syntax**: Validate your YAML in Home Assistant's YAML editor
3. **Clear Browser Cache**: Hard refresh (Ctrl+F5) or clear browser cache
4. **Check Entity Names**: Ensure all entity names match exactly

#### **❌ Problem: Custom Cards Not Working**

**Symptoms:**

- "Custom element doesn't exist" errors
- Missing card types
- Dashboard partially loads

**Solutions:**

1. **Avoid Custom Cards**: Use only standard Home Assistant cards
2. **Install HACS First**: If you want custom cards, install HACS first
3. **Use Basic Components**: Stick to `entities`, `glance`, `call-service`

#### **❌ Problem: Entities Not Showing**

**Symptoms:**

- Empty dashboard sections
- "Entity not found" errors
- Missing data

**Solutions:**

1. **Check Entity Names**: Verify entity IDs in Developer Tools > States
2. **Wait for Integration**: Some entities take time to appear after setup
3. **Check Integration Status**: Ensure the integration is running without errors

### **Dashboard Setup Steps**

#### **Step 1: Start with Basic Dashboard**

```yaml
# Copy basic_dashboard.yaml to your Home Assistant
# This uses only standard components and will definitely work
```

#### **Step 2: Verify Entities Exist**

1. Go to **Developer Tools > States**
2. Search for your integration entities:
   - `sensor.genetic_load_manager_dashboard`
   - `sensor.genetic_load_manager_indexed_pricing`
   - `switch.device_0_schedule`
   - `switch.device_1_schedule`

#### **Step 3: Test Individual Cards**

1. Create a simple test dashboard with just one card
2. Add cards one by one to identify problematic ones
3. Use the YAML editor to validate syntax

#### **Step 4: Check Integration Status**

1. Go to **Settings > Devices & Services**
2. Find your integration and check its status
3. Look for any error messages or warnings

### **Dashboard Types Available**

#### **1. Basic Dashboard** (`basic_dashboard.yaml`)

- ✅ **Guaranteed to work**
- ✅ Uses only standard Home Assistant components
- ✅ Simple, clean interface
- ✅ No custom dependencies

#### **2. Modern Dashboard** (`modern_dashboard.yaml`)

- ✅ Uses modern Home Assistant syntax
- ✅ Responsive design
- ✅ Standard components only
- ⚠️ May need entity adjustments

#### **3. Advanced Dashboard** (`advanced_dashboard.yaml`)

- ❌ **Requires custom cards** (button-card, apexcharts-card)
- ❌ **May not work** without HACS installation
- ❌ Complex configuration

### **Dashboard Checklist**

#### **Before Creating Dashboard:**

- [ ] Integration is installed and configured
- [ ] All required entities exist
- [ ] Integration is running without errors
- [ ] You have basic Home Assistant knowledge

#### **Dashboard Creation:**

- [ ] Start with basic dashboard
- [ ] Test each section individually
- [ ] Verify entity names match exactly
- [ ] Use YAML editor for syntax validation

#### **After Creation:**

- [ ] Dashboard loads without errors
- [ ] All entities display correctly
- [ ] Controls work as expected
- [ ] Mobile view is responsive

---

## 🔧 **Advanced Debugging**

### **Asyncio Issues**

#### **Common Asyncio Errors**

```
Detected blocking call to import_module with args ('custom_components.genetic_load_manager.application_credentials',) inside the event loop
Detected blocking call to import_module with args ('custom_components.genetic_load_manager',) inside the event loop
```

#### **Solutions**

1. **Move imports inside async functions**:

```python
# ❌ WRONG - Blocking import
from .heavy_module import HeavyClass

# ✅ CORRECT - Async import
async def async_function():
    from .heavy_module import HeavyClass
```

2. **Avoid blocking operations**:

```python
# ❌ WRONG - Blocking operation
def blocking_function():
    time.sleep(5)  # Blocks event loop

# ✅ CORRECT - Async operation
async def async_function():
    await asyncio.sleep(5)  # Non-blocking
```

3. **Use proper error handling**:

```python
# ❌ WRONG - No error handling
result = await some_operation()

# ✅ CORRECT - With error handling
try:
    result = await some_operation()
except Exception as e:
    _LOGGER.error(f"Operation failed: {e}")
    return False
```

### **Emergency Commands**

#### **If Integration Won't Load:**

```bash
# Check file permissions
ls -la custom_components/genetic_load_manager/

# Check Python syntax
python -m py_compile custom_components/genetic_load_manager/*.py

# Check for missing imports
grep -r "import" custom_components/genetic_load_manager/
```

#### **If Entities Not Updating:**

```bash
# Check integration status
# Go to Settings > Devices & Services

# Check entity availability
# Go to Developer Tools > States

# Check service registration
# Go to Developer Tools > Services
```

#### **If Algorithm Fails:**

```bash
# Check data sources
# Verify PV forecast entity
# Verify pricing entity
# Check algorithm parameters
```

### **Mobile Debugging**

#### **Use Home Assistant App:**

- Monitor logs on mobile
- Test services remotely
- Check entity states
- Receive notifications

#### **Remote Access:**

- Enable remote access in Home Assistant
- Use external URL for debugging
- Access logs from anywhere
- Test integration remotely

---

## ❓ **FAQ & Support**

### **Common Questions**

#### **Q: Why is my integration not working?**

**A**: Start with these steps:

1. Check Home Assistant logs for specific error messages
2. Verify all required entities exist and are accessible
3. Ensure entity data formats match expected structures
4. Consider using the default configuration temporarily

#### **Q: How do I know if the optimization is working?**

**A**: Look for these indicators:

1. Check `sensor.genetic_algorithm_status` entity
2. Monitor logs for optimization messages
3. Verify device schedules are being updated
4. Check cost analytics for savings calculations

#### **Q: Can I run this without solar panels?**

**A**: Yes, but with limited functionality:

1. The integration will use zero solar generation
2. Optimization will focus on cost and grid stability
3. You'll miss solar maximization benefits
4. Consider creating placeholder solar entities for testing

#### **Q: How often should I update the optimization?**

**A**: Depends on your needs:

1. **Frequent updates** (5-15 minutes): More responsive, higher CPU usage
2. **Standard updates** (15-30 minutes): Balanced performance
3. **Infrequent updates** (1+ hours): Better performance, less responsive

### **Getting Help**

#### **Before Asking for Help:**

1. **Check the logs** for specific error messages
2. **Verify your configuration** using YAML validation tools
3. **Test entities manually** using Developer Tools
4. **Simplify your setup** to isolate the problem

#### **When Reporting Issues:**

Include:

- **Home Assistant version**
- **Integration version**
- **Configuration details** (without sensitive info)
- **Error logs** (filtered by your integration)
- **Steps to reproduce** the issue
- **What you've already tried**

#### **Where to Get Help:**

1. **GitHub Issues**: Report bugs and feature requests
2. **Home Assistant Community**: Ask questions and get help
3. **Documentation**: Check this guide and project README
4. **Discussions**: Join community discussions on GitHub

---

## 🎯 **Success Indicators**

Your integration is working correctly when:

- ✅ Integration loads without errors
- ✅ All entities are created and updating
- ✅ Services execute successfully
- ✅ Algorithm runs and produces results
- ✅ No error messages in logs
- ✅ Dashboard displays correctly
- ✅ Mobile app works properly

---

## 🔄 **Continuous Debugging**

### **Monitor Regularly:**

- Check logs daily
- Test services weekly
- Verify entity updates
- Monitor performance

### **Update Gradually:**

- Make small changes
- Test each change
- Document modifications
- Keep backups

### **Learn from Errors:**

- Analyze error patterns
- Improve error handling
- Add better logging
- Create tests

---

_For more information, development guides, and community support, visit the project repository and documentation._
