"""Switch platform for Genetic Load Manager integration."""
import logging
from typing import Any, Dict, Optional
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType = None):
    """Set up the Genetic Load Manager switch platform."""
    
    # Get the genetic algorithm instance
    genetic_algo = hass.data[DOMAIN].get('genetic_algorithm')
    if not genetic_algo:
        _LOGGER.error("Genetic algorithm not found")
        return
    
    # Get manageable loads - use a public method or get from status
    try:
        # Get manageable loads from the genetic algorithm
        manageable_loads = await genetic_algo.get_manageable_loads()
        
        # Create switch entities for each manageable load
        switches = []
        for load in manageable_loads:
            switch = GeneticLoadSwitch(load, genetic_algo, entry)
            switches.append(switch)
        
        if switches:
            async_add_entities(switches, True)
            _LOGGER.info("Created %d genetic load manager switches", len(switches))
        else:
            _LOGGER.info("No manageable loads found for switches")
            
    except Exception as e:
        _LOGGER.error("Error setting up switches: %s", str(e))
        return

class GeneticLoadSwitch(SwitchEntity):
    """Switch entity for controlling manageable loads."""
    
    def __init__(self, load_info: Dict[str, Any], genetic_algo, config_entry: ConfigEntry):
        """Initialize the switch."""
        self.load_info = load_info
        self.genetic_algo = genetic_algo
        self.config_entry = config_entry
        
        # Set entity properties
        self._attr_name = f"Genetic Load: {load_info.get('name', load_info['entity_id'])}"
        self._attr_unique_id = f"{config_entry.entry_id}_{load_info['entity_id']}"
        self._attr_icon = "mdi:lightning-bolt"
        self._attr_should_poll = True
        
        # Load-specific attributes
        self._attr_available = True
        self._attr_is_on = False
        self._attr_assumed_state = False
        
        # Store load information
        self.entity_id = load_info['entity_id']
        self.power_consumption = load_info.get('power_consumption', 1000)
        self.priority = load_info.get('priority', 1)
        self.flexible = load_info.get('flexible', True)
        
        _LOGGER.debug("Created switch for load: %s (Power: %dW, Priority: %d)", 
                      self.entity_id, self.power_consumption, self.priority)
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "power_consumption_w": self.power_consumption,
            "priority_level": self.priority,
            "flexible": self.flexible,
            "managed_by": "Genetic Load Manager",
            "optimization_enabled": self.genetic_algo.is_running
        }
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the load on."""
        try:
            # Turn on the actual load
            await self.hass.services.async_call(
                'switch', 'turn_on', 
                {'entity_id': self.entity_id}
            )
            
            # Update our state
            self._attr_is_on = True
            
            # Log the action
            _LOGGER.info("Turned ON load: %s", self.entity_id)
            
        except Exception as e:
            error_msg = f"Error turning ON load {self.entity_id}: {str(e)}"
            _LOGGER.error(error_msg)
            raise
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the load off."""
        try:
            # Turn off the actual load
            await self.hass.services.async_call(
                'switch', 'turn_off', 
                {'entity_id': self.entity_id}
            )
            
            # Update our state
            self._attr_is_on = False
            
            # Log the action
            _LOGGER.info("Turned OFF load: %s", self.entity_id)
            
        except Exception as e:
            error_msg = f"Error turning OFF load {self.entity_id}: {str(e)}"
            _LOGGER.error(error_msg)
            raise
    
    async def async_update(self, now=None) -> None:
        """Update the switch state."""
        try:
            # Get current state from the actual load
            load_state = self.hass.states.get(self.entity_id)
            if load_state:
                self._attr_is_on = load_state.state == "on"
                self._attr_available = True
            else:
                self._attr_available = False
                
        except Exception as e:
            _LOGGER.error("Error updating switch state for %s: %s", self.entity_id, str(e))
            self._attr_available = False
    
    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Log that this switch is now available
        self.genetic_algo._log_event(
            "INFO", 
            f"Load switch {self.entity_id} added to Home Assistant"
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        
        # Log that this switch is being removed
        self.genetic_algo._log_event(
            "INFO", 
            f"Load switch {self.entity_id} removed from Home Assistant"
        ) 