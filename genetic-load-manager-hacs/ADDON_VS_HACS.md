# Add-on Store vs HACS: Installation Methods Comparison

## 🔄 **Overview**

Your Genetic Load Manager can be installed in **two different ways** depending on your needs and preferences:

1. **Add-on Store** (Original method)
2. **HACS Integration** (New method)

## 📊 **Feature Comparison**

| Feature | Add-on Store | HACS Integration |
|---------|--------------|------------------|
| **Installation** | Via Add-on Store | Via HACS |
| **Architecture** | Docker container | Native Python integration |
| **Web Interface** | Separate web UI | Integrated into HA |
| **Resource Usage** | Higher (separate container) | Lower (shared with HA) |
| **Updates** | Manual/automatic | Via HACS |
| **Configuration** | Web interface | HA config flow |
| **Monitoring** | Separate logs | HA logs |
| **Integration** | Limited | Full HA integration |

## 🏠 **Add-on Store Method**

### **What It Is**
- Runs as a **separate Docker container**
- Has its **own web interface**
- **Independent service** from Home Assistant

### **Pros**
- ✅ **Isolated environment** - won't affect HA if it crashes
- ✅ **Full web interface** - dedicated UI for configuration
- ✅ **Independent scaling** - can be scaled separately
- ✅ **Easy debugging** - separate logs and processes
- ✅ **No HA version dependency** - works with any HA version

### **Cons**
- ❌ **Higher resource usage** - separate container
- ❌ **Separate management** - need to manage add-on separately
- ❌ **Limited HA integration** - can't use HA services easily
- ❌ **Network complexity** - needs port management

### **Best For**
- Users who want a **dedicated web interface**
- **Production environments** where isolation is important
- Users who prefer **traditional add-on management**
- **Research purposes** where you need full control

## 🌟 **HACS Integration Method**

### **What It Is**
- **Native Python integration** within Home Assistant
- **Integrated configuration** through HA's config flow
- **Native HA entities** and services

### **Pros**
- ✅ **Lower resource usage** - runs within HA
- ✅ **Full HA integration** - uses HA services and entities
- ✅ **Native configuration** - HA config flow
- ✅ **Automatic updates** - via HACS
- ✅ **Better monitoring** - integrated with HA logs
- ✅ **Easier automation** - native HA events and services

### **Cons**
- ❌ **Less isolation** - can affect HA if it crashes
- ❌ **No separate web UI** - configuration through HA
- ❌ **HA version dependency** - requires specific HA version
- ❌ **Limited debugging** - integrated with HA logs

### **Best For**
- Users who want **tight HA integration**
- **Home automation enthusiasts** who use HA extensively
- Users who prefer **native HA configuration**
- **Production environments** where HA integration is key

## 🚀 **Installation Instructions**

### **Add-on Store Installation**
1. Add repository: `https://github.com/filipe0doria/genetic-load-manager`
2. Install "GA Load Manager HA Add-on"
3. Configure via web interface
4. Access via HA sidebar or direct URL

### **HACS Installation**
1. Add custom repository to HACS: `filipe0doria/genetic-load-manager-hacs`
2. Install "Genetic Load Manager" integration
3. Configure via HA config flow
4. Access via HA devices and services

## 🔧 **Configuration Differences**

### **Add-on Store Configuration**
```yaml
# config.yaml
pv_entity_id: "sensor.pv_power"
forecast_entity_id: "sensor.pv_forecast"
battery_soc_entity_id: "sensor.battery_soc"
price_entity_id: "sensor.electricity_price"
optimization_interval: 15
genetic_algorithm:
  population_size: 50
  generations: 100
  mutation_rate: 0.1
  crossover_rate: 0.8
```

### **HACS Configuration**
```yaml
# configuration.yaml
genetic_load_manager:
  pv_entity_id: "sensor.pv_power"
  forecast_entity_id: "sensor.pv_forecast"
  battery_soc_entity_id: "sensor.battery_soc"
  price_entity_id: "sensor.electricity_price"
  optimization_interval: 15
  population_size: 50
  generations: 100
  mutation_rate: 0.1
  crossover_rate: 0.8
```

## 📱 **User Interface Differences**

### **Add-on Store UI**
- **Dedicated web interface** at `/addons/genetic_load_manager/`
- **Full dashboard** with real-time status
- **Configuration panels** for all settings
- **Load management interface**
- **Log viewing and monitoring**

### **HACS Integration UI**
- **HA config flow** for setup
- **HA entities** for monitoring
- **HA services** for control
- **HA automations** for integration
- **HA dashboards** for visualization

## 🔄 **Migration Between Methods**

### **From Add-on to HACS**
1. **Export configuration** from add-on
2. **Install HACS integration**
3. **Import configuration** to HACS
4. **Test functionality**
5. **Remove add-on** when satisfied

### **From HACS to Add-on**
1. **Export configuration** from HACS
2. **Install add-on**
3. **Import configuration** to add-on
4. **Test functionality**
5. **Remove HACS integration** when satisfied

## 🎯 **Recommendation**

### **Choose Add-on Store if:**
- You want a **dedicated web interface**
- You prefer **isolated services**
- You're doing **research or development**
- You want **full control** over the environment

### **Choose HACS if:**
- You want **tight HA integration**
- You prefer **native HA configuration**
- You use **HA extensively** for automation
- You want **lower resource usage**

## 📚 **Documentation**

- **Add-on Store**: See main `README.md`
- **HACS Integration**: See `genetic-load-manager-hacs/README.md`
- **Both methods** provide the same core functionality
- **Choose based on your preferences and needs**

---

**Both installation methods provide the same genetic algorithm load optimization functionality. The choice is primarily about your preferred management style and integration level with Home Assistant.** 