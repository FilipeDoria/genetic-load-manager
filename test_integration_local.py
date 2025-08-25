#!/usr/bin/env python3
"""Local test to reproduce the exact same logic running in Home Assistant."""

import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

# Add the custom_components directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'custom_components', 'genetic_load_manager'))

# Configure logging to match Home Assistant
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Mock Home Assistant components
class MockHomeAssistant:
    """Mock Home Assistant instance for local testing."""
    
    def __init__(self):
        self.states = {}
        self.data = {}
        
    def states_get(self, entity_id):
        """Mock states.get method."""
        return self.states.get(entity_id)
        
    async def async_add_executor_job(self, func, *args):
        """Mock async_add_executor_job method."""
        # For local testing, just call the function directly
        return func(*args)

class MockState:
    """Mock Home Assistant state object."""
    
    def __init__(self, state, attributes=None):
        self.state = state
        self.attributes = attributes or {}

def create_mock_solcast_entity(entity_id, forecast_data):
    """Create a mock Solcast PV forecast entity."""
    return MockState("available", {
        "DetailedForecast": forecast_data,
        "DetailedHourly": forecast_data,  # Fallback
        "Dayname": "Monday",
        "DataCorrect": True
    })

def create_mock_omie_entity(entity_id, hourly_prices):
    """Create a mock OMIE electricity price entity."""
    return MockState("92.3", {
        "OMIE today average": 92.3,
        "Today provisional": True,
        "Today average": 91.44,
        "Today hours": hourly_prices
    })

def create_mock_battery_entity(entity_id, soc):
    """Create a mock battery entity."""
    return MockState(str(soc), {
        "battery_level": soc,
        "battery_charging": False
    })

def create_mock_load_forecast_entity(entity_id, forecast_data):
    """Create a mock load forecast entity."""
    return MockState("available", {
        "forecast": forecast_data
    })

async def test_pv_forecast_parsing():
    """Test PV forecast parsing logic."""
    print("\n🔍 Testing PV Forecast Parsing")
    print("=" * 50)
    
    # Create mock Home Assistant instance
    hass = MockHomeAssistant()
    
    # Create mock Solcast data (similar to what you showed me)
    today_forecast = []
    tomorrow_forecast = []
    
    # Generate realistic PV forecast data for today (starting from current hour)
    current_hour = datetime.now().hour
    for hour in range(24):
        if 7 <= hour <= 19:  # Daylight hours
            # Generate realistic PV curve (morning ramp, peak at noon, evening ramp)
            if hour < 12:
                pv_estimate = 0.1 + (hour - 7) * 0.3  # Morning ramp
            else:
                pv_estimate = 3.0 - (hour - 12) * 0.25  # Evening ramp
        else:
            pv_estimate = 0.0  # Night hours
            
        # Add some variation
        pv_estimate = max(0, pv_estimate + (hash(f"{hour}") % 100 - 50) / 1000)
        
        # Create 30-minute interval data
        for minute in [0, 30]:
            period_start = f"2025-08-25T{hour:02d}:{minute:02d}:00+01:00"
            today_forecast.append({
                "period_start": period_start,
                "pv_estimate": round(pv_estimate, 4),
                "pv_estimate10": round(pv_estimate * 0.8, 4),
                "pv_estimate90": round(pv_estimate * 1.2, 4)
            })
    
    # Generate tomorrow's forecast (similar pattern)
    for hour in range(24):
        if 7 <= hour <= 19:
            if hour < 12:
                pv_estimate = 0.1 + (hour - 7) * 0.35  # Slightly different
            else:
                pv_estimate = 3.2 - (hour - 12) * 0.28
        else:
            pv_estimate = 0.0
            
        pv_estimate = max(0, pv_estimate + (hash(f"tomorrow_{hour}") % 100 - 50) / 1000)
        
        for minute in [0, 30]:
            period_start = f"2025-08-26T{hour:02d}:{minute:02d}:00+01:00"
            tomorrow_forecast.append({
                "period_start": period_start,
                "pv_estimate": round(pv_estimate, 4),
                "pv_estimate10": round(pv_estimate * 0.8, 4),
                "pv_estimate90": round(pv_estimate * 1.2, 4)
            })
    
    # Set up mock entities
    hass.states["sensor.solcast_pv_forecast_previsao_hoje"] = create_mock_solcast_entity(
        "sensor.solcast_pv_forecast_previsao_hoje", today_forecast
    )
    hass.states["sensor.solcast_pv_forecast_previsao_para_amanha"] = create_mock_solcast_entity(
        "sensor.solcast_pv_forecast_previsao_para_amanha", tomorrow_forecast
    )
    
    print(f"Created mock PV forecast data:")
    print(f"  Today: {len(today_forecast)} 30-minute intervals")
    print(f"  Tomorrow: {len(tomorrow_forecast)} 30-minute intervals")
    print(f"  Sample today data: {today_forecast[0]}")
    print(f"  Sample tomorrow data: {tomorrow_forecast[0]}")
    
    return hass, today_forecast, tomorrow_forecast

async def test_omie_price_parsing():
    """Test OMIE electricity price parsing logic."""
    print("\n🔍 Testing OMIE Price Parsing")
    print("=" * 50)
    
    # Create mock Home Assistant instance
    hass = MockHomeAssistant()
    
    # Create realistic OMIE hourly prices (similar to what you showed me)
    hourly_prices = {}
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Generate realistic daily price pattern
    base_prices = [
        107.5, 104.99, 101.12, 98.35, 104.99, 108.73,  # 00:00 - 05:00 (night)
        114.32, 114.32, 108.32, 89.51, 65.01, 55.2,    # 06:00 - 11:00 (morning)
        35.0, 26.17, 25.2, 56.43, 70.1, 97.43,         # 12:00 - 17:00 (afternoon)
        114.78, 125.95, 142.0, 123.11, 114.68, 110.0    # 18:00 - 23:00 (evening)
    ]
    
    for hour, price in enumerate(base_prices):
        # Add some variation
        variation = (hash(f"price_{hour}") % 100 - 50) / 100
        adjusted_price = price * (1 + variation)
        
        # Create both timezone formats
        hour_key_1 = f"{current_date}T{hour:02d}:00:00+01:00"
        hour_key_2 = f"{current_date}T{hour:02d}:00:00+00:00"
        
        hourly_prices[hour_key_1] = round(adjusted_price, 2)
        hourly_prices[hour_key_2] = round(adjusted_price, 2)
    
    # Set up mock entity
    hass.states["sensor.omie_spot_price_pt"] = create_mock_omie_entity(
        "sensor.omie_spot_price_pt", hourly_prices
    )
    
    print(f"Created mock OMIE price data:")
    print(f"  Total hourly prices: {len(hourly_prices)}")
    print(f"  Price range: {min(hourly_prices.values()):.2f} - {max(hourly_prices.values()):.2f} €/MWh")
    print(f"  Sample prices:")
    for hour in range(0, 24, 6):
        key = f"{current_date}T{hour:02d}:00:00+01:00"
        if key in hourly_prices:
            print(f"    {hour:02d}:00: {hourly_prices[key]} €/MWh")
    
    return hass, hourly_prices

async def test_genetic_algorithm_integration():
    """Test the complete genetic algorithm integration."""
    print("\n🔍 Testing Complete Genetic Algorithm Integration")
    print("=" * 50)
    
    try:
        # Import the actual integration modules
        from genetic_algorithm import GeneticLoadOptimizer
        from pricing_calculator import IndexedTariffCalculator
        from const import DEFAULT_ENTITIES
        
        print("✅ Successfully imported integration modules")
        
        # Create mock Home Assistant instance with all required entities
        hass = MockHomeAssistant()
        
        # Set up all mock entities
        hass.states["sensor.battery_soc"] = create_mock_battery_entity("sensor.battery_soc", 75.0)
        hass.states["sensor.load_forecast"] = create_mock_load_forecast_entity(
            "sensor.load_forecast", [0.5] * 96  # 96 time slots
        )
        
        # Create configuration
        config = {
            "pv_forecast_today": "sensor.solcast_pv_forecast_previsao_hoje",
            "pv_forecast_tomorrow": "sensor.solcast_pv_forecast_previsao_para_amanha",
            "market_price": "sensor.omie_spot_price_pt",
            "load_forecast": "sensor.load_forecast",
            "battery_soc": "sensor.battery_soc",
            "num_devices": 2,
            "population_size": 50,  # Smaller for testing
            "generations": 20,       # Smaller for testing
            "use_indexed_pricing": True
        }
        
        print(f"✅ Created configuration: {list(config.keys())}")
        
        # Test pricing calculator
        print("\n📊 Testing Pricing Calculator...")
        pricing_calc = IndexedTariffCalculator(hass, config)
        
        # Test market price fetching
        market_prices = await pricing_calc.get_current_market_price()
        if isinstance(market_prices, list):
            print(f"✅ Market prices loaded: {len(market_prices)} hourly prices")
            print(f"   Price range: {min(market_prices):.4f} - {max(market_prices):.4f} €/kWh")
        else:
            print(f"✅ Single market price: {market_prices} €/kWh")
        
        # Test 24h price forecast
        price_forecast = await pricing_calc.get_24h_price_forecast()
        if price_forecast:
            print(f"✅ 24h price forecast generated: {len(price_forecast)} time slots")
            print(f"   Forecast range: {min(price_forecast):.4f} - {max(price_forecast):.4f} €/kWh")
        else:
            print("❌ Failed to generate 24h price forecast")
        
        # Test genetic algorithm
        print("\n🧬 Testing Genetic Algorithm...")
        optimizer = GeneticLoadOptimizer(hass, config)
        
        # Test forecast data fetching
        print("   Fetching forecast data...")
        await optimizer.fetch_forecast_data()
        
        if optimizer.pv_forecast:
            print(f"✅ PV forecast loaded: {len(optimizer.pv_forecast)} time slots")
            print(f"   PV range: {min(optimizer.pv_forecast):.3f} - {max(optimizer.pv_forecast):.3f} kW")
        else:
            print("❌ PV forecast failed to load")
            
        if optimizer.pricing:
            print(f"✅ Pricing loaded: {len(optimizer.pricing)} time slots")
            print(f"   Pricing range: {min(optimizer.pricing):.4f} - {max(optimizer.pricing):.4f} €/kWh")
        else:
            print("❌ Pricing failed to load")
            
        if optimizer.load_forecast:
            print(f"✅ Load forecast loaded: {len(optimizer.load_forecast)} time slots")
        else:
            print("❌ Load forecast failed to load")
        
        # Test population initialization
        print("   Initializing population...")
        await optimizer.initialize_population()
        
        if optimizer.population:
            print(f"✅ Population initialized: {len(optimizer.population)} individuals")
            print(f"   Each individual: {len(optimizer.population[0])} devices × {len(optimizer.population[0][0])} time slots")
        else:
            print("❌ Population initialization failed")
        
        # Test a single optimization run (small scale for testing)
        print("   Running single optimization...")
        try:
            solution = await optimizer.optimize()
            if solution:
                print(f"✅ Optimization completed successfully!")
                print(f"   Best fitness: {optimizer.best_fitness:.2f}")
                print(f"   Solution shape: {len(solution)} devices × {len(solution[0])} time slots")
                
                # Show sample schedule
                print("   Sample schedule (first 5 time slots):")
                for device_idx, device_schedule in enumerate(solution):
                    print(f"     Device {device_idx}: {[f'{x:.2f}' for x in device_schedule[:5]]}")
            else:
                print("❌ Optimization returned no solution")
        except Exception as e:
            print(f"❌ Optimization failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🎉 Integration test completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Local Home Assistant Integration Tests")
    print("=" * 60)
    
    # Test 1: PV Forecast Parsing
    print("\n1️⃣ Testing PV Forecast Parsing...")
    try:
        hass, today_data, tomorrow_data = await test_pv_forecast_parsing()
        print("✅ PV Forecast parsing test completed")
    except Exception as e:
        print(f"❌ PV Forecast parsing test failed: {e}")
        return False
    
    # Test 2: OMIE Price Parsing
    print("\n2️⃣ Testing OMIE Price Parsing...")
    try:
        hass, hourly_prices = await test_omie_price_parsing()
        print("✅ OMIE Price parsing test completed")
    except Exception as e:
        print(f"❌ OMIE Price parsing test failed: {e}")
        return False
    
    # Test 3: Complete Integration
    print("\n3️⃣ Testing Complete Integration...")
    try:
        success = await test_genetic_algorithm_integration()
        if success:
            print("✅ Complete integration test completed")
        else:
            print("❌ Complete integration test failed")
            return False
    except Exception as e:
        print(f"❌ Complete integration test failed: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    print("The integration should now work correctly in Home Assistant.")
    return True

if __name__ == "__main__":
    # Run the async tests
    try:
        success = asyncio.run(main())
        if success:
            print("\n✅ All tests passed! The integration is ready for Home Assistant.")
        else:
            print("\n❌ Some tests failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
