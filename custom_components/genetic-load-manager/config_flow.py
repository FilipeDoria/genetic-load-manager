"""Config flow for Genetic Load Manager integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.const import (
    CONF_NAME,
    ATTR_DEVICE_CLASS,
    ATTR_UNIT_OF_MEASUREMENT,
    UnitOfEnergy,
    PERCENTAGE,
    CURRENCY_EURO,
    CURRENCY_DOLLAR
)

from .const import (
    DOMAIN,
    CONF_PV_ENTITY_ID,
    CONF_FORECAST_ENTITY_ID,
    CONF_BATTERY_SOC_ENTITY_ID,
    CONF_PRICE_ENTITY_ID,
)

_LOGGER = logging.getLogger(__name__)

# Configuration presets for different optimization strategies
PRESETS = {
    "balanced": {
        "population_size": 100,
        "generations": 200,
        "mutation_rate": 0.05,
        "crossover_rate": 0.8,
        "battery_capacity": 10.0,
        "max_charge_rate": 2.0,
        "max_discharge_rate": 2.0,
        "description": "Balanced optimization between cost, solar usage, and battery life"
    },
    "cost-focused": {
        "population_size": 150,
        "generations": 300,
        "mutation_rate": 0.03,
        "crossover_rate": 0.9,
        "battery_capacity": 15.0,
        "max_charge_rate": 3.0,
        "max_discharge_rate": 3.0,
        "description": "Prioritizes cost savings with aggressive battery usage"
    },
    "battery-preserving": {
        "population_size": 80,
        "generations": 150,
        "mutation_rate": 0.07,
        "crossover_rate": 0.7,
        "battery_capacity": 8.0,
        "max_charge_rate": 1.5,
        "max_discharge_rate": 1.5,
        "description": "Conservative approach to maximize battery lifespan"
    },
    "solar-optimized": {
        "population_size": 120,
        "generations": 250,
        "mutation_rate": 0.04,
        "crossover_rate": 0.85,
        "battery_capacity": 12.0,
        "max_charge_rate": 2.5,
        "max_discharge_rate": 2.5,
        "description": "Maximizes solar energy utilization"
    }
}

# Helper function to create entity selector with multiple filter options
def create_entity_selector(domain="sensor", device_class=None, integration=None, unit=None, multiple=False):
    """Create an entity selector with comprehensive filtering."""
    config = selector.EntitySelectorConfig(domain=domain, multiple=multiple)
    
    if device_class:
        config.device_class = device_class
    
    if integration:
        config.integration = integration
    
    if unit:
        config.unit_of_measurement = unit
    
    return selector.EntitySelector(config)

CONFIG_SCHEMA = vol.Schema({
    vol.Required("preset", description="Select optimization strategy"): vol.In(list(PRESETS.keys())),
    
    # Solar PV Forecast Entities
    vol.Required("pv_forecast_entity", description="Select Solcast PV Forecast for Today"): create_entity_selector(
        domain="sensor",
        device_class="energy",
        integration="solcast_pv_forecast"
    ),
    vol.Required("pv_forecast_tomorrow_entity", description="Select Solcast PV Forecast for Tomorrow"): create_entity_selector(
        domain="sensor",
        device_class="energy",
        integration="solcast_pv_forecast"
    ),
    
    # Load Forecasting
    vol.Required("load_forecast_entity", default="sensor.load_forecast", description="Load Forecast Entity (will be created)"): str,
    vol.Required("load_sensor_entity", description="Select Energy Consumption Sensor for Historical Data"): create_entity_selector(
        domain="sensor",
        device_class="energy",
        unit=UnitOfEnergy.KILO_WATT_HOUR
    ),
    
    # Battery Management
    vol.Required("battery_soc_entity", description="Select Battery State of Charge Sensor"): create_entity_selector(
        domain="sensor",
        device_class="battery",
        unit=PERCENTAGE
    ),
    
    # Pricing Information
    vol.Optional("use_indexed_pricing", default=True, description="Use indexed tariff pricing calculator"): bool,
    vol.Optional("dynamic_pricing_entity", description="Select Electricity Price Sensor (fallback if indexed pricing fails)"): create_entity_selector(
        domain="sensor",
        device_class="monetary"
    ),
    vol.Optional("market_price_entity", description="Select Market Price Entity (e.g., OMIE spot price)"): create_entity_selector(
        domain="sensor",
        device_class="monetary"
    ),
    
    # Device Configuration
    vol.Optional("num_devices", default=2, description="Number of manageable devices (1-10)"): vol.All(
        vol.Coerce(int),
        vol.Range(min=1, max=10)
    ),
    
    # Genetic Algorithm Parameters
    vol.Optional("population_size", description="Genetic algorithm population size (50-500)"): vol.All(
        vol.Coerce(int),
        vol.Range(min=50, max=500)
    ),
    vol.Optional("generations", description="Number of generations to run (100-1000)"): vol.All(
        vol.Coerce(int),
        vol.Range(min=100, max=1000)
    ),
    vol.Optional("mutation_rate", description="Mutation rate (0.01-0.20)"): vol.All(
        vol.Coerce(float),
        vol.Range(min=0.01, max=0.20)
    ),
    vol.Optional("crossover_rate", description="Crossover rate (0.5-0.95)"): vol.All(
        vol.Coerce(float),
        vol.Range(min=0.5, max=0.95)
    ),
    
    # Battery Parameters
    vol.Optional("battery_capacity", description="Battery capacity in kWh (1.0-50.0)"): vol.All(
        vol.Coerce(float),
        vol.Range(min=1.0, max=50.0)
    ),
    vol.Optional("max_charge_rate", description="Maximum battery charge rate in kW (0.5-10.0)"): vol.All(
        vol.Coerce(float),
        vol.Range(min=0.5, max=10.0)
    ),
    vol.Optional("max_discharge_rate", description="Maximum battery discharge rate in kW (0.5-10.0)"): vol.All(
        vol.Coerce(float),
        vol.Range(min=0.5, max=10.0)
    ),
    
    # Control Options
    vol.Optional("binary_control", default=False, description="Use binary (on/off) control instead of continuous"): bool,
    
    # Indexed Pricing Parameters
    vol.Optional("mfrr", default=1.94, description="Frequency Restoration Reserve (€/MWh)"): vol.All(
        vol.Coerce(float),
        vol.Range(min=0.0, max=10.0)
    ),
    vol.Optional("q", default=30.0, description="Quality component (€/MWh)"): vol.All(
        vol.Coerce(float),
        vol.Range(min=0.0, max=100.0)
    ),
    vol.Optional("fp", default=1.1674, description="Fixed percentage/multiplier"): vol.All(
        vol.Coerce(float),
        vol.Range(min=1.0, max=2.0)
    ),
    vol.Optional("tae", default=60.0, description="Transmission and distribution tariff (€/MWh)"): vol.All(
        vol.Coerce(float),
        vol.Range(min=0.0, max=200.0)
    ),
    vol.Optional("vat", default=1.23, description="VAT multiplier (1.23 = 23%)"): vol.All(
        vol.Coerce(float),
        vol.Range(min=1.0, max=1.5)
    ),
    
    # Time-of-Use Modifiers
    vol.Optional("peak_multiplier", default=1.2, description="Peak hours price multiplier"): vol.All(
        vol.Coerce(float),
        vol.Range(min=1.0, max=2.0)
    ),
    vol.Optional("off_peak_multiplier", default=0.8, description="Off-peak hours price multiplier"): vol.All(
        vol.Coerce(float),
        vol.Range(min=0.5, max=1.0)
    ),
})

class GeneticLoadManagerConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Genetic Load Manager."""

    VERSION = 1
    
    # Set the domain for this config flow
    DOMAIN = DOMAIN

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # Apply preset configuration
            preset = user_input.pop("preset", "balanced")
            if preset in PRESETS:
                preset_config = PRESETS[preset].copy()
                # Remove description from preset config
                preset_config.pop("description", None)
                user_input.update(preset_config)
                _LOGGER.info("Applied preset configuration: %s", preset)
            
            # Validate entity selections
            errors = await self._validate_entities(user_input)
            if errors:
                return self.async_show_form(
                    step_id="user",
                    data_schema=CONFIG_SCHEMA,
                    errors=errors
                )
            
            # Create the config entry
            return self.async_create_entry(
                title="Genetic Load Manager",
                data=user_input
            )

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
        )

    async def _validate_entities(self, user_input):
        """Validate that selected entities are appropriate for their purpose."""
        errors = {}
        
        # Validate PV forecast entities
        pv_entity = user_input.get("pv_forecast_entity")
        pv_tomorrow_entity = user_input.get("pv_forecast_tomorrow_entity")
        
        if pv_entity and pv_tomorrow_entity and pv_entity == pv_tomorrow_entity:
            errors["base"] = "Today and tomorrow PV forecast entities must be different"
        
        # Validate load sensor entity
        load_sensor = user_input.get("load_sensor_entity")
        if load_sensor:
            # Check if entity exists and has energy device class
            state = self.hass.states.get(load_sensor)
            if not state:
                errors["load_sensor_entity"] = "Selected load sensor entity does not exist"
            elif state.attributes.get(ATTR_DEVICE_CLASS) != "energy":
                errors["load_sensor_entity"] = "Selected entity should have device class 'energy'"
        
        # Validate battery SOC entity
        battery_entity = user_input.get("battery_soc_entity")
        if battery_entity:
            state = self.hass.states.get(battery_entity)
            if not state:
                errors["battery_soc_entity"] = "Selected battery SOC entity does not exist"
            elif state.attributes.get(ATTR_DEVICE_CLASS) != "battery":
                errors["battery_soc_entity"] = "Selected entity should have device class 'battery'"
        
        # Validate pricing entity
        pricing_entity = user_input.get("dynamic_pricing_entity")
        if pricing_entity:
            state = self.hass.states.get(pricing_entity)
            if not state:
                errors["dynamic_pricing_entity"] = "Selected pricing entity does not exist"
            elif state.attributes.get(ATTR_DEVICE_CLASS) != "monetary":
                errors["dynamic_pricing_entity"] = "Selected entity should have device class 'monetary'"
        
        return errors