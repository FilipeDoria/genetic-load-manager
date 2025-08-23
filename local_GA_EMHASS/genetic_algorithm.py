import numpy as np
import random

class GeneticAlgorithmLocal:
    def __init__(self, population_size=100, generations=200, mutation_rate=0.05, crossover_rate=0.8,
                 num_devices=2, time_slots=96, battery_capacity=10.0, max_charge_rate=2.0,
                 max_discharge_rate=2.0, binary_control=False, device_priorities=None):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.num_devices = num_devices
        self.time_slots = time_slots
        self.battery_capacity = battery_capacity
        self.max_charge_rate = max_charge_rate
        self.max_discharge_rate = max_discharge_rate
        self.binary_control = binary_control
        self.device_priorities = device_priorities or [1.0] * num_devices
        self.population = None

    def initialize_population(self):
        """Initialize population with random or binary schedules."""
        self.population = np.random.uniform(0, 1, (self.population_size, self.num_devices, self.time_slots))
        if self.binary_control:
            for i in range(self.population_size):
                self.population[i] = (self.population[i] > 0.5).astype(float)

    def fitness_function(self, chromosome, pv_forecast, load_forecast, pricing, battery_soc):
        """Evaluate fitness based on cost, solar utilization, battery health, and priorities."""
        cost = 0.0
        solar_utilization = 0.0
        battery_penalty = 0.0
        priority_penalty = 0.0
        current_soc = battery_soc / 100 * self.battery_capacity  # Convert percentage to kWh
        for t in range(self.time_slots):
            total_load = np.sum(chromosome[:, t])
            net_load = total_load + load_forecast[t] - pv_forecast[t]
            grid_energy = max(0, net_load)
            cost += grid_energy * pricing[t]
            solar_utilization += min(pv_forecast[t], total_load) / (pv_forecast[t] + 1e-6)
            battery_change = 0.0
            if net_load < 0:
                battery_change = min(-net_load, self.max_charge_rate)
            elif net_load > 0:
                battery_change = -min(net_load, self.max_discharge_rate)
            current_soc += battery_change
            if current_soc < 0 or current_soc > self.battery_capacity:
                battery_penalty += abs(current_soc - self.battery_capacity / 2) * 100
            current_soc = np.clip(current_soc, 0, self.battery_capacity)
            for d in range(self.num_devices):
                priority_penalty += (1 - chromosome[d, t]) * self.device_priorities[d]
        solar_efficiency = solar_utilization / self.time_slots
        fitness = -(0.5 * cost + 0.3 * battery_penalty + 0.1 * priority_penalty - 0.1 * solar_efficiency)
        return fitness

    def tournament_selection(self, fitness_scores, pv_forecast, load_forecast, pricing, battery_soc):
        """Select parent via tournament selection."""
        tournament_size = 5
        selection = random.sample(range(self.population_size), tournament_size)
        fitness_values = [self.fitness_function(self.population[i], pv_forecast, load_forecast, pricing, battery_soc) for i in selection]
        best_idx = selection[np.argmax(fitness_values)]
        return self.population[best_idx]

    def crossover(self, parent1, parent2):
        """Perform crossover to create two children."""
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.time_slots - 1)
            child1 = np.concatenate((parent1[:, :point], parent2[:, point:]), axis=1)
            child2 = np.concatenate((parent2[:, :point], parent1[:, point:]), axis=1)
            return child1, child2
        return parent1.copy(), parent2.copy()

    def mutate(self, chromosome, generation):
        """Mutate chromosome with adaptive mutation rate."""
        adaptive_rate = self.mutation_rate * (1 - generation / self.generations)
        mutation_mask = np.random.random(chromosome.shape) < adaptive_rate
        if self.binary_control:
            chromosome[mutation_mask] = 1 - chromosome[mutation_mask]
        else:
            chromosome[mutation_mask] = np.random.uniform(0, 1)
        return chromosome

    def optimize(self, pv_forecast, load_forecast, pricing, battery_soc):
        """Run genetic algorithm to optimize device schedules."""
        self.initialize_population()
        best_solution = None
        best_fitness = float("-inf")  # Changed to -inf for maximization
        for generation in range(self.generations):
            fitness_scores = np.array([self.fitness_function(ind, pv_forecast, load_forecast, pricing, battery_soc) for ind in self.population])
            new_population = []
            for _ in range(self.population_size // 2):
                parent1 = self.tournament_selection(fitness_scores, pv_forecast, load_forecast, pricing, battery_soc)
                parent2 = self.tournament_selection(fitness_scores, pv_forecast, load_forecast, pricing, battery_soc)
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1, generation)
                child2 = self.mutate(child2, generation)
                new_population.extend([child1, child2])
            self.population = np.array(new_population)
            max_fitness = np.max(fitness_scores)  # Use max for negative fitness
            if max_fitness > best_fitness:
                best_fitness = max_fitness
                best_solution = self.population[np.argmax(fitness_scores)].copy()
            print(f"Generation {generation}: Best fitness = {max_fitness:.2f}")
        return best_solution, best_fitness