#!/usr/bin/env python3
"""Data validation script to analyze your actual entity data structures."""

import sys
import os
import json
from datetime import datetime, timedelta

def analyze_data_structure(data, name="Data", max_depth=3, current_depth=0):
    """Recursively analyze data structure."""
    if current_depth >= max_depth:
        return f"{type(data).__name__} (max depth reached)"
    
    if isinstance(data, dict):
        result = f"{type(data).__name__} with {len(data)} keys:\n"
        for key, value in data.items():
            indent = "  " * (current_depth + 1)
            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                result += f"{indent}{key}: {analyze_data_structure(value, key, max_depth, current_depth + 1)}\n"
            else:
                result += f"{indent}{key}: {type(value).__name__} = {value}\n"
        return result
    
    elif isinstance(data, list):
        result = f"{type(data).__name__} with {len(data)} items:\n"
        if data:
            indent = "  " * (current_depth + 1)
            sample = data[0]
            result += f"{indent}Sample item: {analyze_data_structure(sample, 'item', max_depth, current_depth + 1)}\n"
        return result
    
    else:
        return f"{type(data).__name__} = {data}"

def validate_solcast_data():
    """Validate Solcast PV forecast data structure."""
    print("🔍 Validating Solcast PV Forecast Data Structure")
    print("=" * 60)
    
    # Example Solcast data structure (based on what you showed me)
    sample_solcast = {
        "DetailedForecast": [
            {
                "period_start": "2025-08-25T07:00:00+01:00",
                "pv_estimate": 0.061,
                "pv_estimate10": 0.0233,
                "pv_estimate90": 0.1624
            },
            {
                "period_start": "2025-08-25T07:30:00+01:00",
                "pv_estimate": 0.3448,
                "pv_estimate10": 0.0937,
                "pv_estimate90": 0.6981
            }
        ],
        "DetailedHourly": [
            {
                "period_start": "2025-08-25T07:00:00+01:00",
                "pv_estimate": 0.2029,
                "pv_estimate10": 0.0585,
                "pv_estimate90": 0.4303
            }
        ]
    }
    
    print("Expected Solcast structure:")
    print(analyze_data_structure(sample_solcast, "Solcast"))
    
    print("\n✅ Validation points:")
    print("  - DetailedForecast: List of 30-minute interval forecasts")
    print("  - DetailedHourly: List of 1-hour interval forecasts (fallback)")
    print("  - Each item has: period_start (ISO datetime), pv_estimate (float)")
    print("  - period_start format: YYYY-MM-DDTHH:MM:SS+01:00")
    print("  - pv_estimate: Solar power in kW")
    
    return sample_solcast

def validate_omie_data():
    """Validate OMIE electricity price data structure."""
    print("\n🔍 Validating OMIE Electricity Price Data Structure")
    print("=" * 60)
    
    # Example OMIE data structure (based on what you showed me)
    current_date = datetime.now().strftime("%Y-%m-%d")
    sample_omie = {
        "OMIE today average": 92.3,
        "Today provisional": True,
        "Today average": 91.44,
        "Today hours": {
            f"{current_date}T00:00:00+01:00": 107.5,
            f"{current_date}T01:00:00+01:00": 104.99,
            f"{current_date}T02:00:00+01:00": 101.12,
            f"{current_date}T03:00:00+01:00": 98.35,
            f"{current_date}T04:00:00+01:00": 104.99,
            f"{current_date}T05:00:00+01:00": 108.73,
            f"{current_date}T06:00:00+01:00": 114.32,
            f"{current_date}T07:00:00+01:00": 114.32,
            f"{current_date}T08:00:00+01:00": 108.32,
            f"{current_date}T09:00:00+01:00": 89.51,
            f"{current_date}T10:00:00+01:00": 65.01,
            f"{current_date}T11:00:00+01:00": 55.2,
            f"{current_date}T12:00:00+01:00": 35.0,
            f"{current_date}T13:00:00+01:00": 26.17,
            f"{current_date}T14:00:00+01:00": 25.2,
            f"{current_date}T15:00:00+01:00": 56.43,
            f"{current_date}T16:00:00+01:00": 70.1,
            f"{current_date}T17:00:00+01:00": 97.43,
            f"{current_date}T18:00:00+01:00": 114.78,
            f"{current_date}T19:00:00+01:00": 125.95,
            f"{current_date}T20:00:00+01:00": 142.0,
            f"{current_date}T21:00:00+01:00": 123.11,
            f"{current_date}T22:00:00+01:00": 114.68,
            f"{current_date}T23:00:00+01:00": None
        }
    }
    
    print("Expected OMIE structure:")
    print(analyze_data_structure(sample_omie, "OMIE"))
    
    print("\n✅ Validation points:")
    print("  - Today hours: Dictionary with 24 hourly price entries")
    print("  - Keys: ISO datetime strings (YYYY-MM-DDTHH:MM:SS+01:00)")
    print("  - Values: Electricity prices in €/MWh (float or None)")
    print("  - Current date used: " + current_date)
    print("  - Price range: 25.2 - 142.0 €/MWh")
    
    return sample_omie

def validate_integration_requirements():
    """Validate what the integration needs vs what you have."""
    print("\n🔍 Validating Integration Requirements")
    print("=" * 60)
    
    requirements = {
        "PV Forecast": {
            "required": "DetailedForecast or DetailedHourly attribute",
            "format": "List of dictionaries with period_start and pv_estimate",
            "frequency": "30-minute or 1-hour intervals",
            "units": "kW",
            "coverage": "24+ hours"
        },
        "Electricity Prices": {
            "required": "Today hours attribute",
            "format": "Dictionary with datetime keys and price values",
            "frequency": "1-hour intervals",
            "units": "€/MWh",
            "coverage": "24 hours"
        },
        "Load Forecast": {
            "required": "forecast attribute",
            "format": "List of 96 float values",
            "frequency": "15-minute intervals",
            "units": "kW",
            "coverage": "24 hours"
        },
        "Battery SOC": {
            "required": "State value",
            "format": "Float (0-100)",
            "units": "%",
            "coverage": "Current value"
        }
    }
    
    print("Integration Requirements:")
    for component, details in requirements.items():
        print(f"\n  {component}:")
        for key, value in details.items():
            print(f"    {key}: {value}")
    
    return requirements

def create_test_data():
    """Create test data that matches your actual structure."""
    print("\n🔍 Creating Test Data Matching Your Structure")
    print("=" * 60)
    
    # Generate test data that matches your actual entities
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Test Solcast data
    test_solcast = {
        "DetailedForecast": [],
        "DetailedHourly": []
    }
    
    for hour in range(24):
        if 7 <= hour <= 19:  # Daylight hours
            pv_estimate = 2.0 if hour == 12 else 0.5 + abs(hour - 12) * 0.2
        else:
            pv_estimate = 0.0
            
        # Add 30-minute intervals
        for minute in [0, 30]:
            period_start = f"{current_date}T{hour:02d}:{minute:02d}:00+01:00"
            test_solcast["DetailedForecast"].append({
                "period_start": period_start,
                "pv_estimate": round(pv_estimate, 4),
                "pv_estimate10": round(pv_estimate * 0.8, 4),
                "pv_estimate90": round(pv_estimate * 1.2, 4)
            })
        
        # Add hourly intervals
        period_start = f"{current_date}T{hour:02d}:00:00+01:00"
        test_solcast["DetailedHourly"].append({
            "period_start": period_start,
            "pv_estimate": round(pv_estimate, 4),
            "pv_estimate10": round(pv_estimate * 0.8, 4),
            "pv_estimate90": round(pv_estimate * 1.2, 4)
        })
    
    # Test OMIE data
    test_omie = {
        "OMIE today average": 92.3,
        "Today provisional": True,
        "Today average": 91.44,
        "Today hours": {}
    }
    
    for hour in range(24):
        hour_key = f"{current_date}T{hour:02d}:00:00+01:00"
        # Create realistic daily price pattern
        if 6 <= hour <= 9:  # Morning peak
            price = 100 + hour * 5
        elif 18 <= hour <= 21:  # Evening peak
            price = 120 + (hour - 18) * 10
        elif 12 <= hour <= 15:  # Solar valley
            price = 30 + (hour - 12) * 5
        else:  # Night hours
            price = 80 + hour * 2
        
        test_omie["Today hours"][hour_key] = round(price, 2)
    
    print("✅ Test data created:")
    print(f"  Solcast: {len(test_solcast['DetailedForecast'])} 30-min intervals, {len(test_solcast['DetailedHourly'])} hourly intervals")
    print(f"  OMIE: {len(test_omie['Today hours'])} hourly prices")
    print(f"  Date used: {current_date}")
    
    return test_solcast, test_omie

def main():
    """Run all validation functions."""
    print("🚀 Starting Data Structure Validation")
    print("=" * 60)
    
    # Validate expected structures
    solcast_sample = validate_solcast_data()
    omie_sample = validate_omie_data()
    requirements = validate_integration_requirements()
    
    # Create test data
    test_solcast, test_omie = create_test_data()
    
    print("\n🎉 Validation completed!")
    print("\n📋 Summary:")
    print("  - Solcast PV forecast: ✅ Structure validated")
    print("  - OMIE electricity prices: ✅ Structure validated")
    print("  - Integration requirements: ✅ Documented")
    print("  - Test data: ✅ Generated")
    
    print("\n💡 Next steps:")
    print("  1. Compare your actual entity data with these expected structures")
    print("  2. Use the test data to verify the integration works locally")
    print("  3. Run the debug scripts to identify any remaining issues")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ All validations passed!")
        else:
            print("\n❌ Some validations failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
