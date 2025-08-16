"""Genetic Algorithm implementation for load optimization."""
import asyncio
import logging
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import time

from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.helpers import entity_registry
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PV_ENTITY_ID,
    CONF_FORECAST_ENTITY_ID,
    CONF_BATTERY_SOC_ENTITY_ID,
    CONF_PRICE_ENTITY_ID,
    CONF_OPTIMIZATION_INTERVAL,
    CONF_POPULATION_SIZE,
    CONF_GENERATIONS,
    CONF_MUTATION_RATE,
    CONF_CROSSOVER_RATE,
    ATTR_OPTIMIZATION_STATUS,
    ATTR_LAST_OPTIMIZATION,
    ATTR_NEXT_OPTIMIZATION,
    ATTR_OPTIMIZATION_COUNT,
    ATTR_BEST_FITNESS,
    ATTR_CURRENT_SCHEDULE,
)

_LOGGER = logging.getLogger(__name__)

class GeneticLoadOptimizer:
    """Genetic Algorithm optimizer for load management."""
    
    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the optimizer."""
        self.hass = hass
        self.config = config
        self.running = False
        self.optimization_count = 0
        self.best_fitness = 0.0
        self.current_schedule = {}
        self.last_optimization = None
        self.next_optimization = None
        self.optimization_thread = None
        self.stop_event = threading.Event()
        
        # Get manageable loads from entity registry
        self.manageable_loads = self._get_manageable_loads()
        
        _LOGGER.info("Genetic Load Optimizer initialized with %d manageable loads", 
                     len(self.manageable_loads))
    
    def _get_manageable_loads(self) -> List[str]:
        """Get list of manageable load entities."""
        loads = []
        entity_reg = entity_registry.async_get(self.hass)
        
        # Look for switch and light entities that can be controlled
        for entity_id, entity in entity_reg.entities.items():
            if (entity.domain in ['switch', 'light'] and 
                entity_id not in loads and
                not entity_id.startswith('switch.genetic_load_manager')):
                loads.append(entity_id)
        
        return loads[:10]  # Limit to first 10 loads
    
    def start(self):
        """Start the optimization service."""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        self.optimization_thread = threading.Thread(target=self._optimization_loop)
        self.optimization_thread.daemon = True
        self.optimization_thread.start()
        
        _LOGGER.info("Genetic Load Optimizer started")
    
    def stop(self):
        """Stop the optimization service."""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        
        _LOGGER.info("Genetic Load Optimizer stopped")
    
    def _optimization_loop(self):
        """Main optimization loop."""
        while self.running and not self.stop_event.is_set():
            try:
                # Run optimization
                self._run_optimization()
                
                # Wait for next optimization
                interval = self.config.get(CONF_OPTIMIZATION_INTERVAL, 15)
                time.sleep(interval * 60)
                
            except Exception as e:
                _LOGGER.error("Error in optimization loop: %s", e)
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _run_optimization(self):
        """Run a single optimization cycle."""
        try:
            _LOGGER.info("Starting load optimization cycle %d", self.optimization_count + 1)
            
            # Get current system state
            system_state = self._get_system_state()
            
            # Run genetic algorithm
            schedule = self._optimize_loads(system_state)
            
            if schedule:
                # Apply the schedule
                self._apply_schedule(schedule)
                
                # Update statistics
                self.optimization_count += 1
                self.last_optimization = datetime.now()
                self.next_optimization = self.last_optimization + timedelta(
                    minutes=self.config.get(CONF_OPTIMIZATION_INTERVAL, 15)
                )
                self.current_schedule = schedule
                
                _LOGGER.info("Optimization completed successfully. Schedule applied.")
                
                # Fire event
                self.hass.bus.fire('genetic_load_manager_optimization_completed', {
                    'optimization_count': self.optimization_count,
                    'best_fitness': self.best_fitness,
                    'schedule': schedule
                })
            
        except Exception as e:
            _LOGGER.error("Error running optimization: %s", e)
    
    def _get_system_state(self) -> Dict:
        """Get current system state from Home Assistant."""
        state = {}
        
        # Get PV power
        pv_entity = self.config.get(CONF_PV_ENTITY_ID)
        if pv_entity:
            pv_state = self.hass.states.get(pv_entity)
            state['pv_power'] = float(pv_state.state) if pv_state else 0.0
        
        # Get battery SOC
        battery_entity = self.config.get(CONF_BATTERY_SOC_ENTITY_ID)
        if battery_entity:
            battery_state = self.hass.states.get(battery_entity)
            state['battery_soc'] = float(battery_state.state) if battery_state else 50.0
        
        # Get electricity price
        price_entity = self.config.get(CONF_PRICE_ENTITY_ID)
        if price_entity:
            price_state = self.hass.states.get(price_entity)
            state['price'] = float(price_state.state) if price_state else 0.15
        
        return state
    
    def _optimize_loads(self, system_state: Dict) -> Dict:
        """Run genetic algorithm optimization."""
        try:
            num_loads = len(self.manageable_loads)
            time_slots = 96  # 24 hours * 4 (15-minute intervals)
            
            # Create initial population
            population = self._create_population(num_loads, time_slots)
            
            # Evolution parameters
            population_size = self.config.get(CONF_POPULATION_SIZE, 50)
            generations = self.config.get(CONF_GENERATIONS, 100)
            mutation_rate = self.config.get(CONF_MUTATION_RATE, 0.1)
            crossover_rate = self.config.get(CONF_CROSSOVER_RATE, 0.8)
            
            best_individual = None
            best_fitness = -float('inf')
            
            # Evolution loop
            for generation in range(generations):
                # Evaluate fitness
                fitness_scores = []
                for individual in population:
                    fitness = self._evaluate_fitness(individual, num_loads, time_slots, system_state)
                    fitness_scores.append((individual, fitness))
                    
                    if fitness > best_fitness:
                        best_fitness = fitness
                        best_individual = individual.copy()
                
                # Selection
                population = self._selection(population, fitness_scores, population_size)
                
                # Crossover and mutation
                new_population = []
                for i in range(0, len(population), 2):
                    if i + 1 < len(population):
                        parent1, parent2 = population[i], population[i + 1]
                        
                        if random.random() < crossover_rate:
                            child1, child2 = self._crossover(parent1, parent2)
                        else:
                            child1, child2 = parent1.copy(), parent2.copy()
                        
                        # Mutation
                        if random.random() < mutation_rate:
                            child1 = self._mutate(child1)
                        if random.random() < mutation_rate:
                            child2 = self._mutate(child2)
                        
                        new_population.extend([child1, child2])
                    else:
                        new_population.append(population[i])
                
                population = new_population
                
                if generation % 10 == 0:
                    _LOGGER.debug("Generation %d: Best fitness = %.4f", generation, best_fitness)
            
            # Convert best individual to schedule
            if best_individual:
                self.best_fitness = best_fitness
                return self._individual_to_schedule(best_individual, num_loads, time_slots)
            
            return {}
            
        except Exception as e:
            _LOGGER.error("Error in genetic algorithm: %s", e)
            return {}
    
    def _create_population(self, num_loads: int, time_slots: int) -> List[List[int]]:
        """Create initial population."""
        population = []
        population_size = self.config.get(CONF_POPULATION_SIZE, 50)
        
        for _ in range(population_size):
            individual = []
            for _ in range(num_loads * time_slots):
                individual.append(random.randint(0, 1))
            population.append(individual)
        
        return population
    
    def _evaluate_fitness(self, individual: List[int], num_loads: int, 
                         time_slots: int, system_state: Dict) -> float:
        """Evaluate fitness of an individual."""
        try:
            pv_power = system_state.get('pv_power', 0.0)
            battery_soc = system_state.get('battery_soc', 50.0)
            price = system_state.get('price', 0.15)
            
            total_cost = 0.0
            pv_utilization = 0.0
            load_balance = 0.0
            
            for t in range(time_slots):
                time_load = sum(individual[i * time_slots + t] for i in range(num_loads))
                
                # Energy cost calculation
                if time_load > pv_power:
                    grid_energy = time_load - pv_power
                    total_cost += grid_energy * price
                
                # PV utilization
                pv_utilization += min(time_load, pv_power)
                
                # Load balance (penalize high peaks)
                load_balance -= abs(time_load - (sum(individual) / time_slots))
            
            # Normalize and combine metrics
            fitness = (pv_utilization * 0.4 - total_cost * 0.4 + load_balance * 0.2)
            
            return fitness
            
        except Exception as e:
            _LOGGER.error("Error evaluating fitness: %s", e)
            return -1000.0
    
    def _selection(self, population: List[List[int]], fitness_scores: List[Tuple], 
                  population_size: int) -> List[List[int]]:
        """Selection using tournament selection."""
        selected = []
        
        for _ in range(population_size):
            # Tournament selection
            tournament_size = 3
            tournament = random.sample(fitness_scores, tournament_size)
            winner = max(tournament, key=lambda x: x[1])
            selected.append(winner[0])
        
        return selected
    
    def _crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """Two-point crossover."""
        if len(parent1) < 2:
            return parent1.copy(), parent2.copy()
        
        point1 = random.randint(0, len(parent1) - 2)
        point2 = random.randint(point1 + 1, len(parent1) - 1)
        
        point1 = random.randint(0, len(parent1) - 2)
        point2 = random.randint(point1 + 1, len(parent1) - 1)
        
        child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
        child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]
        
        return child1, child2
    
    def _mutate(self, individual: List[int]) -> List[int]:
        """Bit-flip mutation."""
        mutated = individual.copy()
        mutation_prob = 0.05
        
        for i in range(len(mutated)):
            if random.random() < mutation_prob:
                mutated[i] = 1 - mutated[i]  # Flip bit
        
        return mutated
    
    def _individual_to_schedule(self, individual: List[int], num_loads: int, 
                               time_slots: int) -> Dict:
        """Convert individual to load schedule."""
        schedule = {}
        
        for i, load in enumerate(self.manageable_loads):
            start_idx = i * time_slots
            end_idx = start_idx + time_slots
            schedule[load] = individual[start_idx:end_idx]
        
        return schedule
    
    def _apply_schedule(self, schedule: Dict):
        """Apply the optimized schedule to Home Assistant entities."""
        try:
            for load, time_slots in schedule.items():
                # For now, just log the schedule
                # In a real implementation, you would control the entities
                _LOGGER.info("Schedule for %s: %s", load, time_slots[:8])
                
                # Here you would:
                # 1. Convert time slots to actual times
                # 2. Set load states via Home Assistant API
                # 3. Handle any errors or conflicts
            
            # Fire event
            self.hass.bus.fire('genetic_load_manager_schedule_applied', {
                'schedule': schedule,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            _LOGGER.error("Error applying schedule: %s", e)
    
    def get_status(self) -> Dict:
        """Get current optimization status."""
        return {
            ATTR_OPTIMIZATION_STATUS: "running" if self.running else "stopped",
            ATTR_LAST_OPTIMIZATION: self.last_optimization.isoformat() if self.last_optimization else None,
            ATTR_NEXT_OPTIMIZATION: self.next_optimization.isoformat() if self.next_optimization else None,
            ATTR_OPTIMIZATION_COUNT: self.optimization_count,
            ATTR_BEST_FITNESS: self.best_fitness,
            ATTR_CURRENT_SCHEDULE: self.current_schedule,
        } 