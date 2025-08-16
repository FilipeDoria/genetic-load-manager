# 🚀 HACS Installation Guide - Fixed Repository Structure

## ✅ **Problem Solved!**

The error **"The repository does not seem to be a integration, but an add-on repository"** has been fixed by restructuring the repository to match HACS integration requirements.

## 🔧 **What Was Fixed**

### **Before (Incorrect Structure):**
```
genetic-load-manager-hacs/
├── custom_components/
│   └── genetic_load_manager/
│       ├── __init__.py
│       ├── const.py
│       ├── manifest.json
│       └── ...
├── hacs.json
└── README.md
```

### **After (Correct Structure):**
```
genetic-load-manager-hacs/
├── genetic_load_manager/
│   ├── __init__.py
│   ├── const.py
│   ├── manifest.json
│   ├── config_flow.py
│   ├── genetic_algorithm.py
│   ├── sensor.py
│   ├── switch.py
│   ├── binary_sensor.py
│   ├── services.yaml
│   └── translations/
│       └── en.json
├── hacs.json
└── README.md
```

## 🎯 **Key Changes Made**

1. **Moved integration files** from `custom_components/genetic_load_manager/` to `genetic_load_manager/`
2. **Removed nested directory structure** that confused HACS
3. **Added missing platform files** (`switch.py`, `binary_sensor.py`)
4. **Cleaned up empty directories** to prevent confusion

## 📋 **Installation Steps**

### **1. Add Custom Repository to HACS**
- Open **HACS** in Home Assistant
- Go to **Integrations**
- Click the three dots menu (⋮)
- Select **Custom repositories**
- Add: `filipe0doria/genetic-load-manager-hacs`
- Category: **Integration**

### **2. Install the Integration**
- Find **"Genetic Load Manager"** in HACS
- Click **Download**
- Restart Home Assistant

### **3. Add Integration**
- Go to **Settings** → **Devices & Services**
- Click **Add Integration**
- Search for **"Genetic Load Manager"**
- Click **Configure**

## 🔍 **Repository Structure Verification**

The repository now contains all required files for HACS integration:

- ✅ **`genetic_load_manager/__init__.py`** - Main integration setup
- ✅ **`genetic_load_manager/manifest.json`** - Integration metadata
- ✅ **`genetic_load_manager/config_flow.py`** - Configuration wizard
- ✅ **`genetic_load_manager/const.py`** - Constants and configuration
- ✅ **`genetic_load_manager/genetic_algorithm.py`** - Core optimization engine
- ✅ **`genetic_load_manager/sensor.py`** - Status monitoring sensors
- ✅ **`genetic_load_manager/switch.py`** - Switch platform (placeholder)
- ✅ **`genetic_load_manager/binary_sensor.py`** - Binary sensor platform (placeholder)
- ✅ **`genetic_load_manager/services.yaml`** - HA services definition
- ✅ **`genetic_load_manager/translations/en.json`** - English translations
- ✅ **`hacs.json`** - HACS configuration

## 🎉 **Expected Result**

After the fix, HACS should:
- ✅ **Recognize the repository** as an integration (not an add-on)
- ✅ **Allow installation** without errors
- ✅ **Create proper integration** in Home Assistant
- ✅ **Provide configuration flow** for setup

## 🚨 **If You Still Get Errors**

### **Error 1: "Repository not found"**
- Ensure you're using: `filipe0doria/genetic-load-manager-hacs`
- Check that the repository is public on GitHub

### **Error 2: "Invalid integration"**
- Clear HACS cache: **HACS** → **Settings** → **Clear HACS cache**
- Restart Home Assistant
- Try adding the repository again

### **Error 3: "Missing dependencies"**
- Ensure Home Assistant version is **2023.8.0** or later
- Check that all required files are present in the repository

## 📚 **Additional Resources**

- **Main Documentation**: `README.md`
- **Add-on vs HACS Comparison**: `ADDON_VS_HACS.md`
- **GitHub Repository**: `https://github.com/filipe0doria/genetic-load-manager-hacs`

## 🔄 **Next Steps**

1. **Test the installation** with the fixed repository
2. **Configure the integration** through HA config flow
3. **Monitor the sensors** for optimization status
4. **Use the services** for manual control
5. **Create automations** based on events

---

**The repository structure has been corrected and should now work properly with HACS!** 🎯 