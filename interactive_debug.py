#!/usr/bin/env python3
"""Interactive debugging script for the Genetic Load Manager integration."""

import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta

# Add the custom_components directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'custom_components', 'genetic_load_manager'))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Mock Home Assistant components
class MockHomeAssistant:
    def __init__(self):
        self.states = {}
        self.data = {}
        
    def states_get(self, entity_id):
        return self.states.get(entity_id)
        
    async def async_add_executor_job(self, func, *args):
        return func(*args)

class MockState:
    def __init__(self, state, attributes=None):
        self.state = state
        self.attributes = attributes or {}

async def interactive_debug():
    """Interactive debugging session."""
    print("🚀 Starting Interactive Debug Session")
    print("=" * 60)
    print("This will drop you into an interactive Python session where you can:")
    print("1. Inspect objects step by step")
    print("2. Test individual methods")
    print("3. Examine data structures")
    print("4. Debug specific issues")
    print("\nType 'help()' for help, 'exit()' to quit")
    print("=" * 60)
    
    try:
        # Import modules
        from genetic_algorithm import GeneticLoadOptimizer
        from pricing_calculator import IndexedTariffCalculator
        from const import DEFAULT_ENTITIES
        
        # Create mock data
        hass = MockHomeAssistant()
        
        # Create realistic test data
        today_forecast = []
        for hour in range(24):
            if 7 <= hour <= 19:
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
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        hourly_prices = {}
        for hour in range(24):
            hour_key = f"{current_date}T{hour:02d}:00:00+01:00"
            hourly_prices[hour_key] = 50 + hour * 2  # Simple price pattern
        
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
        
        # Create configuration
        config = {
            "pv_forecast_today": "sensor.solcast_pv_forecast_previsao_hoje",
            "market_price": "sensor.omie_spot_price_pt",
            "load_forecast": "sensor.load_forecast",
            "battery_soc": "sensor.battery_soc",
            "num_devices": 2,
            "population_size": 10,
            "generations": 5,
        }
        
        # Create objects
        pricing_calc = IndexedTariffCalculator(hass, config)
        optimizer = GeneticLoadOptimizer(hass, config)
        
        print("\n✅ Objects created successfully!")
        print("Available objects:")
        print("  - hass: Mock Home Assistant instance")
        print("  - pricing_calc: IndexedTariffCalculator instance")
        print("  - optimizer: GeneticLoadOptimizer instance")
        print("  - config: Configuration dictionary")
        print("  - today_forecast: Sample PV forecast data")
        print("  - hourly_prices: Sample OMIE price data")
        
        print("\n🔍 Starting interactive session...")
        print("You can now inspect and test these objects interactively.")
        
        # Drop into interactive session
        import code
        code.interact(
            banner="\n🔧 Interactive Debug Session\n" + "="*40 + "\n",
            local=locals()
        )
        
    except Exception as e:
        print(f"❌ Failed to start interactive debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(interactive_debug())
    except KeyboardInterrupt:
        print("\n⏹️ Interactive debug interrupted")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
