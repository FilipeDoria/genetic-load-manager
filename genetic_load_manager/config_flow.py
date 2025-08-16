"""Config flow for Genetic Load Manager integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_PV_ENTITY_ID,
    CONF_FORECAST_ENTITY_ID,
    CONF_BATTERY_SOC_ENTITY_ID,
    CONF_PRICE_ENTITY_ID,
)

_LOGGER = logging.getLogger(__name__)

class GeneticLoadManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Genetic Load Manager."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Genetic Load Manager",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_PV_ENTITY_ID): str,
                vol.Required(CONF_FORECAST_ENTITY_ID): str,
                vol.Required(CONF_BATTERY_SOC_ENTITY_ID): str,
                vol.Required(CONF_PRICE_ENTITY_ID): str,
            }),
        ) 