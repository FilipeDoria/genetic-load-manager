#!/usr/bin/env python3
"""
Test script to validate Solcast integration and forecast data processing.
This script simulates the forecast data fetching and processing logic.
"""

import asyncio
import json
from datetime import datetime, timedelta
import numpy as np

def simulate_solcast_data():
    """Simulate Solcast forecast data structure."""
    # Simulate 30-minute interval data for 24 hours (48 data points)
    base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    solcast_data = []
    for i in range(48):  # 48 x 30-minute intervals = 24 hours
        period_end = base_time + timedelta(minutes=30 * i)
        
        # Simulate solar production (peak at noon, zero at night)
        hour = period_end.hour
        if 6 <= hour <= 18:  # Daytime hours
            # Peak at noon (hour 12), bell curve
            solar_factor = np.exp(-((hour - 12) ** 2) / 8)
            pv_estimate = 5000 * solar_factor  # Peak 5kW, in watts
        else:
            pv_estimate = 0  # Night time
        
        solcast_data.append({
            "period_end": period_end.isoformat(),
            "pv_estimate": round(pv_estimate, 2)
        })
    
    return solcast_data

def process_solcast_forecast(solcast_data, time_slots=96):
    """Process Solcast data to 96-slot (15-minute) horizon."""
    print(f"Processing {len(solcast_data)} Solcast data points to {time_slots} time slots...")
    
    # Extract times and values
    times = []
    values = []
    
    for item in solcast_data:
        if "period_end" in item and "pv_estimate" in item:
            try:
                # Parse time
                period_end = item["period_end"]
                time_obj = datetime.fromisoformat(period_end)
                times.append(time_obj)
                
                # Parse PV estimate (convert to kW if in watts)
                pv_estimate = item["pv_estimate"]
                if isinstance(pv_estimate, (int, float)):
                    # If value is > 100, assume it's in watts and convert to kW
                    if pv_estimate > 100:
                        pv_estimate = pv_estimate / 1000.0
                        print(f"Converted PV estimate from {item['pv_estimate']} W to {pv_estimate:.3f} kW")
                    values.append(pv_estimate)
                else:
                    values.append(0.0)
                    
            except (ValueError, TypeError) as e:
                print(f"Error parsing Solcast data point: {e}")
                continue
    
    print(f"Extracted {len(times)} valid time/value pairs")
    
    # Create 96-slot forecast array
    pv_forecast = np.zeros(time_slots)
    
    if times and values:
        # Align forecasts with current time
        current_time = datetime.now().replace(second=0, microsecond=0)
        slot_duration = timedelta(minutes=15)
        
        for t in range(time_slots):
            slot_time = current_time + t * slot_duration
            
            # Find the closest forecast time
            if times:
                closest_idx = min(range(len(times)), 
                               key=lambda i: abs(times[i] - slot_time))
                if closest_idx < len(values):
                    pv_forecast[t] = values[closest_idx]
                else:
                    pv_forecast[t] = 0.0
            else:
                pv_forecast[t] = 0.0
    
    return pv_forecast

def validate_forecast_data(pv_forecast):
    """Validate the processed forecast data."""
    print("\n=== Forecast Data Validation ===")
    print(f"Array length: {len(pv_forecast)} (expected: 96)")
    print(f"Non-zero values: {np.count_nonzero(pv_forecast)}")
    print(f"Percentage non-zero: {(np.count_nonzero(pv_forecast) / len(pv_forecast)) * 100:.1f}%")
    print(f"Value range: {np.min(pv_forecast):.3f} - {np.max(pv_forecast):.3f} kW")
    print(f"Mean value: {np.mean(pv_forecast):.3f} kW")
    
    # Check for expected solar pattern
    if len(pv_forecast) == 96:
        print("✓ Array length is correct (96 slots)")
    else:
        print("✗ Array length is incorrect")
    
    if np.count_nonzero(pv_forecast) > 0:
        print("✓ Contains non-zero values")
    else:
        print("✗ No non-zero values found")
    
    # Check if we have solar production during daytime hours
    daytime_slots = pv_forecast[24:72]  # Hours 6-18 (assuming 15-minute slots)
    if np.max(daytime_slots) > 0:
        print("✓ Daytime solar production detected")
    else:
        print("✗ No daytime solar production detected")

def main():
    """Main test function."""
    print("=== Solcast Integration Test ===")
    print(f"Test started at: {datetime.now()}")
    
    # Simulate Solcast data
    print("\n1. Simulating Solcast forecast data...")
    solcast_data = simulate_solcast_data()
    print(f"Generated {len(solcast_data)} simulated data points")
    
    # Show sample data
    print("\nSample data points:")
    for i, item in enumerate(solcast_data[:5]):
        print(f"  {i+1}: {item['period_end']} -> {item['pv_estimate']} W")
    print("  ...")
    
    # Process the data
    print("\n2. Processing Solcast data to 96-slot forecast...")
    pv_forecast = process_solcast_forecast(solcast_data)
    
    # Validate the results
    print("\n3. Validating processed forecast data...")
    validate_forecast_data(pv_forecast)
    
    # Show detailed breakdown
    print("\n4. Detailed time slot breakdown:")
    for hour in range(0, 24, 2):  # Show every 2 hours
        start_slot = hour * 4  # 4 slots per hour
        end_slot = start_slot + 4
        hour_avg = np.mean(pv_forecast[start_slot:end_slot])
        print(f"  Hour {hour:2d}:00 - {hour+2:2d}:00: {hour_avg:.3f} kW (slots {start_slot:2d}-{end_slot-1:2d})")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main()
