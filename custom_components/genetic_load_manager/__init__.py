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
    hass.data[DOMAIN] = {}
    conf = config.get(DOMAIN, {})
    
    # Only create genetic algorithm instance if configuration is provided
    if conf:
        try:
            # Import here to avoid blocking during setup
            from .genetic_algorithm import GeneticLoadOptimizer
            genetic_algo = GeneticLoadOptimizer(hass, conf)
            hass.data[DOMAIN]["genetic_algorithm"] = genetic_algo
        except Exception as e:
            _LOGGER.warning(f"Could not initialize genetic algorithm with config: {e}")
    
    await async_register_services(hass)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Genetic Load Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    try:
        # Import here to avoid blocking during setup
        from .genetic_algorithm import GeneticLoadOptimizer
        genetic_algo = GeneticLoadOptimizer(hass, entry.data)
        hass.data[DOMAIN]['genetic_algorithm'] = genetic_algo
        
        # Start the optimizer asynchronously
        await genetic_algo.start()
        _LOGGER.info("Genetic Load Manager optimizer started successfully")
    except Exception as e:
        _LOGGER.error(f"Failed to start optimizer: {e}")
        return False
    
    # Forward the setup to all platforms including sensor
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_services(hass)
    
    # Start periodic optimization and store the tracker
    hass.data[DOMAIN]["async_remove_tracker"] = await genetic_algo.schedule_optimization()
    
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
    
    # Check if services are already registered
    if hass.services.has_service(DOMAIN, "run_optimization"):
        _LOGGER.debug("Services already registered, skipping")
        return
    
    async def handle_run_optimization(call):
        """Handle run_optimization service call."""
        try:
            genetic_algo = hass.data[DOMAIN].get('genetic_algorithm')
            if genetic_algo:
                # Update parameters if provided
                if 'population_size' in call.data:
                    genetic_algo.population_size = call.data['population_size']
                if 'generations' in call.data:
                    genetic_algo.generations = call.data['generations']
                if 'mutation_rate' in call.data:
                    genetic_algo.mutation_rate = call.data['mutation_rate']
                if 'crossover_rate' in call.data:
                    genetic_algo.crossover_rate = call.data['crossover_rate']
                
                # Run optimization asynchronously
                await genetic_algo.run_optimization()
                
                # Update state asynchronously
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

    async def handle_toggle_scheduler(call):
        """Handle toggle_scheduler service call."""
        try:
            genetic_algo = hass.data[DOMAIN].get('genetic_algorithm')
            if genetic_algo:
                mode = call.data.get('mode', 'genetic')
                
                if mode == 'rule-based':
                    # Generate rule-based schedule asynchronously
                    schedule = await genetic_algo.rule_based_schedule()
                    
                    # Update device schedule entities
                    if schedule is not None and hasattr(schedule, 'shape') and schedule.shape[0] > 0:
                        for d in range(schedule.shape[0]):
                            if schedule.shape[1] > 0:
                                schedule_value = "on" if schedule[d][0] > 0.5 else "off"
                                entity_id = f"switch.device_{d}_schedule"
                                
                                await hass.states.async_set(
                                    entity_id,
                                    schedule_value,
                                    attributes={
                                        "schedule": schedule[d].tolist() if hasattr(schedule[d], 'tolist') else schedule[d],
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

    async def handle_update_pricing_parameters(call):
        """Handle updating pricing parameters."""
        try:
            config_updates = call.data
            _LOGGER.info(f"Updating pricing parameters: {config_updates}")
            
            # Update the genetic algorithm configuration if it exists
            if hasattr(hass.data[DOMAIN], 'genetic_algorithm'):
                genetic_algo = hass.data[DOMAIN]['genetic_algorithm']
                if hasattr(genetic_algo, 'pricing_calculator') and hasattr(genetic_algo.pricing_calculator, 'update_config'):
                    genetic_algo.pricing_calculator.update_config(config_updates)
                    _LOGGER.info("Pricing parameters updated successfully")
                else:
                    _LOGGER.warning("Pricing calculator not available for updates")
            
        except Exception as e:
            _LOGGER.error(f"Error updating pricing parameters: {e}")

    async def handle_get_full_schedule(call):
        """Handle getting full schedule data."""
        try:
            target = call.data.get("target", {})
            data_type = call.data.get("data_type", "full_schedule")
            device_id = call.data.get("device_id")
            
            _LOGGER.info(f"Getting schedule data: type={data_type}, device_id={device_id}")
            
            # Get the target entity
            entity_id = target.get("entity", {}).get("entity_id")
            if not entity_id:
                _LOGGER.error("No entity specified in target")
                return
            
            # Get the entity state
            entity_state = hass.states.get(entity_id)
            if not entity_state:
                _LOGGER.error(f"Entity {entity_id} not found")
                return
            
            # Get the schedule data from the entity
            schedule_data = entity_state.attributes.get("detailed_schedule") or entity_state.attributes.get("compressed_schedule")
            
            if not schedule_data:
                _LOGGER.warning(f"No schedule data available for {entity_id}")
                return
            
            # Process based on data type
            if data_type == "summary_only":
                result = {
                    "entity_id": entity_id,
                    "data_type": "summary",
                    "data": entity_state.attributes.get("summary", {})
                }
            elif data_type == "device_schedule" and device_id is not None:
                if "predicted_schedule" in schedule_data and len(schedule_data["predicted_schedule"]) > device_id:
                    device_schedule = schedule_data["predicted_schedule"][device_id]
                    result = {
                        "entity_id": entity_id,
                        "device_id": device_id,
                        "data_type": "device_schedule",
                        "data": device_schedule
                    }
                else:
                    _LOGGER.error(f"Device {device_id} not found in schedule data")
                    return
            else:
                # Return full or compressed schedule
                result = {
                    "entity_id": entity_id,
                    "data_type": data_type,
                    "data": schedule_data
                }
            
            # Log the result (in production, you might want to return this via a different mechanism)
            _LOGGER.info(f"Schedule data retrieved: {len(str(result))} characters")
            
            # You could also store this in a temporary entity or return via websocket
            # For now, we'll just log it
            
        except Exception as e:
            _LOGGER.error(f"Error getting full schedule: {e}")

    async def handle_get_schedule_statistics(call):
        """Handle getting schedule statistics."""
        try:
            target = call.data.get("target", {})
            
            # Get the target entity
            entity_id = target.get("entity", {}).get("entity_id")
            if not entity_id:
                _LOGGER.error("No entity specified in target")
                return
            
            # Get the entity state
            entity_state = hass.states.get(entity_id)
            if not entity_state:
                _LOGGER.error(f"Entity {entity_id} not found")
                return
            
            # Get the schedule data
            schedule_data = entity_state.attributes.get("detailed_schedule") or entity_state.attributes.get("compressed_schedule")
            
            if not schedule_data:
                _LOGGER.warning(f"No schedule data available for {entity_id}")
                return
            
            # Calculate statistics
            stats = calculate_schedule_statistics(schedule_data)
            
            # Log the statistics
            _LOGGER.info(f"Schedule statistics for {entity_id}: {stats}")
            
        except Exception as e:
            _LOGGER.error(f"Error getting schedule statistics: {e}")

    def calculate_schedule_statistics(schedule_data):
        """Calculate statistics from schedule data."""
        try:
            stats = {
                "total_devices": 0,
                "total_time_slots": 0,
                "average_device_usage": 0,
                "peak_usage_time": None,
                "peak_usage_value": 0
            }
            
            if "predicted_schedule" in schedule_data:
                schedule = schedule_data["predicted_schedule"]
                stats["total_devices"] = len(schedule)
                
                if schedule:
                    # Calculate total usage across all devices and time slots
                    total_usage = 0
                    time_slot_usage = []
                    
                    for device_schedule in schedule:
                        if isinstance(device_schedule, dict) and "devices" in device_schedule:
                            device_values = list(device_schedule["devices"].values())
                        elif isinstance(device_schedule, list):
                            device_values = device_schedule
                        else:
                            continue
                        
                        stats["total_time_slots"] = max(stats["total_time_slots"], len(device_values))
                        total_usage += sum(device_values)
                        
                        # Track time slot usage
                        for i, value in enumerate(device_values):
                            while len(time_slot_usage) <= i:
                                time_slot_usage.append(0)
                            time_slot_usage[i] += value
                    
                    if stats["total_devices"] > 0:
                        stats["average_device_usage"] = total_usage / stats["total_devices"]
                    
                    # Find peak usage time
                    if time_slot_usage:
                        peak_idx = time_slot_usage.index(max(time_slot_usage))
                        stats["peak_usage_value"] = max(time_slot_usage)
                        stats["peak_usage_time"] = f"Slot {peak_idx}"
            
            return stats
            
        except Exception as e:
            _LOGGER.error(f"Error calculating schedule statistics: {e}")
            return {"error": str(e)}

    # Register services
    hass.services.async_register(
        DOMAIN, "run_optimization", handle_run_optimization
    )
    hass.services.async_register(
        DOMAIN, "toggle_scheduler", handle_toggle_scheduler
    )
    hass.services.async_register(
        DOMAIN, "update_pricing_parameters", handle_update_pricing_parameters
    )
    hass.services.async_register(
        DOMAIN, "get_full_schedule", handle_get_full_schedule
    )
    hass.services.async_register(
        DOMAIN, "get_schedule_statistics", handle_get_schedule_statistics
    )