import random
import math
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
import logging
from .const import (
    DOMAIN, CONF_OPTIMIZATION_MODE, CONF_UPDATE_INTERVAL, CONF_PV_FORECAST_TODAY,
    CONF_PV_FORECAST_TOMORROW, CONF_LOAD_FORECAST, CONF_BATTERY_SOC, CONF_GRID_EXPORT_LIMIT,
    CONF_DEMAND_RESPONSE, CONF_CARBON_INTENSITY, CONF_WEATHER, CONF_EV_CHARGER,
    CONF_SMART_THERMOSTAT, CONF_SMART_PLUG, CONF_LIGHTING, CONF_MEDIA_PLAYER,
    DEFAULT_OPTIMIZATION_MODE, DEFAULT_UPDATE_INTERVAL, DEFAULT_ENTITIES
)
from .pricing_calculator import IndexedTariffCalculator
import asyncio

_LOGGER = logging.getLogger(__name__)

class GeneticLoadOptimizer:
    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the genetic algorithm optimizer."""
        self.hass = hass
        self.config = config
        
        # Load configuration with defaults
        self.optimization_mode = config.get(CONF_OPTIMIZATION_MODE, DEFAULT_OPTIMIZATION_MODE)
        self.update_interval = config.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        
        # Entity configuration with fallbacks to defaults
        self.pv_forecast_today_entity = config.get(CONF_PV_FORECAST_TODAY, DEFAULT_ENTITIES["pv_forecast_today"])
        self.pv_forecast_tomorrow_entity = config.get(CONF_PV_FORECAST_TOMORROW, DEFAULT_ENTITIES["pv_forecast_tomorrow"])
        self.load_forecast_entity = config.get(CONF_LOAD_FORECAST, DEFAULT_ENTITIES["load_forecast"])
        self.battery_soc_entity = config.get(CONF_BATTERY_SOC, DEFAULT_ENTITIES["battery_soc"])
        self.grid_export_limit_entity = config.get(CONF_GRID_EXPORT_LIMIT, DEFAULT_ENTITIES["grid_export_limit"])
        self.demand_response_entity = config.get(CONF_DEMAND_RESPONSE, DEFAULT_ENTITIES["demand_response"])
        self.carbon_intensity_entity = config.get(CONF_CARBON_INTENSITY, DEFAULT_ENTITIES["carbon_intensity"])
        self.weather_entity = config.get(CONF_WEATHER, DEFAULT_ENTITIES["weather"])
        self.ev_charger_entity = config.get(CONF_EV_CHARGER, DEFAULT_ENTITIES["ev_charger"])
        self.smart_thermostat_entity = config.get(CONF_SMART_THERMOSTAT, DEFAULT_ENTITIES["smart_thermostat"])
        self.smart_plug_entity = config.get(CONF_SMART_PLUG, DEFAULT_ENTITIES["smart_plug"])
        self.lighting_entity = config.get(CONF_LIGHTING, DEFAULT_ENTITIES["lighting"])
        self.media_player_entity = config.get(CONF_MEDIA_PLAYER, DEFAULT_ENTITIES["media_player"])

        self.population_size = config.get("population_size", 100)
        self.generations = config.get("generations", 200)
        self.mutation_rate = config.get("mutation_rate", 0.05)
        self.crossover_rate = config.get("crossover_rate", 0.8)
        self.num_devices = config.get("num_devices", 2)
        self.time_slots = 96
        self.pv_forecast = None
        self.load_forecast = None
        self.battery_capacity = config.get("battery_capacity", 10.0)
        self.max_charge_rate = config.get("max_charge_rate", 2.0)
        self.max_discharge_rate = config.get("max_discharge_rate", 2.0)
        self.binary_control = config.get("binary_control", False)
        
        # Initialize pricing calculator
        self.pricing_calculator = IndexedTariffCalculator(hass, config)
        self.use_indexed_pricing = config.get("use_indexed_pricing", True)
        
        # Initialize optimization tracking attributes
        self.best_fitness = float("-inf")
        self.best_solution = None
        self.current_generation = 0
        self._async_unsub_track_time = None  # Track the time interval unsub function

    async def fetch_forecast_data(self):
        """Fetch and process Solcast PV, load, battery, and pricing data for a 24-hour horizon."""
        current_time = datetime.now().replace(second=0, microsecond=0)
        slot_duration = timedelta(minutes=15)
        forecast_horizon = timedelta(hours=24)
        end_time = current_time + forecast_horizon
        pv_forecast = [0.0] * self.time_slots

        # Fetch today's and tomorrow's Solcast forecasts
        pv_today_state = None
        pv_tomorrow_state = None
        
        if self.pv_forecast_today_entity:
            pv_today_state = self.hass.states.get(self.pv_forecast_today_entity)
            if not pv_today_state:
                _LOGGER.warning(f"PV forecast entity not found: {self.pv_forecast_today_entity}")
            else:
                _LOGGER.debug(f"Found PV today entity: {self.pv_forecast_today_entity}")
                _LOGGER.debug(f"PV today state: {pv_today_state.state}")
                _LOGGER.debug(f"PV today attributes: {list(pv_today_state.attributes.keys())}")
        else:
            _LOGGER.warning("No PV forecast entity configured")
            
        if self.pv_forecast_tomorrow_entity:
            pv_tomorrow_state = self.hass.states.get(self.pv_forecast_tomorrow_entity)
            if not pv_tomorrow_state:
                _LOGGER.warning(f"PV tomorrow forecast entity not found: {self.pv_forecast_tomorrow_entity}")
            else:
                _LOGGER.debug(f"Found PV tomorrow entity: {self.pv_forecast_tomorrow_entity}")
                _LOGGER.debug(f"PV tomorrow state: {pv_tomorrow_state.state}")
                _LOGGER.debug(f"PV tomorrow attributes: {list(pv_tomorrow_state.attributes.keys())}")
        else:
            _LOGGER.warning("No PV tomorrow forecast entity configured")
        
        # Try to get DetailedForecast first (30-minute intervals), fallback to DetailedHourly (1-hour intervals)
        pv_today_raw = []
        pv_tomorrow_raw = []
        
        if pv_today_state:
            pv_today_raw = pv_today_state.attributes.get("DetailedForecast", [])
            if not pv_today_raw:
                pv_today_raw = pv_today_state.attributes.get("DetailedHourly", [])
                _LOGGER.debug("Using DetailedHourly for today's forecast")
            else:
                _LOGGER.debug("Using DetailedForecast for today's forecast")
            _LOGGER.debug(f"Today's forecast data: {len(pv_today_raw)} items")
            if pv_today_raw:
                _LOGGER.debug(f"First item structure: {pv_today_raw[0]}")
                
        if pv_tomorrow_state:
            pv_tomorrow_raw = pv_tomorrow_state.attributes.get("DetailedForecast", [])
            if not pv_tomorrow_raw:
                pv_tomorrow_raw = pv_tomorrow_state.attributes.get("DetailedHourly", [])
                _LOGGER.debug("Using DetailedHourly for tomorrow's forecast")
            else:
                _LOGGER.debug("Using DetailedForecast for tomorrow's forecast")
            _LOGGER.debug(f"Tomorrow's forecast data: {len(pv_tomorrow_raw)} items")
            if pv_tomorrow_raw:
                _LOGGER.debug(f"First item structure: {pv_tomorrow_raw[0]}")

        if not pv_today_raw and not pv_tomorrow_raw:
            _LOGGER.warning("No Solcast PV forecast data available, using zeros")
            self.pv_forecast = pv_forecast
        else:
            # Combine forecasts
            times = []
            values = []
            
            for forecast in [pv_today_raw, pv_tomorrow_raw]:
                if not forecast:
                    continue
                    
                for item in forecast:
                    try:
                        # Handle both DetailedForecast and DetailedHourly structures
                        if isinstance(item, dict) and "period_start" in item and "pv_estimate" in item:
                            period_start = item["period_start"]
                            pv_estimate = item["pv_estimate"]
                            
                            # Parse the period_start string (handle timezone info)
                            if period_start.endswith('+01:00'):
                                period_start = period_start.replace('+01:00', '+01:00')
                            elif period_start.endswith('Z'):
                                period_start = period_start.replace('Z', '+00:00')
                            
                            try:
                                period_time = datetime.fromisoformat(period_start)
                                pv_value = float(pv_estimate)
                                
                                # Only include future times
                                if period_time >= current_time:
                                    times.append(period_time)
                                    values.append(pv_value)
                                    
                            except ValueError as e:
                                _LOGGER.debug(f"Could not parse time '{period_start}': {e}")
                                continue
                                
                    except (KeyError, ValueError, TypeError) as e:
                        _LOGGER.debug(f"Error parsing Solcast forecast item: {e}, item: {item}")
                        continue

            if times:
                # Sort by time to ensure chronological order
                sorted_pairs = sorted(zip(times, values), key=lambda x: x[0])
                times, values = zip(*sorted_pairs)
                times = list(times)
                values = list(values)

                _LOGGER.info(f"Successfully parsed {len(times)} PV forecast data points from {times[0]} to {times[-1]}")

                # Interpolate to 15-minute slots
                for t in range(self.time_slots):
                    slot_time = current_time + t * slot_duration
                    
                    if slot_time < times[0] or slot_time >= times[-1]:
                        pv_forecast[t] = 0.0
                        continue
                        
                    # Find bracketing times for interpolation
                    for i in range(len(times) - 1):
                        if times[i] <= slot_time < times[i + 1]:
                            # Linear interpolation
                            time_diff = (times[i + 1] - times[i]).total_seconds()
                            slot_diff = (slot_time - times[i]).total_seconds()
                            weight = slot_diff / time_diff
                            pv_forecast[t] = values[i] * (1 - weight) + values[i + 1] * weight
                            break
                            
                # Set the final forecast
                self.pv_forecast = pv_forecast
                _LOGGER.info(f"Generated PV forecast with {len(self.pv_forecast)} slots, max value: {max(pv_forecast):.3f} kW")
                
            else:
                _LOGGER.warning("No valid Solcast forecast data parsed, using zeros")
                self.pv_forecast = pv_forecast

        # Fetch load forecast
        if self.load_forecast_entity:
            load_state = self.hass.states.get(self.load_forecast_entity)
            if load_state and load_state.state not in ['unknown', 'unavailable']:
                try:
                    forecast_data = load_state.attributes.get("forecast", [0.1] * self.time_slots)
                    self.load_forecast = [float(x) for x in forecast_data]
                    if len(self.load_forecast) != self.time_slots:
                        _LOGGER.warning(f"Load forecast size mismatch: got {len(self.load_forecast)}, expected {self.time_slots}")
                        # Resize to match time slots
                        if len(self.load_forecast) < self.time_slots:
                            self.load_forecast.extend([0.1] * (self.time_slots - len(self.load_forecast)))
                        elif len(self.load_forecast) > self.time_slots:
                            self.load_forecast = self.load_forecast[:self.time_slots]
                except (ValueError, TypeError) as e:
                    _LOGGER.error(f"Error parsing load forecast data: {e}")
                    self.load_forecast = [0.1] * self.time_slots
            else:
                _LOGGER.warning(f"Load forecast entity unavailable: {self.load_forecast_entity}")
                self.load_forecast = [0.1] * self.time_slots
        else:
            _LOGGER.warning("No load forecast entity configured")
            self.load_forecast = [0.1] * self.time_slots

        # Fetch battery state and pricing
        if self.battery_soc_entity:
            battery_state = self.hass.states.get(self.battery_soc_entity)
            if battery_state and battery_state.state not in ['unknown', 'unavailable']:
                try:
                    self.battery_soc = float(battery_state.state)
                    # Validate battery SOC is within reasonable range (0-100%)
                    if not (0 <= self.battery_soc <= 100):
                        _LOGGER.warning(f"Battery SOC out of range: {self.battery_soc}%, using 50%")
                        self.battery_soc = 50.0
                except (ValueError, TypeError) as e:
                    _LOGGER.error(f"Error parsing battery SOC: {e}")
                    self.battery_soc = 50.0  # Default to 50%
            else:
                _LOGGER.warning(f"Battery SOC entity unavailable: {self.battery_soc_entity}")
                self.battery_soc = 50.0
        else:
            _LOGGER.warning("No battery SOC entity configured")
            self.battery_soc = 50.0
        
        # Use indexed pricing calculator or fallback to simple pricing
        if self.use_indexed_pricing:
            try:
                self.pricing = await self.pricing_calculator.get_24h_price_forecast(current_time)
                _LOGGER.info("Using indexed tariff pricing with 96 time slots")
            except Exception as e:
                _LOGGER.error(f"Error getting indexed pricing: {e}, falling back to simple pricing")
                self.use_indexed_pricing = False
        
        if not self.use_indexed_pricing:
            # Fallback to simple dynamic pricing entity
            pricing_state = self.hass.states.get(self.dynamic_pricing_entity)
            self.pricing = [float(x) for x in pricing_state.attributes.get("prices", [0.1] * self.time_slots)] if pricing_state else [0.1] * self.time_slots
        
        # Ensure pricing is initialized even if both methods fail
        if not hasattr(self, 'pricing') or self.pricing is None:
            _LOGGER.warning("Both indexed and dynamic pricing failed, using default pricing")
            self.pricing = [0.1] * self.time_slots  # Default 0.1 €/kWh
        self.pv_forecast = pv_forecast
        _LOGGER.debug(f"PV forecast (96 slots): {pv_forecast}")

    async def initialize_population(self):
        # Initialize population with random values
        self.population = []
        for _ in range(self.population_size):
            device_schedule = []
            for _ in range(self.num_devices):
                time_schedule = [random.uniform(0, 1) for _ in range(self.time_slots)]
                device_schedule.append(time_schedule)
            self.population.append(device_schedule)
        for i in range(self.population_size):
            for d in range(self.num_devices):
                if self.binary_control:
                    # Convert to binary (0 or 1)
                    for t in range(self.time_slots):
                        self.population[i][d][t] = 1.0 if self.population[i][d][t] > 0.5 else 0.0

    async def fitness_function(self, chromosome):
        try:
            # Validate inputs
            if self.pv_forecast is None or self.pricing is None:
                _LOGGER.warning("Missing forecast data in fitness function")
                return -1000.0  # Heavy penalty for missing data
            
            if len(self.pv_forecast) != self.time_slots or len(self.pricing) != self.time_slots:
                _LOGGER.warning(f"Forecast data size mismatch: PV={len(self.pv_forecast)}, Pricing={len(self.pricing)}, Expected={self.time_slots}")
                return -1000.0
            
            cost = 0.0
            solar_utilization = 0.0
            battery_penalty = 0.0
            priority_penalty = 0.0
            battery_soc = self.battery_soc if hasattr(self, 'battery_soc') and self.battery_soc is not None else 0.0
            
            for t in range(self.time_slots):
                total_load = sum(chromosome[d][t] for d in range(len(chromosome)))
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
                
                # Battery constraint penalty
                if battery_soc < 0 or battery_soc > self.battery_capacity:
                    battery_penalty += abs(battery_soc - self.battery_capacity / 2) * 100
                battery_soc = max(0, min(battery_soc, self.battery_capacity))
                
                # Device priority penalty
                for d in range(self.num_devices):
                    priority_penalty += (1 - chromosome[d][t]) * self.device_priorities[d]
            
            solar_efficiency = solar_utilization / self.time_slots
            fitness = -(0.5 * cost + 0.3 * battery_penalty + 0.1 * priority_penalty - 0.1 * solar_efficiency)
            
            # Ensure finite result
            if not math.isfinite(fitness):
                _LOGGER.warning("Non-finite fitness value calculated")
                return -1000.0
                
            return fitness
            
        except Exception as e:
            _LOGGER.error(f"Error in fitness function: {e}")
            return -1000.0  # Heavy penalty for errors

    async def optimize(self):
        await self.fetch_forecast_data()
        await self.initialize_population()
        
        # Run CPU-intensive optimization in executor to prevent blocking
        best_solution = await self.hass.async_add_executor_job(
            self._run_genetic_optimization
        )
        
        return best_solution

    def _run_genetic_optimization(self):
        """Run the genetic algorithm optimization in executor thread."""
        best_solution = None
        best_fitness = float("-inf")
        
        for generation in range(self.generations):
            # Calculate fitness scores synchronously in executor
            fitness_scores = [self._fitness_function_sync(ind) for ind in self.population]
            
            new_population = []
            for _ in range(self.population_size // 2):
                parent1 = self._tournament_selection_sync(fitness_scores)
                parent2 = self._tournament_selection_sync(fitness_scores)
                child1, child2 = self._crossover_sync(parent1, parent2)
                child1 = self._mutate_sync(child1, generation)
                child2 = self._mutate_sync(child2, generation)
                new_population.extend([child1, child2])
            
            self.population = new_population
            max_fitness = max(fitness_scores)
            if max_fitness > best_fitness:
                best_fitness = max_fitness
                best_solution = [row[:] for row in self.population[fitness_scores.index(max(fitness_scores))]]
                
            # Log progress every 50 generations
            if generation % 50 == 0:
                _LOGGER.debug(f"Generation {generation}: Best fitness = {best_fitness}")
        
        self.best_fitness = best_fitness
        self.best_solution = best_solution
        return best_solution

    def _fitness_function_sync(self, chromosome):
        """Synchronous version of fitness function for executor."""
        # This is the CPU-intensive calculation moved to executor thread
        cost = 0.0
        solar_utilization = 0.0
        battery_usage = 0.0
        
        for t in range(self.time_slots):
            device_consumption = sum(chromosome[d][t] for d in range(len(chromosome)))
            net_load = self.load_forecast[t] + device_consumption - self.pv_forecast[t]
            
            if hasattr(self, 'pricing') and self.pricing is not None:
                cost += net_load * self.pricing[t] / 1000.0
            else:
                cost += net_load * 0.1  # Fallback price
            
            solar_utilization += min(self.pv_forecast[t], self.load_forecast[t] + device_consumption)
            battery_usage += abs(net_load) * 0.1
        
        fitness = -(cost + battery_usage * 0.01) + solar_utilization * 0.02
        return fitness

    def _tournament_selection_sync(self, fitness_scores):
        """Synchronous tournament selection for executor."""
        tournament_size = 5
        selection = random.sample(range(self.population_size), tournament_size)
        best_idx = selection[[fitness_scores[i] for i in selection].index(max([fitness_scores[i] for i in selection]))]
        return self.population[best_idx]

    def _crossover_sync(self, parent1, parent2):
        """Synchronous crossover for executor."""
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.time_slots - 1)
            # Swap the time segments after the crossover point
            for d in range(len(parent1)):
                parent1[d][point:], parent2[d][point:] = parent2[d][point:][:], parent1[d][point:][:]
        # Deep copy the parents
        parent1_copy = [[val for val in device] for device in parent1]
        parent2_copy = [[val for val in device] for device in parent2]
        return parent1_copy, parent2_copy

    def _mutate_sync(self, chromosome, generation):
        """Synchronous mutation for executor."""
        adaptive_rate = self.mutation_rate * (1 - generation / self.generations)
        # Apply mutation to random positions
        for d in range(len(chromosome)):
            for t in range(len(chromosome[d])):
                if random.random() < adaptive_rate:
                    chromosome[d][t] = random.random()
        if self.binary_control:
            # Convert to binary (0 or 1)
            for d in range(len(chromosome)):
                for t in range(len(chromosome[d])):
                    chromosome[d][t] = 1.0 if chromosome[d][t] > 0.5 else 0.0
        return chromosome

    async def tournament_selection(self, fitness_scores):
        tournament_size = 5
        selection = random.sample(range(self.population_size), tournament_size)
        # Use pre-calculated fitness scores instead of recalculating
        tournament_fitness = [fitness_scores[i] for i in selection]
        best_idx = selection[tournament_fitness.index(max(tournament_fitness))]
        return self.population[best_idx]

    async def crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.time_slots - 1)
            # Create children by combining parent schedules
            child1 = []
            child2 = []
            for d in range(len(parent1)):
                child1_device = parent1[d][:point] + parent2[d][point:]
                child2_device = parent2[d][:point] + parent1[d][point:]
                child1.append(child1_device)
                child2.append(child2_device)
            return child1, child2
        # Deep copy the parents
        parent1_copy = [[val for val in device] for device in parent1]
        parent2_copy = [[val for val in device] for device in parent2]
        return parent1_copy, parent2_copy

    async def mutate(self, chromosome, generation):
        adaptive_rate = self.mutation_rate * (1 - generation / self.generations)
        # Apply mutation to random positions
        for d in range(len(chromosome)):
            for t in range(len(chromosome[d])):
                if random.random() < adaptive_rate:
                    if self.binary_control:
                        chromosome[d][t] = 1 - chromosome[d][t]
                    else:
                        chromosome[d][t] = random.uniform(0, 1)
        return chromosome

    async def schedule_optimization(self):
        async def periodic_optimization(now):
            try:
                _LOGGER.info("Starting periodic optimization")
                solution = await self.optimize()
                if solution is not None:
                    for d in range(self.num_devices):
                        try:
                            # Use proper Home Assistant state setting method
                            entity_id = f"switch.device_{d}_schedule"
                            state = "on" if solution[d][0] > 0.5 else "off"
                            attributes = {"schedule": solution[d].tolist() if hasattr(solution[d], 'tolist') else list(solution[d])}
                            
                            # Set state using the proper Home Assistant method
                            self.hass.states.async_set(entity_id, state, attributes)
                        except Exception as e:
                            _LOGGER.error(f"Error updating device {d} schedule: {e}")
                    _LOGGER.info("Periodic optimization completed successfully")
                else:
                    _LOGGER.warning("Optimization returned no solution")
            except Exception as e:
                _LOGGER.error(f"Error in periodic optimization: {e}")
        
        # Run initial optimization
        await periodic_optimization(datetime.now())
        
        # Schedule periodic optimizations
        self._async_unsub_track_time = async_track_time_interval(self.hass, periodic_optimization, timedelta(minutes=15))
        return self._async_unsub_track_time

    async def get_manageable_loads(self):
        """Get list of manageable loads for switch creation."""
        loads = []
        for i in range(self.num_devices):
            load_info = {
                'entity_id': f"switch.device_{i}",
                'name': f"Device {i}",
                'power_consumption': 1000,  # Default 1kW
                'priority': self.device_priorities[i] if i < len(self.device_priorities) else 1.0,
                'flexible': True
            }
            loads.append(load_info)
        return loads

    @property
    def is_running(self):
        """Check if the genetic algorithm is currently running."""
        return hasattr(self, 'population') and self.population is not None

    async def start(self):
        """Start the genetic algorithm optimizer."""
        await self.fetch_forecast_data()
        await self.initialize_population()
        return True

    async def stop(self):
        """Stop the genetic algorithm optimizer."""
        # Clean up time interval tracker
        if self._async_unsub_track_time:
            self._async_unsub_track_time()
            self._async_unsub_track_time = None
        return True

    async def run_optimization(self):
        """Run a single optimization cycle."""
        return await self.optimize()

    async def rule_based_schedule(self):
        """Generate a rule-based schedule as fallback."""
        # Ensure forecast data is available
        if not hasattr(self, 'pv_forecast') or self.pv_forecast is None:
            await self.fetch_forecast_data()
        
        # Simple rule-based scheduling based on PV forecast and pricing
        schedule = [[0.0 for _ in range(self.time_slots)] for _ in range(self.num_devices)]
        
        # Safety check for forecast data
        if hasattr(self, 'pv_forecast') and hasattr(self, 'pricing') and self.pv_forecast is not None and self.pricing is not None:
            for t in range(self.time_slots):
                # Turn on devices when PV generation is high and prices are low
                if self.pv_forecast[t] > 0.5 and self.pricing[t] < sum(self.pricing) / len(self.pricing):
                    for d in range(self.num_devices):
                        schedule[d][t] = 1.0
        
        return schedule

    def _log_event(self, level, message):
        """Log an event with the specified level."""
        if level == "INFO":
            _LOGGER.info(message)
        elif level == "WARNING":
            _LOGGER.warning(message)
        elif level == "ERROR":
            _LOGGER.error(message)
        else:
            _LOGGER.debug(message)