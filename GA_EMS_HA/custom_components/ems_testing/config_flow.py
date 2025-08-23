"""Config flow for EMS Testing integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_ENABLE_CONTROL,
    CONF_OPTIMIZATION_INTERVAL,
    CONF_MONITORED_DEVICES,
    DEFAULT_OPTIMIZATION_INTERVAL,
    DEFAULT_ENABLE_CONTROL,
)

_LOGGER = logging.getLogger(__name__)

class EMSTestingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EMS Testing."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Optional(
                            CONF_ENABLE_CONTROL, default=DEFAULT_ENABLE_CONTROL
                        ): bool,
                        vol.Optional(
                            CONF_OPTIMIZATION_INTERVAL, default=DEFAULT_OPTIMIZATION_INTERVAL
                        ): int,
                        vol.Optional(
                            CONF_MONITORED_DEVICES, default=[]
                        ): str,
                    }
                ),
            )

        # Validate the input
        try:
            # Parse monitored devices from comma-separated string
            devices_str = user_input.get(CONF_MONITORED_DEVICES, "")
            monitored_devices = [device.strip() for device in devices_str.split(",") if device.strip()]
            
            config_data = {
                CONF_ENABLE_CONTROL: user_input.get(CONF_ENABLE_CONTROL, DEFAULT_ENABLE_CONTROL),
                CONF_OPTIMIZATION_INTERVAL: user_input.get(CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL),
                CONF_MONITORED_DEVICES: monitored_devices,
            }
            
            # Create the config entry
            return self.async_create_entry(
                title="EMS Testing Integration",
                data=config_data,
            )
            
        except Exception as e:
            _LOGGER.error(f"Configuration error: {e}")
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Optional(
                            CONF_ENABLE_CONTROL, default=DEFAULT_ENABLE_CONTROL
                        ): bool,
                        vol.Optional(
                            CONF_OPTIMIZATION_INTERVAL, default=DEFAULT_OPTIMIZATION_INTERVAL
                        ): int,
                        vol.Optional(
                            CONF_MONITORED_DEVICES, default=""
                        ): str,
                    }
                ),
                errors={"base": "invalid_config"},
            )
