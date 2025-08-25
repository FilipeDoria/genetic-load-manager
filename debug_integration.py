#!/usr/bin/env python3
"""Comprehensive debugging script for the Genetic Load Manager integration."""

import sys
import os
import asyncio
import logging
import json
from datetime import datetime, timedelta
from pprint import pprint

# Add the custom_components directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'custom_components', 'genetic_load_manager'))

# Configure very detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Mock Home Assistant components
class MockHomeAssistant:
    """Mock Home Assistant instance for debugging."""
    
    def __init__(self):
        self.states = {}
        self.data = {}
        self._logger = logging.getLogger("MockHASS")
        
    def states_get(self, entity_id):
        """Mock states.get method with logging."""
        state = self.states.get(entity_id)
        self._logger.debug(f"states.get('{entity_id}') -> {state}")
        return state
        
    async def async_add_executor_job(self, func, *args):
        """Mock async_add_executor_job method with logging."""
        self._logger.debug(f"async_add_executor_job({func.__name__}, {args})")
        # For debugging, just call the function directly
        return func(*args)

class MockState:
    """Mock Home Assistant state object."""
    
    def __init__(self, state, attributes=None):
        self.state = state
        self.attributes = attributes or {}
    
    def __repr__(self):
        return f"MockState(state='{self.state}', attributes={self.attributes})"

def debug_entity_data(entity_id, state):
    """Debug helper to show entity data structure."""
    print(f"\n🔍 Entity: {entity_id}")
    print(f"   State: {state.state}")
    print(f"   Attributes: {len(state.attributes)} items")
    for key, value in state.attributes.items():
        if isinstance(value, (list, dict)) and len(str(value)) > 100:
            print(f"     {key}: {type(value).__name__} with {len(value)} items")
            if isinstance(value, list) and value:
                print(f"       Sample: {value[0]}")
        else:
            print(f"     {key}: {value}")

async def debug_step_by_step():
    """Debug the integration step by step with detailed logging."""
    print("🚀 Starting Step-by-Step Debug")
    print("=" * 60)
    
    try:
        # Step 1: Import modules
        print("\n1️⃣ Importing modules...")
        from genetic_algorithm import GeneticLoadOptimizer
        from pricing_calculator import IndexedTariffCalculator
        from const import DEFAULT_ENTITIES
        
        print("✅ Modules imported successfully")
        print(f"   Available constants: {list(DEFAULT_ENTITIES.keys())}")
        
        # Step 2: Create mock data
        print("\n2️⃣ Creating mock data...")
        hass = MockHomeAssistant()
        
        # Create realistic Solcast data
        today_forecast = []
        for hour in range(24):
            if 7 <= hour <= 19:  # Daylight hours
                pv_estimate = 2.0 if hour == 12 else 0.5 + abs(hour - 12) * 0.2
            else:
                pv_estimate = 0.0
                
            for minute in [0, 30]:
                period_start = f"2025-08-25T{hour:02d}:{minute:02d}:00+01:00"
                today_forecast.append({
                    "period_start": period_start,
                    "pv_estimate": round(pv_estimate, 4),
                    "pv_estimate10": round(pv_estimate * 0.8, 4),
                    "pv_estimate90": round(pv_estimate * 1.2, 4)
                })
        
        # Create realistic OMIE data
        hourly_prices = {}
        current_date = datetime.now().strftime("%Y-%m-%d")
        base_prices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 25, 30, 35, 40, 45, 50, 55]
        
        for hour, price in enumerate(base_prices):
            hour_key = f"{current_date}T{hour:02d}:00:00+01:00"
            hourly_prices[hour_key] = price
        
        # Set up entities
        hass.states["sensor.solcast_pv_forecast_previsao_hoje"] = MockState("available", {
            "DetailedForecast": today_forecast,
            "DetailedHourly": today_forecast
        })
        
        hass.states["sensor.omie_spot_price_pt"] = MockState("92.3", {
            "Today hours": hourly_prices
        })
        
        hass.states["sensor.battery_soc"] = MockState("75.0")
        hass.states["sensor.load_forecast"] = MockState("available", {
            "forecast": [0.5] * 96
        })
        
        print("✅ Mock data created")
        print(f"   PV forecast: {len(today_forecast)} intervals")
        print(f"   OMIE prices: {len(hourly_prices)} hours")
        
        # Step 3: Test pricing calculator
        print("\n3️⃣ Testing Pricing Calculator...")
        config = {"market_price": "sensor.omie_spot_price_pt"}
        pricing_calc = IndexedTariffCalculator(hass, config)
        
        print("   Testing get_current_market_price...")
        market_prices = await pricing_calc.get_current_market_price()
        print(f"   Result: {type(market_prices)} = {market_prices}")
        
        if isinstance(market_prices, list):
            print(f"   List length: {len(market_prices)}")
            print(f"   Price range: {min(market_prices):.4f} - {max(market_prices):.4f}")
            print(f"   Sample prices: {market_prices[:5]}")
        
        # Step 4: Test genetic algorithm initialization
        print("\n4️⃣ Testing Genetic Algorithm Initialization...")
        ga_config = {
            "pv_forecast_today": "sensor.solcast_pv_forecast_previsao_hoje",
            "pv_forecast_tomorrow": "sensor.solcast_pv_forecast_previsao_para_amanha",
            "market_price": "sensor.omie_spot_price_pt",
            "load_forecast": "sensor.load_forecast",
            "battery_soc": "sensor.battery_soc",
            "num_devices": 2,
            "population_size": 10,  # Very small for debugging
            "generations": 5,        # Very small for debugging
        }
        
        optimizer = GeneticLoadOptimizer(hass, ga_config)
        print("✅ GeneticLoadOptimizer created")
        print(f"   Configuration: {ga_config}")
        
        # Step 5: Test forecast data fetching
        print("\n5️⃣ Testing Forecast Data Fetching...")
        print("   Calling fetch_forecast_data...")
        
        await optimizer.fetch_forecast_data()
        
        print("   Results:")
        print(f"     PV forecast: {type(optimizer.pv_forecast)} = {len(optimizer.pv_forecast) if optimizer.pv_forecast else 'None'}")
        if optimizer.pv_forecast:
            print(f"       Range: {min(optimizer.pv_forecast):.3f} - {max(optimizer.pv_forecast):.3f} kW")
            print(f"       Sample: {optimizer.pv_forecast[:5]}")
        
        print(f"     Pricing: {type(optimizer.pricing)} = {len(optimizer.pricing) if optimizer.pricing else 'None'}")
        if optimizer.pricing:
            print(f"       Range: {min(optimizer.pricing):.4f} - {max(optimizer.pricing):.4f} €/kWh")
            print(f"       Sample: {optimizer.pricing[:5]}")
        
        print(f"     Load forecast: {type(optimizer.load_forecast)} = {len(optimizer.load_forecast) if optimizer.load_forecast else 'None'}")
        if optimizer.load_forecast:
            print(f"       Sample: {optimizer.load_forecast[:5]}")
        
        # Step 6: Test population initialization
        print("\n6️⃣ Testing Population Initialization...")
        await optimizer.initialize_population()
        
        if optimizer.population:
            print(f"✅ Population initialized")
            print(f"   Size: {len(optimizer.population)} individuals")
            print(f"   Shape: {len(optimizer.population[0])} devices × {len(optimizer.population[0][0])} time slots")
            print(f"   Sample individual: {optimizer.population[0][0][:5]}")
        else:
            print("❌ Population initialization failed")
        
        # Step 7: Test fitness function
        print("\n7️⃣ Testing Fitness Function...")
        if optimizer.population:
            try:
                fitness = await optimizer.fitness_function(optimizer.population[0])
                print(f"✅ Fitness calculated: {fitness:.2f}")
            except Exception as e:
                print(f"❌ Fitness calculation failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Step 8: Test optimization (very small scale)
        print("\n8️⃣ Testing Optimization (Small Scale)...")
        try:
            print("   Running optimization...")
            solution = await optimizer.optimize()
            
            if solution:
                print(f"✅ Optimization completed!")
                print(f"   Best fitness: {optimizer.best_fitness:.2f}")
                print(f"   Solution shape: {len(solution)} devices × {len(solution[0])} time slots")
                
                # Show detailed solution
                for device_idx, device_schedule in enumerate(solution):
                    print(f"     Device {device_idx}:")
                    print(f"       First 10 slots: {[f'{x:.2f}' for x in device_schedule[:10]]}")
                    print(f"       On/Off ratio: {sum(1 for x in device_schedule if x > 0.5)}/{len(device_schedule)}")
            else:
                print("❌ Optimization returned no solution")
                
        except Exception as e:
            print(f"❌ Optimization failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🎉 Step-by-step debug completed!")
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def debug_data_flow():
    """Debug the data flow through the system."""
    print("\n🔍 Debugging Data Flow")
    print("=" * 60)
    
    try:
        from genetic_algorithm import GeneticLoadOptimizer
        from pricing_calculator import IndexedTariffCalculator
        
        # Create minimal test setup
        hass = MockHomeAssistant()
        
        # Test with minimal data
        print("1️⃣ Testing with minimal data...")
        
        # Single PV forecast point
        hass.states["sensor.pv_test"] = MockState("available", {
            "DetailedForecast": [{
                "period_start": "2025-08-25T12:00:00+01:00",
                "pv_estimate": 2.0
            }]
        })
        
        # Single price point
        current_date = datetime.now().strftime("%Y-%m-%d")
        hass.states["sensor.price_test"] = MockState("100.0", {
            "Today hours": {
                f"{current_date}T12:00:00+01:00": 100.0
            }
        })
        
        config = {
            "pv_forecast_today": "sensor.pv_test",
            "market_price": "sensor.price_test",
            "num_devices": 1,
            "population_size": 2,
            "generations": 2
        }
        
        print("2️⃣ Testing minimal optimization...")
        optimizer = GeneticLoadOptimizer(hass, config)
        
        print("   Fetching data...")
        await optimizer.fetch_forecast_data()
        
        print(f"   PV forecast: {optimizer.pv_forecast}")
        print(f"   Pricing: {optimizer.pricing}")
        
        print("   Initializing population...")
        await optimizer.initialize_population()
        
        print(f"   Population: {len(optimizer.population)} individuals")
        
        print("   Running optimization...")
        solution = await optimizer.optimize()
        
        if solution:
            print(f"✅ Minimal optimization successful!")
            print(f"   Solution: {solution}")
        else:
            print("❌ Minimal optimization failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Data flow debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all debug functions."""
    print("🚀 Starting Comprehensive Debug Session")
    print("=" * 60)
    
    # Debug 1: Step by step
    success1 = await debug_step_by_step()
    
    # Debug 2: Data flow
    success2 = await debug_data_flow()
    
    if success1 and success2:
        print("\n🎉 All debug tests passed!")
        print("The integration should work correctly.")
    else:
        print("\n❌ Some debug tests failed.")
        print("Check the output above for specific issues.")
    
    return success1 and success2

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Debug interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
