#!/usr/bin/env python3
"""
GA Load Manager HA Add-on
Intelligent load management using genetic algorithms for Home Assistant
"""

import os
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random

import math
import random
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from deap import base, creator, tools, algorithms

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configuration
CONFIG_FILE = '/data/options.json'
DEFAULT_CONFIG = {
    'pv_entity_id': 'sensor.pv_power',
    'forecast_entity_id': 'sensor.pv_forecast',
    'battery_soc_entity_id': 'sensor.battery_soc',
    'price_entity_id': 'sensor.electricity_price',
    'optimization_interval': 15,
    'genetic_algorithm': {
        'population_size': 50,
        'generations': 100,
        'mutation_rate': 0.1,
        'crossover_rate': 0.8
    }
}

# Home Assistant configuration
HA_URL = os.environ.get('SUPERVISOR_URL', 'http://supervisor')
HA_TOKEN = os.environ.get('SUPERVISOR_TOKEN')

# Pure Python mathematical functions to replace numpy/scipy
def mean(values):
    """Calculate mean of a list of values"""
    if not values:
        return 0
    return sum(values) / len(values)

def std(values):
    """Calculate standard deviation of a list of values"""
    if not values:
        return 0
    avg = mean(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    return math.sqrt(variance)

def min_max_normalize(values, target_min=0, target_max=1):
    """Normalize values to a target range"""
    if not values:
        return []
    data_min = min(values)
    data_max = max(values)
    if data_max == data_min:
        return [target_min] * len(values)
    return [target_min + (x - data_min) * (target_max - target_min) / (data_max - data_min) for x in values]

# Global variables
config = DEFAULT_CONFIG.copy()
scheduler = BackgroundScheduler()
load_schedule = {}
optimization_logs = []
manageable_loads = []

class LoadManager:
    """Manages load optimization using genetic algorithms"""
    
    def __init__(self):
        self.config = config
        self.ha_session = requests.Session()
        if HA_TOKEN:
            self.ha_session.headers.update({'Authorization': f'Bearer {HA_TOKEN}'})
    
    def get_entity_state(self, entity_id: str) -> Optional[float]:
        """Get current state of a Home Assistant entity"""
        try:
            response = self.ha_session.get(f'{HA_URL}/core/api/states/{entity_id}')
            if response.status_code == 200:
                data = response.json()
                return float(data['state'])
        except Exception as e:
            logger.error(f"Error getting entity {entity_id}: {e}")
        return None
    
    def get_forecast_data(self, entity_id: str, hours: int = 24) -> List[float]:
        """Get forecast data for the next N hours"""
        try:
            # This would need to be implemented based on your forecast entity structure
            # For now, returning a simple prediction using pure Python math
            current_value = self.get_entity_state(entity_id) or 0
            return [current_value * (1 + 0.1 * math.sin(i * math.pi / 12)) for i in range(hours * 4)]
        except Exception as e:
            logger.error(f"Error getting forecast for {entity_id}: {e}")
            return [0] * (hours * 4)
    
    def create_individual(self, num_loads: int, time_slots: int) -> List[int]:
        """Create a random individual for genetic algorithm"""
        return [random.randint(0, 1) for _ in range(num_loads * time_slots)]
    
    def evaluate_fitness(self, individual: List[int], num_loads: int, time_slots: int) -> float:
        """Evaluate fitness of an individual (load schedule)"""
        try:
            # Get current system state
            pv_power = self.get_entity_state(self.config['pv_entity_id']) or 0
            battery_soc = self.get_entity_state(self.config['battery_soc_entity_id']) or 50
            price = self.get_entity_state(self.config['price_entity_id']) or 0.15
            
            # Calculate fitness based on:
            # 1. Energy cost minimization
            # 2. PV utilization maximization
            # 3. Battery efficiency
            # 4. Load balancing
            
            total_cost = 0
            pv_utilization = 0
            load_balance = 0
            
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
            logger.error(f"Error evaluating fitness: {e}")
            return -1000.0
    
    def optimize_loads(self, loads: List[str]) -> Dict[str, List[int]]:
        """Optimize load schedule using genetic algorithm"""
        try:
            num_loads = len(loads)
            time_slots = 96  # 24 hours * 4 (15-minute intervals)
            
            # Genetic algorithm setup
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMax)
            
            toolbox = base.Toolbox()
            toolbox.register("individual", tools.initIterate, creator.Individual, 
                           lambda: self.create_individual(num_loads, time_slots))
            toolbox.register("population", tools.initRepeat, list, toolbox.individual)
            toolbox.register("evaluate", self.evaluate_fitness, num_loads, time_slots)
            toolbox.register("mate", tools.cxTwoPoint)
            toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
            toolbox.register("select", tools.selTournament, tournsize=3)
            
            # Create population
            pop = toolbox.population(n=self.config['genetic_algorithm']['population_size'])
            
            # Statistics using pure Python functions
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("avg", mean)
            stats.register("std", std)
            stats.register("min", min)
            stats.register("max", max)
            
            # Evolution
            best_individual = None
            best_fitness = -float('inf')
            
            for gen in range(self.config['genetic_algorithm']['generations']):
                # Select and clone the next generation individuals
                offspring = map(toolbox.clone, toolbox.select(pop, len(pop)))
                offspring = list(offspring)
                
                # Apply crossover and mutation
                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < self.config['genetic_algorithm']['crossover_rate']:
                        toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values
                
                for mutant in offspring:
                    if random.random() < self.config['genetic_algorithm']['mutation_rate']:
                        toolbox.mutate(mutant)
                        del mutant.fitness.values
                
                # Evaluate the individuals with an invalid fitness
                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = map(toolbox.evaluate, invalid_ind)
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = (fit,)
                
                # Replace population
                pop[:] = offspring
                
                # Track best individual
                for ind in pop:
                    if ind.fitness.values[0] > best_fitness:
                        best_fitness = ind.fitness.values[0]
                        best_individual = toolbox.clone(ind)
                
                # Log progress
                if gen % 10 == 0:
                    logger.info(f"Generation {gen}: Best fitness = {best_fitness}")
            
            # Convert best individual to schedule
            if best_individual:
                schedule = {}
                for i, load in enumerate(loads):
                    schedule[load] = best_individual[i * time_slots:(i + 1) * time_slots]
                
                return schedule
            
            return {}
            
        except Exception as e:
            logger.error(f"Error in load optimization: {e}")
            return {}
    
    def apply_schedule(self, schedule: Dict[str, List[int]]):
        """Apply the optimized schedule to Home Assistant entities"""
        try:
            for load, time_slots in schedule.items():
                # This would need to be implemented based on your load control entities
                # For now, just logging the schedule
                logger.info(f"Schedule for {load}: {time_slots[:8]}...")  # Show first 2 hours
                
                # Here you would:
                # 1. Convert time slots to actual times
                # 2. Set load states via Home Assistant API
                # 3. Handle any errors or conflicts
                
        except Exception as e:
            logger.error(f"Error applying schedule: {e}")

# Global load manager instance
load_manager = LoadManager()

def load_config():
    """Load configuration from file"""
    global config
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config.update(json.load(f))
                logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")

def save_config():
    """Save configuration to file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved successfully")
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")

def run_optimization():
    """Run the load optimization process"""
    try:
        logger.info("Starting load optimization...")
        
        # Get manageable loads (this would be configured via UI)
        loads = manageable_loads if manageable_loads else ['switch.load1', 'switch.load2']
        
        # Run optimization
        schedule = load_manager.optimize_loads(loads)
        
        if schedule:
            # Apply schedule
            load_manager.apply_schedule(schedule)
            
            # Store schedule
            global load_schedule
            load_schedule = schedule
            
            # Log optimization
            optimization_logs.append({
                'timestamp': datetime.now().isoformat(),
                'loads': loads,
                'schedule': schedule,
                'status': 'success'
            })
            
            logger.info("Load optimization completed successfully")
        else:
            logger.warning("Load optimization failed - no valid schedule generated")
            
    except Exception as e:
        logger.error(f"Error in optimization process: {e}")
        optimization_logs.append({
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'status': 'error'
        })

def start_scheduler():
    """Start the background scheduler"""
    try:
        scheduler.add_job(
            func=run_optimization,
            trigger='interval',
            minutes=config['optimization_interval'],
            id='load_optimization'
        )
        scheduler.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")

# Flask routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         config=config, 
                         manageable_loads=manageable_loads,
                         load_schedule=load_schedule)

@app.route('/config', methods=['GET', 'POST'])
def configuration():
    """Configuration page"""
    global config
    
    if request.method == 'POST':
        try:
            # Update configuration
            config.update({
                'pv_entity_id': request.form['pv_entity_id'],
                'forecast_entity_id': request.form['forecast_entity_id'],
                'battery_soc_entity_id': request.form['battery_soc_id'],
                'price_entity_id': request.form['price_entity_id'],
                'optimization_interval': int(request.form['optimization_interval']),
                'genetic_algorithm': {
                    'population_size': int(request.form['population_size']),
                    'generations': int(request.form['generations']),
                    'mutation_rate': float(request.form['mutation_rate']),
                    'crossover_rate': float(request.form['crossover_rate'])
                }
            })
            
            save_config()
            
            # Restart scheduler with new interval
            scheduler.remove_job('load_optimization')
            start_scheduler()
            
            return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return jsonify({'error': str(e)}), 400
    
    return render_template('config.html', config=config)

@app.route('/loads', methods=['GET', 'POST'])
def manage_loads():
    """Manage loads page"""
    global manageable_loads
    
    if request.method == 'POST':
        try:
            loads = request.form.getlist('loads')
            manageable_loads = loads
            logger.info(f"Updated manageable loads: {loads}")
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error updating loads: {e}")
            return jsonify({'error': str(e)}), 400
    
    return render_template('loads.html', manageable_loads=manageable_loads)

@app.route('/logs')
def view_logs():
    """View logs page"""
    return render_template('logs.html', logs=optimization_logs)

@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    """API endpoint to trigger optimization"""
    try:
        run_optimization()
        return jsonify({'status': 'success', 'message': 'Optimization started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Templates
@app.route('/templates/<template_name>')
def get_template(template_name):
    """Serve HTML templates"""
    templates = {
        'index.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>GA Load Manager</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#"><i class="fas fa-bolt"></i> GA Load Manager</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/config">Configuration</a>
                <a class="nav-link" href="/loads">Manage Loads</a>
                <a class="nav-link" href="/logs">Logs</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-cog"></i> System Status</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>PV Power:</strong> <span id="pv-power">Loading...</span></p>
                        <p><strong>Battery SOC:</strong> <span id="battery-soc">Loading...</span></p>
                        <p><strong>Electricity Price:</strong> <span id="price">Loading...</span></p>
                        <p><strong>Next Optimization:</strong> <span id="next-opt">Loading...</span></p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> Manageable Loads</h5>
                    </div>
                    <div class="card-body">
                        <ul id="loads-list">
                            {% for load in manageable_loads %}
                            <li>{{ load }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-calendar"></i> Current Schedule</h5>
                        <button class="btn btn-primary btn-sm" onclick="triggerOptimization()">
                            <i class="fas fa-sync"></i> Run Optimization
                        </button>
                    </div>
                    <div class="card-body">
                        <div id="schedule-display">
                            {% if load_schedule %}
                                <pre>{{ load_schedule | tojson(indent=2) }}</pre>
                            {% else %}
                                <p>No schedule available. Run optimization to generate one.</p>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function updateStatus() {
            // This would make API calls to get real-time status
            document.getElementById('pv-power').textContent = '2.5 kW';
            document.getElementById('battery-soc').textContent = '75%';
            document.getElementById('price').textContent = '€0.15/kWh';
            document.getElementById('next-opt').textContent = '15 minutes';
        }
        
        function triggerOptimization() {
            fetch('/api/optimize', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Optimization started successfully!');
                        location.reload();
                    } else {
                        alert('Error: ' + data.message);
                    }
                });
        }
        
        // Update status every 30 seconds
        setInterval(updateStatus, 30000);
        updateStatus();
    </script>
</body>
</html>
        ''',
        'config.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Configuration - GA Load Manager</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-bolt"></i> GA Load Manager</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link active" href="/config">Configuration</a>
                <a class="nav-link" href="/loads">Manage Loads</a>
                <a class="nav-link" href="/logs">Logs</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-cog"></i> Configuration</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <h6>Entity IDs</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">PV Power Entity</label>
                                <input type="text" class="form-control" name="pv_entity_id" 
                                       value="{{ config.pv_entity_id }}" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Forecast Entity</label>
                                <input type="text" class="form-control" name="forecast_entity_id" 
                                       value="{{ config.forecast_entity_id }}" required>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Battery SOC Entity</label>
                                <input type="text" class="form-control" name="battery_soc_id" 
                                       value="{{ config.battery_soc_entity_id }}" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Price Entity</label>
                                <input type="text" class="form-control" name="price_entity_id" 
                                       value="{{ config.price_entity_id }}" required>
                            </div>
                        </div>
                    </div>
                    
                    <h6>Optimization Settings</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Optimization Interval (minutes)</label>
                                <input type="number" class="form-control" name="optimization_interval" 
                                       value="{{ config.optimization_interval }}" min="5" max="60" required>
                            </div>
                        </div>
                    </div>
                    
                    <h6>Genetic Algorithm Parameters</h6>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Population Size</label>
                                <input type="number" class="form-control" name="population_size" 
                                       value="{{ config.genetic_algorithm.population_size }}" min="10" max="200" required>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Generations</label>
                                <input type="number" class="form-control" name="generations" 
                                       value="{{ config.genetic_algorithm.generations }}" min="10" max="500" required>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Mutation Rate</label>
                                <input type="number" class="form-control" name="mutation_rate" 
                                       value="{{ config.genetic_algorithm.mutation_rate }}" min="0.01" max="0.5" step="0.01" required>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="mb-3">
                                <label class="form-label">Crossover Rate</label>
                                <input type="number" class="form-control" name="crossover_rate" 
                                       value="{{ config.genetic_algorithm.crossover_rate }}" min="0.1" max="1.0" step="0.1" required>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <button type="submit" class="btn btn-primary">Save Configuration</button>
                        <a href="/" class="btn btn-secondary">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
        ''',
        'loads.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Manage Loads - GA Load Manager</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-bolt"></i> GA Load Manager</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/config">Configuration</a>
                <a class="nav-link active" href="/loads">Manage Loads</a>
                <a class="nav-link" href="/logs">Logs</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-list"></i> Manage Loads</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <p class="text-muted">Select which loads should be managed by the genetic algorithm:</p>
                    
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="loads" value="switch.load1" 
                                   {% if 'switch.load1' in manageable_loads %}checked{% endif %}>
                            <label class="form-check-label">Load 1 (Kitchen)</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="loads" value="switch.load2" 
                                   {% if 'switch.load2' in manageable_loads %}checked{% endif %}>
                            <label class="form-check-label">Load 2 (Living Room)</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="loads" value="switch.load3" 
                                   {% if 'switch.load3' in manageable_loads %}checked{% endif %}>
                            <label class="form-check-label">Load 3 (Bedroom)</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="loads" value="switch.load4" 
                                   {% if 'switch.load4' in manageable_loads %}checked{% endif %}>
                            <label class="form-check-label">Load 4 (Office)</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="loads" value="switch.load5" 
                                   {% if 'switch.load5' in manageable_loads %}checked{% endif %}>
                            <label class="form-check-label">Load 5 (Garage)</label>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <button type="submit" class="btn btn-primary">Save Loads</button>
                        <a href="/" class="btn btn-secondary">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
        ''',
        'logs.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Logs - GA Load Manager</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-bolt"></i> GA Load Manager</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/config">Configuration</a>
                <a class="nav-link" href="/loads">Manage Loads</a>
                <a class="nav-link active" href="/logs">Logs</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-file-alt"></i> Optimization Logs</h5>
            </div>
            <div class="card-body">
                {% if logs %}
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Status</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for log in logs[-20:] %}
                                <tr>
                                    <td>{{ log.timestamp }}</td>
                                    <td>
                                        {% if log.status == 'success' %}
                                            <span class="badge bg-success">Success</span>
                                        {% elif log.status == 'error' %}
                                            <span class="badge bg-danger">Error</span>
                                        {% else %}
                                            <span class="badge bg-secondary">{{ log.status }}</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if log.status == 'success' %}
                                            <small>Optimized {{ log.loads | length }} loads</small>
                                        {% elif log.status == 'error' %}
                                            <small class="text-danger">{{ log.error }}</small>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="text-muted">No logs available yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
        '''
    }
    
    if template_name in templates:
        return templates[template_name]
    else:
        return "Template not found", 404

def main():
    """Main application entry point"""
    try:
        # Load configuration
        load_config()
        
        # Start scheduler
        start_scheduler()
        
        # Run initial optimization
        run_optimization()
        
        # Start Flask app
        app.run(host='0.0.0.0', port=8123, debug=False)
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        if scheduler.running:
            scheduler.shutdown()

if __name__ == '__main__':
    main() 