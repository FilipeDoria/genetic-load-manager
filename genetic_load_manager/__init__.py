"""The Genetic Load Manager integration."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

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
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Genetic Load Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Store config entry
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Forward the setup to the platforms
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
    
    # Start the optimization service
    await hass.async_add_executor_job(
        start_optimization_service, hass, entry.data
    )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

def start_optimization_service(hass: HomeAssistant, config: dict):
    """Start the genetic algorithm optimization service."""
    from .genetic_algorithm import GeneticLoadOptimizer
    
    optimizer = GeneticLoadOptimizer(hass, config)
    optimizer.start()
    
    # Store optimizer instance for access from other components
    hass.data[DOMAIN]['optimizer'] = optimizer 