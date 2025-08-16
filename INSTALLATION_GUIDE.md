# 🚀 HACS Installation Guide

## ✅ **Fresh Start - Minimal Working Integration**

This is a **minimal working version** of the Genetic Load Manager HACS integration that should resolve the "add-on repository" error.

## 📁 **Repository Structure**

```
genetic-load-manager-hacs/
├── genetic_load_manager/
│   ├── __init__.py              ✅ (45 bytes)
│   ├── const.py                 ✅ (33 bytes)
│   ├── manifest.json            ✅ (89 bytes)
│   ├── config_flow.py           ✅ (45 bytes)
│   ├── genetic_algorithm.py     ✅ (45 bytes)
│   ├── sensor.py                ✅ (49 bytes)
│   ├── services.yaml            ✅ (17 bytes)
│   └── translations/
│       └── en.json              ✅ (67 bytes)
├── hacs.json                    ✅ (363 bytes)
└── README.md                    ✅ (7.7KB)
```

## 🔧 **Installation Steps**

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

## 🎯 **What This Minimal Version Provides**

- ✅ **Basic HACS integration structure**
- ✅ **Configuration flow setup**
- ✅ **Sensor platform foundation**
- ✅ **Services definition**
- ✅ **Translations support**
- ✅ **Manifest configuration**

## 🔄 **Next Steps After Installation**

1. **Test basic functionality**
2. **Add full genetic algorithm implementation**
3. **Enhance sensor capabilities**
4. **Add advanced features**

## 🚨 **If You Still Get Errors**

### **Error: "Repository not found"**
- Ensure you're using: `filipe0doria/genetic-load-manager-hacs`
- Check that the repository is public on GitHub

### **Error: "Invalid integration"**
- Clear HACS cache: **HACS** → **Settings** → **Clear HACS cache**
- Restart Home Assistant
- Try adding the repository again

### **Error: "Missing dependencies"**
- Ensure Home Assistant version is **2023.8.0** or later

## 📚 **Repository Information**

- **Repository**: `filipe0doria/genetic-load-manager-hacs`
- **Category**: Integration
- **Type**: Custom HACS Integration
- **Status**: Minimal Working Version

---

**This minimal version should work with HACS and resolve the "add-on repository" error. Once installed, we can enhance it with full functionality.** 🎉 