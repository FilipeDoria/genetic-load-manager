"""Application credentials for Genetic Load Manager integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.config_entry_oauth2_flow import (
    AbstractOAuth2FlowHandler,
    OAuth2FlowHandler,
)
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GeneticLoadManagerOAuth2FlowHandler(AbstractOAuth2FlowHandler, domain=DOMAIN):
    """Handle OAuth2 flow for Genetic Load Manager."""

    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "scope": "energy_management optimization_control",
            "response_type": "code",
        }

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> FlowResult:
        """Create an entry for the flow."""
        return self.async_create_entry(
            title="Genetic Load Manager OAuth",
            data=data,
        )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Genetic Load Manager application credentials."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigType) -> bool:
    """Set up Genetic Load Manager application credentials from a config entry."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigType) -> bool:
    """Unload a config entry."""
    return True
