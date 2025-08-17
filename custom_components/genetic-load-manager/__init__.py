"""The Genetic Load Manager integration."""
import logging
from datetime import timedelta, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from .genetic_algorithm import GeneticLoadOptimizer
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "switch"]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Genetic Load Manager from configuration."""
    hass.data[DOMAIN] = {}
    conf = config.get(DOMAIN, {})
    genetic_algo = GeneticLoadOptimizer(hass, conf)
    hass.data[DOMAIN]["genetic_algorithm"] = genetic_algo
    await async_register_services(hass)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Genetic Load Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    try:
        genetic_algo = GeneticLoadOptimizer(hass, entry.data)
        hass.data[DOMAIN]['genetic_algorithm'] = genetic_algo
        await genetic_algo.start()
        _LOGGER.info("Genetic Load Manager optimizer started successfully")
    except Exception as e:
        _LOGGER.error(f"Failed to start optimizer: {e}")
        return False
    
    # Forward the setup to all platforms including sensor
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_services(hass)
    await genetic_algo.schedule_optimization() # Start periodic optimization
    
    _LOGGER.info("Genetic Load Manager integration setup completed successfully")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if 'genetic_algorithm' in hass.data[DOMAIN]:
        try:
            await hass.data[DOMAIN]['genetic_algorithm'].stop()
        except Exception as e:
            _LOGGER.error(f"Error stopping optimizer: {e}")
    
    if "async_remove_tracker" in hass.data[DOMAIN]:
        hass.data[DOMAIN]["async_remove_tracker"]()
        del hass.data[DOMAIN]["async_remove_tracker"]
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    _LOGGER.info("Genetic Load Manager integration unloaded successfully")
    return unload_ok

async def async_register_services(hass: HomeAssistant):
    """Register custom services."""
    
    @callback
    async def handle_run_optimization(call):
        """Handle run_optimization service call."""
        try:
            genetic_algo = hass.data[DOMAIN].get('genetic_algorithm')
            if genetic_algo:
                if 'population_size' in call.data:
                    genetic_algo.population_size = call.data['population_size']
                if 'generations' in call.data:
                    genetic_algo.generations = call.data['generations']
                if 'mutation_rate' in call.data:
                    genetic_algo.mutation_rate = call.data['mutation_rate']
                if 'crossover_rate' in call.data:
                    genetic_algo.crossover_rate = call.data['crossover_rate']
                
                await genetic_algo.run_optimization()
                
                await hass.states.async_set(
                    "sensor.genetic_algorithm_status",
                    "completed",
                    attributes={
                        "generation": genetic_algo.generations, 
                        "best_fitness": genetic_algo.best_fitness
                    }
                )
                
                _LOGGER.info("Manual optimization triggered successfully")
            else:
                _LOGGER.error("Optimizer not available")
        except Exception as e:
            _LOGGER.error(f"Error in manual optimization: {e}")

    @callback
    async def handle_start_optimization(call):
        """Handle start_optimization service call."""
        try:
            genetic_algo = hass.data[DOMAIN].get('genetic_algorithm')
            if genetic_algo:
                if "async_remove_tracker" not in hass.data[DOMAIN]:
                    hass.data[DOMAIN]["async_remove_tracker"] = await genetic_algo.schedule_optimization()
                    await hass.states.async_set(
                        "sensor.genetic_algorithm_status",
                        "started",
                        attributes={"message": "Periodic optimization started"}
                    )
                    _LOGGER.info("Periodic optimization started successfully")
                else:
                    _LOGGER.warning("Optimization tracker already active")
            else:
                _LOGGER.error("Optimizer not available")
        except Exception as e:
            _LOGGER.error(f"Error starting optimization: {e}")

    @callback
    async def handle_stop_optimization(call):
        """Handle stop_optimization service call."""
        try:
            if "async_remove_tracker" in hass.data[DOMAIN]:
                hass.data[DOMAIN]["async_remove_tracker"]()
                del hass.data[DOMAIN]["async_remove_tracker"]
                await hass.states.async_set(
                    "sensor.genetic_algorithm_status",
                    "stopped",
                    attributes={"message": "Periodic optimization stopped"}
                )
                _LOGGER.info("Periodic optimization stopped successfully")
            else:
                _LOGGER.warning("No optimization tracker to stop")
        except Exception as e:
            _LOGGER.error(f"Error stopping optimization: {e}")

    @callback
    async def handle_toggle_scheduler(call):
        """Handle toggle_scheduler service call."""
        try:
            genetic_algo = hass.data[DOMAIN].get('genetic_algorithm')
            if genetic_algo:
                mode = call.data.get('mode', 'genetic')
                
                if mode == 'rule-based':
                    # Generate rule-based schedule
                    schedule = await genetic_algo.rule_based_schedule()
                    
                    # Update device schedule entities
                    for d in range(schedule.shape[0]):
                        if schedule.shape[1] > 0:
                            schedule_value = "on" if schedule[d][0] > 0.5 else "off"
                            entity_id = f"switch.device_{d}_schedule"
                            
                            await hass.states.async_set(
                                entity_id,
                                schedule_value,
                                attributes={
                                    "schedule": schedule[d].tolist(),
                                    "scheduler_mode": "rule-based",
                                    "timestamp": datetime.now().isoformat()
                                }
                            )
                    
                    await hass.states.async_set(
                        "sensor.genetic_algorithm_status",
                        "rule-based",
                        attributes={
                            "message": "Rule-based scheduling active",
                            "scheduler_mode": "rule-based",
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    _LOGGER.info("Switched to rule-based scheduling")
                    
                else:
                    # Switch back to genetic algorithm
                    await hass.states.async_set(
                        "sensor.genetic_algorithm_status",
                        "genetic",
                        attributes={
                            "message": "Genetic algorithm scheduling active",
                            "scheduler_mode": "genetic",
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    _LOGGER.info("Switched to genetic algorithm scheduling")
            else:
                _LOGGER.error("Optimizer not available")
        except Exception as e:
            _LOGGER.error(f"Error toggling scheduler: {e}")

    hass.services.async_register(DOMAIN, "run_optimization", handle_run_optimization)
    hass.services.async_register(DOMAIN, "start_optimization", handle_start_optimization)
    hass.services.async_register(DOMAIN, "stop_optimization", handle_stop_optimization)
    hass.services.async_register(DOMAIN, "toggle_scheduler", handle_toggle_scheduler)