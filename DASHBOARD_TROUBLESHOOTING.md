# Dashboard Troubleshooting Guide

## 🚨 Common Dashboard Issues & Solutions

### **❌ Problem: Dashboard Won't Load**
**Symptoms:**
- Dashboard shows "Error loading dashboard"
- Blank white screen
- "Invalid YAML" errors

**Solutions:**
1. **Use the Basic Dashboard**: Start with `basic_dashboard.yaml` - it uses only standard components
2. **Check YAML Syntax**: Validate your YAML in Home Assistant's YAML editor
3. **Clear Browser Cache**: Hard refresh (Ctrl+F5) or clear browser cache
4. **Check Entity Names**: Ensure all entity names match exactly

### **❌ Problem: Custom Cards Not Working**
**Symptoms:**
- "Custom element doesn't exist" errors
- Missing card types
- Dashboard partially loads

**Solutions:**
1. **Avoid Custom Cards**: Use only standard Home Assistant cards
2. **Install HACS First**: If you want custom cards, install HACS first
3. **Use Basic Components**: Stick to `entities`, `glance`, `call-service`

### **❌ Problem: Entities Not Showing**
**Symptoms:**
- Empty dashboard sections
- "Entity not found" errors
- Missing data

**Solutions:**
1. **Check Entity Names**: Verify entity IDs in Developer Tools > States
2. **Wait for Integration**: Some entities take time to appear after setup
3. **Check Integration Status**: Ensure the integration is running without errors

## 🔧 Dashboard Setup Steps

### **Step 1: Start with Basic Dashboard**
```yaml
# Copy basic_dashboard.yaml to your Home Assistant
# This uses only standard components and will definitely work
```

### **Step 2: Verify Entities Exist**
1. Go to **Developer Tools > States**
2. Search for your integration entities:
   - `sensor.genetic_load_manager_dashboard`
   - `sensor.genetic_load_manager_indexed_pricing`
   - `switch.device_0_schedule`
   - `switch.device_1_schedule`

### **Step 3: Test Individual Cards**
1. Create a simple test dashboard with just one card
2. Add cards one by one to identify problematic ones
3. Use the YAML editor to validate syntax

### **Step 4: Check Integration Status**
1. Go to **Settings > Devices & Services**
2. Find your integration and check its status
3. Look for any error messages or warnings

## 📱 Dashboard Types Available

### **1. Basic Dashboard** (`basic_dashboard.yaml`)
- ✅ **Guaranteed to work**
- ✅ Uses only standard Home Assistant components
- ✅ Simple, clean interface
- ✅ No custom dependencies

### **2. Modern Dashboard** (`modern_dashboard.yaml`)
- ✅ Uses modern Home Assistant syntax
- ✅ Responsive design
- ✅ Standard components only
- ⚠️ May need entity adjustments

### **3. Advanced Dashboard** (`advanced_dashboard.yaml`)
- ❌ **Requires custom cards** (button-card, apexcharts-card)
- ❌ **May not work** without HACS installation
- ❌ Complex configuration

## 🎯 Recommended Approach

### **For Immediate Use:**
1. **Start with `basic_dashboard.yaml`**
2. **Verify it works** in Home Assistant
3. **Customize gradually** by adding more cards

### **For Advanced Users:**
1. **Install HACS** first
2. **Install custom cards** (button-card, mini-graph-card)
3. **Use `modern_dashboard.yaml`** as a base
4. **Add custom features** incrementally

## 🔍 Troubleshooting Commands

### **Check Integration Status:**
```bash
# In Home Assistant logs, look for:
# - "Error occurred loading flow for integration genetic_load_manager"
# - "Failed to start optimizer"
# - "No PV forecast data available"
```

### **Verify Entity Data:**
```bash
# In Developer Tools > States, check:
# - Entity state values
# - Entity attributes
# - Entity availability
```

### **Test Services:**
```bash
# In Developer Tools > Services, test:
# - genetic_load_manager.run_optimization
# - genetic_load_manager.stop_optimization
```

## 📋 Dashboard Checklist

### **Before Creating Dashboard:**
- [ ] Integration is installed and configured
- [ ] All required entities exist
- [ ] Integration is running without errors
- [ ] You have basic Home Assistant knowledge

### **Dashboard Creation:**
- [ ] Start with basic dashboard
- [ ] Test each section individually
- [ ] Verify entity names match exactly
- [ ] Use YAML editor for syntax validation

### **After Creation:**
- [ ] Dashboard loads without errors
- [ ] All entities display correctly
- [ ] Controls work as expected
- [ ] Mobile view is responsive

## 🆘 Getting Help

### **If Basic Dashboard Doesn't Work:**
1. **Check Home Assistant logs** for integration errors
2. **Verify entity names** in Developer Tools
3. **Test integration services** manually
4. **Restart Home Assistant** if needed

### **If You Want Advanced Features:**
1. **Install HACS** first
2. **Install required custom cards**
3. **Use modern dashboard** as template
4. **Customize incrementally**

### **Common Error Messages:**
- **"Entity not found"** → Check entity name spelling
- **"Invalid YAML"** → Use YAML editor to validate syntax
- **"Custom element doesn't exist"** → Install required custom cards
- **"Dashboard not found"** → Check dashboard path and name

## 💡 Pro Tips

1. **Start Simple**: Always begin with basic components
2. **Test Incrementally**: Add features one at a time
3. **Use Developer Tools**: Verify entities and test services
4. **Check Logs**: Home Assistant logs contain valuable error information
5. **Backup Configs**: Save working dashboard configurations

## 🎉 Success Indicators

Your dashboard is working correctly when:
- ✅ Dashboard loads without errors
- ✅ All entities display current values
- ✅ Controls respond to user input
- ✅ Mobile view is responsive
- ✅ No error messages in logs
- ✅ Integration status shows "Running"
