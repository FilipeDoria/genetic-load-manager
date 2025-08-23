import numpy as np
import matplotlib.pyplot as plt
from genetic_algorithm import GeneticAlgorithmLocal
from data_simulation import simulate_pv_forecast, simulate_load_forecast, simulate_pricing, simulate_battery_soc

def plot_schedules(solution, pv_forecast, total_load, device1_load, device2_load, vehicle_load, unmanaged_load, pricing, num_devices):
    """Plot device schedules, PV forecast, total load, and individual load profiles."""
    plt.figure(figsize=(12, 8))
    time = np.arange(96) * 15 / 60  # Hours
    for d in range(num_devices):
        plt.plot(time, solution[d], label=f"Device {d} Schedule", linewidth=1.5)
    plt.plot(time, pv_forecast, label="PV Forecast", linestyle="--", color="orange", linewidth=2)
    plt.plot(time, total_load, label="Total Forecasted Load", linestyle="--", color="green", linewidth=2.5)
    plt.plot(time, device1_load, label="Device 1 Load", linestyle=":", color="blue", alpha=0.7)
    plt.plot(time, device2_load, label="Device 2 Load", linestyle=":", color="red", alpha=0.7)
    plt.plot(time, vehicle_load, label="Vehicle Charger Load", linestyle=":", color="purple", alpha=0.7)
    plt.plot(time, unmanaged_load, label="Unmanaged Load", linestyle=":", color="gray", alpha=0.7)
    plt.xlabel("Time (hours)")
    plt.ylabel("Power (kWh) or Schedule (0/1)")
    plt.legend()
    plt.grid(True)
    plt.savefig("schedules.png")
    plt.close()

# Configuration parameters (matching Home Assistant inputs)
config = {
    "population_size": 100,
    "generations": 200,
    "mutation_rate": 0.05,
    "crossover_rate": 0.8,
    "num_devices": 3,  # Device 1, Device 2, Vehicle Charger
    "time_slots": 96,
    "battery_capacity": 10.0,
    "max_charge_rate": 2.0,
    "max_discharge_rate": 2.0,
    "binary_control": True,  # On/off schedules
    "device_priorities": [1.0, 0.8, 0.9]  # Priorities for Device 1, Device 2, Vehicle Charger
}

# Simulate input data
pv_forecast = simulate_pv_forecast(time_slots=config["time_slots"])
total_load, device1_load, device2_load, vehicle_load, unmanaged_load = simulate_load_forecast(time_slots=config["time_slots"])
pricing = simulate_pricing(time_slots=config["time_slots"])
battery_soc = simulate_battery_soc()

# Log input data to file
with open("inputs.txt", "w") as f:
    f.write(f"PV forecast: {pv_forecast.tolist()}\n")
    f.write(f"Total load forecast: {total_load.tolist()}\n")
    f.write(f"Device 1 load: {device1_load.tolist()}\n")
    f.write(f"Device 2 load: {device2_load.tolist()}\n")
    f.write(f"Vehicle charger load: {vehicle_load.tolist()}\n")
    f.write(f"Unmanaged load: {unmanaged_load.tolist()}\n")
    f.write(f"Pricing: {pricing.tolist()}\n")
    f.write(f"Battery SoC: {battery_soc}\n")

# Run optimization
ga = GeneticAlgorithmLocal(**config)
best_solution, best_fitness = ga.optimize(pv_forecast, total_load, pricing, battery_soc)

# Check if optimization was successful
if best_solution is not None:
    # Plot schedules
    plot_schedules(best_solution, pv_forecast, total_load, device1_load, device2_load, vehicle_load, unmanaged_load, pricing, config["num_devices"])

    # Output results
    print(f"\nBest fitness: {best_fitness:.2f}")
    for d in range(config["num_devices"]):
        print(f"Best schedule for device {d}: {best_solution[d].tolist()}")
else:
    print("Optimization failed - no solution found")