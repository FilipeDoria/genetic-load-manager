"""Sensor platform for Genetic Load Manager."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Genetic Load Manager sensor platform."""
    
    # Create a simple status sensor
    sensor = GeneticLoadManagerSensor(config_entry)
    async_add_entities([sensor], True)

class GeneticLoadManagerSensor(SensorEntity):
    """Sensor for Genetic Load Manager status."""
    
    def __init__(self, config_entry: ConfigEntry):
        """Initialize the sensor."""
        self.config_entry = config_entry
        self._attr_name = "Genetic Load Manager Status"
        self._attr_unique_id = f"{config_entry.entry_id}_status"
        self._attr_icon = "mdi:lightning-bolt"
        self._attr_should_poll = False
    
    @property
    def native_value(self):
        """Return the state of the sensor."""
        return "Active"
    
    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return {
            "integration": "Genetic Load Manager",
            "status": "Active"
        } 