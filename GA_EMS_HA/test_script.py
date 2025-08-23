import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from data_creation import generate_test_data, EMSOptimizer

# Assuming the previous code for generate_test_dsata and EMSOptimizer is available.
# Paste or import them here if needed. For this script, we'll define them briefly or assume defined.

# [Insert the code from generate_test_data and EMSOptimizer class here]
# For brevity, assume they are defined above.

def visualize_ems_data(data, best_schedules, sim_results):
    """
    Visualize EMS parameters over the 24-hour day using matplotlib.
    
    Parameters:
    data (dict): Test data from generate_test_data.
    best_schedules (dict): Optimized schedules from EMSOptimizer.
    sim_results (tuple): From simulate_schedule: cost, pure_cost, penalty, soc, imported, exported.
    """
    times = data['times']
    hours = [t.hour for t in times]  # For x-axis
    
    total_cost, cost, penalty, soc, imported, exported = sim_results
    soc = soc[1:] / data['battery']['capacity']  # SOC fraction over time (after initial)
    
    # Calculate total controllable loads
    ctrl_loads = np.sum([best_schedules[dev['name']] for dev in data['devices']], axis=0)
    total_load = ctrl_loads + data['non_ctrl_loads']
    
    # Figure 1: Prices and PV Forecast
    fig1, ax1 = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax1[0].plot(hours, data['buy_prices'], label='Buy Price (EUR/kWh)', color='red')
    ax1[0].plot(hours, data['sell_prices'], label='Sell Price (EUR/kWh)', color='green')
    ax1[0].set_title('Electricity Prices')
    ax1[0].set_ylabel('Price (EUR/kWh)')
    ax1[0].legend()
    ax1[0].grid(True)
    
    ax1[1].plot(hours, data['pv_forecast'], label='PV Production (kW)', color='orange')
    ax1[1].set_title('PV Production Forecast')
    ax1[1].set_ylabel('Power (kW)')
    ax1[1].set_xlabel('Hour of Day')
    ax1[1].legend()
    ax1[1].grid(True)
    
    # Figure 2: Loads
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.plot(hours, data['non_ctrl_loads'], label='Non-Controllable Loads (kW)', color='gray')
    ax2.plot(hours, ctrl_loads, label='Controllable Loads (kW)', color='blue')
    ax2.plot(hours, total_load, label='Total Loads (kW)', color='black', linestyle='--')
    ax2.set_title('Load Profiles')
    ax2.set_ylabel('Power (kW)')
    ax2.set_xlabel('Hour of Day')
    ax2.legend()
    ax2.grid(True)
    
    # Figure 3: Battery
    fig3, ax3 = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax3[0].plot(hours, best_schedules['battery'], label='Battery Action (kW, +charge/-discharge)', color='purple')
    ax3[0].set_title('Battery Actions')
    ax3[0].set_ylabel('Power (kW)')
    ax3[0].legend()
    ax3[0].grid(True)
    
    ax3[1].plot(hours, soc, label='Battery SOC (fraction)', color='cyan')
    ax3[1].axhline(y=data['battery']['min_soc'], color='red', linestyle='--', label='Min SOC')
    ax3[1].axhline(y=data['battery']['max_soc'], color='green', linestyle='--', label='Max SOC')
    ax3[1].set_title('Battery State of Charge')
    ax3[1].set_ylabel('SOC')
    ax3[1].set_xlabel('Hour of Day')
    ax3[1].legend()
    ax3[1].grid(True)
    
    # Figure 4: Grid Interactions
    fig4, ax4 = plt.subplots(figsize=(12, 6))
    ax4.plot(hours, imported, label='Imported from Grid (kW)', color='red')
    ax4.plot(hours, exported, label='Exported to Grid (kW)', color='green')
    ax4.set_title('Grid Import/Export')
    ax4.set_ylabel('Power (kW)')
    ax4.set_xlabel('Hour of Day')
    ax4.legend()
    ax4.grid(True)
    
    # Figure 5: Individual Device Schedules
    num_devices = len(data['devices'])
    fig5, ax5 = plt.subplots(num_devices, 1, figsize=(12, 4 * num_devices), sharex=True)
    for i, dev in enumerate(data['devices']):
        ax5[i].step(hours, best_schedules[dev['name']], where='mid', label=f"{dev['name']} Power (kW)", color='blue')
        ax5[i].set_title(f"{dev['name']} Schedule")
        ax5[i].set_ylabel('Power (kW)')
        ax5[i].legend()
        ax5[i].grid(True)
    ax5[-1].set_xlabel('Hour of Day')
    
    # Display all figures
    plt.tight_layout()
    # plt.show()  # Uncomment to show plots if running locally
    # For REPL or script, save them if needed
    fig1.savefig('prices_pv.png')
    fig2.savefig('loads.png')
    fig3.savefig('battery.png')
    fig4.savefig('grid.png')
    fig5.savefig('devices.png')
    print("Plots saved as PNG files: prices_pv.png, loads.png, battery.png, grid.png, devices.png")
    print(f"Total Optimized Cost: {total_cost:.2f} EUR (Pure Cost: {cost:.2f}, Penalty: {penalty:.2f})")

# Main execution
if __name__ == "__main__":
    test_data = generate_test_data(start_date='2025-08-19')
    optimizer = EMSOptimizer(test_data)
    best_schedules, best_cost = optimizer.run_ga()
    sim_results = optimizer.simulate_schedule(best_schedules)
    visualize_ems_data(test_data, best_schedules, sim_results)