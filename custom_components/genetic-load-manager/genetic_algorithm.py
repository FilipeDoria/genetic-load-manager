"""Genetic Algorithm implementation for Load Optimization."""
import logging
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio

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
        
        _LOGGER.info("Genetic Load Optimizer initialized with population_size=%d, generations=%d", 
                     self.population_size, self.generations)
    
    async def start(self):
        """Start the optimization service."""
        if self.is_running:
            _LOGGER.warning("Optimization service already running")
            return
        
        self.is_running = True
        self._log_event("INFO", "Genetic Load Optimizer started")
        
        # Start the optimization loop
        asyncio.create_task(self._optimization_loop())
        
        _LOGGER.info("Genetic Load Optimizer started successfully")
    
    async def stop(self):
        """Stop the optimization service."""
        self.is_running = False
        self._log_event("INFO", "Genetic Load Optimizer stopped")
        _LOGGER.info("Genetic Load Optimizer stopped")
    
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
                if entity_state.domain == 'switch' and 'load' in entity_id.lower():
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