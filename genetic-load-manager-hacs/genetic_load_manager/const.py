"""Constants for the Genetic Load Manager integration."""

DOMAIN = "genetic_load_manager"

# Configuration keys
CONF_PV_ENTITY_ID = "pv_entity_id"
CONF_FORECAST_ENTITY_ID = "forecast_entity_id"
CONF_BATTERY_SOC_ENTITY_ID = "battery_soc_entity_id"
CONF_PRICE_ENTITY_ID = "price_entity_id"
CONF_OPTIMIZATION_INTERVAL = "optimization_interval"
CONF_POPULATION_SIZE = "population_size"
CONF_GENERATIONS = "generations"
CONF_MUTATION_RATE = "mutation_rate"
CONF_CROSSOVER_RATE = "crossover_rate"

# Default values
DEFAULT_OPTIMIZATION_INTERVAL = 15
DEFAULT_POPULATION_SIZE = 50
DEFAULT_GENERATIONS = 100
DEFAULT_MUTATION_RATE = 0.1
DEFAULT_CROSSOVER_RATE = 0.8

# Entity attributes
ATTR_OPTIMIZATION_STATUS = "optimization_status"
ATTR_LAST_OPTIMIZATION = "last_optimization"
ATTR_NEXT_OPTIMIZATION = "next_optimization"
ATTR_OPTIMIZATION_COUNT = "optimization_count"
ATTR_BEST_FITNESS = "best_fitness"
ATTR_CURRENT_SCHEDULE = "current_schedule"

# Service names
SERVICE_OPTIMIZE_LOADS = "optimize_loads"
SERVICE_APPLY_SCHEDULE = "apply_schedule"
SERVICE_RESET_OPTIMIZATION = "reset_optimization"

# Event types
EVENT_OPTIMIZATION_STARTED = "genetic_load_manager_optimization_started"
EVENT_OPTIMIZATION_COMPLETED = "genetic_load_manager_optimization_completed"
EVENT_SCHEDULE_APPLIED = "genetic_load_manager_schedule_applied" 