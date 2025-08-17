"""Genetic Algorithm implementation for Load Optimization."""
import logging
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import numpy as np

_LOGGER = logging.getLogger(__name__)

class GeneticLoadOptimizer:
    """Genetic Algorithm for optimizing load schedules."""
    
    def __init__(self, hass, config: Dict[str, Any]):
        """Initialize the genetic algorithm optimizer."""
        self.hass = hass
        self.config = config
        self.population_size = config.get('population_size', 50)
        self.generations = config.get('generations', 100)
        self.mutation_rate = config.get('mutation_rate', 0.1)
        self.crossover_rate = config.get('crossover_rate', 0.8)
        
        # Solcast integration entities
        self.pv_forecast_entity = config.get('pv_forecast_entity', 'sensor.solcast_pv_forecast_forecast_today')
        self.load_forecast_entity = config.get('load_forecast_entity', 'sensor.load_forecast')
        self.battery_soc_entity = config.get('battery_soc_entity_id', 'sensor.battery_soc')
        self.dynamic_pricing_entity = config.get('price_entity_id', 'sensor.electricity_price')
        
        # Time slots: 96 slots for 24 hours (15-minute intervals)
        self.time_slots = 96
        
        # Forecast data arrays
        self.pv_forecast = np.zeros(self.time_slots)
        self.load_forecast = np.zeros(self.time_slots)
        self.pricing = np.full(self.time_slots, 0.15)  # Default electricity price
        
        # Battery parameters
        self.battery_soc = 50.0  # Default 50% SOC
        self.battery_capacity = config.get('battery_capacity', 10.0)  # kWh
        self.max_charge_rate = config.get('max_charge_rate', 2.0)  # kW
        self.max_discharge_rate = config.get('max_discharge_rate', 2.0)  # kW
        
        # Optimization state
        self.is_running = False
        self.current_generation = 0
        self.best_fitness = 0.0
        self.best_schedule = None
        self.optimization_count = 0
        self.last_optimization = None
        self.next_optimization = None
        
        # Load management
        self.manageable_loads = []
        self.load_schedules = {}
        
        # Logging
        self.log_entries = []
        self.max_log_entries = 100
        
        # Performance optimization - data caching
        self._last_forecast_update = None
        self._forecast_cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        self._data_listener = None
        
        _LOGGER.info("Genetic Load Optimizer initialized with population_size=%d, generations=%d", 
                     self.population_size, self.generations)
        _LOGGER.info("Solcast PV forecast entity: %s", self.pv_forecast_entity)
    
    async def start(self):
        """Start the optimization service."""
        if self.is_running:
            _LOGGER.warning("Optimization service already running")
            return
        
        self.is_running = True
        self._log_event("INFO", "Genetic Load Optimizer started")
        
        # Setup state change listener for performance optimization
        await self._setup_data_listener()
        
        # Fetch initial forecast data
        await self.fetch_forecast_data()
        
        _LOGGER.info("Genetic Load Optimizer started successfully")
    
    async def stop(self):
        """Stop the optimization service."""
        self.is_running = False
        self._log_event("INFO", "Genetic Load Optimizer stopped")
        
        # Remove state change listener
        if self._data_listener:
            self._data_listener()
            self._data_listener = None
        
        _LOGGER.info("Genetic Load Optimizer stopped")
    
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
    
    async def schedule_optimization(self):
        """Schedule periodic optimization every 15 minutes."""
        async def periodic_optimization(now):
            """Run optimization and update device schedules."""
            try:
                if self.is_running:
                    solution = await self._run_optimization()
                    
                    # Update device schedule entities
                    for d in range(len(self.manageable_loads)):
                        if d < len(solution) and len(solution[d]) > 0:
                            schedule_value = "on" if solution[d][0] > 0.5 else "off"
                            entity_id = f"switch.device_{d}_schedule"
                            
                            await self.hass.states.async_set(
                                entity_id,
                                schedule_value,
                                attributes={"schedule": solution[d].tolist() if hasattr(solution[d], 'tolist') else solution[d]}
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
    
    async def fetch_forecast_data(self, force_update=False):
        """Fetch forecast data with caching and fallback handling."""
        try:
            # Check if we need to update (cache check)
            if (not force_update and 
                self._last_forecast_update and 
                datetime.now() - self._last_forecast_update < self._forecast_cache_duration):
                _LOGGER.debug("Using cached forecast data (last update: %s)", 
                            self._last_forecast_update.strftime("%H:%M:%S"))
                return
            
            _LOGGER.info("Fetching forecast data from Solcast and other sources...")
            
            # Fetch Solcast PV forecast with fallback handling
            await self._fetch_pv_forecast_with_fallback()
            
            # Fetch load forecast with fallback handling
            await self._fetch_load_forecast_with_fallback()
            
            # Fetch battery state with fallback handling
            await self._fetch_battery_state_with_fallback()
            
            # Fetch dynamic pricing with fallback handling
            await self._fetch_pricing_with_fallback()
            
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
    
    async def _fetch_pv_forecast_with_fallback(self):
        """Fetch PV forecast with comprehensive fallback handling."""
        try:
            pv_state = self.hass.states.get(self.pv_forecast_entity)
            
            if pv_state and pv_state.state != 'unavailable':
                pv_forecast_raw = pv_state.attributes.get("detailed_forecast", [])
                _LOGGER.info("Found Solcast PV forecast with %d data points", len(pv_forecast_raw))
                
                if pv_forecast_raw:
                    # Process Solcast data (30-minute intervals to 15-minute slots)
                    times = []
                    values = []
                    
                    for item in pv_forecast_raw:
                        if "period_end" in item and "pv_estimate" in item:
                            try:
                                # Parse time (handle both ISO format and other formats)
                                period_end = item["period_end"]
                                if "Z" in period_end:
                                    period_end = period_end.replace("Z", "+00:00")
                                
                                time_obj = datetime.fromisoformat(period_end)
                                times.append(time_obj)
                                
                                # Parse PV estimate (convert to kW if in watts)
                                pv_estimate = item["pv_estimate"]
                                if isinstance(pv_estimate, (int, float)):
                                    # If value is > 100, assume it's in watts and convert to kW
                                    if pv_estimate > 100:
                                        pv_estimate = pv_estimate / 1000.0
                                        _LOGGER.debug("Converted PV estimate from %s W to %.3f kW", 
                                                     item["pv_estimate"], pv_estimate)
                                    values.append(pv_estimate)
                                else:
                                    values.append(0.0)
                                    
                            except (ValueError, TypeError) as e:
                                _LOGGER.warning("Error parsing Solcast data point: %s", e)
                                continue
                    
                    if times and values:
                        # Align forecasts with current time
                        current_time = datetime.now().replace(second=0, microsecond=0)
                        slot_duration = timedelta(minutes=15)
                        
                        for t in range(self.time_slots):
                            slot_time = current_time + t * slot_duration
                            
                            # Find the closest forecast time
                            if times:
                                closest_idx = min(range(len(times)), 
                                               key=lambda i: abs(times[i] - slot_time))
                                if closest_idx < len(values):
                                    self.pv_forecast[t] = values[closest_idx]
                                else:
                                    self.pv_forecast[t] = 0.0
                            else:
                                self.pv_forecast[t] = 0.0
                        
                        _LOGGER.info("Processed PV forecast: %d slots filled, range: %.3f - %.3f kW", 
                                   np.count_nonzero(self.pv_forecast), 
                                   np.min(self.pv_forecast), 
                                   np.max(self.pv_forecast))
                    else:
                        _LOGGER.warning("No valid time/value pairs found in Solcast data, using fallback")
                        await self._use_pv_forecast_fallback()
                else:
                    _LOGGER.warning("No detailed_forecast attribute found in Solcast entity, using fallback")
                    await self._use_pv_forecast_fallback()
            else:
                _LOGGER.warning("Solcast PV forecast entity %s not available, using fallback", self.pv_forecast_entity)
                await self._use_pv_forecast_fallback()
                
        except Exception as e:
            _LOGGER.error("Error fetching PV forecast: %s, using fallback", str(e))
            await self._use_pv_forecast_fallback()
    
    async def _use_pv_forecast_fallback(self):
        """Use fallback PV forecast data when Solcast is unavailable."""
        try:
            _LOGGER.info("Using PV forecast fallback data...")
            
            # Try to get current PV state as fallback
            pv_state = self.hass.states.get(self.pv_forecast_entity)
            if pv_state and pv_state.state != 'unavailable':
                try:
                    current_pv = float(pv_state.state)
                    # If value is > 100, assume it's in watts and convert to kW
                    if current_pv > 100:
                        current_pv = current_pv / 1000.0
                    
                    # Create a simple diurnal pattern based on current time
                    current_hour = datetime.now().hour
                    if 6 <= current_hour <= 18:  # Daytime hours
                        # Create a bell curve around current time
                        for t in range(self.time_slots):
                            slot_hour = (datetime.now() + timedelta(minutes=15 * t)).hour
                            if 6 <= slot_hour <= 18:
                                # Bell curve centered at noon
                                solar_factor = np.exp(-((slot_hour - 12) ** 2) / 8)
                                self.pv_forecast[t] = current_pv * solar_factor
                            else:
                                self.pv_forecast[t] = 0.0
                    else:
                        # Night time - no solar
                        self.pv_forecast = np.zeros(self.time_slots)
                    
                    _LOGGER.info("Applied PV forecast fallback: diurnal pattern with peak %.3f kW", current_pv)
                    
                except (ValueError, TypeError):
                    _LOGGER.warning("Invalid PV state value, using zero forecast")
                    self.pv_forecast = np.zeros(self.time_slots)
            else:
                # No PV data available at all - use historical average or zero
                _LOGGER.warning("No PV data available, using zero forecast")
                self.pv_forecast = np.zeros(self.time_slots)
                
        except Exception as e:
            _LOGGER.error("Error applying PV forecast fallback: %s", str(e))
            self.pv_forecast = np.zeros(self.time_slots)
    
    async def _fetch_load_forecast_with_fallback(self):
        """Fetch load forecast with fallback handling."""
        try:
            load_state = self.hass.states.get(self.load_forecast_entity)
            if load_state and load_state.state != 'unavailable':
                load_forecast_raw = load_state.attributes.get("forecast", [])
                if load_forecast_raw and len(load_forecast_raw) >= self.time_slots:
                    self.load_forecast = np.array([float(x) for x in load_forecast_raw[:self.time_slots]])
                    _LOGGER.info("Loaded load forecast: %d slots", len(self.load_forecast))
                else:
                    _LOGGER.warning("Load forecast not available or insufficient data, using fallback")
                    await self._use_load_forecast_fallback()
            else:
                _LOGGER.warning("Load forecast entity %s not available, using fallback", self.load_forecast_entity)
                await self._use_load_forecast_fallback()
                
        except Exception as e:
            _LOGGER.error("Error fetching load forecast: %s, using fallback", str(e))
            await self._use_load_forecast_fallback()
    
    async def _use_load_forecast_fallback(self):
        """Use fallback load forecast data."""
        try:
            _LOGGER.info("Using load forecast fallback data...")
            
            # Create a simple load pattern based on typical household usage
            current_hour = datetime.now().hour
            
            for t in range(self.time_slots):
                slot_hour = (datetime.now() + timedelta(minutes=15 * t)).hour
                
                # Base load
                base_load = 0.5  # 500W base load
                
                # Morning peak (6-9 AM)
                if 6 <= slot_hour <= 9:
                    base_load += 1.0
                
                # Evening peak (6-9 PM)
                elif 18 <= slot_hour <= 21:
                    base_load += 1.5
                
                # Night time reduction (11 PM - 6 AM)
                elif 23 <= slot_hour or slot_hour <= 6:
                    base_load *= 0.3
                
                self.load_forecast[t] = base_load
            
            _LOGGER.info("Applied load forecast fallback: typical household pattern")
            
        except Exception as e:
            _LOGGER.error("Error applying load forecast fallback: %s", str(e))
            self.load_forecast = np.full(self.time_slots, 1.0)  # Default 1kW load
    
    async def _fetch_battery_state_with_fallback(self):
        """Fetch battery state with fallback handling."""
        try:
            battery_state = self.hass.states.get(self.battery_soc_entity)
            if battery_state and battery_state.state != 'unavailable':
                try:
                    self.battery_soc = float(battery_state.state)
                    _LOGGER.info("Battery SOC: %.1f%%", self.battery_soc)
                except (ValueError, TypeError):
                    _LOGGER.warning("Invalid battery SOC value: %s, using fallback", battery_state.state)
                    self.battery_soc = 50.0
            else:
                _LOGGER.warning("Battery SOC entity %s not available, using fallback", self.battery_soc_entity)
                self.battery_soc = 50.0
                
        except Exception as e:
            _LOGGER.error("Error fetching battery state: %s, using fallback", str(e))
            self.battery_soc = 50.0
    
    async def _fetch_pricing_with_fallback(self):
        """Fetch dynamic pricing with fallback handling."""
        try:
            pricing_state = self.hass.states.get(self.dynamic_pricing_entity)
            if pricing_state and pricing_state.state != 'unavailable':
                pricing_raw = pricing_state.attributes.get("prices", [])
                if pricing_raw and len(pricing_raw) >= self.time_slots:
                    self.pricing = np.array([float(x) for x in pricing_raw[:self.time_slots]])
                    _LOGGER.info("Loaded pricing data: %d slots, range: %.3f - %.3f", 
                               len(self.pricing), np.min(self.pricing), np.max(self.pricing))
                else:
                    _LOGGER.warning("Pricing data not available or insufficient data, using fallback")
                    await self._use_pricing_fallback()
            else:
                _LOGGER.warning("Pricing entity %s not available, using fallback", self.dynamic_pricing_entity)
                await self._use_pricing_fallback()
                
        except Exception as e:
            _LOGGER.error("Error fetching pricing data: %s, using fallback", str(e))
            await self._use_pricing_fallback()
    
    async def _use_pricing_fallback(self):
        """Use fallback pricing data."""
        try:
            _LOGGER.info("Using pricing fallback data...")
            
            # Create a simple time-of-use pricing pattern
            for t in range(self.time_slots):
                slot_hour = (datetime.now() + timedelta(minutes=15 * t)).hour
                
                # Base price
                base_price = 0.15  # $0.15/kWh base price
                
                # Peak hours (6-9 AM and 6-9 PM) - higher price
                if (6 <= slot_hour <= 9) or (18 <= slot_hour <= 21):
                    base_price *= 1.5  # 50% increase during peak hours
                
                # Off-peak hours (11 PM - 6 AM) - lower price
                elif 23 <= slot_hour or slot_hour <= 6:
                    base_price *= 0.7  # 30% decrease during off-peak
                
                self.pricing[t] = base_price
            
            _LOGGER.info("Applied pricing fallback: time-of-use pattern with base price $%.3f/kWh", np.mean(self.pricing))
            
        except Exception as e:
            _LOGGER.error("Error applying pricing fallback: %s", str(e))
            self.pricing = np.full(self.time_slots, 0.15)  # Default $0.15/kWh
    
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
    
    async def optimize(self):
        """Run genetic algorithm optimization with comprehensive logging."""
        try:
            _LOGGER.info("Starting genetic algorithm optimization...")
            
            # Fetch latest forecast data
            await self.fetch_forecast_data()
            
            # Initialize population
            await self.initialize_population()
            
            best_solution = None
            best_fitness = float("-inf")
            log_data = []
            
            _LOGGER.info("Running optimization for %d generations with population size %d", 
                        self.generations, self.population_size)
            
            for generation in range(self.generations):
                # Evaluate fitness for all individuals
                fitness_scores = np.array([await self.fitness_function(ind) for ind in self.population])
                max_fitness = np.max(fitness_scores)
                avg_fitness = np.mean(fitness_scores)
                
                # Log generation data
                generation_log = {
                    "generation": generation,
                    "best_fitness": float(max_fitness),
                    "avg_fitness": float(avg_fitness),
                    "min_fitness": float(np.min(fitness_scores)),
                    "std_fitness": float(np.std(fitness_scores)),
                    "timestamp": datetime.now().isoformat()
                }
                log_data.append(generation_log)
                
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
                        "avg_fitness": float(avg_fitness),
                        "convergence_progress": (generation / self.generations) * 100,
                        "log_data": log_data[-10:]  # Last 10 generations for UI
                    }
                )
                
                # Evolution logic (selection, crossover, mutation)
                await self._evolve_population(fitness_scores)
                
                # Log progress every 10 generations
                if generation % 10 == 0:
                    _LOGGER.info("Generation %d/%d: Best=%.4f, Avg=%.4f, Std=%.4f", 
                                generation, self.generations, max_fitness, avg_fitness, np.std(fitness_scores))
            
            # Final logging and analysis
            final_log = {
                "optimization_complete": True,
                "total_generations": self.generations,
                "final_best_fitness": float(best_fitness),
                "convergence_data": log_data,
                "completion_timestamp": datetime.now().isoformat()
            }
            
            # Save detailed log to file
            await self._save_optimization_log(final_log)
            
            # Update final status
            await self.hass.states.async_set(
                "sensor.genetic_algorithm_status",
                "completed",
                attributes={
                    "generation": self.generations,
                    "best_fitness": float(best_fitness),
                    "final_solution": best_solution.tolist() if best_solution is not None else None,
                    "convergence_summary": {
                        "initial_fitness": float(log_data[0]["best_fitness"]) if log_data else 0.0,
                        "final_fitness": float(best_fitness),
                        "improvement": float(best_fitness - (log_data[0]["best_fitness"] if log_data else 0.0)),
                        "convergence_rate": self._calculate_convergence_rate(log_data)
                    }
                }
            )
            
            _LOGGER.info("Optimization completed. Best fitness: %.4f", best_fitness)
            return best_solution
            
        except Exception as e:
            error_msg = f"Error in optimization: {str(e)}"
            _LOGGER.error(error_msg)
            self._log_event("ERROR", error_msg)
            
            # Update status on error
            await self.hass.states.async_set(
                "sensor.genetic_algorithm_status",
                "error",
                attributes={"error": error_msg, "timestamp": datetime.now().isoformat()}
            )
            raise
    
    async def rule_based_schedule(self):
        """Generate rule-based schedule for comparative analysis."""
        try:
            _LOGGER.info("Generating rule-based schedule...")
            
            # Get number of devices from manageable loads
            num_devices = len(self.manageable_loads) if self.manageable_loads else 2
            schedule = np.zeros((num_devices, self.time_slots))
            
            # Rule 1: Prioritize solar usage
            solar_priority_slots = []
            for t in range(self.time_slots):
                if self.pv_forecast[t] > self.load_forecast[t] * 0.5:  # Excess solar
                    solar_priority_slots.append(t)
            
            # Rule 2: Low price periods
            avg_price = np.mean(self.pricing)
            low_price_slots = [t for t in range(self.time_slots) if self.pricing[t] < avg_price * 0.8]
            
            # Rule 3: Battery optimization
            battery_priority_slots = []
            for t in range(self.time_slots):
                # Charge during low prices and excess solar
                if (self.pricing[t] < avg_price * 0.7 and 
                    self.pv_forecast[t] > 0.1 and 
                    self.battery_soc < 80.0):
                    battery_priority_slots.append(t)
                
                # Discharge during high prices and low solar
                elif (self.pricing[t] > avg_price * 1.3 and 
                      self.pv_forecast[t] < 0.1 and 
                      self.battery_soc > 20.0):
                    battery_priority_slots.append(t)
            
            # Apply rules to schedule
            for t in range(self.time_slots):
                priority_score = 0
                
                # Solar priority (highest weight)
                if t in solar_priority_slots:
                    priority_score += 3
                
                # Low price priority
                if t in low_price_slots:
                    priority_score += 2
                
                # Battery optimization priority
                if t in battery_priority_slots:
                    priority_score += 2
                
                # Time-based priority (avoid peak hours)
                hour = (t * 15) // 60  # Convert slot to hour
                if 6 <= hour <= 9 or 18 <= hour <= 21:  # Peak hours
                    priority_score -= 1
                
                # Set schedule based on priority
                if priority_score >= 3:
                    schedule[:, t] = 1.0  # High priority - turn on all devices
                elif priority_score >= 1:
                    schedule[:, t] = 0.5  # Medium priority - partial usage
                else:
                    schedule[:, t] = 0.0  # Low priority - turn off
            
            _LOGGER.info("Rule-based schedule generated with %d high-priority slots", 
                        len([t for t in range(self.time_slots) if np.any(schedule[:, t] > 0.5)]))
            
            return schedule
            
        except Exception as e:
            error_msg = f"Error generating rule-based schedule: {str(e)}"
            _LOGGER.error(error_msg)
            self._log_event("ERROR", error_msg)
            return np.zeros((2, self.time_slots))  # Return empty schedule on error
    
    async def _evolve_population(self, fitness_scores):
        """Evolve population through selection, crossover, and mutation."""
        try:
            # Selection
            new_population = []
            for _ in range(self.population_size // 2):
                parent1 = self._selection(fitness_scores)
                parent2 = self._selection(fitness_scores)
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutation
                if random.random() < self.mutation_rate:
                    self._mutate(child1)
                if random.random() < self.mutation_rate:
                    self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            # Ensure population size is maintained
            self.population = new_population[:self.population_size]
            
        except Exception as e:
            _LOGGER.error("Error in population evolution: %s", str(e))
            raise
    
    async def _save_optimization_log(self, log_data):
        """Save optimization log data to file."""
        try:
            import json
            import os
            
            # Create logs directory if it doesn't exist
            log_dir = "/config/genetic_load_manager_logs"
            os.makedirs(log_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"optimization_log_{timestamp}.json"
            filepath = os.path.join(log_dir, filename)
            
            # Save log data
            with open(filepath, "w") as f:
                json.dump(log_data, f, indent=2, default=str)
            
            _LOGGER.info("Optimization log saved to: %s", filepath)
            
            # Also save to Home Assistant entity for easy access
            await self.hass.states.async_set(
                "sensor.genetic_algorithm_log_file",
                filename,
                attributes={
                    "file_path": filepath,
                    "file_size": os.path.getsize(filepath),
                    "timestamp": datetime.now().isoformat(),
                    "log_summary": {
                        "total_generations": log_data.get("total_generations", 0),
                        "final_fitness": log_data.get("final_best_fitness", 0.0),
                        "convergence_data_points": len(log_data.get("convergence_data", []))
                    }
                }
            )
            
        except Exception as e:
            _LOGGER.error("Error saving optimization log: %s", str(e))
    
    def _calculate_convergence_rate(self, log_data):
        """Calculate convergence rate from log data."""
        try:
            if len(log_data) < 2:
                return 0.0
            
            # Calculate improvement per generation
            initial_fitness = log_data[0]["best_fitness"]
            final_fitness = log_data[-1]["best_fitness"]
            
            if initial_fitness == 0:
                return 0.0
            
            total_improvement = final_fitness - initial_fitness
            avg_improvement_per_gen = total_improvement / len(log_data)
            
            # Normalize by initial fitness
            convergence_rate = (avg_improvement_per_gen / abs(initial_fitness)) * 100
            
            return round(convergence_rate, 2)
            
        except Exception as e:
            _LOGGER.error("Error calculating convergence rate: %s", str(e))
            return 0.0
    
    async def initialize_population(self):
        """Initialize the population for optimization."""
        try:
            num_devices = len(self.manageable_loads) if self.manageable_loads else 2
            
            self.population = []
            for _ in range(self.population_size):
                individual = np.random.random((num_devices, self.time_slots))
                # Convert to binary (0 or 1) based on threshold
                individual = (individual > 0.5).astype(float)
                self.population.append(individual)
            
            _LOGGER.info("Initialized population: %d individuals, %d devices, %d time slots", 
                        self.population_size, num_devices, self.time_slots)
            
        except Exception as e:
            _LOGGER.error("Error initializing population: %s", str(e))
            raise
    
    async def fitness_function(self, individual):
        """Calculate fitness score for an individual."""
        try:
            # This is a simplified fitness function - you can enhance it based on your needs
            fitness = 0.0
            
            # Solar utilization bonus
            solar_usage = np.sum(individual * self.pv_forecast.reshape(1, -1))
            fitness += solar_usage * 10.0
            
            # Cost minimization
            total_consumption = np.sum(individual)
            total_cost = total_consumption * np.mean(self.pricing)
            fitness -= total_cost * 5.0
            
            # Battery optimization
            battery_efficiency = 0.0
            for t in range(self.time_slots):
                if self.pv_forecast[t] > 0.1:  # Solar available
                    if np.any(individual[:, t] > 0.5):  # Device on
                        battery_efficiency += 1.0
            
            fitness += battery_efficiency * 2.0
            
            return max(0.0, fitness)  # Ensure non-negative fitness
            
        except Exception as e:
            _LOGGER.error("Error in fitness function: %s", str(e))
            return 0.0
    
    async def run_optimization(self):
        """Public method to run optimization manually."""
        if not self.is_running:
            _LOGGER.warning("Optimizer not running, cannot run optimization")
            return
        
        try:
            await self._run_optimization()
            _LOGGER.info("Manual optimization completed successfully")
        except Exception as e:
            error_msg = f"Error in manual optimization: {str(e)}"
            self._log_event("ERROR", error_msg)
            _LOGGER.error(error_msg)
            raise
    
    async def _optimization_loop(self):
        """Main optimization loop that runs every 15 minutes."""
        while self.is_running:
            try:
                await self._run_optimization()
                self.optimization_count += 1
                self.last_optimization = datetime.now()
                self.next_optimization = self.last_optimization + timedelta(minutes=15)
                
                _LOGGER.info("Optimization cycle %d completed. Best fitness: %.4f", 
                             self.optimization_count, self.best_fitness)
                
                # Wait 15 minutes before next optimization
                await asyncio.sleep(15 * 60)
                
            except Exception as e:
                error_msg = f"Error in optimization loop: {str(e)}"
                self._log_event("ERROR", error_msg)
                _LOGGER.error(error_msg)
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _run_optimization(self):
        """Run a single optimization cycle."""
        try:
            # Get current system state
            system_state = await self._get_system_state()
            
            # Create initial population
            population = self._create_population()
            
            # Evolution loop
            for generation in range(self.generations):
                self.current_generation = generation
                
                # Evaluate fitness
                fitness_scores = [self._evaluate_fitness(individual, system_state) 
                                for individual in population]
                
                # Find best individual
                best_idx = fitness_scores.index(max(fitness_scores))
                if fitness_scores[best_idx] > self.best_fitness:
                    self.best_fitness = fitness_scores[best_idx]
                    self.best_schedule = population[best_idx].copy()
                    self._log_event("INFO", f"New best fitness: {self.best_fitness:.4f}")
                
                # Selection
                new_population = []
                for _ in range(self.population_size // 2):
                    parent1 = self._selection(population, fitness_scores)
                    parent2 = self._selection(population, fitness_scores)
                    
                    # Crossover
                    if random.random() < self.crossover_rate:
                        child1, child2 = self._crossover(parent1, parent2)
                    else:
                        child1, child2 = parent1.copy(), parent2.copy()
                    
                    # Mutation
                    if random.random() < self.mutation_rate:
                        self._mutate(child1)
                    if random.random() < self.mutation_rate:
                        self._mutate(child2)
                    
                    new_population.extend([child1, child2])
                
                population = new_population[:self.population_size]
                
                # Log progress every 10 generations
                if generation % 10 == 0:
                    self._log_event("DEBUG", f"Generation {generation}: Best fitness = {self.best_fitness:.4f}")
            
            # Apply best schedule
            if self.best_schedule:
                await self._apply_schedule(self.best_schedule)
                self._log_event("INFO", f"Applied schedule with fitness: {self.best_fitness:.4f}")
                
        except Exception as e:
            error_msg = f"Error in optimization: {str(e)}"
            self._log_event("ERROR", error_msg)
            _LOGGER.error(error_msg)
            raise
    
    async def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state from Home Assistant entities."""
        try:
            state = {}
            
            # Get PV production
            pv_entity = self.config.get('pv_entity_id')
            if pv_entity:
                pv_state = self.hass.states.get(pv_entity)
                state['pv_power'] = float(pv_state.state) if pv_state and pv_state.state != 'unavailable' else 0.0
            
            # Get battery SOC
            battery_entity = self.config.get('battery_soc_entity_id')
            if battery_entity:
                battery_state = self.hass.states.get(battery_entity)
                state['battery_soc'] = float(battery_state.state) if battery_state and battery_state.state != 'unavailable' else 50.0
            
            # Get electricity price
            price_entity = self.config.get('price_entity_id')
            if price_entity:
                price_state = self.hass.states.get(price_entity)
                state['electricity_price'] = float(price_state.state) if price_state and price_state.state != 'unavailable' else 0.15
            
            # Get manageable loads
            state['manageable_loads'] = await self._get_manageable_loads()
            
            return state
            
        except Exception as e:
            self._log_event("ERROR", f"Error getting system state: {str(e)}")
            raise
    
    async def _get_manageable_loads(self) -> List[Dict[str, Any]]:
        """Get list of manageable loads from Home Assistant."""
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
            self._log_event("ERROR", f"Error getting manageable loads: {str(e)}")
            return []
    
    def _create_population(self) -> List[List[int]]:
        """Create initial population of load schedules."""
        population = []
        
        for _ in range(self.population_size):
            # Each individual is a schedule for 96 time slots (15-minute intervals for 24 hours)
            individual = []
            for _ in range(96):
                # Randomly decide if load should be on (1) or off (0)
                individual.append(random.randint(0, 1))
            population.append(individual)
        
        return population
    
    def _evaluate_fitness(self, individual: List[int], system_state: Dict[str, Any]) -> float:
        """Evaluate fitness of a load schedule."""
        try:
            fitness = 0.0
            
            # Convert individual to time-based schedule
            schedule = self._individual_to_schedule(individual)
            
            # Calculate total energy consumption
            total_consumption = sum(schedule.values())
            
            # Calculate cost based on electricity price
            total_cost = total_consumption * system_state.get('electricity_price', 0.15)
            
            # Penalty for high consumption during peak hours
            peak_penalty = self._calculate_peak_penalty(schedule)
            
            # Bonus for using solar power when available
            solar_bonus = self._calculate_solar_bonus(schedule, system_state)
            
            # Fitness = minimize cost + maximize solar usage - peak penalties
            fitness = 1000.0 - total_cost + solar_bonus - peak_penalty
            
            return max(0.0, fitness)  # Ensure non-negative fitness
            
        except Exception as e:
            self._log_event("ERROR", f"Error evaluating fitness: {str(e)}")
            return 0.0
    
    def _individual_to_schedule(self, individual: List[int]) -> Dict[str, int]:
        """Convert genetic individual to time-based schedule."""
        schedule = {}
        
        for i, value in enumerate(individual):
            time_slot = i * 15  # 15-minute intervals
            schedule[time_slot] = value
        
        return schedule
    
    def _calculate_peak_penalty(self, schedule: Dict[str, int]) -> float:
        """Calculate penalty for high consumption during peak hours."""
        penalty = 0.0
        
        # Peak hours: 6-9 AM and 6-9 PM
        for time_slot, consumption in schedule.items():
            hour = (time_slot // 60) % 24
            
            if (6 <= hour <= 9) or (18 <= hour <= 21):
                if consumption > 0:
                    penalty += consumption * 0.5  # Higher penalty during peak hours
        
        return penalty
    
    def _calculate_solar_bonus(self, schedule: Dict[str, int], system_state: Dict[str, Any]) -> float:
        """Calculate bonus for using solar power when available."""
        bonus = 0.0
        
        # Solar hours: 8 AM to 6 PM
        for time_slot, consumption in schedule.items():
            hour = (time_slot // 60) % 24
            
            if 8 <= hour <= 18:
                if consumption > 0:
                    # Bonus for using power during solar hours
                    bonus += consumption * 0.3
        
        return bonus
    
    def _selection(self, population: List[List[int]], fitness_scores: List[float]) -> List[int]:
        """Tournament selection."""
        tournament_size = 3
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        
        winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
        return population[winner_idx]
    
    def _crossover(self, parent1: List[int], parent2: List[int]) -> tuple:
        """Single-point crossover."""
        crossover_point = random.randint(1, len(parent1) - 1)
        
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2
    
    def _mutate(self, individual: List[int]):
        """Random mutation."""
        for i in range(len(individual)):
            if random.random() < 0.01:  # 1% mutation rate per gene
                individual[i] = 1 - individual[i]  # Flip bit
    
    async def _apply_schedule(self, schedule: List[int]):
        """Apply the optimized schedule to Home Assistant."""
        try:
            # Convert schedule to load control actions
            load_actions = self._schedule_to_load_actions(schedule)
            
            # Apply each action
            for action in load_actions:
                await self._control_load(action['entity_id'], action['action'])
                await asyncio.sleep(0.1)  # Small delay between actions
            
            self._log_event("INFO", f"Applied schedule with {len(load_actions)} actions")
            
        except Exception as e:
            error_msg = f"Error applying schedule: {str(e)}"
            self._log_event("ERROR", error_msg)
            raise
    
    def _schedule_to_load_actions(self, schedule: List[int]) -> List[Dict[str, Any]]:
        """Convert schedule to load control actions."""
        actions = []
        
        # This is a simplified version - in practice, you'd map time slots to specific loads
        for time_slot, should_be_on in enumerate(schedule):
            if should_be_on:
                # Find a load to turn on (simplified logic)
                for load in self.manageable_loads:
                    if load.get('flexible', True):
                        actions.append({
                            'entity_id': load['entity_id'],
                            'action': 'turn_on',
                            'time_slot': time_slot
                        })
                        break
        
        return actions
    
    async def _control_load(self, entity_id: str, action: str):
        """Control a load in Home Assistant."""
        try:
            if action == 'turn_on':
                await self.hass.services.async_call('switch', 'turn_on', {'entity_id': entity_id})
            elif action == 'turn_off':
                await self.hass.services.async_call('switch', 'turn_off', {'entity_id': entity_id})
            
            self._log_event("DEBUG", f"Controlled {entity_id}: {action}")
            
        except Exception as e:
            error_msg = f"Error controlling load {entity_id}: {str(e)}"
            self._log_event("ERROR", error_msg)
            raise
    
    def _log_event(self, level: str, message: str):
        """Log an event with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        
        self.log_entries.append(log_entry)
        
        # Keep only the last max_log_entries
        if len(self.log_entries) > self.max_log_entries:
            self.log_entries = self.log_entries[-self.max_log_entries:]
        
        # Also log to Home Assistant logger
        if level == 'ERROR':
            _LOGGER.error(message)
        elif level == 'WARNING':
            _LOGGER.warning(message)
        elif level == 'INFO':
            _LOGGER.info(message)
        else:
            _LOGGER.debug(message)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current optimization status."""
        return {
            'is_running': self.is_running,
            'current_generation': self.current_generation,
            'best_fitness': self.best_fitness,
            'optimization_count': self.optimization_count,
            'last_optimization': self.last_optimization.isoformat() if self.last_optimization else None,
            'next_optimization': self.next_optimization.isoformat() if self.next_optimization else None,
            'manageable_loads_count': len(self.manageable_loads),
            'log_entries_count': len(self.log_entries)
        }
    
    def get_logs(self, level: Optional[str] = None, limit: int = 50) -> List[Dict[str, str]]:
        """Get optimization logs."""
        logs = self.log_entries
        
        if level:
            logs = [log for log in logs if log['level'] == level.upper()]
        
        return logs[-limit:] if limit > 0 else logs
    
    async def get_manageable_loads(self) -> List[Dict[str, Any]]:
        """Public method to get manageable loads."""
        try:
            return await self._get_manageable_loads()
        except Exception as e:
            self._log_event("ERROR", f"Error getting manageable loads: {str(e)}")
            return [] 