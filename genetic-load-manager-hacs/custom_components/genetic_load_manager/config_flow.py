"""Config flow for Genetic Load Manager integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_PV_ENTITY_ID,
    CONF_FORECAST_ENTITY_ID,
    CONF_BATTERY_SOC_ENTITY_ID,
    CONF_PRICE_ENTITY_ID,
    CONF_OPTIMIZATION_INTERVAL,
    CONF_POPULATION_SIZE,
    CONF_GENERATIONS,
    CONF_MUTATION_RATE,
    CONF_CROSSOVER_RATE,
    DEFAULT_OPTIMIZATION_INTERVAL,
    DEFAULT_POPULATION_SIZE,
    DEFAULT_GENERATIONS,
    DEFAULT_MUTATION_RATE,
    DEFAULT_CROSSOVER_RATE,
)

_LOGGER = logging.getLogger(__name__)

class GeneticLoadManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Genetic Load Manager."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate entity IDs exist
                await self._validate_entities(user_input)
                
                # Create config entry
                return self.async_create_entry(
                    title="Genetic Load Manager",
                    data=user_input
                )
            except Exception as err:
                _LOGGER.error("Error in config flow: %s", err)
                errors["base"] = "unknown"

        # Show form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_PV_ENTITY_ID): str,
                vol.Required(CONF_FORECAST_ENTITY_ID): str,
                vol.Required(CONF_BATTERY_SOC_ENTITY_ID): str,
                vol.Required(CONF_PRICE_ENTITY_ID): str,
                vol.Optional(
                    CONF_OPTIMIZATION_INTERVAL,
                    default=DEFAULT_OPTIMIZATION_INTERVAL
                ): vol.Range(min=5, max=60),
                vol.Optional(
                    CONF_POPULATION_SIZE,
                    default=DEFAULT_POPULATION_SIZE
                ): vol.Range(min=10, max=200),
                vol.Optional(
                    CONF_GENERATIONS,
                    default=DEFAULT_GENERATIONS
                ): vol.Range(min=10, max=500),
                vol.Optional(
                    CONF_MUTATION_RATE,
                    default=DEFAULT_MUTATION_RATE
                ): vol.Range(min=0.01, max=0.5),
                vol.Optional(
                    CONF_CROSSOVER_RATE,
                    default=DEFAULT_CROSSOVER_RATE
                ): vol.Range(min=0.1, max=1.0),
            }),
            errors=errors,
        )

    async def _validate_entities(self, user_input):
        """Validate that the specified entities exist."""
        entity_ids = [
            user_input[CONF_PV_ENTITY_ID],
            user_input[CONF_FORECAST_ENTITY_ID],
            user_input[CONF_BATTERY_SOC_ENTITY_ID],
            user_input[CONF_PRICE_ENTITY_ID],
        ]
        
        for entity_id in entity_ids:
            if not self.hass.states.async_available(entity_id):
                raise ValueError(f"Entity {entity_id} does not exist")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return GeneticLoadManagerOptionsFlow(config_entry)

class GeneticLoadManagerOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_OPTIMIZATION_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_OPTIMIZATION_INTERVAL,
                        self.config_entry.data.get(CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL)
                    )
                ): vol.Range(min=5, max=60),
                vol.Optional(
                    CONF_POPULATION_SIZE,
                    default=self.config_entry.options.get(
                        CONF_POPULATION_SIZE,
                        self.config_entry.data.get(CONF_POPULATION_SIZE, DEFAULT_POPULATION_SIZE)
                    )
                ): vol.Range(min=10, max=200),
                vol.Optional(
                    CONF_GENERATIONS,
                    default=self.config_entry.options.get(
                        CONF_GENERATIONS,
                        self.config_entry.data.get(CONF_GENERATIONS, DEFAULT_GENERATIONS)
                    )
                ): vol.Range(min=10, max=500),
                vol.Optional(
                    CONF_MUTATION_RATE,
                    default=self.config_entry.options.get(
                        CONF_MUTATION_RATE,
                        self.config_entry.data.get(CONF_MUTATION_RATE, DEFAULT_MUTATION_RATE)
                    )
                ): vol.Range(min=0.01, max=0.5),
                vol.Optional(
                    CONF_CROSSOVER_RATE,
                    default=self.config_entry.options.get(
                        CONF_CROSSOVER_RATE,
                        self.config_entry.data.get(CONF_CROSSOVER_RATE, DEFAULT_CROSSOVER_RATE)
                    )
                ): vol.Range(min=0.1, max=1.0),
            })
        ) 