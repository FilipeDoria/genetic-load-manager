"""The Genetic Load Manager integration."""
import logging
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .genetic_algorithm import GeneticLoadOptimizer

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Genetic Load Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Initialize the genetic algorithm optimizer
    optimizer = GeneticLoadOptimizer(hass, entry.data)
    hass.data[DOMAIN]['optimizer'] = optimizer
    
    # Start the optimization service
    await optimizer.start()
    
    # Forward the setup to the platforms using the correct API
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Genetic Load Manager integration setup completed successfully")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Stop the optimizer
    optimizer = hass.data[DOMAIN].get('optimizer')
    if optimizer:
        await optimizer.stop()
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    _LOGGER.info("Genetic Load Manager integration unloaded successfully")
    return unload_ok 