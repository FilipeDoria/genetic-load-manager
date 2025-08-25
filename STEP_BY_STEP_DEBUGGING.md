# Step-by-Step Debugging Guide for Genetic Load Manager

## 🎯 **Overview**

This guide shows you how to debug the integration **within Home Assistant** and then **reproduce errors locally** for testing and fixing.

## 🔍 **Phase 1: Debugging Within Home Assistant**

### **Step 1: Enable Detailed Logging**

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

**What this does:**
- Shows detailed logs for your integration
- Reveals exactly where failures occur
- Shows data flow between components

### **Step 2: Check Integration Status**

1. Go to **Settings > Devices & Services**
2. Find your integration
3. Check status (should show "Running")
4. Look for any error messages
5. Click on the integration to see details

**Look for:**
- ✅ **Running** - Integration is working
- ❌ **Failed to load** - Configuration error
- ⚠️ **Not loaded** - Missing dependencies

### **Step 3: Monitor Real-Time Logs**

**Option A: Home Assistant Logs**
1. Go to **Settings > System > Logs**
2. Look for entries with `custom_components.genetic_load_manager`
3. Filter by your integration name

**Option B: Developer Tools > Logs (Real-time)**
1. Go to **Developer Tools > Logs**
2. Filter by integration name
3. Watch logs as you interact with the integration

### **Step 4: Test Individual Services**

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

### **Step 5: Check Entity States**

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

### **Step 6: Monitor Algorithm Execution**

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

## 🧪 **Phase 2: Reproducing Errors Locally**

### **Step 1: Run the Error Reproduction Script**

```bash
# In your development directory
python local_error_reproduction.py
```

**This script will:**
- Test normal operation
- Reproduce common errors
- Show error patterns
- Provide debugging insights

### **Step 2: Analyze Error Patterns**

**Common Error Types:**

1. **PV Forecast Errors:**
   ```bash
   ERROR - No Solcast PV forecast data available
   ERROR - Failed to parse PV forecast data structure
   ```

2. **Pricing Errors:**
   ```bash
   ERROR - No hourly prices found in OMIE entity attributes
   ERROR - Failed to parse pricing data structure
   ```

3. **Startup Errors:**
   ```bash
   ERROR - Failed to start optimizer: missing required attributes
   ERROR - Required entities not configured
   ```

4. **Algorithm Errors:**
   ```bash
   ERROR - Genetic algorithm encountered numerical error
   ERROR - Optimization failed due to invalid data
   ```

### **Step 3: Compare Local vs Home Assistant Behavior**

**What to compare:**
- Error messages
- Error timing
- Data flow patterns
- Component interactions

**If local works but Home Assistant doesn't:**
- Check Home Assistant configuration
- Verify entity names match
- Check for missing dependencies

**If both fail the same way:**
- The issue is in the core logic
- Focus on fixing the algorithm
- Test with different data sets

## 🔧 **Phase 3: Fixing Issues**

### **Step 1: Identify the Root Cause**

**Use the logs to determine:**
- Which component is failing
- What data is missing
- When the failure occurs
- What triggers the error

### **Step 2: Fix the Issue**

**Common fixes:**

1. **Missing Entity Data:**
   ```python
   # Add default values
   if not pv_forecast:
       pv_forecast = [0.0] * 96
       self.hass.log("warning", "Using default PV forecast")
   ```

2. **Data Parsing Errors:**
   ```python
   # Add error handling
   try:
       data = parse_entity_data(entity_state)
   except Exception as e:
       self.hass.log("error", f"Failed to parse data: {e}")
       return default_data
   ```

3. **Missing Configuration:**
   ```python
   # Check required config
   if not self.config.get("required_setting"):
       self.hass.log("error", "Missing required configuration")
       return False
   ```

### **Step 3: Test the Fix**

1. **Make the change** in your code
2. **Restart Home Assistant** (required for custom integrations)
3. **Test the same scenario** that caused the error
4. **Check logs** to confirm the error is resolved

## 📊 **Debugging Checklist**

### **Before Starting:**
- [ ] Integration is installed
- [ ] Detailed logging is enabled
- [ ] You have access to Home Assistant logs
- [ ] You understand the expected behavior

### **During Debugging:**
- [ ] Monitor logs in real-time
- [ ] Test individual services
- [ ] Check entity states
- [ ] Note error patterns
- [ ] Document failure scenarios

### **After Fixing:**
- [ ] Test the fix in Home Assistant
- [ ] Verify error is resolved
- [ ] Test related functionality
- [ ] Update documentation
- [ ] Consider adding tests

## 🚨 **Emergency Debugging**

### **If Integration Won't Load:**

1. **Check configuration:**
   ```yaml
   # Verify your config_flow.py is correct
   # Check for syntax errors
   # Verify all required files exist
   ```

2. **Check Home Assistant logs:**
   ```bash
   # Look for import errors
   # Check for missing dependencies
   # Verify file permissions
   ```

3. **Restart Home Assistant:**
   ```bash
   # Sometimes a restart fixes loading issues
   # Check if the integration appears after restart
   ```

### **If Integration Loads But Doesn't Work:**

1. **Check entity creation:**
   - Are sensors being created?
   - Do they have the right names?
   - Are they updating?

2. **Check service registration:**
   - Are services available in Developer Tools?
   - Do they respond when called?
   - What errors appear in logs?

3. **Check data flow:**
   - Is PV forecast data being fetched?
   - Is pricing data being parsed?
   - Is the algorithm running?

## 💡 **Pro Tips**

1. **Start with the basics** - Don't assume complex issues
2. **Test incrementally** - Fix one issue at a time
3. **Use the logs** - They contain the answers
4. **Compare local vs Home Assistant** - Identify environment differences
5. **Document everything** - Keep track of what you've tried
6. **Ask for help** - Share logs and error messages

## 🎯 **Next Steps**

1. **Enable detailed logging** in Home Assistant
2. **Run the error reproduction script** locally
3. **Compare error patterns** between local and Home Assistant
4. **Fix issues** one by one
5. **Test fixes** in Home Assistant
6. **Document solutions** for future reference

## 🆘 **Getting Help**

When asking for help, include:
- **Home Assistant logs** (filtered by your integration)
- **Error messages** from the UI
- **Configuration details** (without sensitive info)
- **Steps to reproduce** the issue
- **What you've already tried**

This will help others provide targeted assistance quickly.
