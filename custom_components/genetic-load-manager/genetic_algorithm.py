"""Genetic Algorithm implementation for Load Optimization."""
import logging
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import numpy as np
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GeneticLoadOptimizer:
    """Genetic Algorithm for optimizing load schedules."""
    
    def __init__(self, hass, config: Dict[str, Any]):
        """Initialize the genetic algorithm optimizer."""
        self.hass = hass
        self.config = config  # Store config for access in other methods
        self.population_size = config.get('population_size', 100)
        self.generations = config.get('generations', 200)
        self.mutation_rate = config.get('mutation_rate', 0.05)
        self.crossover_rate = config.get('crossover_rate', 0.8)
        self.num_devices = config.get('num_devices', 2)
        self.time_slots = 96  # 24 hours * 15-minute intervals
        
        # Solcast integration entities
        self.pv_forecast_entity = config.get('pv_forecast_entity')
        self.pv_forecast_tomorrow_entity = config.get('pv_forecast_tomorrow_entity')
        self.load_forecast_entity = config.get('load_forecast_entity')
        self.battery_soc_entity = config.get('battery_soc_entity')
        self.dynamic_pricing_entity = config.get('dynamic_pricing_entity')
        
        # Device priorities for optimization
        self.device_priorities = config.get('device_priorities', [1.0] * self.num_devices)
        
        # Battery parameters
        self.battery_capacity = config.get('battery_capacity', 10.0)  # kWh
        self.max_charge_rate = config.get('max_charge_rate', 2.0)  # kW
        self.max_discharge_rate = config.get('max_discharge_rate', 2.0)  # kW
        
        # Optimization state
        self.is_running = False
        self.population = None
        self.pv_forecast = None
        self.load_forecast = None
        self.pricing = None
        self.battery_soc = 50.0  # Default 50% SOC
        
        # Performance optimization - data caching
        self._last_forecast_update = None
        self._forecast_cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        self._data_listener = None
        
        _LOGGER.info("Genetic Load Optimizer initialized with population_size=%d, generations=%d, num_devices=%d", 
                     self.population_size, self.generations, self.num_devices)
        _LOGGER.info("Solcast PV forecast entities: %s, %s", self.pv_forecast_entity, self.pv_forecast_tomorrow_entity)
    
    async def start(self):
        """Start the optimization service."""
        if self.is_running:
            _LOGGER.warning("Optimization service already running")
            return
        
        self.is_running = True
        _LOGGER.info("Genetic Load Optimizer started")
        
        # Setup state change listener for performance optimization
        await self._setup_data_listener()
        
        # Fetch initial forecast data
        await self.fetch_forecast_data()
        
        _LOGGER.info("Genetic Load Optimizer started successfully")
    
    async def stop(self):
        """Stop the optimization service."""
        self.is_running = False
        _LOGGER.info("Genetic Load Optimizer stopped")
        
        # Remove state change listener
        if self._data_listener:
            self._data_listener()
            self._data_listener = None
    
    async def _setup_data_listener(self):
        """Setup state change listener for automatic forecast updates."""
        try:
            from homeassistant.core import callback
            
            @callback
            def handle_state_change(event):
                """Handle state changes for forecast entities."""
                entity_id = event.data.get("entity_id")
                if entity_id in [
                    self.pv_forecast_entity, 
                    self.pv_forecast_tomorrow_entity,
                    self.load_forecast_entity, 
                    self.battery_soc_entity, 
                    self.dynamic_pricing_entity
                ]:
                    _LOGGER.debug("State change detected for %s, scheduling forecast update", entity_id)
                    # Schedule forecast update (non-blocking)
                    asyncio.create_task(self._schedule_forecast_update())
            
            # Register the listener
            self._data_listener = self.hass.bus.async_listen("state_changed", handle_state_change)
            _LOGGER.info("State change listener registered for forecast entities")
            
        except Exception as e:
            _LOGGER.error("Error setting up state change listener: %s", str(e))
    
    async def _schedule_forecast_update(self):
        """Schedule a forecast update with debouncing."""
        try:
            # Debounce rapid state changes
            if (self._last_forecast_update and 
                datetime.now() - self._last_forecast_update < timedelta(seconds=30)):
                _LOGGER.debug("Skipping forecast update - too recent")
                return
            
            # Wait a bit to allow multiple rapid changes to settle
            await asyncio.sleep(2)
            
            # Update forecasts
            await self.fetch_forecast_data()
            self._last_forecast_update = datetime.now()
            
            _LOGGER.info("Forecast data updated via state change listener")
            
        except Exception as e:
            _LOGGER.error("Error in scheduled forecast update: %s", str(e))
    
    async def fetch_forecast_data(self, force_update=False):
        """Fetch and process Solcast PV, load, battery, and pricing data for a 24-hour horizon."""
        try:
            # Check if we need to update (cache check)
            if (not force_update and 
                self._last_forecast_update and 
                datetime.now() - self._last_forecast_update < self._forecast_cache_duration):
                _LOGGER.debug("Using cached forecast data (last update: %s)", 
                            self._last_forecast_update.strftime("%H:%M:%S"))
                return
            
            _LOGGER.info("Fetching forecast data from Solcast and other sources...")
            
            current_time = datetime.now().replace(second=0, microsecond=0)
            slot_duration = timedelta(minutes=15)
            forecast_horizon = timedelta(hours=24)
            end_time = current_time + forecast_horizon
            pv_forecast = np.zeros(self.time_slots)

            # Fetch today's and tomorrow's Solcast forecasts
            pv_today_state = self.hass.states.get(self.pv_forecast_entity)
            pv_tomorrow_state = self.hass.states.get(self.pv_forecast_tomorrow_entity)
            pv_today_raw = pv_today_state.attributes.get("DetailedForecast", []) if pv_today_state else []
            pv_tomorrow_raw = pv_tomorrow_state.attributes.get("DetailedForecast", []) if pv_tomorrow_state else []

            if not pv_today_raw and not pv_tomorrow_raw:
                _LOGGER.warning("No Solcast PV forecast data available, using zeros")
                self.pv_forecast = pv_forecast
            else:
                # Combine forecasts
                times = []
                values = []
                for forecast in [pv_today_raw, pv_tomorrow_raw]:
                    for item in forecast:
                        try:
                            period_start = datetime.fromisoformat(item["period_start"].replace("Z", "+00:00"))
                            pv_estimate = float(item["pv_estimate"])
                            times.append(period_start)
                            values.append(pv_estimate)
                        except (KeyError, ValueError) as e:
                            _LOGGER.error(f"Error parsing Solcast forecast: {e}")
                            continue

                if times:
                    # Sort by time to ensure chronological order
                    sorted_pairs = sorted(zip(times, values), key=lambda x: x[0])
                    times, values = zip(*sorted_pairs)
                    times = list(times)
                    values = list(values)

                    # Interpolate to 15-minute slots
                    for t in range(self.time_slots):
                        slot_time = current_time + t * slot_duration
                        if slot_time < times[0] or slot_time >= times[-1]:
                            pv_forecast[t] = 0.0
                            continue
                        # Find bracketing times
                        for i in range(len(times) - 1):
                            if times[i] <= slot_time < times[i + 1]:
                                # Linear interpolation
                                time_diff = (times[i + 1] - times[i]).total_seconds()
                                slot_diff = (slot_time - times[i]).total_seconds()
                                weight = slot_diff / time_diff
                                pv_forecast[t] = values[i] * (1 - weight) + values[i + 1] * weight
                                break

            # Fetch load forecast
            load_state = self.hass.states.get(self.load_forecast_entity)
            self.load_forecast = np.array([float(x) for x in load_state.attributes.get("forecast", [0] * self.time_slots)] if load_state else [0] * self.time_slots)

            # Fetch battery state and pricing
            battery_state = self.hass.states.get(self.battery_soc_entity)
            pricing_state = self.hass.states.get(self.dynamic_pricing_entity)
            self.battery_soc = float(battery_state.state) if battery_state else 0.0
            self.pricing = np.array([float(x) for x in pricing_state.attributes.get("prices", [0.1] * self.time_slots)] if pricing_state else [0.1] * self.time_slots)
            self.pv_forecast = pv_forecast
            
            # Log summary of forecast data
            await self._log_forecast_summary()
            
            # Update cache timestamp
            self._last_forecast_update = datetime.now()
            
        except Exception as e:
            _LOGGER.error("Error fetching forecast data: %s", str(e))
            # Set default values on error
            self.pv_forecast = np.zeros(self.time_slots)
            self.load_forecast = np.zeros(self.time_slots)
            self.pricing = np.full(self.time_slots, 0.15)
            self.battery_soc = 50.0
    
    async def _log_forecast_summary(self):
        """Log a summary of all forecast data."""
        try:
            _LOGGER.info("=== Forecast Data Summary ===")
            _LOGGER.info("PV Forecast: %d slots, %.1f%% non-zero, max: %.3f kW", 
                       len(self.pv_forecast), 
                       (np.count_nonzero(self.pv_forecast) / len(self.pv_forecast)) * 100,
                       np.max(self.pv_forecast))
            _LOGGER.info("Load Forecast: %d slots, %.1f%% non-zero, max: %.3f kW", 
                       len(self.load_forecast),
                       (np.count_nonzero(self.load_forecast) / len(self.load_forecast)) * 100,
                       np.max(self.load_forecast))
            _LOGGER.info("Pricing: %d slots, range: %.3f - %.3f", 
                       len(self.pricing), np.min(self.pricing), np.max(self.pricing))
            _LOGGER.info("Battery SOC: %.1f%%", self.battery_soc)
            
        except Exception as e:
            _LOGGER.error("Error logging forecast summary: %s", str(e))
    
    async def initialize_population(self):
        """Initialize the population for optimization."""
        try:
            self.population = np.random.uniform(0, 1, (self.population_size, self.num_devices, self.time_slots))
            
            # Apply binary control if configured
            if hasattr(self, 'config') and self.config.get("binary_control", False):
                for i in range(self.population_size):
                    for d in range(self.num_devices):
                        self.population[i, d, :] = (self.population[i, d, :] > 0.5).astype(float)
            
            _LOGGER.info("Initialized population: %d individuals, %d devices, %d time slots", 
                        self.population_size, self.num_devices, self.time_slots)
            
        except Exception as e:
            _LOGGER.error("Error initializing population: %s", str(e))
            raise
    
    async def fitness_function(self, chromosome):
        """Calculate fitness score for an individual."""
        try:
            cost = 0.0
            solar_utilization = 0.0
            battery_penalty = 0.0
            priority_penalty = 0.0
            battery_soc = self.battery_soc
            
            for t in range(self.time_slots):
                total_load = np.sum(chromosome[:, t])
                net_load = total_load - self.pv_forecast[t]
                grid_energy = max(0, net_load)
                cost += grid_energy * self.pricing[t]
                solar_utilization += min(self.pv_forecast[t], total_load) / (self.pv_forecast[t] + 1e-6)
                
                # Battery management
                battery_change = 0
                if net_load < 0:
                    battery_change = min(-net_load, self.max_charge_rate)
                elif net_load > 0:
                    battery_change = -min(net_load, self.max_discharge_rate)
                
                battery_soc += battery_change
                if battery_soc < 0 or battery_soc > self.battery_capacity:
                    battery_penalty += abs(battery_soc - self.battery_capacity / 2) * 100
                battery_soc = np.clip(battery_soc, 0, self.battery_capacity)
                
                # Device priority penalty
                for d in range(self.num_devices):
                    priority_penalty += (1 - chromosome[d, t]) * self.device_priorities[d]
            
            solar_efficiency = solar_utilization / self.time_slots
            fitness = -(0.5 * cost + 0.3 * battery_penalty + 0.1 * priority_penalty - 0.1 * solar_efficiency)
            
            return fitness
            
        except Exception as e:
            _LOGGER.error("Error in fitness function: %s", str(e))
            return 0.0
    
    async def tournament_selection(self, fitness_scores):
        """Tournament selection for parent selection."""
        try:
            tournament_size = 5
            selection = random.sample(range(self.population_size), tournament_size)
            best_idx = selection[np.argmax([fitness_scores[i] for i in selection])]
            return self.population[best_idx]
            
        except Exception as e:
            _LOGGER.error("Error in tournament selection: %s", str(e))
            return self.population[0]  # Fallback to first individual
    
    async def crossover(self, parent1, parent2):
        """Perform crossover between two parents."""
        try:
            if random.random() < self.crossover_rate:
                point = random.randint(1, self.time_slots - 1)
                child1 = np.concatenate((parent1[:, :point], parent2[:, point:]), axis=1)
                child2 = np.concatenate((parent2[:, :point], parent1[:, point:]), axis=1)
                return child1, child2
            return parent1.copy(), parent2.copy()
            
        except Exception as e:
            _LOGGER.error("Error in crossover: %s", str(e))
            return parent1.copy(), parent2.copy()
    
    async def mutate(self, chromosome, generation):
        """Apply mutation to a chromosome."""
        try:
            adaptive_rate = self.mutation_rate * (1 - generation / self.generations)
            mutation_mask = np.random.random(chromosome.shape) < adaptive_rate
            
            if hasattr(self, 'config') and self.config.get("binary_control", False):
                chromosome[mutation_mask] = 1 - chromosome[mutation_mask]
            else:
                chromosome[mutation_mask] = np.random.uniform(0, 1)
            
            return chromosome
            
        except Exception as e:
            _LOGGER.error("Error in mutation: %s", str(e))
            return chromosome
    
    async def optimize(self):
        """Run genetic algorithm optimization."""
        try:
            _LOGGER.info("Starting genetic algorithm optimization...")
            
            # Fetch latest forecast data
            await self.fetch_forecast_data()
            
            # Initialize population
            await self.initialize_population()
            
            best_solution = None
            best_fitness = float("-inf")
            
            _LOGGER.info("Running optimization for %d generations with population size %d", 
                        self.generations, self.population_size)
            
            for generation in range(self.generations):
                # Evaluate fitness for all individuals
                fitness_scores = np.array([await self.fitness_function(ind) for ind in self.population])
                max_fitness = np.max(fitness_scores)
                
                # Update best solution
                if max_fitness > best_fitness:
                    best_fitness = max_fitness
                    best_solution = self.population[np.argmax(fitness_scores)].copy()
                    _LOGGER.info("Generation %d: New best fitness: %.4f", generation, best_fitness)
                
                # Update status sensor
                await self.hass.states.async_set(
                    "sensor.genetic_algorithm_status",
                    "running",
                    attributes={
                        "generation": generation,
                        "best_fitness": float(max_fitness),
                        "convergence_progress": (generation / self.generations) * 100
                    }
                )
                
                # Create new population
                new_population = []
                for _ in range(self.population_size // 2):
                    parent1 = await self.tournament_selection(fitness_scores)
                    parent2 = await self.tournament_selection(fitness_scores)
                    child1, child2 = await self.crossover(parent1, parent2)
                    child1 = await self.mutate(child1, generation)
                    child2 = await self.mutate(child2, generation)
                    new_population.extend([child1, child2])
                
                self.population = np.array(new_population)
                
                # Log progress every 10 generations
                if generation % 10 == 0:
                    _LOGGER.info("Generation %d/%d: Best fitness = %.4f", 
                                generation, self.generations, max_fitness)
            
            # Update final status
            await self.hass.states.async_set(
                "sensor.genetic_algorithm_status",
                "completed",
                attributes={
                    "generation": self.generations,
                    "best_fitness": float(best_fitness)
                }
            )
            
            _LOGGER.info("Optimization completed. Best fitness: %.4f", best_fitness)
            return best_solution
            
        except Exception as e:
            error_msg = f"Error in optimization: {str(e)}"
            _LOGGER.error(error_msg)
            
            # Update status on error
            await self.hass.states.async_set(
                "sensor.genetic_algorithm_status",
                "error",
                attributes={"error": error_msg, "timestamp": datetime.now().isoformat()}
            )
            raise
    
    async def schedule_optimization(self):
        """Schedule periodic optimization every 15 minutes."""
        async def periodic_optimization(now):
            """Run optimization and update device schedules."""
            try:
                if self.is_running:
                    solution = await self.optimize()
                    
                    # Update device schedule entities
                    for d in range(self.num_devices):
                        if solution is not None and d < solution.shape[0] and solution.shape[1] > 0:
                            schedule_value = "on" if solution[d][0] > 0.5 else "off"
                            entity_id = f"switch.device_{d}_schedule"
                            
                            await self.hass.states.async_set(
                                entity_id,
                                schedule_value,
                                attributes={"schedule": solution[d].tolist()}
                            )
                            
                            _LOGGER.debug("Updated %s: %s", entity_id, schedule_value)
                    
                    _LOGGER.info("Periodic optimization completed successfully")
                else:
                    _LOGGER.warning("Optimizer not running, skipping periodic optimization")
                    
            except Exception as e:
                _LOGGER.error("Error in periodic optimization: %s", str(e))
        
        # Run initial optimization
        await periodic_optimization(datetime.now())
        
        # Schedule periodic execution every 15 minutes
        async_remove_tracker = self.hass.helpers.event.async_track_time_interval(
            periodic_optimization, 
            timedelta(minutes=15)
        )
        
        # Store tracker in hass.data for access by stop service
        self.hass.data[DOMAIN]["async_remove_tracker"] = async_remove_tracker
        
        _LOGGER.info("Scheduled periodic optimization every 15 minutes")
        return async_remove_tracker
    
    async def run_optimization(self):
        """Public method to run optimization manually."""
        if not self.is_running:
            _LOGGER.warning("Optimizer not running, cannot run optimization")
            return
        
        try:
            await self.optimize()
            _LOGGER.info("Manual optimization completed successfully")
        except Exception as e:
            error_msg = f"Error in manual optimization: {str(e)}"
            _LOGGER.error(error_msg)
            raise
    
    async def get_manageable_loads(self) -> List[Dict[str, Any]]:
        """Public method to get manageable loads."""
        try:
            loads = []
            
            # Look for switch entities that might be manageable loads
            for entity_id, entity_state in self.hass.states.async_all():
                if entity_state.domain == 'switch':
                    loads.append({
                        'entity_id': entity_id,
                        'name': entity_state.attributes.get('friendly_name', entity_id),
                        'state': entity_state.state,
                        'power_consumption': entity_state.attributes.get('power_consumption', 1000),  # Watts
                        'priority': entity_state.attributes.get('priority', 1),  # 1-5, 1 being highest
                        'flexible': entity_state.attributes.get('flexible', True)
                    })
            
            return loads
            
        except Exception as e:
            _LOGGER.error("Error getting manageable loads: %s", str(e))
            return [] 