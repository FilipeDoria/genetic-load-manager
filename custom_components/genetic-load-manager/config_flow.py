"""Config flow for Genetic Load Manager integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

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

class GeneticLoadManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Genetic Load Manager."""

    VERSION = 1

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
            
            # Create the config entry
            return self.async_create_entry(
                title="Genetic Load Manager",
                data=user_input
            )

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("preset", description="Select optimization strategy"): vol.In(list(PRESETS.keys())),
                vol.Required("pv_forecast_entity", description="Select Solcast PV Forecast Entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor", integration="solcast_pv_forecast")
                ),
                vol.Required("load_forecast_entity"): str,
                vol.Required("battery_soc_entity"): str,
                vol.Required("dynamic_pricing_entity"): str,
                vol.Optional("num_devices", default=2): int,
                vol.Optional("population_size"): int,
                vol.Optional("generations"): int,
                vol.Optional("mutation_rate"): float,
                vol.Optional("crossover_rate"): float,
                vol.Optional("battery_capacity"): float,
                vol.Optional("max_charge_rate"): float,
                vol.Optional("max_discharge_rate"): float,
                vol.Optional("binary_control", default=False): bool,
            }),
        )