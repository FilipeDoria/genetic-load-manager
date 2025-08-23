import matplotlib.pyplot as plt
import re

def read_inputs(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    return content

def parse_data(content):
    pv_forecast = []
    load_forecast = []
    pricing = []
    battery_soc = 0.0
    
    for line in content:
        if 'PV forecast:' in line:
            pv_forecast = [float(x) for x in re.findall(r'\d+\.\d+', line)]
        elif 'Load forecast:' in line:
            load_forecast = [float(x) for x in re.findall(r'\d+\.\d+', line)]
        elif 'Pricing:' in line:
            pricing = [float(x) for x in re.findall(r'\d+\.\d+', line)]
        elif 'Battery SoC:' in line:
            battery_soc = float(re.search(r'\d+\.\d+', line).group())
    
    return pv_forecast, load_forecast, pricing, battery_soc

def calculate_battery_soc(pv_forecast, load_forecast, initial_soc):
    soc = [initial_soc]
    battery_capacity_kwh = 20.0  # Battery capacity in kWh
    
    for i in range(len(pv_forecast)):
        # Calculate net power (PV - Load)
        net_power_kw = pv_forecast[i] - load_forecast[i]
        # Update SoC based on net power (simplified model)
        # Power in kW over 15 minutes (0.25 hours) affects SoC as a fraction of capacity
        soc_change_percent = (net_power_kw * 0.25 / battery_capacity_kwh) * 100.0
        new_soc = soc[-1] + soc_change_percent
        # Limit SoC between 0 and 100 percent
        new_soc = max(0.0, min(100.0, new_soc))
        soc.append(new_soc)
    
    return soc[:-1]  # Return SoC for the same number of time steps as forecasts

def plot_forecasts(pv_forecast, load_forecast, pricing, battery_soc_initial):
    # 96 steps for 24 hours, each step is 15 minutes
    hours = [i * 0.25 for i in range(len(pv_forecast))]  # Convert to hours
    battery_soc = calculate_battery_soc(pv_forecast, load_forecast, battery_soc_initial)
    
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    # Plot PV and Load forecasts on the first y-axis
    ax1.set_xlabel('Time (Hours)')
    ax1.set_ylabel('Power (kW)', color='tab:blue')
    ax1.plot(hours, pv_forecast, label='PV Forecast', color='tab:green')
    ax1.plot(hours, load_forecast, label='Load Forecast', color='tab:red')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.legend(loc='upper left')
    
    # Create a second y-axis for pricing and battery SoC
    ax2 = ax1.twinx()
    ax2.set_ylabel('Price / Battery SoC (%)', color='tab:purple')
    ax2.plot(hours, pricing, label='Pricing', color='tab:purple')
    ax2.plot(hours, battery_soc, label='Battery SoC', color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:purple')
    ax2.legend(loc='upper right')
    
    plt.title('PV Forecast, Load Forecast, Pricing, and Battery SoC Over 24 Hours')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('local_GA_EMHASS/forecasts_plot.png')
    plt.show()

def main():
    content = read_inputs('local_GA_EMHASS/inputs.txt')
    pv_forecast, load_forecast, pricing, battery_soc = parse_data(content)
    plot_forecasts(pv_forecast, load_forecast, pricing, battery_soc)

if __name__ == '__main__':
    main()
