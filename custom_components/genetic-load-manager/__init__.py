"""The Genetic Load Manager integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .genetic_algorithm import GeneticLoadOptimizer
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "switch"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Genetic Load Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Create the genetic algorithm optimizer
    try:
        optimizer = GeneticLoadOptimizer(hass, entry.data)
        hass.data[DOMAIN]['optimizer'] = optimizer
        await optimizer.start()
        _LOGGER.info("Genetic Load Manager optimizer started successfully")
    except Exception as e:
        _LOGGER.error(f"Failed to start optimizer: {e}")
        return False
    
    # Forward the setup to the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    await async_register_services(hass)
    
    _LOGGER.info("Genetic Load Manager integration setup completed successfully")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Stop the optimizer
    if 'optimizer' in hass.data[DOMAIN]:
        try:
            await hass.data[DOMAIN]['optimizer'].stop()
        except Exception as e:
            _LOGGER.error(f"Error stopping optimizer: {e}")
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    _LOGGER.info("Genetic Load Manager integration unloaded successfully")
    return unload_ok

async def async_register_services(hass: HomeAssistant):
    """Register custom services."""
    
    async def handle_run_optimization(call):
        """Handle run_optimization service call."""
        try:
            optimizer = hass.data[DOMAIN].get('optimizer')
            if optimizer:
                # Update parameters if provided
                if 'population_size' in call.data:
                    optimizer.population_size = call.data['population_size']
                if 'generations' in call.data:
                    optimizer.generations = call.data['generations']
                if 'mutation_rate' in call.data:
                    optimizer.mutation_rate = call.data['mutation_rate']
                if 'crossover_rate' in call.data:
                    optimizer.crossover_rate = call.data['crossover_rate']
                
                # Run optimization
                await optimizer.run_optimization()
                _LOGGER.info("Manual optimization triggered successfully")
            else:
                _LOGGER.error("Optimizer not available")
        except Exception as e:
            _LOGGER.error(f"Error in manual optimization: {e}")

    async def handle_stop_optimization(call):
        """Handle stop_optimization service call."""
        try:
            optimizer = hass.data[DOMAIN].get('optimizer')
            if optimizer:
                await optimizer.stop()
                _LOGGER.info("Optimization stopped successfully")
            else:
                _LOGGER.error("Optimizer not available")
        except Exception as e:
            _LOGGER.error(f"Error stopping optimization: {e}")

    # Register the services
    hass.services.async_register(DOMAIN, "run_optimization", handle_run_optimization)
    hass.services.async_register(DOMAIN, "stop_optimization", handle_stop_optimization)