"""Constants for the Genetic Load Manager integration."""

DOMAIN = "genetic_load_manager"

# Configuration keys
CONF_PV_ENTITY_ID = "pv_entity_id"
CONF_FORECAST_ENTITY_ID = "forecast_entity_id"
CONF_BATTERY_SOC_ENTITY_ID = "battery_soc_entity_id"
CONF_PRICE_ENTITY_ID = "price_entity_id"

# New configuration keys for Solcast integration
CONF_PV_FORECAST_ENTITY = "pv_forecast_entity"
CONF_LOAD_FORECAST_ENTITY = "load_forecast_entity"
CONF_DYNAMIC_PRICING_ENTITY = "dynamic_pricing_entity"
CONF_NUM_DEVICES = "num_devices"
CONF_BATTERY_CAPACITY = "battery_capacity"
CONF_MAX_CHARGE_RATE = "max_charge_rate"
CONF_MAX_DISCHARGE_RATE = "max_discharge_rate"
CONF_BINARY_CONTROL = "binary_control"

# Indexed pricing configuration keys
CONF_USE_INDEXED_PRICING = "use_indexed_pricing"
CONF_MARKET_PRICE_ENTITY = "market_price_entity"
CONF_MFRR = "mfrr"
CONF_Q = "q"
CONF_FP = "fp"
CONF_TAE = "tae"
CONF_VAT = "vat"
CONF_PEAK_MULTIPLIER = "peak_multiplier"
CONF_OFF_PEAK_MULTIPLIER = "off_peak_multiplier" 