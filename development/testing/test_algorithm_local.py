#!/usr/bin/env python3
"""
Local Testing Script for Genetic Load Manager Algorithm
Tests the genetic algorithm without requiring Home Assistant
"""

import sys
import os
import asyncio
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import time

# Add the custom_components to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'custom_components'))

try:
    from genetic_load_manager.genetic_algorithm import GeneticLoadOptimizer
    from genetic_load_manager.pricing_calculator import IndexedTariffCalculator
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the development/testing directory")
    sys.exit(1)

class MockHomeAssistant:
    """Mock Home Assistant environment for local testing"""
    
    def __init__(self):
        self.states = {}
        self.data = {}
        
    def states_get(self, entity_id):
        """Mock states.get method"""
        return self.states.get(entity_id, MockState(entity_id, "unknown"))
    
    async def states_async_set(self, entity_id, state, attributes=None):
        """Mock async_set method"""
        self.states[entity_id] = MockState(entity_id, state, attributes or {})
        print(f"📊 Set {entity_id} = {state}")
        return True
    
    async def async_add_executor_job(self, func, *args):
        """Mock executor job method"""
        return func(*args)

class MockState:
    """Mock Home Assistant state object"""
    
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.attributes = attributes or {}

class MockPricingCalculator:
    """Mock pricing calculator for local testing"""
    
    def __init__(self, hass, config):
        self.hass = hass
        self.config = config
    
    async def get_24h_price_forecast(self, current_time):
        """Generate mock 24-hour pricing data"""
        # Simulate realistic electricity pricing (higher during day, lower at night)
        hours = np.arange(24)
        base_price = 0.15  # Base price in €/kWh
        
        # Add time-of-use variation
        time_variation = 0.05 * np.sin(2 * np.pi * (hours - 6) / 24)  # Peak around 6-18h
        # Add some randomness
        random_variation = 0.02 * np.random.random(24)
        
        prices = base_price + time_variation + random_variation
        # Ensure prices are positive
        prices = np.maximum(prices, 0.05)
        
        # Convert to 96 time slots (15-minute intervals)
        slot_prices = []
        for hour in range(24):
            for quarter in range(4):
                slot_prices.append(prices[hour])
        
        return np.array(slot_prices)

def create_mock_data():
    """Create realistic mock data for testing"""
    
    # Mock PV forecast data (96 slots = 24 hours * 4 quarters)
    pv_forecast = np.zeros(96)
    
    # Simulate solar production (peak around noon, zero at night)
    for i in range(96):
        hour = i // 4  # Convert slot to hour
        if 6 <= hour <= 18:  # Daylight hours
            # Bell curve for solar production
            solar_peak = 5.0  # 5 kW peak
            peak_hour = 12
            pv_forecast[i] = solar_peak * np.exp(-0.5 * ((hour - peak_hour) / 3) ** 2)
            # Add some randomness
            pv_forecast[i] *= (0.8 + 0.4 * np.random.random())
    
    # Mock load forecast (higher in morning and evening)
    load_forecast = np.ones(96) * 1.0  # Base load 1 kW
    for i in range(96):
        hour = i // 4
        if 7 <= hour <= 9:  # Morning peak
            load_forecast[i] = 2.5 + 0.5 * np.random.random()
        elif 18 <= hour <= 21:  # Evening peak
            load_forecast[i] = 3.0 + 0.5 * np.random.random()
        else:
            load_forecast[i] = 1.0 + 0.3 * np.random.random()
    
    return pv_forecast, load_forecast

def test_algorithm_performance():
    """Test algorithm performance with different parameters"""
    
    print("🚀 Testing Algorithm Performance...")
    
    # Test different population sizes
    population_sizes = [50, 100, 200]
    generations = [100, 200, 300]
    
    results = []
    
    for pop_size in population_sizes:
        for gen in generations:
            print(f"\n📊 Testing: Population={pop_size}, Generations={gen}")
            
            start_time = time.time()
            
            # Create mock environment
            mock_hass = MockHomeAssistant()
            config = {
                "population_size": pop_size,
                "generations": gen,
                "mutation_rate": 0.05,
                "crossover_rate": 0.8,
                "num_devices": 2,
                "battery_capacity": 10.0,
                "max_charge_rate": 2.0,
                "max_discharge_rate": 2.0,
                "binary_control": False,
                "use_indexed_pricing": True
            }
            
            # Create optimizer
            optimizer = GeneticLoadOptimizer(mock_hass, config)
            
            # Set mock data
            pv_forecast, load_forecast = create_mock_data()
            optimizer.pv_forecast = pv_forecast
            optimizer.load_forecast = load_forecast
            optimizer.battery_soc = 50.0
            
            # Mock pricing
            mock_pricing = MockPricingCalculator(mock_hass, config)
            optimizer.pricing_calculator = mock_pricing
            
            # Run optimization
            try:
                solution = asyncio.run(optimizer.optimize())
                end_time = time.time()
                duration = end_time - start_time
                
                if solution is not None:
                    fitness = optimizer.best_fitness
                    results.append({
                        'population': pop_size,
                        'generations': gen,
                        'fitness': fitness,
                        'duration': duration,
                        'solution_shape': solution.shape
                    })
                    print(f"✅ Success: Fitness={fitness:.2f}, Duration={duration:.2f}s")
                else:
                    print("❌ No solution found")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    return results

def test_fitness_function():
    """Test the fitness function with various inputs"""
    
    print("\n🧬 Testing Fitness Function...")
    
    mock_hass = MockHomeAssistant()
    config = {
        "population_size": 100,
        "generations": 200,
        "num_devices": 2,
        "battery_capacity": 10.0,
        "max_charge_rate": 2.0,
        "max_discharge_rate": 2.0,
        "binary_control": False
    }
    
    optimizer = GeneticLoadOptimizer(mock_hass, config)
    
    # Set mock data
    pv_forecast, load_forecast = create_mock_data()
    optimizer.pv_forecast = pv_forecast
    optimizer.load_forecast = load_forecast
    optimizer.battery_soc = 50.0
    
    # Create mock pricing
    mock_pricing = MockPricingCalculator(mock_hass, config)
    optimizer.pricing_calculator = mock_pricing
    
    # Test different chromosome configurations
    test_chromosomes = [
        np.random.random((2, 96)),  # Random schedule
        np.ones((2, 96)) * 0.5,    # Half power all day
        np.zeros((2, 96)),          # No power
        np.random.random((2, 96)) * 0.8  # High power
    ]
    
    for i, chromosome in enumerate(test_chromosomes):
        try:
            fitness = asyncio.run(optimizer.fitness_function(chromosome))
            print(f"📊 Test {i+1}: Fitness = {fitness:.2f}")
        except Exception as e:
            print(f"❌ Test {i+1} failed: {e}")

def visualize_results(results):
    """Create visualizations of the test results"""
    
    if not results:
        print("❌ No results to visualize")
        return
    
    print("\n📈 Creating visualizations...")
    
    # Performance comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Fitness vs Parameters
    for result in results:
        ax1.scatter(result['population'], result['fitness'], 
                   s=100, alpha=0.7, label=f"Gen={result['generations']}")
    
    ax1.set_xlabel('Population Size')
    ax1.set_ylabel('Fitness Score')
    ax1.set_title('Fitness vs Population Size')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Duration vs Parameters
    for result in results:
        ax2.scatter(result['generations'], result['duration'], 
                   s=100, alpha=0.7, label=f"Pop={result['population']}")
    
    ax2.set_xlabel('Generations')
    ax2.set_ylabel('Duration (seconds)')
    ax2.set_title('Performance vs Generations')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('algorithm_performance_test.png', dpi=300, bbox_inches='tight')
    print("💾 Saved visualization as 'algorithm_performance_test.png'")
    
    # Print summary
    print("\n📊 Performance Summary:")
    print("-" * 50)
    best_result = max(results, key=lambda x: x['fitness'])
    fastest_result = min(results, key=lambda x: x['duration'])
    
    print(f"🏆 Best Fitness: {best_result['fitness']:.2f}")
    print(f"   Population: {best_result['population']}, Generations: {best_result['generations']}")
    print(f"   Duration: {best_result['duration']:.2f}s")
    
    print(f"⚡ Fastest: {fastest_result['duration']:.2f}s")
    print(f"   Fitness: {fastest_result['fitness']:.2f}")
    print(f"   Population: {fastest_result['population']}, Generations: {fastest_result['generations']}")

def main():
    """Main testing function"""
    
    print("🧬 Genetic Load Manager - Local Algorithm Testing")
    print("=" * 60)
    
    # Test 1: Fitness Function
    test_fitness_function()
    
    # Test 2: Algorithm Performance
    results = test_algorithm_performance()
    
    # Test 3: Visualize Results
    visualize_results(results)
    
    print("\n🎉 Local testing completed!")
    print("\n📝 Next Steps:")
    print("1. Review the performance visualization")
    print("2. Adjust parameters based on results")
    print("3. Test with different data scenarios")
    print("4. Run integration tests in development environment")

if __name__ == "__main__":
    main()
