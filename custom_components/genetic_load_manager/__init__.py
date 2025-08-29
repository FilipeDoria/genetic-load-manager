"""The Genetic Load Manager integration."""
import logging
from datetime import timedelta, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "switch"]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Genetic Load Manager from configuration."""
    _LOGGER.info("=== Setting up Genetic Load Manager integration ===")
    
    hass.data[DOMAIN] = {}
    conf = config.get(DOMAIN, {})
    
    # Only create genetic algorithm instance if configuration is provided
    if conf:
        try:
            # Import here to avoid blocking during setup
            from .genetic_algorithm import GeneticLoadOptimizer
            genetic_algo = GeneticLoadOptimizer(hass, conf)
            hass.data[DOMAIN]["genetic_algorithm"] = genetic_algo
            
            # Initialize debug service
            try:
                from .debug_service import GeneticLoadManagerDebugService
                debug_service = GeneticLoadManagerDebugService(hass, genetic_algo)
                await debug_service.register_services()
                hass.data[DOMAIN]["debug_service"] = debug_service
                _LOGGER.info("Debug service initialized successfully")
            except Exception as e:
                _LOGGER.warning(f"Could not initialize debug service: {e}")
                _LOGGER.warning("Debug capabilities will not be available")
            
        except Exception as e:
            _LOGGER.error(f"Could not initialize genetic algorithm with config: {e}")
            _LOGGER.error(f"Exception type: {type(e).__name__}")
            import traceback
            _LOGGER.error(f"Traceback: {traceback.format_exc()}")
    
    await async_register_services(hass)
    _LOGGER.info("Genetic Load Manager integration setup completed")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Genetic Load Manager from a config entry."""
    _LOGGER.info("=== Setting up Genetic Load Manager from config entry ===")
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    try:
        # Import here to avoid blocking during setup
        from .genetic_algorithm import GeneticLoadOptimizer
        genetic_algo = GeneticLoadOptimizer(hass, entry.data)
        hass.data[DOMAIN]['genetic_algorithm'] = genetic_algo
        
        # Initialize debug service
        try:
            from .debug_service import GeneticLoadManagerDebugService
            debug_service = GeneticLoadManagerDebugService(hass, genetic_algo)
            await debug_service.register_services()
            hass.data[DOMAIN]["debug_service"] = debug_service
            _LOGGER.info("Debug service initialized successfully")
        except Exception as e:
            _LOGGER.warning(f"Could not initialize debug service: {e}")
            _LOGGER.warning("Debug capabilities will not be available")
        
        # Start the optimizer asynchronously
        _LOGGER.info("Starting genetic algorithm optimizer...")
        await genetic_algo.start()
        _LOGGER.info("Genetic Load Manager optimizer started successfully")
    except Exception as e:
        _LOGGER.error(f"Failed to start optimizer: {e}")
        _LOGGER.error(f"Exception type: {type(e).__name__}")
        import traceback
        _LOGGER.error(f"Traceback: {traceback.format_exc()}")
        return False
    
    # Forward the setup to all platforms including sensor
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_services(hass)
    
    # Start periodic optimization and store the tracker
    _LOGGER.info("Scheduling periodic optimization...")
    hass.data[DOMAIN]["async_remove_tracker"] = await genetic_algo.schedule_optimization()
    
    _LOGGER.info("Genetic Load Manager integration setup completed successfully")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("=== Unloading Genetic Load Manager integration ===")
    
    if 'genetic_algorithm' in hass.data[DOMAIN]:
        try:
            await hass.data[DOMAIN]['genetic_algorithm'].stop()
            _LOGGER.info("Genetic algorithm optimizer stopped successfully")
        except Exception as e:
            _LOGGER.error(f"Error stopping optimizer: {e}")
            _LOGGER.error(f"Exception type: {type(e).__name__}")
    
    if "async_remove_tracker" in hass.data[DOMAIN]:
        try:
            hass.data[DOMAIN]["async_remove_tracker"]()
            del hass.data[DOMAIN]["async_remove_tracker"]
            _LOGGER.info("Periodic optimization tracker removed")
        except Exception as e:
            _LOGGER.error(f"Error removing optimization tracker: {e}")
    
    # Clean up debug service
    if "debug_service" in hass.data[DOMAIN]:
        try:
            del hass.data[DOMAIN]["debug_service"]
            _LOGGER.info("Debug service cleaned up")
        except Exception as e:
            _LOGGER.error(f"Error cleaning up debug service: {e}")
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    _LOGGER.info("Genetic Load Manager integration unloaded successfully")
    return unload_ok

async def async_register_services(hass: HomeAssistant):
    """Register custom services."""
    
    # Check if services are already registered
    if hass.services.has_service(DOMAIN, "run_optimization"):
        _LOGGER.debug("Services already registered, skipping")
        return
    
    async def handle_run_optimization(call):
        """Handle run_optimization service call."""
        _LOGGER.info("=== Service call: run_optimization ===")
        
        try:
            genetic_algo = hass.data[DOMAIN].get('genetic_algorithm')
            if genetic_algo:
                # Update parameters if provided
                if 'population_size' in call.data:
                    genetic_algo.population_size = call.data['population_size']
                    _LOGGER.info(f"Updated population size to: {call.data['population_size']}")
                if 'generations' in call.data:
                    genetic_algo.generations = call.data['generations']
                    _LOGGER.info(f"Updated generations to: {call.data['generations']}")
                if 'mutation_rate' in call.data:
                    genetic_algo.mutation_rate = call.data['mutation_rate']
                    _LOGGER.info(f"Updated mutation rate to: {call.data['mutation_rate']}")
                if 'crossover_rate' in call.data:
                    genetic_algo.crossover_rate = call.data['crossover_rate']
                    _LOGGER.info(f"Updated crossover rate to: {call.data['crossover_rate']}")
                
                # Run optimization
                _LOGGER.info("Running optimization...")
                solution = await genetic_algo.optimize()
                
                if solution is not None:
                    _LOGGER.info("Optimization completed successfully")
                    _LOGGER.info(f"Solution shape: {len(solution)} devices x {len(solution[0]) if solution[0] else 0} time slots")
                else:
                    _LOGGER.error("Optimization returned no solution")
                    
            else:
                _LOGGER.error("Genetic algorithm not available")
                
        except Exception as e:
            _LOGGER.error(f"Error in run_optimization service: {e}")
            _LOGGER.error(f"Exception type: {type(e).__name__}")
            import traceback
            _LOGGER.error(f"Traceback: {traceback.format_exc()}")
    
    async def handle_debug_optimization(call):
        """Handle debug_optimization service call."""
        _LOGGER.info("=== Service call: debug_optimization ===")
        
        try:
            debug_service = hass.data[DOMAIN].get('debug_service')
            if debug_service:
                await debug_service.debug_optimization(call)
            else:
                _LOGGER.error("Debug service not available")
        except Exception as e:
            _LOGGER.error(f"Error in debug_optimization service: {e}")
    
    async def handle_generate_debug_report(call):
        """Handle generate_debug_report service call."""
        _LOGGER.info("=== Service call: generate_debug_report ===")
        
        try:
            debug_service = hass.data[DOMAIN].get('debug_service')
            if debug_service:
                result = await debug_service.generate_debug_report(call)
                _LOGGER.info(f"Debug report generation result: {result}")
            else:
                _LOGGER.error("Debug service not available")
        except Exception as e:
            _LOGGER.error(f"Error in generate_debug_report service: {e}")
    
    # Register services
    hass.services.async_register(DOMAIN, "run_optimization", handle_run_optimization)
    hass.services.async_register(DOMAIN, "debug_optimization", handle_debug_optimization)
    hass.services.async_register(DOMAIN, "generate_debug_report", handle_generate_debug_report)
    
    _LOGGER.info("Custom services registered successfully")