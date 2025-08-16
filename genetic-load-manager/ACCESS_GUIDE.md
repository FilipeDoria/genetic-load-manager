# Quick Access Guide

## How to Access the GA Load Manager Web Interface

### 🏠 **Through Home Assistant (Recommended)**

**URL**: `http://your-ha-ip:8123/addons/genetic_load_manager/`

**Steps**:
1. Open Home Assistant in your browser
2. Go to **Settings** → **Add-ons**
3. Find "GA Load Manager HA Add-on"
4. Click **Open Web UI**

**Benefits**:
- ✅ Integrated with Home Assistant
- ✅ Uses HA authentication and security
- ✅ Appears in HA sidebar
- ✅ Secure access through HA's ingress system
- ✅ No additional ports to open

---

### 🌐 **Direct External Access**

**URL**: `http://your-ha-ip:8123/`

**Prerequisites**:
- Add-on must be running
- `enable_external_access: true` in add-on options
- Port 8123 must be accessible

**Benefits**:
- ✅ Direct access from any device
- ✅ Can bookmark the URL
- ✅ Works independently of HA interface
- ✅ Useful for mobile apps or external monitoring
- ✅ Faster access (no HA interface overhead)

---

### ⚙️ **Configuration Options**

In the add-on configuration, you can control access:

```yaml
enable_external_access: true    # Allow direct access
external_port: 8123            # Port for direct access
```

**Default Settings**:
- External access: **Enabled**
- Port: **8123**
- Both access methods work simultaneously

---

### 🔧 **Troubleshooting Access Issues**

#### Can't access through Home Assistant?
1. Ensure add-on is **running**
2. Check add-on **logs** for errors
3. Try **restarting** the add-on
4. Verify **ingress** is enabled in config

#### Can't access directly?
1. Ensure add-on is **running**
2. Check `enable_external_access: true`
3. Verify **port 8123** is not blocked
4. Check **firewall** settings
5. Try accessing through HA first

#### Port conflicts?
1. Change `external_port` in add-on options
2. Ensure no other service uses the same port
3. Restart the add-on after changing port

---

### 📱 **Mobile Access**

#### Through Home Assistant App
1. Open HA app
2. Go to **Settings** → **Add-ons**
3. Tap "GA Load Manager"
4. Tap **Open Web UI**

#### Direct Mobile Access
1. Ensure external access is enabled
2. Access: `http://your-ha-ip:8123/`
3. Bookmark for quick access
4. Works on any mobile browser

---

### 🔒 **Security Considerations**

#### Home Assistant Access
- ✅ Uses HA's built-in security
- ✅ Requires HA authentication
- ✅ Secure through HA's ingress system

#### Direct Access
- ⚠️ Accessible from any device on your network
- ⚠️ No additional authentication
- ✅ Useful for trusted network environments
- ✅ Can be disabled by setting `enable_external_access: false`

---

### 🚀 **Quick Start**

1. **Install** the add-on
2. **Start** the add-on
3. **Configure** entities and parameters
4. **Access** through Home Assistant (recommended)
5. **Enable** direct access if needed
6. **Bookmark** the URL for convenience

---

**Note**: Both access methods work simultaneously, so you can use whichever is most convenient for your use case! 