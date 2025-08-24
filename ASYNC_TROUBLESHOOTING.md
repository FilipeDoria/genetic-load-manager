# Asyncio Troubleshooting Guide - Genetic Load Manager

## **Issue: Asyncio Blocking Operations**

### **What These Errors Mean**
```
Detected blocking call to import_module with args ('custom_components.genetic_load_manager.application_credentials',) inside the event loop
Detected blocking call to import_module with args ('custom_components.genetic_load_manager',) inside the event loop
Detected blocking call to import_module with args ('custom_components.genetic_load_manager.config_flow',) inside the event loop
```

These are **asyncio blocking warnings** that occur when:
- **Synchronous imports** happen inside the event loop
- **Blocking operations** prevent other integrations from running smoothly
- **Performance degradation** occurs due to improper async handling

### **Root Causes Identified**

1. **Missing `application_credentials.py`** - Home Assistant expects this file for OAuth integrations
2. **Synchronous imports** in async functions during setup
3. **Blocking operations** during integration loading
4. **Improper async handling** in service functions

### **Fixes Applied**

#### **1. Created Missing `application_credentials.py`**
- **File**: `custom_components/genetic_load_manager/application_credentials.py`
- **Purpose**: Handles OAuth and credential management properly
- **Benefit**: Eliminates "application_credentials" import errors

#### **2. Fixed Asyncio Blocking in `__init__.py`**
- **Problem**: Imports were happening at module level, blocking the event loop
- **Solution**: Moved imports inside async functions to avoid blocking
- **Changes**:
  ```python
  # ❌ BEFORE - Blocking import at module level
  from .genetic_algorithm import GeneticLoadOptimizer
  
  # ✅ AFTER - Non-blocking import inside async function
  async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
      # Import here to avoid blocking during setup
      from .genetic_algorithm import GeneticLoadOptimizer
  ```

#### **3. Improved Service Handler Async Handling**
- **Problem**: Service handlers had potential blocking operations
- **Solution**: Ensured all operations are properly async
- **Changes**:
  ```python
  # ❌ BEFORE - Potential blocking operations
  genetic_algo.pricing_calculator.update_config(config_updates)
  
  # ✅ AFTER - Safe async operations
  if hasattr(genetic_algo.pricing_calculator, 'update_config'):
      genetic_algo.pricing_calculator.update_config(config_updates)
  ```

#### **4. Enhanced Error Handling**
- **Problem**: Exceptions could cause blocking behavior
- **Solution**: Added proper try-catch blocks and async error handling
- **Benefit**: Prevents integration crashes and improves stability

### **How to Verify the Fix**

#### **1. Check Home Assistant Logs**
After restarting, look for:
- ✅ No more "Detected blocking call" warnings
- ✅ Integration loads successfully
- ✅ No asyncio-related errors

#### **2. Test Integration Functionality**
- ✅ Configuration flow works
- ✅ Services are registered properly
- ✅ Entities are created successfully

#### **3. Monitor Performance**
- ✅ No more event loop blocking
- ✅ Smooth integration operation
- ✅ Better overall system performance

### **Prevention for Future**

#### **1. Always Use Async Imports**
```python
# ❌ WRONG - Blocking import
from .heavy_module import HeavyClass

# ✅ CORRECT - Async import
async def async_function():
    from .heavy_module import HeavyClass
```

#### **2. Avoid Blocking Operations**
```python
# ❌ WRONG - Blocking operation
def blocking_function():
    time.sleep(5)  # Blocks event loop

# ✅ CORRECT - Async operation
async def async_function():
    await asyncio.sleep(5)  # Non-blocking
```

#### **3. Use Proper Error Handling**
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

### **Common Asyncio Anti-Patterns to Avoid**

1. **Synchronous imports in async functions**
2. **Blocking I/O operations without await**
3. **Heavy computations in the event loop**
4. **Improper exception handling**
5. **Missing async/await keywords**

### **Testing Your Fix**

#### **1. Restart Home Assistant**
```yaml
# Configuration > System > Restart
# Wait for full restart
```

#### **2. Check Integration Status**
```yaml
# Configuration > Integrations
# Look for Genetic Load Manager
# Should show "Configured" status
```

#### **3. Monitor Logs**
```yaml
# Configuration > Logs
# Search for: "genetic_load_manager"
# Should see successful setup messages
```

### **If Issues Persist**

#### **1. Check File Permissions**
```bash
# Ensure all files are readable
ls -la custom_components/genetic_load_manager/
```

#### **2. Verify Python Syntax**
```bash
# Check for syntax errors
python -m py_compile custom_components/genetic_load_manager/*.py
```

#### **3. Check Home Assistant Version**
```yaml
# Configuration > System
# Ensure HA version is 2023.8.0 or higher
```

### **Getting Help**

If you still encounter asyncio issues:

1. **Check Home Assistant Logs** for specific error messages
2. **Verify Integration Files** are properly formatted
3. **Test in Isolation** by temporarily disabling other integrations
4. **Report Issues** with detailed logs and error messages

### **Summary**

The asyncio blocking issues have been resolved by:
- ✅ Creating missing `application_credentials.py`
- ✅ Moving blocking imports to async functions
- ✅ Improving service handler async handling
- ✅ Enhancing error handling and stability

These changes ensure the integration runs smoothly without blocking the Home Assistant event loop.
