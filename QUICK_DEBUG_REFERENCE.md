# Quick Debug Reference Card - Genetic Load Manager

## 🚨 **Common Errors & Quick Fixes**

### **1. "No PV forecast data available"**
**Quick Fix:**
```python
# In genetic_algorithm.py, add fallback:
if not pv_forecast:
    pv_forecast = [0.0] * 96
    self.hass.log("warning", "Using default PV forecast")
```

**Debug Steps:**
1. Check Solcast entity in Developer Tools > States
2. Verify `DetailedForecast` attribute exists
3. Check timezone handling in parsing

### **2. "No hourly prices found in OMIE entity"**
**Quick Fix:**
```python
# In pricing_calculator.py, add fallback:
if not hourly_prices:
    hourly_prices = [100.0] * 24  # Default price
    self.hass.log("warning", "Using default pricing")
```

**Debug Steps:**
1. Check OMIE entity in Developer Tools > States
2. Verify `Today hours` attribute structure
3. Check date format in hour_key generation

### **3. "Failed to start optimizer"**
**Quick Fix:**
```python
# In genetic_algorithm.py, check required attributes:
required_attrs = ['device_priorities', 'dynamic_pricing_entity']
for attr in required_attrs:
    if not hasattr(self, attr):
        setattr(self, attr, None)
```

**Debug Steps:**
1. Check integration configuration
2. Verify all required entities are configured
3. Check Home Assistant logs for specific error

### **4. "State attributes exceed maximum size"**
**Quick Fix:**
```python
# In sensor.py, compress data:
if len(str(attributes)) > 16000:
    attributes = self._get_compressed_data()
```

**Debug Steps:**
1. Check entity attribute sizes
2. Reduce data granularity
3. Use summary data instead of full details

## 🔍 **Quick Debug Commands**

### **Enable Debug Logging:**
```yaml
# In configuration.yaml
logger:
  custom_components.genetic_load_manager: debug
```

### **Check Entity States:**
```bash
# In Developer Tools > States, search for:
sensor.genetic_load_manager_dashboard
sensor.genetic_load_manager_indexed_pricing
switch.device_0_schedule
switch.device_1_schedule
```

### **Test Services:**
```yaml
# In Developer Tools > Services
service: genetic_load_manager.run_optimization
data:
  population_size: 50
  generations: 100
```

### **Monitor Logs:**
```bash
# In Developer Tools > Logs, filter by:
custom_components.genetic_load_manager
```

## 📊 **Debug Checklist**

### **Integration Loading:**
- [ ] Integration appears in Devices & Services
- [ ] Status shows "Running"
- [ ] No import errors in logs
- [ ] All required files exist

### **Entity Creation:**
- [ ] Sensors are created with correct names
- [ ] Switches are available
- [ ] Entities have expected attributes
- [ ] Data is updating regularly

### **Service Functionality:**
- [ ] Services appear in Developer Tools
- [ ] Services execute without errors
- [ ] Logs show successful execution
- [ ] Expected results are produced

### **Data Flow:**
- [ ] PV forecast data is fetched
- [ ] Pricing data is parsed
- [ ] Algorithm runs successfully
- [ ] Results are stored in entities

## 🧪 **Local Testing Commands**

### **Run Error Reproduction:**
```bash
python local_error_reproduction.py
```

### **Test Specific Error:**
```python
# In the script, set specific error mode:
optimizer.set_error_mode("no_pv_data")
optimizer.set_error_mode("pricing_parsing_error")
optimizer.set_error_mode("startup_failure")
```

### **Compare with Home Assistant:**
1. Run local test
2. Check Home Assistant logs
3. Compare error messages
4. Identify differences

## 🚀 **Quick Fix Workflow**

### **1. Identify the Error**
- Check Home Assistant logs
- Note exact error message
- Identify which component failed

### **2. Reproduce Locally**
- Run error reproduction script
- Set appropriate error mode
- Compare error patterns

### **3. Apply Fix**
- Modify the relevant file
- Add error handling
- Add fallback values

### **4. Test Fix**
- Restart Home Assistant
- Test the same scenario
- Verify error is resolved

### **5. Document Solution**
- Note what was fixed
- Update documentation
- Consider adding tests

## 💡 **Pro Debugging Tips**

1. **Start with logs** - They contain the answers
2. **Test incrementally** - Fix one issue at a time
3. **Use local testing** - Faster than Home Assistant restarts
4. **Check entity states** - Verify data is flowing
5. **Test services manually** - Isolate issues
6. **Compare local vs HA** - Identify environment differences

## 🆘 **Emergency Commands**

### **If Integration Won't Load:**
```bash
# Check file permissions
ls -la custom_components/genetic_load_manager/

# Check Python syntax
python -m py_compile custom_components/genetic_load_manager/*.py

# Check for missing imports
grep -r "import" custom_components/genetic_load_manager/
```

### **If Entities Not Updating:**
```bash
# Check integration status
# Go to Settings > Devices & Services

# Check entity availability
# Go to Developer Tools > States

# Check service registration
# Go to Developer Tools > Services
```

### **If Algorithm Fails:**
```bash
# Check data sources
# Verify PV forecast entity
# Verify pricing entity
# Check algorithm parameters
```

## 📱 **Mobile Debugging**

### **Use Home Assistant App:**
- Monitor logs on mobile
- Test services remotely
- Check entity states
- Receive notifications

### **Remote Access:**
- Enable remote access in Home Assistant
- Use external URL for debugging
- Access logs from anywhere
- Test integration remotely

## 🎯 **Success Indicators**

Your integration is working correctly when:
- ✅ Integration loads without errors
- ✅ All entities are created and updating
- ✅ Services execute successfully
- ✅ Algorithm runs and produces results
- ✅ No error messages in logs
- ✅ Dashboard displays correctly
- ✅ Mobile app works properly

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
