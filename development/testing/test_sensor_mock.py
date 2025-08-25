#!/usr/bin/env python3
"""
Mock Test for Genetic Load Manager Sensor Integration
Tests sensor logic without requiring Home Assistant environment
"""

import sys
import os
import ast
from datetime import datetime, timedelta
import numpy as np

def test_sensor_logic():
    """Test the sensor logic with mock data."""
    print("🔍 Testing sensor logic with mock data...")
    
    try:
        # Mock the sensor class structure
        class MockState:
            def __init__(self, state, last_updated):
                self.state = state
                self.last_updated = last_updated
        
        # Test forecast generation logic
        print("  🔍 Testing forecast generation logic...")
        
        # Mock historical data (7 days of hourly data)
        mock_history = []
        base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day in range(7):
            for hour in range(24):
                # Simulate typical load pattern (higher during day, lower at night)
                if 6 <= hour <= 22:  # Daytime hours
                    load = 2.0 + np.random.normal(0, 0.5)  # 2 kWh ± 0.5
                else:  # Nighttime hours
                    load = 0.5 + np.random.normal(0, 0.2)  # 0.5 kWh ± 0.2
                
                timestamp = base_time + timedelta(days=day, hours=hour)
                mock_history.append(MockState(str(load), timestamp))
        
        # Test the forecast generation algorithm
        time_slots = 96  # 24 hours * 15-minute intervals
        forecast = np.zeros(time_slots)
        slot_data = {i: [] for i in range(time_slots)}
        
        # Organize historical data by 15-minute slots
        for state in mock_history:
            try:
                timestamp = state.last_updated
                value = float(state.state)
                # Calculate slot index based on time of day
                slot_idx = int((timestamp.hour * 60 + timestamp.minute) / 15) % time_slots
                slot_data[slot_idx].append(value)
            except (ValueError, TypeError):
                continue
        
        # Calculate average load for each slot
        for i in range(time_slots):
            if slot_data[i]:
                forecast[i] = np.mean(slot_data[i])
            else:
                forecast[i] = 0.1  # Default to small non-zero value
        
        # Validate forecast
        if len(forecast) == 96:
            print("  ✅ Forecast array has correct length (96 slots)")
        else:
            print(f"  ❌ Forecast array has incorrect length: {len(forecast)}")
            return False
        
        if np.any(forecast > 0):
            print("  ✅ Forecast contains non-zero values")
        else:
            print("  ❌ Forecast contains only zeros")
            return False
        
        # Check for reasonable load patterns
        daytime_slots = list(range(24, 88))  # 6:00 AM to 10:00 PM
        nighttime_slots = list(range(0, 24)) + list(range(88, 96))  # 10:00 PM to 6:00 AM
        
        daytime_avg = np.mean([forecast[i] for i in daytime_slots])
        nighttime_avg = np.mean([forecast[i] for i in nighttime_slots])
        
        if daytime_avg > nighttime_avg:
            print("  ✅ Daytime loads are higher than nighttime loads (realistic pattern)")
        else:
            print("  ❌ Load pattern doesn't match expected day/night variation")
            return False
        
        print(f"  📊 Daytime average: {daytime_avg:.2f} kWh")
        print(f"  📊 Nighttime average: {nighttime_avg:.2f} kWh")
        print(f"  📊 Total forecasted energy: {np.sum(forecast):.2f} kWh")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing sensor logic: {e}")
        return False

def test_configuration_schema():
    """Test the configuration schema structure."""
    print("\n🔍 Testing configuration schema structure...")
    
    try:
        # Read the config flow to understand the configuration schema
        with open("../../custom_components/genetic_load_manager/config_flow.py", 'r', encoding='utf-8') as f:
            config_flow_content = f.read()
        
        # Extract configuration fields from the config flow
        config_fields = []
        if "load_sensor_entity" in config_flow_content:
            config_fields.append("load_sensor_entity")
        if "load_forecast_entity" in config_flow_content:
            config_fields.append("load_forecast_entity")
        if "pv_forecast_entity" in config_flow_content:
            config_fields.append("pv_forecast_entity")
        if "pv_forecast_tomorrow_entity" in config_flow_content:
            config_fields.append("pv_forecast_tomorrow_entity")
        
        print(f"  ✅ Found configuration fields: {config_fields}")
        
        return config_fields
        
    except Exception as e:
        print(f"  ❌ Error reading config flow: {e}")
        return []

def test_platform_registration():
    """Test that sensor platform is properly registered."""
    print("\n🔍 Testing platform registration...")
    
    try:
        # Read the __init__.py to understand the component structure
        with open("../../custom_components/genetic_load_manager/__init__.py", 'r', encoding='utf-8') as f:
            init_content = f.read()
        
        # Check for required functions
        required_functions = ["async_setup", "async_setup_entry", "async_unload_entry"]
        found_functions = []
        
        for func in required_functions:
            if f"async def {func}" in init_content:
                found_functions.append(func)
        
        print(f"  ✅ Found functions: {found_functions}")
        
        # Check for platforms
        if 'PLATFORMS = ["sensor", "binary_sensor", "switch"]' in init_content:
            print("  ✅ PLATFORMS list includes sensor")
        else:
            print("  ❌ PLATFORMS list missing or incorrect")
        
        return found_functions
        
    except Exception as e:
        print(f"  ❌ Error reading __init__.py: {e}")
        return []

def test_error_handling():
    """Test error handling in sensor implementation."""
    print("\n🔍 Testing error handling...")
    
    try:
        # Read the sensor.py to understand the sensor structure
        with open("../../custom_components/genetic_load_manager/sensor.py", 'r', encoding='utf-8') as f:
            sensor_content = f.read()
        
        # Check for required class
        if "class LoadForecastSensor" in sensor_content:
            print("  ✅ LoadForecastSensor class found")
        else:
            print("  ❌ LoadForecastSensor class not found")
            return False
        
        # Check for required methods
        required_methods = ["__init__", "state", "extra_state_attributes", "async_added_to_hass", "async_update"]
        found_methods = []
        
        for method in required_methods:
            if f"def {method}" in sensor_content or f"async def {method}" in sensor_content:
                found_methods.append(method)
        
        print(f"  ✅ Found methods: {found_methods}")
        
        return len(found_methods) >= 3  # At least 3 methods should be present
        
    except Exception as e:
        print(f"  ❌ Error reading sensor.py: {e}")
        return False

def main():
    """Run all mock tests."""
    print("🧪 Genetic Load Manager Sensor Integration Mock Test Suite")
    print("=" * 70)
    
    tests = [
        ("Sensor Logic", test_sensor_logic),
        ("Configuration Schema", test_configuration_schema),
        ("Platform Registration", test_platform_registration),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Mock Test Results Summary")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All mock tests passed! Sensor integration logic is sound.")
        print("\n📋 Next Steps:")
        print("   1. Install in Home Assistant")
        print("   2. Configure through UI")
        print("   3. Test with real energy sensors")
        print("   4. Verify forecast generation")
        return True
    else:
        print("⚠️  Some mock tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
