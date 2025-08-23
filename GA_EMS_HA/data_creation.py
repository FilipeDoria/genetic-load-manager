import numpy as np
import pandas as pd # type: ignore
import random
from datetime import datetime, timedelta

# Part 1: Test Data Creation Script
# This script generates mock test data for a 24-hour horizon, divided into 24 hourly slots.
# It includes electricity prices (buy and sell), PV production forecast, non-controllable loads,
# controllable devices parameters, battery parameters, and user settings.
# All data is mock but structured to mimic real Portuguese market (e.g., variable buy prices from OMIE-like, fixed sell).

def generate_test_data(time_slots=24, start_date='2025-08-19'):
    """
    Generate mock test data for EMS algorithm testing.
    
    Parameters:
    time_slots (int): Number of time slots (default 24 for hourly).
    start_date (str): Start date in YYYY-MM-DD format.
    
    Returns:
    dict: Dictionary containing all inputs.
    """
    # Time index
    start_time = datetime.strptime(start_date, '%Y-%m-%d')
    times = [start_time + timedelta(hours=i) for i in range(time_slots)]
    data: dict = {'times': times}
    
    # Electricity prices (Portuguese market mock)
    # Buy prices: Variable day-ahead, e.g., lower at night, peaks daytime (in EUR/MWh, convert to EUR/kWh)
    buy_prices = np.array([0.05 + 0.1 * np.sin(2 * np.pi * i / 24 + np.pi) + random.uniform(-0.02, 0.02) for i in range(time_slots)])  # EUR/kWh
    # Sell prices: Fixed feed-in tariff, e.g., 0.04 EUR/kWh for excess
    #sell_prices = np.full(time_slots, 0.04)  # EUR/kWh
    sell_prices = buy_prices * 0.85   # EUR/kWh
    data['buy_prices'] = buy_prices
    data['sell_prices'] = sell_prices
    
    # PV production forecast (kW per hour, assuming 5kWp system, sinusoidal day profile)
    pv_production = np.maximum(0, 5 * np.sin(2 * np.pi * (np.arange(time_slots) - 6) / 24) + np.random.uniform(-0.5, 0.5, time_slots))  # kW
    data['pv_forecast'] = pv_production
    
    # Non-controllable loads (kW per hour, mock household base load)
    non_ctrl_loads = np.array([0.5 + 0.3 * np.sin(2 * np.pi * i / 24) + random.uniform(0, 0.2) for i in range(time_slots)])  # kW
    data['non_ctrl_loads'] = non_ctrl_loads
    
    # Grid connection limits
    grid_limits = {
        'max_import_power': 6.9,  # kW
        'max_export_power': 4.0   # kW
    }
    data['grid_limits'] = grid_limits
    
    # Battery parameters
    battery = {
        'capacity': 20.0,  # kWh
        'max_charge_rate': 5.0,  # kW
        'max_discharge_rate': 5.0,  # kW
        'efficiency': 0.95,  # round-trip
        'min_soc': 0.1,  # fraction
        'max_soc': 1.0,  # fraction
        'initial_soc': 0.5  # starting SOC
    }
    data['battery'] = battery
    
    # Controllable devices: List of dicts with parameters and constraints
    devices = [
        # Water heater
        {
            'name': 'water_heater',
            'power_levels': [0, 1.6],  # kW (off, low, high)
            'min_runtime': 1,  # hours continuous if on
            'daily_energy_need': 5.0,  # kWh/day minimum
            'allowed_times': list(range(24)),  # all hours ok
            'current_state': {'temp': 45}  # e.g., current water temp
        },
        # AC
        {
            'name': 'ac',
            'power_levels': [0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0],  # kW
            'comfort_bounds': (20, 25),  # deg C
            'allowed_times': list(range(8, 22)),  # daytime only
            'current_state': {'room_temp': 24}
        },
        # EV charger
        {
            'name': 'ev_charger',
            'power_levels': [0, 1.4, 1.8, 2.3, 3.0, 3.7],  # kW
            'battery_capacity': 60.0,  # kWh
            'required_soc': 0.6,  # by end of period
            'departure_time': 8,  # hour of next day (0-23)
            'current_state': {'soc': 0.4}
        },
        # Dehumidifier
        {
            'name': 'dehumidifier',
            'power_levels': [0, 0.2],  # kW
            'humidity_target': 50,  # %
            'allowed_times': list(range(24)),
            'current_state': {'humidity': 70}
        },
        # Pump
        {
            'name': 'pump',
            'power_levels': [0, 1.0],  # kW
            'min_runtime': 2,  # hours/day
            'allowed_times': list(range(24)),
            'current_state': {}
        }
    ]
    data['devices'] = devices
    
    # User settings
    user_settings = {
        'comfort_tolerance': 2.0,  # e.g., deg C deviation allowed
        'energy_cap': None,  # daily kWh limit, None for no cap
        'priorities': {'ev_charger': 'high', 'water_heater': 'medium'}  # example
    }
    data['user_settings'] = user_settings
    
    # Convert to DataFrame for time-series data
    df = pd.DataFrame({
        'time': times,
        'buy_price': buy_prices,
        'sell_price': sell_prices,
        'pv_forecast': pv_production,
        'non_ctrl_load': non_ctrl_loads
    })
    data['df'] = df
    
    return data

# Part 2: EMS Algorithm Base (Genetic Algorithm for Scheduling)
# This is a basic implementation of a Genetic Algorithm using NumPy.
# It accounts for all inputs and constraints.
# Schedules are represented as chromosomes: a 2D array where rows are devices + battery, columns are time slots.
# For devices: power level index (int), for battery: charge/discharge power (float, negative for discharge).

class EMSOptimizer:
    def __init__(self, data):
        self.data = data
        self.time_slots = len(data['df'])
        self.devices = data['devices']
        self.num_devices = len(self.devices)
        self.battery = data['battery']
        # Chromosome length: (devices + battery charge/discharge) * time_slots
        # Battery: one value per slot (positive charge, negative discharge, 0 idle)
        self.chrom_length = (self.num_devices + 1) * self.time_slots
    
    def generate_individual(self):
        """Generate a random feasible individual (schedule)."""
        chrom = np.zeros(self.chrom_length)
        idx = 0
        for dev in self.devices:
            allowed = dev.get('allowed_times', list(range(self.time_slots)))
            for t in range(self.time_slots):
                if t in allowed:
                    chrom[idx] = random.choice(range(len(dev['power_levels'])))
                idx += 1
        
        # Battery: generate more intelligent schedule considering SOC constraints
        battery_soc = self.battery['initial_soc'] * self.battery['capacity']
        for t in range(self.time_slots):
            # Check if battery can discharge (has enough SOC)
            can_discharge = battery_soc > self.battery['min_soc'] * self.battery['capacity']
            # Check if battery can charge (has room for more SOC)
            can_charge = battery_soc < self.battery['max_soc'] * self.battery['capacity']
            
            if can_discharge and can_charge:
                # Can do both, random choice
                chrom[idx] = random.uniform(-self.battery['max_discharge_rate'], self.battery['max_charge_rate'])
            elif can_discharge:
                # Can only discharge
                chrom[idx] = random.uniform(-self.battery['max_discharge_rate'], 0)
            elif can_charge:
                # Can only charge
                chrom[idx] = random.uniform(0, self.battery['max_charge_rate'])
            else:
                # Can't do anything, stay idle
                chrom[idx] = 0
            
            # Update SOC for next time step (simplified)
            if chrom[idx] > 0:  # charging
                battery_soc = min(battery_soc + chrom[idx] * self.battery['efficiency'], 
                                self.battery['max_soc'] * self.battery['capacity'])
            elif chrom[idx] < 0:  # discharging
                battery_soc = max(battery_soc + chrom[idx] / self.battery['efficiency'], 
                                self.battery['min_soc'] * self.battery['capacity'])
            
            idx += 1
        return chrom
    
    def decode_chromosome(self, chrom):
        """Decode chromosome to power schedules."""
        schedules = {}
        idx = 0
        for i, dev in enumerate(self.devices):
            dev_sched = []
            for t in range(self.time_slots):
                level_idx = int(chrom[idx])
                power = dev['power_levels'][level_idx] if 0 <= level_idx < len(dev['power_levels']) else 0
                dev_sched.append(power)
                idx += 1
            schedules[dev['name']] = np.array(dev_sched)
        battery_sched = chrom[idx:]  # charge positive, discharge negative
        schedules['battery'] = battery_sched
        return schedules
    
    def simulate_schedule(self, schedules):
        """Simulate energy flows, costs, and check constraints."""
        pv = self.data['pv_forecast']
        non_ctrl = self.data['non_ctrl_loads']
        buy_price = self.data['buy_prices']
        sell_price = self.data['sell_prices']
        max_import = self.data['grid_limits']['max_import_power']
        max_export = self.data['grid_limits']['max_export_power']
        
        ctrl_loads = np.sum([schedules[dev['name']] for dev in self.devices], axis=0)
        total_demand = ctrl_loads + non_ctrl
        battery_action = schedules['battery']  # pos charge, neg discharge
        
        # Battery SOC simulation
        soc = np.zeros(self.time_slots + 1)
        soc[0] = self.battery['initial_soc'] * self.battery['capacity']
        charge_eff = self.battery['efficiency']
        discharge_eff = 1 / self.battery['efficiency']  # effective for discharge calc
        
        for t in range(self.time_slots):
            action = battery_action[t]
            if action > 0:  # charge
                actual_charge = min(action, self.battery['max_charge_rate'], (self.battery['capacity'] * self.battery['max_soc'] - soc[t]) / charge_eff)
                soc[t+1] = soc[t] + actual_charge * charge_eff
            elif action < 0:  # discharge
                actual_discharge = min(-action, self.battery['max_discharge_rate'], (soc[t] - self.battery['capacity'] * self.battery['min_soc']) * discharge_eff)
                soc[t+1] = soc[t] - actual_discharge / discharge_eff
            else:
                soc[t+1] = soc[t]
        
        # Energy balance (assuming hourly, energy = power * 1h)
        battery_net = -battery_action  # pos if discharge (adds to supply), neg if charge (adds to demand)
        supply = pv + np.maximum(0, battery_net)
        demand = total_demand + np.maximum(0, -battery_net)
        imported = np.minimum(np.maximum(0, demand - supply), max_import)
        exported = np.minimum(np.maximum(0, supply - demand), max_export)
        
        # Cost
        cost = np.sum(buy_price * imported - sell_price * exported)
        
        # Penalties for constraints
        penalty = 0.0
        
        # Battery constraints - much stronger penalties
        soc_violations = np.sum(np.maximum(0, self.battery['min_soc'] - soc[1:] / self.battery['capacity'])) + \
                        np.sum(np.maximum(0, soc[1:] / self.battery['capacity'] - self.battery['max_soc']))
        if soc_violations > 0:
            penalty += 10000 * soc_violations  # Much harsher penalty for SOC violations
        
        # Penalty for attempting impossible battery actions
        impossible_actions = 0
        for t in range(self.time_slots):
            action = battery_action[t]
            if action < 0 and soc[t] <= self.battery['min_soc'] * self.battery['capacity']:
                # Trying to discharge when at min SOC
                impossible_actions += abs(action)
            elif action > 0 and soc[t] >= self.battery['max_soc'] * self.battery['capacity']:
                # Trying to charge when at max SOC
                impossible_actions += action
        
        if impossible_actions > 0:
            penalty += 5000 * impossible_actions  # Penalty for impossible actions
        
        # Device-specific constraints
        for dev in self.devices:
            dev_sched = schedules[dev['name']]
            if 'daily_energy_need' in dev:
                total_energy = np.sum(dev_sched)  # kWh (assuming 1h slots)
                if total_energy < dev['daily_energy_need']:
                    penalty += 500 * (dev['daily_energy_need'] - total_energy)
            if 'min_runtime' in dev:
                on_times = np.sum(dev_sched > 0)
                if on_times < dev['min_runtime']:
                    penalty += 200 * (dev['min_runtime'] - on_times)
            # Add more, e.g., for EV SOC simulation (similar to battery)
            if dev['name'] == 'ev_charger':
                ev_soc = dev['current_state']['soc'] * dev['battery_capacity']
                for t in range(self.time_slots):
                    ev_soc += dev_sched[t] * 0.95  # assuming efficiency
                final_soc_frac = ev_soc / dev['battery_capacity']
                if final_soc_frac < dev['required_soc']:
                    penalty += 1000 * (dev['required_soc'] - final_soc_frac)
            # Comfort, etc. (mock, assume violation check)
            # For AC, dehumidifier: assume simple penalty if on when needed
        
        # User settings penalties, e.g., comfort tolerance
        # Mock: add if needed
        
        return cost + penalty, cost, penalty, soc, imported, exported
    
    def fitness(self, individual):
        """Fitness function: negative total cost + penalties (maximize fitness -> minimize cost)."""
        schedules = self.decode_chromosome(individual)
        total_cost, _, _, _, _, _ = self.simulate_schedule(schedules)
        return -total_cost  # GA maximizes, so negate
    
    # Simple GA implementation
    def run_ga(self, pop_size=50, generations=30, cx_prob=0.7, mut_prob=0.2):
        """Run genetic algorithm."""
        # Initialize population
        population = [self.generate_individual() for _ in range(pop_size)]
        
        for gen in range(generations):
            # Evaluate fitness
            fitnesses = [self.fitness(ind) for ind in population]
            
            # Selection: tournament
            selected = []
            for _ in range(pop_size):
                i1, i2 = random.sample(range(pop_size), 2)
                selected.append(population[i1] if fitnesses[i1] > fitnesses[i2] else population[i2])
            
            # Crossover
            offspring = []
            for i in range(0, pop_size, 2):
                if random.random() < cx_prob and i+1 < pop_size:
                    child1, child2 = self.crossover(selected[i], selected[i+1])
                    offspring.extend([child1, child2])
                else:
                    offspring.extend([selected[i], selected[i+1] if i+1 < pop_size else selected[i]])
            
            # Mutation
            for ind in offspring:
                if random.random() < mut_prob:
                    self.mutate(ind)
            
            population = offspring
        
        # Best individual
        best_idx = np.argmax([self.fitness(ind) for ind in population])
        best = population[best_idx]
        best_schedules = self.decode_chromosome(best)
        best_cost = -self.fitness(best)
        return best_schedules, best_cost
    
    def crossover(self, ind1, ind2):
        """Single-point crossover."""
        point = random.randint(1, self.chrom_length - 1)
        child1 = np.concatenate((ind1[:point], ind2[point:]))
        child2 = np.concatenate((ind2[:point], ind1[point:]))
        return child1, child2
    
    def mutate(self, ind):
        """Mutate: random change in one gene."""
        gene = random.randint(0, self.chrom_length - 1)
        if gene < self.num_devices * self.time_slots:
            # Device level: random new level
            dev_idx = gene // self.time_slots
            dev = self.devices[dev_idx]
            ind[gene] = random.choice(range(len(dev['power_levels'])))
        else:
            # Battery: random new action, but respect SOC constraints
            battery_idx = gene - (self.num_devices * self.time_slots)
            time_slot = battery_idx
            
            # Simulate SOC up to this time slot to check constraints
            soc = self.battery['initial_soc'] * self.battery['capacity']
            for t in range(time_slot):
                action_idx = self.num_devices * self.time_slots + t
                action = ind[action_idx]
                if action > 0:  # charging
                    soc = min(soc + action * self.battery['efficiency'], 
                             self.battery['max_soc'] * self.battery['capacity'])
                elif action < 0:  # discharging
                    soc = max(soc + action / self.battery['efficiency'], 
                             self.battery['min_soc'] * self.battery['capacity'])
            
            # Generate new action respecting current SOC
            can_discharge = soc > self.battery['min_soc'] * self.battery['capacity']
            can_charge = soc < self.battery['max_soc'] * self.battery['capacity']
            
            if can_discharge and can_charge:
                ind[gene] = random.uniform(-self.battery['max_discharge_rate'], self.battery['max_charge_rate'])
            elif can_discharge:
                ind[gene] = random.uniform(-self.battery['max_discharge_rate'], 0)
            elif can_charge:
                ind[gene] = random.uniform(0, self.battery['max_charge_rate'])
            else:
                ind[gene] = 0  # Can't do anything

# Example usage
# test_data = generate_test_data()
# optimizer = EMSOptimizer(test_data)
# best_schedules, best_cost = optimizer.run_ga()
# print("Best cost:", best_cost)
# print("Best battery schedule:", best_schedules['battery'])