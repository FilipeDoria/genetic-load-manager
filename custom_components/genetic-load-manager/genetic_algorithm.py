import numpy as np
import random
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
import logging

_LOGGER = logging.getLogger(__name__)

class GeneticAlgorithm:
    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.population_size = config.get("population_size", 100)
        self.generations = config.get("generations", 200)
        self.mutation_rate = config.get("mutation_rate", 0.05)
        self.crossover_rate = config.get("crossover_rate", 0.8)
        self.num_devices = config.get("num_devices", 2)
        self.time_slots = 96
        self.pv_forecast_entity = config.get("pv_forecast_entity")
        self.pv_forecast_tomorrow_entity = config.get("pv_forecast_tomorrow_entity")
        self.load_forecast_entity = config.get("load_forecast_entity")
        self.battery_soc_entity = config.get("battery_soc_entity")
        self.dynamic_pricing_entity = config.get("dynamic_pricing_entity")
        self.device_priorities = config.get("device_priorities", [1.0] * self.num_devices)
        self.population = None
        self.pv_forecast = None
        self.load_forecast = None
        self.battery_capacity = config.get("battery_capacity", 10.0)
        self.max_charge_rate = config.get("max_charge_rate", 2.0)
        self.max_discharge_rate = config.get("max_discharge_rate", 2.0)

    async def fetch_forecast_data(self):
        """Fetch and process Solcast PV, load, battery, and pricing data for a 24-hour horizon."""
        current_time = datetime.now().replace(second=0, microsecond=0)
        slot_duration = timedelta(minutes=15)
        forecast_horizon = timedelta(hours=24)
        end_time = current_time + forecast_horizon
        pv_forecast = np.zeros(self.time_slots)

        # Fetch today's and tomorrow's Solcast forecasts
        pv_today_state = await self.hass.states.async_get(self.pv_forecast_entity)
        pv_tomorrow_state = await self.hass.states.async_get(self.pv_forecast_tomorrow_entity)
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
            else:
                _LOGGER.warning("No valid Solcast forecast data parsed, using zeros")
                self.pv_forecast = pv_forecast
                return

        # Fetch load forecast
        load_state = await self.hass.states.async_get(self.load_forecast_entity)
        self.load_forecast = np.array([float(x) for x in load_state.attributes.get("forecast", [0.1] * self.time_slots)] if load_state else [0.1] * self.time_slots)

        # Fetch battery state and pricing
        battery_state = await self.hass.states.async_get(self.battery_soc_entity)
        pricing_state = await self.hass.states.async_get(self.dynamic_pricing_entity)
        self.battery_soc = float(battery_state.state) if battery_state else 0.0
        self.pricing = np.array([float(x) for x in pricing_state.attributes.get("prices", [0.1] * self.time_slots)] if pricing_state else [0.1] * self.time_slots)
        self.pv_forecast = pv_forecast
        _LOGGER.debug(f"PV forecast (96 slots): {pv_forecast.tolist()}")

    async def initialize_population(self):
        self.population = np.random.uniform(0, 1, (self.population_size, self.num_devices, self.time_slots))
        for i in range(self.population_size):
            for d in range(self.num_devices):
                if config.get("binary_control", False):
                    self.population[i, d, :] = (self.population[i, d, :] > 0.5).astype(float)

    async def fitness_function(self, chromosome):
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
            battery_change = 0
            if net_load < 0:
                battery_change = min(-net_load, self.max_charge_rate)
            elif net_load > 0:
                battery_change = -min(net_load, self.max_discharge_rate)
            battery_soc += battery_change
            if battery_soc < 0 or battery_soc > self.battery_capacity:
                battery_penalty += abs(battery_soc - self.battery_capacity / 2) * 100
            battery_soc = np.clip(battery_soc, 0, self.battery_capacity)
            for d in range(self.num_devices):
                priority_penalty += (1 - chromosome[d, t]) * self.device_priorities[d]
        solar_efficiency = solar_utilization / self.time_slots
        fitness = -(0.5 * cost + 0.3 * battery_penalty + 0.1 * priority_penalty - 0.1 * solar_efficiency)
        return fitness

    async def tournament_selection(self, fitness_scores):
        tournament_size = 5
        selection = random.sample(range(self.population_size), tournament_size)
        best_idx = selection[np.argmax([await self.fitness_function(self.population[i]) for i in selection])]
        return self.population[best_idx]

    async def crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.time_slots - 1)
            child1 = np.concatenate((parent1[:, :point], parent2[:, point:]), axis=1)
            child2 = np.concatenate((parent2[:, :point], parent1[:, point:]), axis=1)
            return child1, child2
        return parent1.copy(), parent2.copy()

    async def mutate(self, chromosome, generation):
        adaptive_rate = self.mutation_rate * (1 - generation / self.generations)
        mutation_mask = np.random.random(chromosome.shape) < adaptive_rate
        if config.get("binary_control", False):
            chromosome[mutation_mask] = 1 - chromosome[mutation_mask]
        else:
            chromosome[mutation_mask] = np.random.uniform(0, 1)
        return chromosome

    async def optimize(self):
        await self.fetch_forecast_data()
        await self.initialize_population()
        best_solution = None
        best_fitness = float("-inf")
        for generation in range(self.generations):
            fitness_scores = np.array([await self.fitness_function(ind) for ind in self.population])
            new_population = []
            for _ in range(self.population_size // 2):
                parent1 = await self.tournament_selection(fitness_scores)
                parent2 = await self.tournament_selection(fitness_scores)
                child1, child2 = await self.crossover(parent1, parent2)
                child1 = await self.mutate(child1, generation)
                child2 = await self.mutate(child2, generation)
                new_population.extend([child1, child2])
            self.population = np.array(new_population)
            max_fitness = np.max(fitness_scores)
            if max_fitness > best_fitness:
                best_fitness = max_fitness
                best_solution = self.population[np.argmax(fitness_scores)].copy()
            await self.hass.states.async_set(
                "sensor.genetic_algorithm_status",
                "running",
                attributes={"generation": generation, "best_fitness": max_fitness}
            )
        return best_solution

    async def schedule_optimization(self):
        async def periodic_optimization(now):
            solution = await self.optimize()
            for d in range(self.num_devices):
                await self.hass.states.async_set(
                    f"switch.device_{d}_schedule",
                    "on" if solution[d][0] > 0.5 else "off",
                    attributes={"schedule": solution[d].tolist()}
                )
        await periodic_optimization(datetime.now())
        async_remove_tracker = async_track_time_interval(self.hass, periodic_optimization, timedelta(minutes=15))
        self.hass.data[DOMAIN]["async_remove_tracker"] = async_remove_tracker
        return async_remove_tracker