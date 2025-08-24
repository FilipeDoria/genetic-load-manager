"""Constants for the EMS Testing integration."""

DOMAIN = "ems_testing"

# Configuration keys
CONF_ENABLE_CONTROL = "enable_control"
CONF_OPTIMIZATION_INTERVAL = "optimization_interval"
CONF_MONITORED_DEVICES = "monitored_devices"

# Default values
DEFAULT_OPTIMIZATION_INTERVAL = 900  # 15 minutes
DEFAULT_ENABLE_CONTROL = False

# Entity names
SENSOR_OPTIMIZATION_STATUS = "ems_optimization_status"
SENSOR_NEXT_ACTION = "ems_next_action"
SENSOR_ESTIMATED_SAVINGS = "ems_estimated_savings"
SENSOR_BATTERY_SCHEDULE = "ems_battery_schedule"
SENSOR_DEVICE_SCHEDULE = "ems_device_schedule"
