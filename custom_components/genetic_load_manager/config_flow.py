"""Config flow for Genetic Load Manager."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector
from homeassistant.helpers.typing import DiscoveryInfoType

from .const import (
    DOMAIN,
    CONF_POPULATION_SIZE,
    CONF_GENERATIONS,
    CONF_MUTATION_RATE,
    CONF_CROSSOVER_RATE,
    CONF_NUM_DEVICES,
    CONF_BATTERY_CAPACITY,
    CONF_MAX_CHARGE_RATE,
    CONF_MAX_DISCHARGE_RATE,
    CONF_BINARY_CONTROL,
    CONF_USE_INDEXED_PRICING,
    CONF_OPTIMIZATION_MODE,
    CONF_PV_FORECAST_TODAY,
    CONF_PV_FORECAST_TOMORROW,
    CONF_LOAD_FORECAST,
    CONF_LOAD_SENSOR,
    CONF_BATTERY_SOC,
    CONF_MARKET_PRICE,
    CONF_GRID_POWER,
    CONF_DEMAND_RESPONSE,
    CONF_CARBON_INTENSITY,
    CONF_WEATHER,
    CONF_EV_CHARGER,
    CONF_SMART_THERMOSTAT,
    CONF_SMART_PLUG,
    CONF_LIGHTING,
    CONF_MEDIA_PLAYER,
    CONF_UPDATE_INTERVAL,
    DEFAULT_POPULATION_SIZE,
    DEFAULT_GENERATIONS,
    DEFAULT_MUTATION_RATE,
    DEFAULT_CROSSOVER_RATE,
    DEFAULT_NUM_DEVICES,
    DEFAULT_BATTERY_CAPACITY,
    DEFAULT_MAX_CHARGE_RATE,
    DEFAULT_MAX_DISCHARGE_RATE,
    DEFAULT_BINARY_CONTROL,
    DEFAULT_USE_INDEXED_PRICING,
    DEFAULT_OPTIMIZATION_MODE,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_ENTITIES,
)

_LOGGER = logging.getLogger(__name__)

class GeneticLoadManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Genetic Load Manager."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.config_data = {}

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the input
                await self._validate_input(user_input)
                
                # Store the config data
                self.config_data.update(user_input)
                
                # Move to the next step
                return await self.async_step_algorithm_params()
                
            except Exception as ex:
                _LOGGER.error("Error in user step: %s", ex)
                errors["base"] = "unknown"

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_OPTIMIZATION_MODE,
                    default=DEFAULT_OPTIMIZATION_MODE
                ): vol.In([
                    "cost_savings",
                    "comfort",
                    "battery_health", 
                    "grid_stability",
                    "carbon_reduction"
                ]),
                vol.Required(
                    CONF_UPDATE_INTERVAL,
                    default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=5, max=1440)
                ),
                vol.Optional(
                    CONF_USE_INDEXED_PRICING,
                    default=DEFAULT_USE_INDEXED_PRICING
                ): bool,
            }),
            errors=errors,
        )

    async def async_step_algorithm_params(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the algorithm parameters step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the input
                await self._validate_algorithm_params(user_input)
                
                # Store the config data
                self.config_data.update(user_input)
                
                # Move to the next step
                return await self.async_step_device_config()
                
            except Exception as ex:
                _LOGGER.error("Error in algorithm params step: %s", ex)
                errors["base"] = "unknown"

        # Show the form
        return self.async_show_form(
            step_id="algorithm_params",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_POPULATION_SIZE,
                    default=DEFAULT_POPULATION_SIZE
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=20, max=500)
                ),
                vol.Required(
                    CONF_GENERATIONS,
                    default=DEFAULT_GENERATIONS
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=50, max=1000)
                ),
                vol.Required(
                    CONF_MUTATION_RATE,
                    default=DEFAULT_MUTATION_RATE
                ): vol.All(
                    vol.Coerce(float),
                    vol.Range(min=0.01, max=0.5)
                ),
                vol.Required(
                    CONF_CROSSOVER_RATE,
                    default=DEFAULT_CROSSOVER_RATE
                ): vol.All(
                    vol.Coerce(float),
                    vol.Range(min=0.1, max=1.0)
                ),
                vol.Required(
                    CONF_NUM_DEVICES,
                    default=DEFAULT_NUM_DEVICES
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=20)
                ),
            }),
            errors=errors,
        )

    async def async_step_device_config(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the device configuration step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the input
                await self._validate_device_config(user_input)
                
                # Store the config data
                self.config_data.update(user_input)
                
                # Move to the next step
                return await self.async_step_entity_mapping()
                
            except Exception as ex:
                _LOGGER.error("Error in device config step: %s", ex)
                errors["base"] = "unknown"

        # Show the form
        return self.async_show_form(
            step_id="device_config",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_BATTERY_CAPACITY,
                    default=DEFAULT_BATTERY_CAPACITY
                ): vol.All(
                    vol.Coerce(float),
                    vol.Range(min=1.0, max=100.0)
                ),
                vol.Required(
                    CONF_MAX_CHARGE_RATE,
                    default=DEFAULT_MAX_CHARGE_RATE
                ): vol.All(
                    vol.Coerce(float),
                    vol.Range(min=0.5, max=50.0)
                ),
                vol.Required(
                    CONF_MAX_DISCHARGE_RATE,
                    default=DEFAULT_MAX_DISCHARGE_RATE
                ): vol.All(
                    vol.Coerce(float),
                    vol.Range(min=0.5, max=50.0)
                ),
                vol.Optional(
                    CONF_BINARY_CONTROL,
                    default=DEFAULT_BINARY_CONTROL
                ): bool,
            }),
            errors=errors,
        )

    async def async_step_entity_mapping(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the entity mapping step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the input
                await self._validate_entity_mapping(user_input)
                
                # Store the config data
                self.config_data.update(user_input)
                
                # Create the config entry
                return self.async_create_entry(
                    title="Genetic Load Manager",
                    data=self.config_data
                )
                
            except Exception as ex:
                _LOGGER.error("Error in entity mapping step: %s", ex)
                errors["base"] = "unknown"

        # Show the form
        return self.async_show_form(
            step_id="entity_mapping",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_PV_FORECAST_TODAY,
                    default=DEFAULT_ENTITIES["pv_forecast_today"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        # More flexible selector for detailed forecast entities
                        integration="solcast"
                    )
                ),
                vol.Optional(
                    CONF_PV_FORECAST_TOMORROW,
                    default=DEFAULT_ENTITIES["pv_forecast_tomorrow"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        # More flexible selector for detailed forecast entities
                        integration="solcast"
                    )
                ),
                vol.Optional(
                    CONF_LOAD_FORECAST,
                    default=DEFAULT_ENTITIES["load_forecast"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        # Allow any sensor for load forecast
                    )
                ),
                vol.Optional(
                    CONF_LOAD_SENSOR,
                    default=DEFAULT_ENTITIES["load_sensor"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="power"
                    )
                ),
                vol.Optional(
                    CONF_BATTERY_SOC,
                    default=DEFAULT_ENTITIES["battery_soc"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="battery"
                    )
                ),
                vol.Optional(
                    CONF_MARKET_PRICE,
                    default=DEFAULT_ENTITIES["market_price"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        # Allow any sensor for market price
                    )
                ),
                vol.Optional(
                    CONF_GRID_POWER,
                    default=DEFAULT_ENTITIES["grid_power"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="power"
                    )
                ),
                vol.Optional(
                    CONF_DEMAND_RESPONSE,
                    default=DEFAULT_ENTITIES["demand_response"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="binary_sensor"
                    )
                ),
                vol.Optional(
                    CONF_CARBON_INTENSITY,
                    default=DEFAULT_ENTITIES["carbon_intensity"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor"
                    )
                ),
                vol.Optional(
                    CONF_WEATHER,
                    default=DEFAULT_ENTITIES["weather"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="weather"
                    )
                ),
                vol.Optional(
                    CONF_EV_CHARGER,
                    default=DEFAULT_ENTITIES["ev_charger"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="switch"
                    )
                ),
                vol.Optional(
                    CONF_SMART_THERMOSTAT,
                    default=DEFAULT_ENTITIES["smart_thermostat"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="climate"
                    )
                ),
                vol.Optional(
                    CONF_SMART_PLUG,
                    default=DEFAULT_ENTITIES["smart_plug"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="switch"
                    )
                ),
                vol.Optional(
                    CONF_LIGHTING,
                    default=DEFAULT_ENTITIES["lighting"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="light"
                    )
                ),
                vol.Optional(
                    CONF_MEDIA_PLAYER,
                    default=DEFAULT_ENTITIES["media_player"]
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="media_player"
                    )
                ),
            }),
            errors=errors,
        )

    async def _validate_input(self, user_input: Dict[str, Any]) -> None:
        """Validate the user input."""
        # Basic validation logic
        if user_input.get(CONF_UPDATE_INTERVAL, 0) < 5:
            raise ValueError("Update interval must be at least 5 minutes")

    async def _validate_algorithm_params(self, user_input: Dict[str, Any]) -> None:
        """Validate the algorithm parameters."""
        # Validate population size and generations
        population = user_input.get(CONF_POPULATION_SIZE, 0)
        generations = user_input.get(CONF_GENERATIONS, 0)
        
        if population * generations > 100000:
            raise ValueError("Population size × generations should not exceed 100,000 for performance reasons")

    async def _validate_device_config(self, user_input: Dict[str, Any]) -> None:
        """Validate the device configuration."""
        # Validate battery parameters
        capacity = user_input.get(CONF_BATTERY_CAPACITY, 0)
        charge_rate = user_input.get(CONF_MAX_CHARGE_RATE, 0)
        discharge_rate = user_input.get(CONF_MAX_DISCHARGE_RATE, 0)
        
        if charge_rate > capacity:
            raise ValueError("Maximum charge rate cannot exceed battery capacity")
        
        if discharge_rate > capacity:
            raise ValueError("Maximum discharge rate cannot exceed battery capacity")

    async def _validate_entity_mapping(self, user_input: Dict[str, Any]) -> None:
        """Validate the entity mapping."""
        # Check if at least some entities are configured
        required_entities = [
            CONF_PV_FORECAST_TODAY,
            CONF_PV_FORECAST_TOMORROW,
            CONF_LOAD_FORECAST,
            CONF_BATTERY_SOC
        ]
        
        if not any(user_input.get(entity) for entity in required_entities):
            raise ValueError("At least one of PV forecast, load forecast, or battery SOC entities must be configured")

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

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update the config entry
            new_data = self.config_entry.data.copy()
            new_data.update(user_input)
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            
            return self.async_create_entry(title="", data={})

        # Show current options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=5, max=1440)
                ),
                vol.Optional(
                    CONF_OPTIMIZATION_MODE,
                    default=self.config_entry.data.get(CONF_OPTIMIZATION_MODE, DEFAULT_OPTIMIZATION_MODE)
                ): vol.In([
                    "cost_savings",
                    "comfort",
                    "battery_health",
                    "grid_stability",
                    "carbon_reduction"
                ]),
            })
        )