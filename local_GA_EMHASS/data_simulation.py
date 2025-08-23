import numpy as np
from datetime import datetime, timedelta

def simulate_pv_forecast(time_slots=96):
    """Simulate PV forecast as a 96-slot array in kWh, mimicking Solcast's pv_estimate for a single 24-hour period."""
    # TODO: Integrate real weather data or historical PV data for more accurate simulation
    # Placeholder for weather impact on PV output
    weather_factor = get_weather_factor()  # Placeholder function for weather data
    current_time = datetime.now().replace(second=0, microsecond=0)
    pv = np.zeros(time_slots)
    # Generate 48 slots (30-minute intervals) for today and tomorrow
    today_forecast = np.zeros(48)
    tomorrow_forecast = np.zeros(48)
    for t in range(48):
        hour = (t // 2) % 24
        if 6 <= hour <= 18:
            base_pv = 2.0 * np.sin(np.pi * (hour - 6) / 12) + np.random.uniform(0, 0.1)
            today_forecast[t] = base_pv * weather_factor[t % 24]  # Adjust based on hourly weather
            tomorrow_forecast[t] = base_pv * weather_factor[t % 24]  # Same for tomorrow for simplicity
        else:
            today_forecast[t] = np.random.uniform(0, 0.05)
            tomorrow_forecast[t] = np.random.uniform(0, 0.05)
    # Combine into a single 24-hour forecast (96 slots, 15-minute intervals)
    start_slot = int((current_time.hour * 60 + current_time.minute) / 30)  # 30-minute slots
    for t in range(time_slots):
        time_hour = current_time + timedelta(minutes=15 * t)
        hour = time_hour.hour + time_hour.minute / 60
        if time_hour.date() == current_time.date():
            # Use today's forecast until midnight
            idx = int((hour - current_time.hour) * 2)  # 30-minute slots
            if 0 <= idx < 48:
                pv[t] = today_forecast[idx]
            else:
                pv[t] = 0.0  # Fallback for edge cases
        else:
            # Use tomorrow's forecast after midnight
            idx = int((hour + (24 - current_time.hour)) * 2)
            if 0 <= idx < 48:
                pv[t] = tomorrow_forecast[idx]
            else:
                pv[t] = 0.0
        # Interpolate to 15-minute intervals
        if t % 2 == 1 and t > 0:
            pv[t] = (pv[t] + pv[t-1]) / 2
    return pv

# Placeholder function for weather data
def get_weather_factor():
    """Simulate a weather factor for PV output adjustment (e.g., cloud cover impact)."""
    # TODO: Replace with actual weather API or data source
    return np.random.uniform(0.5, 1.0, 24)  # Random factor between 50% and 100% for each hour

def simulate_device_load(time_slots=96, peak_hours=(18, 22), base_load=0.3, peak_load=0.8):
    """Simulate load for a controllable device (e.g., Device 1 or 2)."""
    # TODO: Incorporate user behavior patterns or historical load data for realism
    user_behavior_factor = get_user_behavior_factor()  # Placeholder function for user behavior data
    load = np.zeros(time_slots)
    for t in range(time_slots):
        hour = (datetime.now().hour + t // 4) % 24
        base_load_value = base_load + np.random.uniform(-0.05, 0.05)
        peak_load_value = peak_load + np.random.uniform(-0.1, 0.1)
        if peak_hours[0] <= hour <= peak_hours[1]:
            load[t] = peak_load_value * user_behavior_factor[hour]  # Adjust based on user behavior
        else:
            load[t] = base_load_value * user_behavior_factor[hour]  # Adjust based on user behavior
    return load

# Placeholder function for user behavior data
def get_user_behavior_factor():
    """Simulate a user behavior factor for load adjustment (e.g., usage patterns)."""
    # TODO: Replace with actual user data or historical patterns
    return np.random.uniform(0.8, 1.2, 24)  # Random factor between 80% and 120% for each hour

def simulate_vehicle_charger_load(time_slots=96):
    """Simulate vehicle charger load (Device X) with evening charging."""
    load = np.zeros(time_slots)
    for t in range(time_slots):
        hour = (datetime.now().hour + t // 4) % 24
        if 20 <= hour <= 23:  # Charging from 20:00 to 23:00
            load[t] = 3.5 + np.random.uniform(-0.3, 0.3)  # ~3.5 kW charger
        else:
            load[t] = 0.0
    return load

def simulate_unmanaged_load(time_slots=96):
    """Simulate unmanaged loads (e.g., lighting, appliances) with low constant demand."""
    load = np.zeros(time_slots)
    for t in range(time_slots):
        hour = (datetime.now().hour + t // 4) % 24
        if 6 <= hour <= 22:  # Active during waking hours
            load[t] = 0.4 + np.random.uniform(-0.1, 0.1)
        else:
            load[t] = 0.1 + np.random.uniform(-0.05, 0.05)
    return load

def simulate_load_forecast(time_slots=96):
    """Simulate total load forecast as the sum of device loads and unmanaged loads."""
    device1_load = simulate_device_load(time_slots, peak_hours=(18, 22), base_load=0.3, peak_load=0.8)
    device2_load = simulate_device_load(time_slots, peak_hours=(17, 21), base_load=0.2, peak_load=0.6)
    vehicle_load = simulate_vehicle_charger_load(time_slots)
    unmanaged_load = simulate_unmanaged_load(time_slots)
    total_load = device1_load + device2_load + vehicle_load + unmanaged_load
    return total_load, device1_load, device2_load, vehicle_load, unmanaged_load

def simulate_pricing(time_slots=96):
    """Simulate dynamic pricing as a 96-slot array in currency per kWh."""
    pricing = np.full(time_slots, 0.1)
    for t in range(time_slots):
        hour = (datetime.now().hour + t // 4) % 24
        if 17 <= hour <= 21:
            pricing[t] = 0.2 + np.random.uniform(0, 0.05)
    return pricing

def simulate_battery_soc():
    """Simulate initial battery state of charge in percentage."""
    return np.random.uniform(20, 80)