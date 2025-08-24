"""Constants for the Genetic Load Manager integration."""

# Domain
DOMAIN = "genetic_load_manager"

# Configuration keys
CONF_POPULATION_SIZE = "population_size"
CONF_GENERATIONS = "generations"
CONF_MUTATION_RATE = "mutation_rate"
CONF_CROSSOVER_RATE = "crossover_rate"
CONF_NUM_DEVICES = "num_devices"
CONF_BATTERY_CAPACITY = "battery_capacity"
CONF_MAX_CHARGE_RATE = "max_charge_rate"
CONF_MAX_DISCHARGE_RATE = "max_discharge_rate"
CONF_BINARY_CONTROL = "binary_control"
CONF_USE_INDEXED_PRICING = "use_indexed_pricing"
CONF_OPTIMIZATION_MODE = "optimization_mode"
CONF_UPDATE_INTERVAL = "update_interval"

# Entity mapping keys
CONF_PV_FORECAST_ENTITY = "pv_forecast_entity"
CONF_LOAD_FORECAST_ENTITY = "load_forecast_entity"
CONF_BATTERY_SOC_ENTITY = "battery_soc_entity"
CONF_GRID_IMPORT_ENTITY = "grid_import_entity"
CONF_GRID_EXPORT_ENTITY = "grid_export_entity"
CONF_SOLAR_POWER_ENTITY = "solar_power_entity"
CONF_ELECTRICITY_PRICE_ENTITY = "electricity_price_entity"
CONF_WEATHER_ENTITY = "weather_entity"
CONF_DEVICE_ENTITIES = "device_entities"

# Default values
DEFAULT_POPULATION_SIZE = 100
DEFAULT_GENERATIONS = 200
DEFAULT_MUTATION_RATE = 0.05
DEFAULT_CROSSOVER_RATE = 0.8
DEFAULT_NUM_DEVICES = 2
DEFAULT_BATTERY_CAPACITY = 10.0
DEFAULT_MAX_CHARGE_RATE = 2.0
DEFAULT_MAX_DISCHARGE_RATE = 2.0
DEFAULT_BINARY_CONTROL = False
DEFAULT_USE_INDEXED_PRICING = True
DEFAULT_OPTIMIZATION_MODE = "cost_savings"
DEFAULT_UPDATE_INTERVAL = 15

# Default entity IDs to avoid warnings
DEFAULT_ENTITIES = {
    "pv_forecast_today": "sensor.solcast_pv_forecast_today",
    "pv_forecast_tomorrow": "sensor.solcast_pv_forecast_tomorrow",
    "load_forecast": "sensor.load_forecast",
    "load_sensor": "sensor.power_consumption",
    "battery_soc": "sensor.battery_soc",
    "market_price": "sensor.omie_electricity_price",
    "grid_export_limit": "sensor.grid_export_limit",
    "demand_response": "binary_sensor.demand_response_active",
    "carbon_intensity": "sensor.carbon_intensity",
    "weather": "weather.home",
    "ev_charger": "switch.ev_charger",
    "smart_thermostat": "climate.home_thermostat",
    "smart_plug": "switch.smart_plug",
    "lighting": "light.living_room",
    "media_player": "media_player.tv"
}

# Entity validation patterns
ENTITY_PATTERNS = {
    "pv_forecast": ["sensor.solcast_", "sensor.pv_forecast_", "sensor.solar_forecast_"],
    "load_forecast": ["sensor.load_forecast", "sensor.power_forecast", "sensor.energy_forecast"],
    "battery": ["sensor.battery_", "sensor.energy_storage_", "sensor.powerwall_"],
    "market_price": ["sensor.omie_", "sensor.electricity_price_", "sensor.energy_price_"],
    "weather": ["weather.", "sensor.temperature_", "sensor.humidity_"]
}

# Optimization modes
OPTIMIZATION_MODES = [
    "cost_savings",
    "comfort",
    "battery_health",
    "grid_stability",
    "carbon_reduction"
]

# Device types
DEVICE_TYPES = [
    "climate",
    "switch",
    "light",
    "media_player",
    "fan",
    "humidifier",
    "dehumidifier"
]

# Entity domains
SUPPORTED_DOMAINS = [
    "sensor",
    "binary_sensor",
    "switch",
    "climate",
    "light",
    "media_player",
    "fan",
    "humidifier",
    "dehumidifier",
    "weather"
]

# Device classes for entity selection
POWER_DEVICE_CLASSES = ["power", "energy", "battery"]
MONETARY_DEVICE_CLASSES = ["monetary"]
WEATHER_DEVICE_CLASSES = ["temperature", "humidity", "pressure"]

# Time intervals (in minutes)
UPDATE_INTERVALS = [
    (5, "5 minutes"),
    (15, "15 minutes"),
    (30, "30 minutes"),
    (60, "1 hour"),
    (120, "2 hours"),
    (240, "4 hours"),
    (480, "8 hours"),
    (1440, "24 hours")
]

# Genetic algorithm constraints
MIN_POPULATION_SIZE = 20
MAX_POPULATION_SIZE = 500
MIN_GENERATIONS = 50
MAX_GENERATIONS = 1000
MIN_MUTATION_RATE = 0.01
MAX_MUTATION_RATE = 0.5
MIN_CROSSOVER_RATE = 0.1
MAX_CROSSOVER_RATE = 1.0

# Battery constraints
MIN_BATTERY_CAPACITY = 1.0
MAX_BATTERY_CAPACITY = 100.0
MIN_CHARGE_RATE = 0.5
MAX_CHARGE_RATE = 50.0
MIN_DISCHARGE_RATE = 0.5
MAX_DISCHARGE_RATE = 50.0

# Device constraints
MIN_NUM_DEVICES = 1
MAX_NUM_DEVICES = 20

# Update interval constraints
MIN_UPDATE_INTERVAL = 5
MAX_UPDATE_INTERVAL = 1440

# Service names
SERVICE_START_OPTIMIZATION = "start_optimization"
SERVICE_STOP_OPTIMIZATION = "stop_optimization"
SERVICE_UPDATE_PARAMETERS = "update_parameters"
SERVICE_RUN_SINGLE_OPTIMIZATION = "run_single_optimization"

# Attribute names
ATTR_OPTIMIZATION_STATUS = "optimization_status"
ATTR_CURRENT_FITNESS = "current_fitness"
ATTR_BEST_FITNESS = "best_fitness"
ATTR_GENERATION = "generation"
ATTR_DEVICES_OPTIMIZED = "devices_optimized"
ATTR_ENERGY_SAVINGS = "energy_savings"
ATTR_COST_SAVINGS = "cost_savings"
ATTR_CARBON_REDUCTION = "carbon_reduction"
ATTR_LAST_OPTIMIZATION = "last_optimization"
ATTR_NEXT_OPTIMIZATION = "next_optimization"

# State values
STATE_IDLE = "idle"
STATE_OPTIMIZING = "optimizing"
STATE_PAUSED = "paused"
STATE_ERROR = "error"

# Error messages
ERROR_INVALID_CONFIG = "Invalid configuration"
ERROR_ENTITY_NOT_FOUND = "Entity not found"
ERROR_OPTIMIZATION_FAILED = "Optimization failed"
ERROR_INSUFFICIENT_DATA = "Insufficient data for optimization"
ERROR_BATTERY_CONSTRAINTS = "Battery constraints violated"
ERROR_DEVICE_CONSTRAINTS = "Device constraints violated"

# Logging
LOGGER_NAME = "custom_components.genetic_load_manager"
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"

# File paths
CONFIG_DIR = "genetic_load_manager"
DATA_DIR = "genetic_load_manager"
LOG_DIR = "logs"
CACHE_DIR = "cache"

# File names
CONFIG_FILE = "config.yaml"
LOG_FILE = "genetic_load_manager.log"
CACHE_FILE = "optimization_cache.pkl"
HISTORY_FILE = "optimization_history.json"

# Cache settings
CACHE_EXPIRY_HOURS = 24
MAX_CACHE_SIZE = 1000

# Performance settings
MAX_OPTIMIZATION_TIME = 300  # 5 minutes
MAX_MEMORY_USAGE = 512  # MB
MAX_CPU_USAGE = 80  # percent

# Integration info
INTEGRATION_NAME = "Genetic Load Manager"
INTEGRATION_VERSION = "1.0.0"
INTEGRATION_DESCRIPTION = "Advanced load management using genetic algorithms"
INTEGRATION_AUTHOR = "Your Name"
INTEGRATION_DOMAIN = "genetic_load_manager"
INTEGRATION_ISSUE_TRACKER = "https://github.com/yourusername/genetic-load-manager/issues"
INTEGRATION_DOCUMENTATION = "https://github.com/yourusername/genetic-load-manager"

# HACS specific
HACS_MINIMUM_HA_VERSION = "2023.8.0"
HACS_CATEGORIES = ["energy", "optimization", "automation"]
HACS_DEFAULT_REPOSITORY = "yourusername/genetic-load-manager"
HACS_DEFAULT_BRANCH = "main" 