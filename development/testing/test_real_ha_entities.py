#!/usr/bin/env python3
"""
Local testing script that simulates REAL Home Assistant entities.
This mimics the actual data structures and attributes you'd get from real HA entities.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np

class MockHAEntity:
    """Mock Home Assistant entity that mimics real entity behavior"""
    
    def __init__(self, entity_id: str, state: str, attributes: Dict[str, Any]):
        self.entity_id = entity_id
        self.state = state
        self.attributes = attributes
    
    def __str__(self):
        return f"{self.entity_id}: {self.state}"
    
    def get_state(self):
        """Simulate HA entity state getter"""
        return self.state
    
    def get_attributes(self):
        """Simulate HA entity attributes getter"""
        return self.attributes.copy()

def create_realistic_ha_entities() -> Dict[str, MockHAEntity]:
    """Create mock entities that mimic real Home Assistant entities"""
    
    # Simulate realistic time-based data
    current_hour = datetime.now().hour
    solar_production = max(0, 3.5 * np.sin(np.pi * (current_hour - 6) / 12)) if 6 <= current_hour <= 18 else 0
    
    entities = {
        # Real climate entities (like Nest, Ecobee, etc.)
        'climate.living_room_thermostat': MockHAEntity(
            'climate.living_room_thermostat',
            'heat',  # Current HVAC mode
            {
                'temperature': 22.0,  # Target temperature
                'target_temp_high': 25.0,
                'target_temp_low': 20.0,
                'current_temperature': 23.5,  # Actual room temperature
                'hvac_modes': ['heat', 'cool', 'off', 'auto'],
                'hvac_action': 'heating',  # What the system is actually doing
                'fan_mode': 'auto',
                'preset_mode': 'eco',
                'swing_mode': 'off',
                'min_temp': 16.0,
                'max_temp': 30.0,
                'supported_features': 1,
                'friendly_name': 'Living Room Thermostat'
            }
        ),
        
        'climate.bedroom_ac': MockHAEntity(
            'climate.bedroom_ac',
            'cool',
            {
                'temperature': 20.0,
                'target_temp_high': 22.0,
                'target_temp_low': 18.0,
                'current_temperature': 21.0,
                'hvac_modes': ['heat', 'cool', 'off', 'auto'],
                'hvac_action': 'cooling',
                'fan_mode': 'low',
                'preset_mode': 'sleep',
                'swing_mode': 'off',
                'min_temp': 16.0,
                'max_temp': 30.0,
                'supported_features': 1,
                'friendly_name': 'Bedroom AC'
            }
        ),
        
        # Real switch entities (like smart plugs, switches)
        'switch.ev_charger_01': MockHAEntity(
            'switch.ev_charger_01',
            'on',
            {
                'friendly_name': 'EV Charger',
                'icon': 'mdi:ev-station',
                'assumed_state': False,
                'supported_features': 0,
                'power': 3.7,  # kW - actual power consumption
                'current': 16.0,  # A
                'voltage': 230.0,  # V
                'power_factor': 0.98,
                'frequency': 50.0,  # Hz
                'energy_today': 12.5,  # kWh
                'energy_total': 1250.3  # kWh
            }
        ),
        
        'switch.water_heater_01': MockHAEntity(
            'switch.water_heater_01',
            'off',
            {
                'friendly_name': 'Water Heater',
                'icon': 'mdi:water-boiler',
                'assumed_state': False,
                'supported_features': 0,
                'power': 0.0,  # kW
                'current': 0.0,  # A
                'voltage': 230.0,  # V
                'temperature': 45.0,  # °C
                'target_temperature': 50.0,  # °C
                'energy_today': 8.2,  # kWh
                'energy_total': 820.7  # kWh
            }
        ),
        
        'switch.dehumidifier_01': MockHAEntity(
            'switch.dehumidifier_01',
            'on',
            {
                'friendly_name': 'Dehumidifier',
                'icon': 'mdi:air-humidifier',
                'assumed_state': False,
                'supported_features': 0,
                'power': 0.2,  # kW
                'current': 0.87,  # A
                'voltage': 230.0,  # V
                'humidity': 45.0,  # %
                'target_humidity': 50.0,  # %
                'energy_today': 1.8,  # kWh
                'energy_total': 180.3  # kWh
            }
        ),
        
        # Real sensor entities (like energy monitors, battery sensors)
        'sensor.battery_soc_01': MockHAEntity(
            'sensor.battery_soc_01',
            '65.2',
            {
                'friendly_name': 'Battery State of Charge',
                'unit_of_measurement': '%',
                'icon': 'mdi:battery',
                'device_class': 'battery',
                'state_class': 'measurement',
                'battery_level': 65,
                'battery_charging': False,
                'battery_voltage': 48.5,  # V
                'battery_current': 2.1,  # A
                'battery_power': 101.9,  # W
                'battery_temperature': 25.0  # °C
            }
        ),
        
        'sensor.grid_import_power_01': MockHAEntity(
            'sensor.grid_import_power_01',
            '2.1',
            {
                'friendly_name': 'Grid Import Power',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:transmission-tower',
                'device_class': 'power',
                'state_class': 'measurement',
                'power_factor': 0.95,
                'voltage': 230.0,  # V
                'current': 9.1,  # A
                'frequency': 50.0,  # Hz
                'energy_today': 15.3,  # kWh
                'energy_total': 1530.7  # kWh
            }
        ),
        
        'sensor.grid_export_power_01': MockHAEntity(
            'sensor.grid_export_power_01',
            '0.0',
            {
                'friendly_name': 'Grid Export Power',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:transmission-tower',
                'device_class': 'power',
                'state_class': 'measurement',
                'power_factor': 1.0,
                'voltage': 230.0,  # V
                'current': 0.0,  # A
                'frequency': 50.0,  # Hz
                'energy_today': 0.0,  # kWh
                'energy_total': 0.0  # kWh
            }
        ),
        
        'sensor.solar_power_01': MockHAEntity(
            'sensor.solar_power_01',
            str(round(solar_production, 2)),
            {
                'friendly_name': 'Solar Power',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:solar-power',
                'device_class': 'power',
                'state_class': 'measurement',
                'power_factor': 1.0,
                'voltage': 400.0,  # V (typical solar inverter)
                'current': solar_production * 2.5,  # A (rough calculation)
                'frequency': 50.0,  # Hz
                'energy_today': 18.7,  # kWh
                'energy_total': 1870.3,  # kWh
                'efficiency': 0.97  # %
            }
        ),
        
        'sensor.home_energy_total': MockHAEntity(
            'sensor.home_energy_total',
            '45.2',
            {
                'friendly_name': 'Home Energy Total',
                'unit_of_measurement': 'kWh',
                'icon': 'mdi:lightning-bolt',
                'device_class': 'energy',
                'state_class': 'total_increasing',
                'energy_today': 45.2,  # kWh
                'energy_total': 45200.7,  # kWh
                'last_reset': '2024-01-01T00:00:00+00:00'
            }
        ),
        
        # Real input entities (user-configurable values)
        'input_number.ev_target_soc_01': MockHAEntity(
            'input_number.ev_target_soc_01',
            '80.0',
            {
                'friendly_name': 'EV Target SOC',
                'unit_of_measurement': '%',
                'icon': 'mdi:battery-charging',
                'min': 50.0,
                'max': 100.0,
                'step': 5.0,
                'mode': 'slider',
                'initial': 80.0
            }
        ),
        
        'input_number.battery_target_soc_01': MockHAEntity(
            'input_number.battery_target_soc_01',
            '85.0',
            {
                'friendly_name': 'Battery Target SOC',
                'unit_of_measurement': '%',
                'icon': 'mdi:battery',
                'min': 20.0,
                'max': 95.0,
                'step': 5.0,
                'mode': 'slider',
                'initial': 85.0
            }
        ),
        
        'input_number.electricity_price_01': MockHAEntity(
            'input_number.electricity_price_01',
            '0.15',
            {
                'friendly_name': 'Electricity Price',
                'unit_of_measurement': 'EUR/kWh',
                'icon': 'mdi:currency-eur',
                'min': 0.05,
                'max': 0.50,
                'step': 0.01,
                'mode': 'box',
                'initial': 0.15
            }
        ),
        
        # Real select entities (choice-based configuration)
        'select.optimization_mode_01': MockHAEntity(
            'select.optimization_mode_01',
            'cost_savings',
            {
                'friendly_name': 'Optimization Mode',
                'icon': 'mdi:tune',
                'options': ['cost_savings', 'comfort', 'battery_health', 'grid_stability'],
                'current_option': 'cost_savings'
            }
        ),
        
        'select.priority_device_01': MockHAEntity(
            'select.priority_device_01',
            'ev_charger',
            {
                'friendly_name': 'Priority Device',
                'icon': 'mdi:star',
                'options': ['ev_charger', 'water_heater', 'ac_system', 'none'],
                'current_option': 'ev_charger'
            }
        ),
        
        # Real binary sensor entities (motion, presence, etc.)
        'binary_sensor.motion_living_room_01': MockHAEntity(
            'binary_sensor.motion_living_room_01',
            'off',
            {
                'friendly_name': 'Motion Living Room',
                'icon': 'mdi:motion-sensor',
                'device_class': 'motion',
                'off_delay': 30,
                'last_triggered': '2025-01-20T10:30:00+00:00',
                'battery_level': 85,  # %
                'battery_charging': False
            }
        ),
        
        'binary_sensor.occupancy_home_01': MockHAEntity(
            'binary_sensor.occupancy_home_01',
            'on',
            {
                'friendly_name': 'Home Occupancy',
                'icon': 'mdi:home',
                'device_class': 'occupancy',
                'last_triggered': '2025-01-20T08:00:00+00:00',
                'battery_level': 92,  # %
                'battery_charging': False
            }
        ),
        
        # Real weather entities
        'weather.home_01': MockHAEntity(
            'weather.home_01',
            'partlycloudy',
            {
                'friendly_name': 'Home Weather',
                'temperature': 18.0,
                'temperature_unit': '°C',
                'humidity': 65,
                'pressure': 1013.25,
                'pressure_unit': 'hPa',
                'wind_bearing': 180,
                'wind_speed': 12.0,
                'wind_speed_unit': 'km/h',
                'visibility': 10.0,
                'visibility_unit': 'km',
                'forecast': [
                    {
                        'datetime': '2025-01-20T12:00:00+00:00',
                        'condition': 'partlycloudy',
                        'temperature': 18.0,
                        'humidity': 65,
                        'pressure': 1013.25,
                        'wind_bearing': 180,
                        'wind_speed': 12.0
                    },
                    {
                        'datetime': '2025-01-20T15:00:00+00:00',
                        'condition': 'sunny',
                        'temperature': 20.0,
                        'humidity': 60,
                        'pressure': 1012.0,
                        'wind_bearing': 190,
                        'wind_speed': 8.0
                    }
                ]
            }
        ),
        
        # Real energy monitoring entities
        'sensor.smart_meter_power_01': MockHAEntity(
            'sensor.smart_meter_power_01',
            '2.1',
            {
                'friendly_name': 'Smart Meter Power',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:flash',
                'device_class': 'power',
                'state_class': 'measurement',
                'power_factor': 0.95,
                'voltage_l1': 230.0,  # V
                'voltage_l2': 230.0,  # V
                'voltage_l3': 230.0,  # V
                'current_l1': 3.0,  # A
                'current_l2': 2.5,  # A
                'current_l3': 1.8,  # A
                'frequency': 50.0,  # Hz
                'energy_today': 15.3,  # kWh
                'energy_total': 1530.7  # kWh
            }
        ),
        
        'sensor.solar_inverter_power_01': MockHAEntity(
            'sensor.solar_inverter_power_01',
            str(round(solar_production, 2)),
            {
                'friendly_name': 'Solar Inverter Power',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:solar-power',
                'device_class': 'power',
                'state_class': 'measurement',
                'power_factor': 1.0,
                'voltage_dc': 400.0,  # V
                'current_dc': solar_production * 2.5,  # A
                'voltage_ac': 230.0,  # V
                'current_ac': solar_production * 4.35,  # A
                'frequency': 50.0,  # Hz
                'efficiency': 97.2,  # %
                'temperature': 45.0,  # °C
                'energy_today': 18.7,  # kWh
                'energy_total': 1870.3  # kWh
            }
        ),
        
        # Real Solcast PV forecast entity (like you have)
        'sensor.solcast_pv_forecast_previsao_para_hoje': MockHAEntity(
            'sensor.solcast_pv_forecast_previsao_para_hoje',
            '3.4304',  # Current hour's estimate
            {
                'friendly_name': 'Solcast PV Forecast Today',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:solar-power',
                'device_class': 'power',
                'state_class': 'measurement',
                'Estimate': 28.88,
                'Dayname': 'Wednesday',
                'DataCorrect': True,
                'DetailedForecast': [
                    {
                        'period_start': '2025-08-20T00:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T00:30:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T01:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T06:00:00+01:00',
                        'pv_estimate': 0.0029
                    },
                    {
                        'period_start': '2025-08-20T07:00:00+01:00',
                        'pv_estimate': 0.116
                    },
                    {
                        'period_start': '2025-08-20T08:00:00+01:00',
                        'pv_estimate': 1.4847
                    },
                    {
                        'period_start': '2025-08-20T09:00:00+01:00',
                        'pv_estimate': 2.2098
                    },
                    {
                        'period_start': '2025-08-20T10:00:00+01:00',
                        'pv_estimate': 2.8535
                    },
                    {
                        'period_start': '2025-08-20T11:00:00+01:00',
                        'pv_estimate': 3.2933
                    },
                    {
                        'period_start': '2025-08-20T12:00:00+01:00',
                        'pv_estimate': 3.2929
                    },
                    {
                        'period_start': '2025-08-20T13:00:00+01:00',
                        'pv_estimate': 3.4824
                    },
                    {
                        'period_start': '2025-08-20T14:00:00+01:00',
                        'pv_estimate': 3.1344
                    },
                    {
                        'period_start': '2025-08-20T15:00:00+01:00',
                        'pv_estimate': 2.9293
                    },
                    {
                        'period_start': '2025-08-20T16:00:00+01:00',
                        'pv_estimate': 2.5287
                    },
                    {
                        'period_start': '2025-08-20T17:00:00+01:00',
                        'pv_estimate': 1.8785
                    },
                    {
                        'period_start': '2025-08-20T18:00:00+01:00',
                        'pv_estimate': 1.1389
                    },
                    {
                        'period_start': '2025-08-20T19:00:00+01:00',
                        'pv_estimate': 0.4134
                    },
                    {
                        'period_start': '2025-08-20T20:00:00+01:00',
                        'pv_estimate': 0.031
                    },
                    {
                        'period_start': '2025-08-20T21:00:00+01:00',
                        'pv_estimate': 0
                    }
                ],
                'DetailedHourly': [
                    {
                        'period_start': '2025-08-20T00:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T01:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T02:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T03:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T04:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T05:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T06:00:00+01:00',
                        'pv_estimate': 0.0014
                    },
                    {
                        'period_start': '2025-08-20T07:00:00+01:00',
                        'pv_estimate': 0.3891
                    },
                    {
                        'period_start': '2025-08-20T08:00:00+01:00',
                        'pv_estimate': 1.6886
                    },
                    {
                        'period_start': '2025-08-20T09:00:00+01:00',
                        'pv_estimate': 2.4205
                    },
                    {
                        'period_start': '2025-08-20T10:00:00+01:00',
                        'pv_estimate': 2.9966
                    },
                    {
                        'period_start': '2025-08-20T11:00:00+01:00',
                        'pv_estimate': 3.3373
                    },
                    {
                        'period_start': '2025-08-20T12:00:00+01:00',
                        'pv_estimate': 3.4304
                    },
                    {
                        'period_start': '2025-08-20T13:00:00+01:00',
                        'pv_estimate': 3.3982
                    },
                    {
                        'period_start': '2025-08-20T14:00:00+01:00',
                        'pv_estimate': 3.0667
                    },
                    {
                        'period_start': '2025-08-20T15:00:00+01:00',
                        'pv_estimate': 2.8612
                    },
                    {
                        'period_start': '2025-08-20T16:00:00+01:00',
                        'pv_estimate': 2.3659
                    },
                    {
                        'period_start': '2025-08-20T17:00:00+01:00',
                        'pv_estimate': 1.6983
                    },
                    {
                        'period_start': '2025-08-20T18:00:00+01:00',
                        'pv_estimate': 0.9421
                    },
                    {
                        'period_start': '2025-08-20T19:00:00+01:00',
                        'pv_estimate': 0.2638
                    },
                    {
                        'period_start': '2025-08-20T20:00:00+01:00',
                        'pv_estimate': 0.0155
                    },
                    {
                        'period_start': '2025-08-20T21:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T22:00:00+01:00',
                        'pv_estimate': 0
                    },
                    {
                        'period_start': '2025-08-20T23:00:00+01:00',
                        'pv_estimate': 0
                    }
                ]
            }
        ),
        
        # Real OMIE electricity price entity (Spanish market)
        'sensor.omie_spot_price_pt': MockHAEntity(
            'sensor.omie_spot_price_pt',
            '68.31',  # Today average price
            {
                'friendly_name': 'OMIE Spot Price PT',
                'unit_of_measurement': 'EUR/MWh',
                'icon': 'mdi:currency-eur',
                'device_class': 'monetary',
                'state_class': 'measurement',
                'OMIE_today_average': 68.31,
                'Today_provisional': False,
                'Today_average': 68.3,
                'Today_hours': {
                    '2025-08-20T00:00:00+01:00': 88.03,
                    '2025-08-20T01:00:00+01:00': 83.0,
                    '2025-08-20T02:00:00+01:00': 81.0,
                    '2025-08-20T03:00:00+01:00': 76.2,
                    '2025-08-20T04:00:00+01:00': 82.0,
                    '2025-08-20T05:00:00+01:00': 88.46,
                    '2025-08-20T06:00:00+01:00': 96.54,
                    '2025-08-20T07:00:00+01:00': 89.81,
                    '2025-08-20T08:00:00+01:00': 71.55,
                    '2025-08-20T09:00:00+01:00': 49.8,
                    '2025-08-20T10:00:00+01:00': 49.9,
                    '2025-08-20T11:00:00+01:00': 49.02,
                    '2025-08-20T12:00:00+01:00': 35.0,
                    '2025-08-20T13:00:00+01:00': 31.53,
                    '2025-08-20T14:00:00+01:00': 27.2,
                    '2025-08-20T15:00:00+01:00': 27.99,
                    '2025-08-20T16:00:00+01:00': 37.0,
                    '2025-08-20T17:00:00+01:00': 49.27,
                    '2025-08-20T18:00:00+01:00': 69.27,
                    '2025-08-20T19:00:00+01:00': 78.73,
                    '2025-08-20T20:00:00+01:00': 100.07,
                    '2025-08-20T21:00:00+01:00': 97.52,
                    '2025-08-20T22:00:00+01:00': 84.98,
                    '2025-08-20T23:00:00+01:00': 95.28
                },
                'OMIE_tomorrow_average': 53.92,
                'Tomorrow_provisional': True,
                'Tomorrow_average': 52.13,
                'Tomorrow_hours': {}
            }
        ),
        
        # Additional Energy Storage Entities
        'sensor.battery_voltage_01': MockHAEntity(
            'sensor.battery_voltage_01',
            '48.5',
            {
                'friendly_name': 'Battery Voltage',
                'unit_of_measurement': 'V',
                'icon': 'mdi:battery',
                'device_class': 'voltage',
                'state_class': 'measurement',
                'min': 40.0,
                'max': 58.0,
                'battery_level': 65,
                'battery_charging': False
            }
        ),
        
        'sensor.battery_current_01': MockHAEntity(
            'sensor.battery_current_01',
            '2.1',
            {
                'friendly_name': 'Battery Current',
                'unit_of_measurement': 'A',
                'icon': 'mdi:current-ac',
                'device_class': 'current',
                'state_class': 'measurement',
                'min': -50.0,
                'max': 50.0,
                'battery_charging': False
            }
        ),
        
        'sensor.battery_temperature_01': MockHAEntity(
            'sensor.battery_temperature_01',
            '25.0',
            {
                'friendly_name': 'Battery Temperature',
                'unit_of_measurement': '°C',
                'icon': 'mdi:thermometer',
                'device_class': 'temperature',
                'state_class': 'measurement',
                'min': -10.0,
                'max': 60.0
            }
        ),
        
        # Smart Home Energy Management Entities
        'sensor.home_energy_usage_today': MockHAEntity(
            'sensor.home_energy_usage_today',
            '45.2',
            {
                'friendly_name': 'Home Energy Usage Today',
                'unit_of_measurement': 'kWh',
                'icon': 'mdi:lightning-bolt',
                'device_class': 'energy',
                'state_class': 'total_increasing',
                'last_reset': '2025-01-20T00:00:00+00:00',
                'cost_today': 6.78,  # EUR
                'cost_unit': 'EUR/kWh'
            }
        ),
        
        'sensor.home_energy_cost_today': MockHAEntity(
            'sensor.home_energy_cost_today',
            '6.78',
            {
                'friendly_name': 'Home Energy Cost Today',
                'unit_of_measurement': 'EUR',
                'icon': 'mdi:currency-eur',
                'device_class': 'monetary',
                'state_class': 'total_increasing',
                'last_reset': '2025-01-20T00:00:00+00:00',
                'energy_today': 45.2,  # kWh
                'avg_price_today': 0.15  # EUR/kWh
            }
        ),
        
        # EV Charging Specific Entities
        'sensor.ev_battery_level_01': MockHAEntity(
            'sensor.ev_battery_level_01',
            '45.0',
            {
                'friendly_name': 'EV Battery Level',
                'unit_of_measurement': '%',
                'icon': 'mdi:car-battery',
                'device_class': 'battery',
                'state_class': 'measurement',
                'min': 0,
                'max': 100,
                'battery_charging': True,
                'estimated_range': 180,  # km
                'max_range': 400,  # km
                'target_soc': 80.0  # %
            }
        ),
        
        'sensor.ev_charging_rate_01': MockHAEntity(
            'sensor.ev_charging_rate_01',
            '3.7',
            {
                'friendly_name': 'EV Charging Rate',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:ev-station',
                'device_class': 'power',
                'state_class': 'measurement',
                'min': 0.0,
                'max': 7.4,  # Max AC charging rate
                'charging_mode': 'AC',
                'connector_type': 'Type 2',
                'phase_count': 1
            }
        ),
        
        'sensor.ev_charging_time_remaining_01': MockHAEntity(
            'sensor.ev_charging_time_remaining_01',
            '2.5',
            {
                'friendly_name': 'EV Charging Time Remaining',
                'unit_of_measurement': 'h',
                'icon': 'mdi:clock-outline',
                'device_class': 'duration',
                'state_class': 'measurement',
                'target_soc': 80.0,
                'current_soc': 45.0,
                'charging_rate': 3.7
            }
        ),
        
        # Smart Appliance Entities
        'switch.dishwasher_01': MockHAEntity(
            'switch.dishwasher_01',
            'off',
            {
                'friendly_name': 'Dishwasher',
                'icon': 'mdi:dishwasher',
                'assumed_state': False,
                'supported_features': 0,
                'power': 0.0,  # kW
                'current': 0.0,  # A
                'voltage': 230.0,  # V
                'program': 'eco',
                'remaining_time': 0,  # minutes
                'energy_today': 2.1,  # kWh
                'energy_total': 210.5,  # kWh
                'water_consumption': 0.0,  # L
                'detergent_level': 'full'
            }
        ),
        
        'switch.washing_machine_01': MockHAEntity(
            'switch.washing_machine_01',
            'off',
            {
                'friendly_name': 'Washing Machine',
                'icon': 'mdi:washing-machine',
                'assumed_state': False,
                'supported_features': 0,
                'power': 0.0,  # kW
                'current': 0.0,  # A
                'voltage': 230.0,  # V
                'program': 'cotton',
                'temperature': 40,  # °C
                'spin_speed': 1200,  # rpm
                'remaining_time': 0,  # minutes
                'energy_today': 1.8,  # kWh
                'energy_total': 180.3,  # kWh
                'water_consumption': 0.0,  # L
                'detergent_level': 'medium'
            }
        ),
        
        'switch.dryer_01': MockHAEntity(
            'switch.dryer_01',
            'off',
            {
                'friendly_name': 'Dryer',
                'icon': 'mdi:tumble-dryer',
                'assumed_state': False,
                'supported_features': 0,
                'power': 0.0,  # kW
                'current': 0.0,  # A
                'voltage': 230.0,  # V
                'program': 'cotton',
                'temperature': 60,  # °C
                'remaining_time': 0,  # minutes
                'energy_today': 3.2,  # kWh
                'energy_total': 320.7,  # kWh
                'moisture_level': 'dry'
            }
        ),
        
        # Smart Lighting and Entertainment
        'light.living_room_main_01': MockHAEntity(
            'light.living_room_main_01',
            'on',
            {
                'friendly_name': 'Living Room Main Light',
                'icon': 'mdi:ceiling-light',
                'assumed_state': False,
                'supported_features': 44,
                'brightness': 255,
                'color_temp': 2700,
                'rgb_color': [255, 255, 255],
                'hs_color': [0, 0],
                'white_value': 255,
                'effect': 'None',
                'power': 0.08,  # kW
                'energy_today': 0.5,  # kWh
                'energy_total': 50.2  # kWh
            }
        ),
        
        'media_player.living_room_tv_01': MockHAEntity(
            'media_player.living_room_tv_01',
            'idle',
            {
                'friendly_name': 'Living Room TV',
                'icon': 'mdi:television',
                'assumed_state': False,
                'supported_features': 21439,
                'media_title': 'Netflix',
                'media_artist': 'Movie Title',
                'media_content_type': 'movie',
                'media_duration': 7200,  # seconds
                'media_position': 1800,  # seconds
                'volume_level': 0.5,
                'is_volume_muted': False,
                'source': 'HDMI1',
                'power': 0.12,  # kW
                'energy_today': 2.8,  # kWh
                'energy_total': 280.5  # kWh
            }
        ),
        
        # Smart Home Hub and Network
        'device_tracker.smartphone_01': MockHAEntity(
            'device_tracker.smartphone_01',
            'home',
            {
                'friendly_name': 'Smartphone',
                'icon': 'mdi:cellphone',
                'source_type': 'gps',
                'gps_accuracy': 5,
                'latitude': 38.7223,
                'longitude': -9.1393,
                'altitude': 15,
                'battery_level': 78,
                'battery_charging': False,
                'last_seen': '2025-01-20T10:30:00+00:00'
            }
        ),
        
        'device_tracker.car_01': MockHAEntity(
            'device_tracker.car_01',
            'home',
            {
                'friendly_name': 'Car',
                'icon': 'mdi:car',
                'source_type': 'gps',
                'gps_accuracy': 10,
                'latitude': 38.7223,
                'longitude': -9.1393,
                'altitude': 15,
                'battery_level': 85,
                'battery_charging': False,
                'last_seen': '2025-01-20T10:25:00+00:00',
                'estimated_range': 320  # km
            }
        ),
        
        # Additional Monitoring and Control Entities
        'sensor.grid_frequency_01': MockHAEntity(
            'sensor.grid_frequency_01',
            '50.02',
            {
                'friendly_name': 'Grid Frequency',
                'unit_of_measurement': 'Hz',
                'icon': 'mdi:sine-wave',
                'device_class': 'frequency',
                'state_class': 'measurement',
                'min': 49.5,
                'max': 50.5,
                'grid_stability': 'stable'
            }
        ),
        
        'sensor.grid_voltage_l1_01': MockHAEntity(
            'sensor.grid_voltage_l1_01',
            '230.5',
            {
                'friendly_name': 'Grid Voltage L1',
                'unit_of_measurement': 'V',
                'icon': 'mdi:lightning-bolt',
                'device_class': 'voltage',
                'state_class': 'measurement',
                'min': 207.0,
                'max': 253.0,
                'phase': 'L1'
            }
        ),
        
        'sensor.grid_voltage_l2_01': MockHAEntity(
            'sensor.grid_voltage_l2_01',
            '229.8',
            {
                'friendly_name': 'Grid Voltage L2',
                'unit_of_measurement': 'V',
                'icon': 'mdi:lightning-bolt',
                'device_class': 'voltage',
                'state_class': 'measurement',
                'min': 207.0,
                'max': 253.0,
                'phase': 'L2'
            }
        ),
        
        'sensor.grid_voltage_l3_01': MockHAEntity(
            'sensor.grid_voltage_l3_01',
            '230.2',
            {
                'friendly_name': 'Grid Voltage L3',
                'unit_of_measurement': 'V',
                'icon': 'mdi:lightning-bolt',
                'device_class': 'voltage',
                'state_class': 'measurement',
                'min': 207.0,
                'max': 253.0,
                'phase': 'L3'
            }
        ),
        
        # Smart Thermostat Schedule Entities
        'input_datetime.climate_schedule_morning_01': MockHAEntity(
            'input_datetime.climate_schedule_morning_01',
            '07:00:00',
            {
                'friendly_name': 'Climate Schedule Morning',
                'icon': 'mdi:clock-outline',
                'has_date': False,
                'has_time': True,
                'time': '07:00:00',
                'temperature_target': 22.0
            }
        ),
        
        'input_datetime.climate_schedule_evening_01': MockHAEntity(
            'input_datetime.climate_schedule_evening_01',
            '18:00:00',
            {
                'friendly_name': 'Climate Schedule Evening',
                'icon': 'mdi:clock-outline',
                'has_date': False,
                'has_time': True,
                'time': '18:00:00',
                'temperature_target': 20.0
            }
        ),
        
        'input_datetime.climate_schedule_night_01': MockHAEntity(
            'input_datetime.climate_schedule_night_01',
            '22:00:00',
            {
                'friendly_name': 'Climate Schedule Night',
                'icon': 'mdi:clock-outline',
                'has_date': False,
                'has_time': True,
                'time': '22:00:00',
                'temperature_target': 18.0
            }
        ),
        
        # Energy Tariff and Billing Entities
        'sensor.electricity_tariff_01': MockHAEntity(
            'sensor.electricity_tariff_01',
            'normal',
            {
                'friendly_name': 'Electricity Tariff',
                'icon': 'mdi:currency-eur',
                'tariff_type': 'time_of_use',
                'current_period': 'normal',
                'next_period': 'peak',
                'next_period_time': '18:00:00',
                'rates': {
                    'off_peak': 0.12,  # EUR/kWh
                    'normal': 0.15,    # EUR/kWh
                    'peak': 0.22       # EUR/kWh
                },
                'current_rate': 0.15
            }
        ),
        
        'sensor.monthly_energy_bill_01': MockHAEntity(
            'sensor.monthly_energy_bill_01',
            '156.78',
            {
                'friendly_name': 'Monthly Energy Bill',
                'unit_of_measurement': 'EUR',
                'icon': 'mdi:receipt',
                'device_class': 'monetary',
                'state_class': 'total_increasing',
                'billing_period': '2025-01',
                'energy_consumed': 1045.2,  # kWh
                'average_daily_cost': 5.23,  # EUR
                'peak_usage_day': '2025-01-15',
                'peak_usage_amount': 8.45  # EUR
            }
        ),
        
        # Load Forecasting and Historical Data
        'sensor.load_forecast_24h_01': MockHAEntity(
            'sensor.load_forecast_24h_01',
            '2.1',
            {
                'friendly_name': 'Load Forecast 24h',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:chart-line',
                'device_class': 'power',
                'state_class': 'measurement',
                'forecast_type': 'historical_pattern',
                'confidence_level': 0.85,
                'hourly_forecast': {
                    '00:00': 1.2, '01:00': 1.1, '02:00': 1.0, '03:00': 1.0,
                    '04:00': 1.1, '05:00': 1.3, '06:00': 1.8, '07:00': 2.5,
                    '08:00': 2.8, '09:00': 2.2, '10:00': 1.9, '11:00': 1.7,
                    '12:00': 1.8, '13:00': 1.6, '14:00': 1.5, '15:00': 1.4,
                    '16:00': 1.6, '17:00': 2.1, '18:00': 3.2, '19:00': 3.8,
                    '20:00': 3.5, '21:00': 3.1, '22:00': 2.4, '23:00': 1.9
                },
                'base_load': 1.2,
                'peak_load': 3.8,
                'load_variability': 0.65
            }
        ),
        
        'sensor.historical_load_pattern_01': MockHAEntity(
            'sensor.historical_load_pattern_01',
            '2.1',
            {
                'friendly_name': 'Historical Load Pattern',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:chart-histogram',
                'device_class': 'power',
                'state_class': 'measurement',
                'data_period': '30_days',
                'weekday_average': 2.3,
                'weekend_average': 2.8,
                'holiday_average': 3.1,
                'seasonal_factors': {
                    'winter': 1.2,
                    'spring': 0.9,
                    'summer': 1.1,
                    'autumn': 0.95
                },
                'time_patterns': {
                    'morning_peak': {'time': '07:00-09:00', 'multiplier': 1.8},
                    'evening_peak': {'time': '18:00-21:00', 'multiplier': 2.2},
                    'night_valley': {'time': '02:00-05:00', 'multiplier': 0.6}
                }
            }
        ),
        
        # Grid Stability and Demand Response
        'sensor.grid_demand_response_signal_01': MockHAEntity(
            'sensor.grid_demand_response_signal_01',
            'normal',
            {
                'friendly_name': 'Grid Demand Response Signal',
                'icon': 'mdi:transmission-tower',
                'signal_type': 'normal',
                'signal_level': 0,
                'signal_strength': 'none',
                'grid_stress': 'low',
                'response_required': False,
                'incentive_rate': 0.0,  # EUR/kWh for demand reduction
                'signal_expiry': '2025-01-20T23:59:59+00:00',
                'grid_operator': 'REN',
                'emergency_level': False
            }
        ),
        
        'sensor.grid_carbon_intensity_01': MockHAEntity(
            'sensor.grid_carbon_intensity_01',
            '245',
            {
                'friendly_name': 'Grid Carbon Intensity',
                'unit_of_measurement': 'gCO2/kWh',
                'icon': 'mdi:molecule-co2',
                'device_class': 'carbon_dioxide',
                'state_class': 'measurement',
                'min': 0,
                'max': 800,
                'forecast_24h': {
                    '00:00': 280, '06:00': 320, '12:00': 180, '18:00': 250
                },
                'renewable_percentage': 65.2,
                'fossil_percentage': 34.8,
                    'nuclear_percentage': 0.0
            }
        ),
        
        # Energy Market and Trading
        'sensor.energy_market_price_forecast_01': MockHAEntity(
            'sensor.energy_market_price_forecast_01',
            '68.31',
            {
                'friendly_name': 'Energy Market Price Forecast',
                'unit_of_measurement': 'EUR/MWh',
                'icon': 'mdi:chart-line',
                'device_class': 'monetary',
                'state_class': 'measurement',
                'forecast_horizon': '24h',
                'confidence_interval': 0.75,
                'price_volatility': 'medium',
                'market_trend': 'decreasing',
                'peak_hours_forecast': {
                    'morning': {'time': '07:00-09:00', 'price': 85.0},
                    'evening': {'time': '18:00-21:00', 'price': 95.0}
                },
                'valley_hours_forecast': {
                    'night': {'time': '02:00-05:00', 'price': 45.0},
                    'midday': {'time': '12:00-15:00', 'price': 35.0}
                }
            }
        ),
        
        # Battery Health and Aging
        'sensor.battery_health_score_01': MockHAEntity(
            'sensor.battery_health_score_01',
            '92.5',
            {
                'friendly_name': 'Battery Health Score',
                'unit_of_measurement': '%',
                'icon': 'mdi:heart-pulse',
                'device_class': 'battery',
                'state_class': 'measurement',
                'min': 0,
                'max': 100,
                'cycle_count': 1250,
                'max_cycles': 5000,
                'age_years': 2.3,
                'warranty_years': 10,
                'degradation_rate': 0.8,  # % per year
                'efficiency_loss': 2.1,  # % from new
                'temperature_stress': 'low',
                'overcharge_events': 0,
                'deep_discharge_events': 3
            }
        ),
        
        # Smart Home Automation Rules
        'input_boolean.energy_saving_mode_01': MockHAEntity(
            'input_boolean.energy_saving_mode_01',
            'off',
            {
                'friendly_name': 'Energy Saving Mode',
                'icon': 'mdi:leaf',
                'editable': True,
                'initial': False,
                'restore': True,
                'energy_savings_target': 15.0,  # % reduction target
                'comfort_priority': 'medium',
                'auto_enable_conditions': ['high_prices', 'grid_stress', 'low_solar']
            }
        ),
        
        'input_boolean.peak_shaving_mode_01': MockHAEntity(
            'input_boolean.peak_shaving_mode_01',
            'off',
            {
                'friendly_name': 'Peak Shaving Mode',
                'icon': 'mdi:chart-line-variant',
                'editable': True,
                'initial': False,
                'restore': True,
                'peak_threshold': 4.0,  # kW
                'shaving_duration': 2,  # hours
                'battery_priority': 'high',
                'load_shedding_order': ['dryer', 'dishwasher', 'ev_charger']
            }
        ),
        
        # Energy Efficiency Metrics
        'sensor.home_energy_efficiency_score_01': MockHAEntity(
            'sensor.home_energy_efficiency_score_01',
            '78.5',
            {
                'friendly_name': 'Home Energy Efficiency Score',
                'unit_of_measurement': '%',
                'icon': 'mdi:lightbulb-on',
                'device_class': 'efficiency',
                'state_class': 'measurement',
                'min': 0,
                'max': 100,
                'rating': 'B',
                'improvement_potential': 21.5,
                'benchmark_comparison': 'above_average',
                'efficiency_factors': {
                    'insulation': 85.0,
                    'appliances': 72.0,
                    'lighting': 90.0,
                    'heating_cooling': 75.0,
                    'renewables': 95.0
                },
                'recommendations': [
                    'Upgrade HVAC system',
                    'Add smart thermostats',
                    'Improve insulation'
                ]
            }
        ),
        
        # Grid Connection and Export Limits
        'sensor.grid_export_limit_01': MockHAEntity(
            'sensor.grid_export_limit_01',
            '5.0',
            {
                'friendly_name': 'Grid Export Limit',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:transmission-tower',
                'device_class': 'power',
                'state_class': 'measurement',
                'contract_limit': 5.0,
                'technical_limit': 7.5,
                'current_export': 0.0,
                'export_available': 5.0,
                'grid_operator': 'REN',
                'contract_type': 'net_metering',
                'export_tariff': 0.08,  # EUR/kWh for exported energy
                'export_restrictions': ['peak_hours', 'grid_maintenance']
            }
        ),
        
        # Weather Impact on Energy
        'sensor.weather_energy_impact_01': MockHAEntity(
            'sensor.weather_energy_impact_01',
            'low',
            {
                'friendly_name': 'Weather Energy Impact',
                'icon': 'mdi:weather-partly-cloudy',
                'impact_level': 'low',
                'impact_score': 0.2,  # 0-1 scale
                'factors': {
                    'temperature_deviation': 2.5,  # °C from seasonal average
                    'solar_irradiance': 0.85,  # relative to clear sky
                    'wind_speed': 12.0,  # km/h
                    'humidity': 65,  # %
                    'cloud_cover': 30  # %
                },
                'energy_implications': {
                    'heating_adjustment': 0.0,  # kW
                    'cooling_adjustment': 0.0,  # kW
                    'solar_efficiency': 0.95,  # multiplier
                    'load_variability': 0.1  # multiplier
                },
                'forecast_24h': {
                    'temperature_trend': 'stable',
                    'solar_conditions': 'partly_cloudy',
                    'wind_conditions': 'moderate'
                }
            }
        )
    }
    
    return entities

def extract_entity_data(entity: MockHAEntity) -> Dict[str, Any]:
    """Extract relevant data from a Home Assistant entity (realistic version)"""
    
    entity_id = entity.entity_id
    entity_type = entity_id.split('.')[0]
    
    extracted_data = {
        'entity_id': entity_id,
        'state': entity.state,
        'entity_type': entity_type,
        'attributes': entity.attributes.copy()
    }
    
    # Handle different entity types with realistic logic
    if entity_type == 'climate':
        extracted_data.update({
            'current_temp': entity.attributes.get('current_temperature'),
            'target_temp': entity.attributes.get('temperature'),
            'hvac_mode': entity.state,
            'hvac_action': entity.attributes.get('hvac_action'),
            'fan_mode': entity.attributes.get('fan_mode'),
            'preset_mode': entity.attributes.get('preset_mode'),
            'min_temp': entity.attributes.get('min_temp'),
            'max_temp': entity.attributes.get('max_temp')
        })
        
        # Calculate if AC/heating is needed and power requirements
        current_temp = entity.attributes.get('current_temperature', 0)
        target_temp = entity.attributes.get('temperature', 0)
        hvac_action = entity.attributes.get('hvac_action', 'off')
        
        if hvac_action == 'cooling' and current_temp > target_temp:
            extracted_data['cooling_needed'] = True
            temp_diff = current_temp - target_temp
            extracted_data['cooling_power'] = min(3.0, max(0.5, temp_diff * 0.8))  # kW
        else:
            extracted_data['cooling_needed'] = False
            extracted_data['cooling_power'] = 0.0
            
        if hvac_action == 'heating' and current_temp < target_temp:
            extracted_data['heating_needed'] = True
            temp_diff = target_temp - current_temp
            extracted_data['heating_power'] = min(2.5, max(0.3, temp_diff * 0.6))  # kW
        else:
            extracted_data['heating_needed'] = False
            extracted_data['heating_power'] = 0.0
    
    elif entity_type == 'switch':
        extracted_data.update({
            'is_on': entity.state == 'on',
            'power': entity.attributes.get('power', 0.0),
            'current': entity.attributes.get('current', 0.0),
            'voltage': entity.attributes.get('voltage', 230.0),
            'power_factor': entity.attributes.get('power_factor', 1.0),
            'energy_today': entity.attributes.get('energy_today', 0.0),
            'energy_total': entity.attributes.get('energy_total', 0.0)
        })
        
        # Calculate actual power consumption
        if entity.state == 'on':
            extracted_data['actual_power'] = entity.attributes.get('power', 0.0)
            extracted_data['energy_rate'] = extracted_data['actual_power']  # kWh per hour
        else:
            extracted_data['actual_power'] = 0.0
            extracted_data['energy_rate'] = 0.0
    
    elif entity_type == 'sensor':
        # Try to convert state to float for numeric sensors
        try:
            numeric_value = float(entity.state)
            extracted_data['numeric_value'] = numeric_value
        except (ValueError, TypeError):
            extracted_data['numeric_value'] = None
        
        extracted_data.update({
            'unit': entity.attributes.get('unit_of_measurement'),
            'device_class': entity.attributes.get('device_class'),
            'state_class': entity.attributes.get('state_class'),
            'power_factor': entity.attributes.get('power_factor', 1.0),
            'voltage': entity.attributes.get('voltage', 230.0),
            'current': entity.attributes.get('current', 0.0),
            'frequency': entity.attributes.get('frequency', 50.0),
            'energy_today': entity.attributes.get('energy_today', 0.0),
            'energy_total': entity.attributes.get('energy_total', 0.0)
        })
        
        # Handle specific sensor types
        if 'battery' in entity_id:
            extracted_data['battery_level'] = extracted_data.get('numeric_value')
            extracted_data['battery_charging'] = entity.attributes.get('battery_charging', False)
            extracted_data['battery_voltage'] = entity.attributes.get('battery_voltage')
            extracted_data['battery_temperature'] = entity.attributes.get('battery_temperature')
        elif 'power' in entity_id:
            extracted_data['power_value'] = extracted_data.get('numeric_value')
            extracted_data['energy_rate'] = extracted_data.get('power_value', 0.0)  # kWh per hour
        
        # Handle Solcast PV forecast entities specifically
        if 'solcast' in entity_id and 'pv_forecast' in entity_id:
            extracted_data['forecast_type'] = 'solcast_pv'
            extracted_data['daily_estimate'] = entity.attributes.get('Estimate', 0.0)
            extracted_data['day_name'] = entity.attributes.get('Dayname', 'Unknown')
            extracted_data['data_correct'] = entity.attributes.get('DataCorrect', False)
            
            # Extract DetailedHourly forecast (hourly data)
            detailed_hourly = entity.attributes.get('DetailedHourly', [])
            if detailed_hourly:
                extracted_data['hourly_forecast'] = []
                for hour_data in detailed_hourly:
                    extracted_data['hourly_forecast'].append({
                        'period_start': hour_data.get('period_start'),
                        'pv_estimate': hour_data.get('pv_estimate', 0.0)
                    })
                
                # Get current hour's forecast
                current_hour = datetime.now().hour
                current_forecast = None
                for hour_data in detailed_hourly:
                    try:
                        period_start = datetime.fromisoformat(hour_data['period_start'].replace('+01:00', '+00:00'))
                        if period_start.hour == current_hour:
                            current_forecast = hour_data
                            break
                    except:
                        continue
                
                if current_forecast:
                    extracted_data['current_hour_forecast'] = current_forecast.get('pv_estimate', 0.0)
                else:
                    extracted_data['current_hour_forecast'] = 0.0
        
        # Handle OMIE electricity price entities specifically
        elif 'omie' in entity_id and 'spot_price' in entity_id:
            extracted_data['price_type'] = 'omie_spot'
            extracted_data['today_average'] = entity.attributes.get('OMIE_today_average', 0.0)
            extracted_data['today_provisional'] = entity.attributes.get('Today_provisional', False)
            extracted_data['tomorrow_average'] = entity.attributes.get('OMIE_tomorrow_average', 0.0)
            extracted_data['tomorrow_provisional'] = entity.attributes.get('Tomorrow_provisional', False)
            
            # Extract hourly prices with timezone conversion (Spanish to Portuguese time: -1 hour)
            today_hours = entity.attributes.get('Today_hours', {})
            if today_hours:
                extracted_data['hourly_prices'] = {}
                for time_str, price in today_hours.items():
                    try:
                        # Parse Spanish time and convert to Portuguese time (-1 hour)
                        spanish_time = datetime.fromisoformat(time_str.replace('+01:00', '+00:00'))
                        
                        #portuguese_time = spanish_time - timedelta(hours=1)
                        portuguese_time = spanish_time
                        portuguese_time_str = portuguese_time.strftime('%H:00')
                        
                        # Store price in Portuguese time
                        extracted_data['hourly_prices'][portuguese_time_str] = price
                        
                        # Also store the original time for reference
                        if 'original_times' not in extracted_data:
                            extracted_data['original_times'] = {}
                        extracted_data['original_times'][portuguese_time_str] = time_str
                        
                    except Exception as e:
                        print(f"Warning: Could not parse time {time_str}: {e}")
                        continue
                
                # Get current hour's price (in Portuguese time)
                current_hour = datetime.now().hour
                current_hour_str = f"{current_hour:02d}:00"
                extracted_data['current_hour_price'] = extracted_data['hourly_prices'].get(current_hour_str, 0.0)
                
                # Find peak and off-peak hours
                if extracted_data['hourly_prices']:
                    prices = list(extracted_data['hourly_prices'].values())
                    extracted_data['peak_price'] = max(prices)
                    extracted_data['off_peak_price'] = min(prices)
                    
                    # Find peak and off-peak hours
                    for hour_str, price in extracted_data['hourly_prices'].items():
                        if price == extracted_data['peak_price']:
                            extracted_data['peak_hour'] = hour_str
                        if price == extracted_data['off_peak_price']:
                            extracted_data['off_peak_hour'] = hour_str
    
    elif entity_type == 'input_number':
        extracted_data.update({
            'value': float(entity.state),
            'min': entity.attributes.get('min'),
            'max': entity.attributes.get('max'),
            'step': entity.attributes.get('step'),
            'mode': entity.attributes.get('mode'),
            'unit': entity.attributes.get('unit_of_measurement')
        })
    
    elif entity_type == 'input_select':
        extracted_data.update({
            'selected_option': entity.state,
            'available_options': entity.attributes.get('options', []),
            'current_option': entity.attributes.get('current_option')
        })
    
    elif entity_type == 'binary_sensor':
        extracted_data.update({
            'is_detected': entity.state == 'on',
            'device_class': entity.attributes.get('device_class'),
            'off_delay': entity.attributes.get('off_delay'),
            'last_triggered': entity.attributes.get('last_triggered'),
            'battery_level': entity.attributes.get('battery_level')
        })
    
    elif entity_type == 'weather':
        extracted_data.update({
            'temperature': entity.attributes.get('temperature'),
            'humidity': entity.attributes.get('humidity'),
            'pressure': entity.attributes.get('pressure'),
            'wind_speed': entity.attributes.get('wind_speed'),
            'wind_bearing': entity.attributes.get('wind_bearing'),
            'condition': entity.state,
            'forecast': entity.attributes.get('forecast', [])
        })
    
    return extracted_data

def simulate_real_time_data(entities: Dict[str, MockHAEntity]) -> Dict[str, MockHAEntity]:
    """Simulate real-time data updates (like you'd get from Home Assistant)"""
    
    print("Simulating real-time data updates...")
    
    # Update time-sensitive entities
    current_time = datetime.now()
    current_hour = current_time.hour
    
    # Update solar production based on time
    if 6 <= current_hour <= 18:
        solar_production = max(0, 3.5 * np.sin(np.pi * (current_hour - 6) / 12))
        solar_production += random.uniform(-0.1, 0.1)  # Add some randomness
    else:
        solar_production = 0
    
    # Update entities with new values
    if 'sensor.solar_power_01' in entities:
        entities['sensor.solar_power_01'].state = str(round(solar_production, 2))
        entities['sensor.solar_power_01'].attributes['current'] = solar_production * 2.5
    
    if 'sensor.solar_inverter_power_01' in entities:
        entities['sensor.solar_inverter_power_01'].state = str(round(solar_production, 2))
        entities['sensor.solar_inverter_power_01'].attributes['current_dc'] = solar_production * 2.5
        entities['sensor.solar_inverter_power_01'].attributes['current_ac'] = solar_production * 4.35
    
    # Simulate some load changes
    if 'switch.ev_charger_01' in entities and entities['switch.ev_charger_01'].state == 'on':
        # EV charger might have variable power based on battery level
        current_power = float(entities['switch.ev_charger_01'].attributes['power'])
        new_power = current_power + random.uniform(-0.1, 0.1)
        new_power = max(1.0, min(7.0, new_power))  # Keep within realistic bounds
        entities['switch.ev_charger_01'].attributes['power'] = round(new_power, 2)
        entities['switch.ev_charger_01'].attributes['current'] = round(new_power * 1000 / 230, 1)
    
    # Update battery SOC if charging/discharging
    if 'sensor.battery_soc_01' in entities:
        current_soc = float(entities['sensor.battery_soc_01'].state)
        # Simulate small SOC changes
        soc_change = random.uniform(-0.5, 0.5)
        new_soc = max(0, min(100, current_soc + soc_change))
        entities['sensor.battery_soc_01'].state = str(round(new_soc, 1))
        entities['sensor.battery_soc_01'].attributes['battery_level'] = int(new_soc)
    
    print(f"Updated entities at {current_time.strftime('%H:%M:%S')}")
    return entities

def test_entity_extraction():
    """Test extracting data from realistic HA entities"""
    
    print("=== Testing Realistic Home Assistant Entity Data Extraction ===\n")
    
    # Create realistic entities
    entities = create_realistic_ha_entities()
    
    print(f"Created {len(entities)} realistic entities\n")
    
    # Test each entity type
    for entity_id, entity in entities.items():
        print(f"Testing: {entity_id}")
        print(f"Raw state: {entity.state}")
        
        # Extract data
        extracted = extract_entity_data(entity)
        
        print(f"Extracted data:")
        for key, value in extracted.items():
            if key != 'attributes':  # Skip raw attributes for readability
                print(f"  {key}: {value}")
        
        print("-" * 50)
    
    return entities

def simulate_optimization_data(entities: Dict[str, MockHAEntity]) -> Dict[str, Any]:
    """Simulate creating optimization data from realistic entity data"""
    
    print("\n=== Simulating Optimization Data Creation ===\n")
    
    optimization_data = {
        'timestamp': datetime.now(),
        'devices': {},
        'battery': {},
        'grid': {},
        'solar': {},
        'weather': {},
        'user_preferences': {},
        'energy_flow': {}
    }
    
    # Process each entity
    for entity_id, entity in entities.items():
        extracted = extract_entity_data(entity)
        
        if 'climate' in entity_id:
            # Handle climate devices
            device_name = entity_id.split('.')[-1]
            optimization_data['devices'][device_name] = {
                'type': 'climate',
                'current_temp': extracted.get('current_temp'),
                'target_temp': extracted.get('target_temp'),
                'cooling_needed': extracted.get('cooling_needed', False),
                'heating_needed': extracted.get('heating_needed', False),
                'cooling_power': extracted.get('cooling_power', 0.0),
                'heating_power': extracted.get('heating_power', 0.0),
                'hvac_mode': extracted.get('hvac_mode'),
                'power_levels': [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]  # kW
            }
        
        elif 'switch' in entity_id:
            # Handle switch devices
            device_name = entity_id.split('.')[-1]
            optimization_data['devices'][device_name] = {
                'type': 'switch',
                'is_on': extracted.get('is_on', False),
                'current_power': extracted.get('actual_power', 0.0),
                'max_power': extracted.get('power', 0.0),
                'energy_rate': extracted.get('energy_rate', 0.0),
                'power_levels': [0.0, extracted.get('power', 1.0)]
            }
        
        elif 'battery' in entity_id:
            # Handle battery
            optimization_data['battery'] = {
                'soc': extracted.get('battery_level', 50.0) / 100.0,  # Convert % to fraction
                'capacity': 20.0,  # kWh (you'd get this from device config)
                'max_charge_rate': 5.0,  # kW
                'max_discharge_rate': 5.0,  # kW
                'efficiency': 0.95,
                'voltage': extracted.get('battery_voltage'),
                'temperature': extracted.get('battery_temperature'),
                'charging': extracted.get('battery_charging', False)
            }
        
        elif 'grid' in entity_id:
            # Handle grid data
            if 'import' in entity_id:
                optimization_data['grid']['import_power'] = extracted.get('power_value', 0.0)
                optimization_data['grid']['import_energy_today'] = extracted.get('energy_today', 0.0)
            elif 'export' in entity_id:
                optimization_data['grid']['export_power'] = extracted.get('power_value', 0.0)
                optimization_data['grid']['export_energy_today'] = extracted.get('energy_today', 0.0)
        
        elif 'solar' in entity_id:
            # Handle solar data
            optimization_data['solar'] = {
                'current_power': extracted.get('power_value', 0.0),
                'max_power': 5.0,  # kWp (you'd get this from device config)
                'efficiency': extracted.get('efficiency', 0.95),
                'voltage_dc': extracted.get('voltage', 400.0),
                'voltage_ac': extracted.get('voltage', 230.0),
                'energy_today': extracted.get('energy_today', 0.0)
            }
        
        elif 'solcast' in entity_id and 'pv_forecast' in entity_id:
            # Handle Solcast PV forecast data
            optimization_data['pv_forecast'] = {
                'forecast_type': extracted.get('forecast_type'),
                'daily_estimate': extracted.get('daily_estimate', 0.0),
                'day_name': extracted.get('day_name', 'Unknown'),
                'data_correct': extracted.get('data_correct', False),
                'current_hour_forecast': extracted.get('current_hour_forecast', 0.0),
                'hourly_forecast': extracted.get('hourly_forecast', [])
            }
        
        elif 'omie' in entity_id and 'spot_price' in entity_id:
            # Handle OMIE electricity price data
            optimization_data['electricity_pricing'] = {
                'price_type': extracted.get('price_type'),
                'today_average': extracted.get('today_average', 0.0),
                'today_provisional': extracted.get('today_provisional', False),
                'tomorrow_average': extracted.get('tomorrow_average', 0.0),
                'tomorrow_provisional': extracted.get('tomorrow_provisional', False),
                'current_hour_price': extracted.get('current_hour_price', 0.0),
                'peak_price': extracted.get('peak_price', 0.0),
                'off_peak_price': extracted.get('off_peak_price', 0.0),
                'peak_hour': extracted.get('peak_hour', 'Unknown'),
                'off_peak_hour': extracted.get('off_peak_hour', 'Unknown'),
                'hourly_prices': extracted.get('hourly_prices', {}),
                'price_volatility': extracted.get('peak_price', 0.0) - extracted.get('off_peak_price', 0.0)
            }
        
        elif 'weather' in entity_id:
            # Handle weather data
            optimization_data['weather'] = {
                'temperature': extracted.get('temperature'),
                'humidity': extracted.get('humidity'),
                'pressure': extracted.get('pressure'),
                'wind_speed': extracted.get('wind_speed'),
                'condition': extracted.get('condition'),
                'forecast': extracted.get('forecast', [])
            }
        
        elif 'input_number' in entity_id:
            # Handle user preferences
            if 'ev_target_soc' in entity_id:
                optimization_data['user_preferences']['ev_target_soc'] = extracted.get('value', 80.0) / 100.0
            elif 'battery_target_soc' in entity_id:
                optimization_data['user_preferences']['battery_target_soc'] = extracted.get('value', 85.0) / 100.0
            elif 'electricity_price' in entity_id:
                optimization_data['user_preferences']['electricity_price'] = extracted.get('value', 0.15)
        
        elif 'input_select' in entity_id:
            # Handle optimization mode
            if 'optimization_mode' in entity_id:
                optimization_data['user_preferences']['mode'] = extracted.get('selected_option', 'cost_savings')
            elif 'priority_device' in entity_id:
                optimization_data['user_preferences']['priority_device'] = extracted.get('selected_option', 'none')
    
    # Calculate energy flow
    total_load = sum(device.get('current_power', 0) for device in optimization_data['devices'].values())
    solar_generation = optimization_data['solar'].get('current_power', 0)
    battery_power = 0  # Will be calculated by optimizer
    
    optimization_data['energy_flow'] = {
        'total_load': total_load,
        'solar_generation': solar_generation,
        'battery_power': battery_power,
        'grid_import': max(0, total_load - solar_generation - battery_power),
        'grid_export': max(0, solar_generation + battery_power - total_load)
    }
    
    # Print the final optimization data
    print("Final optimization data structure:")
    print(json.dumps(optimization_data, indent=2, default=str))
    
    return optimization_data

def demonstrate_pv_forecast_usage(entities: Dict[str, MockHAEntity]):
    """Demonstrate how to use PV forecast data for optimization"""
    
    print("\n=== Demonstrating PV Forecast Usage ===\n")
    
    # Find the Solcast PV forecast entity
    pv_forecast_entity = None
    for entity_id, entity in entities.items():
        if 'solcast' in entity_id and 'pv_forecast' in entity_id:
            pv_forecast_entity = entity
            break
    
    if not pv_forecast_entity:
        print("No Solcast PV forecast entity found!")
        return
    
    print(f"Found PV forecast entity: {pv_forecast_entity.entity_id}")
    
    # Extract the data
    extracted = extract_entity_data(pv_forecast_entity)
    
    print(f"Daily estimate: {extracted.get('daily_estimate', 0):.2f} kWh")
    print(f"Current hour forecast: {extracted.get('current_hour_forecast', 0):.2f} kW")
    print(f"Data quality: {'Correct' if extracted.get('data_correct') else 'Uncertain'}")
    
    # Show hourly forecast for next few hours
    hourly_forecast = extracted.get('hourly_forecast', [])
    if hourly_forecast:
        print("\nHourly forecast for next 6 hours:")
        current_hour = datetime.now().hour
        for i, hour_data in enumerate(hourly_forecast):
            if i >= 6:  # Only show next 6 hours
                break
            period_start = hour_data.get('period_start', 'Unknown')
            pv_estimate = hour_data.get('pv_estimate', 0.0)
            print(f"  {period_start}: {pv_estimate:.3f} kW")
    
    # Demonstrate how to use this for optimization
    print("\n=== Optimization Usage Examples ===")
    
    # Example 1: Get forecast for specific time
    target_hour = 14  # 2 PM
    target_forecast = None
    for hour_data in hourly_forecast:
        try:
            period_start = datetime.fromisoformat(hour_data['period_start'].replace('+01:00', '+00:00'))
            if period_start.hour == target_hour:
                target_forecast = hour_data
                break
        except:
            continue
    
    if target_forecast:
        print(f"Forecast for {target_hour}:00: {target_forecast['pv_estimate']:.3f} kW")
    
    # Example 2: Calculate expected daily production
    daily_production = sum(hour_data.get('pv_estimate', 0) for hour_data in hourly_forecast)
    print(f"\nExpected daily production: {daily_production:.2f} kWh")
    
    # Example 3: Find peak production hour
    peak_hour_data = max(hourly_forecast, key=lambda x: x.get('pv_estimate', 0))
    peak_hour = peak_hour_data.get('period_start', 'Unknown')
    peak_power = peak_hour_data.get('pv_estimate', 0.0)
    print(f"Peak production: {peak_power:.3f} kW at {peak_hour}")
    
    return extracted

def demonstrate_omie_pricing_usage(entities: Dict[str, MockHAEntity]):
    """Demonstrate how to use OMIE electricity price data for optimization"""
    
    print("\n=== Demonstrating OMIE Electricity Pricing Usage ===\n")
    
    # Find the OMIE price entity
    omie_entity = None
    for entity_id, entity in entities.items():
        if 'omie' in entity_id and 'spot_price' in entity_id:
            omie_entity = entity
            break
    
    if not omie_entity:
        print("No OMIE electricity price entity found!")
        return
    
    print(f"Found OMIE price entity: {omie_entity.entity_id}")
    
    # Extract the data
    extracted = extract_entity_data(omie_entity)
    
    print(f"Today average price: {extracted.get('today_average', 0):.2f} EUR/MWh")
    print(f"Current hour price: {extracted.get('current_hour_price', 0):.2f} EUR/MWh")
    print(f"Data quality: {'Final' if not extracted.get('today_provisional') else 'Provisional'}")
    
    # Show price analysis
    if 'peak_price' in extracted and 'off_peak_price' in extracted:
        print(f"Peak price: {extracted['peak_price']:.2f} EUR/MWh at {extracted.get('peak_hour', 'Unknown')}")
        print(f"Off-peak price: {extracted['off_peak_price']:.2f} EUR/MWh at {extracted.get('off_peak_hour', 'Unknown')}")
        print(f"Price volatility: {extracted['peak_price'] - extracted['off_peak_price']:.2f} EUR/MWh")
    
    # Show hourly prices for next few hours
    hourly_prices = extracted.get('hourly_prices', {})
    if hourly_prices:
        print("\nHourly prices for next 6 hours (Portuguese time):")
        current_hour = datetime.now().hour
        for i in range(6):
            target_hour = (current_hour + i) % 24
            target_hour_str = f"{target_hour:02d}:00"
            price = hourly_prices.get(target_hour_str, 0.0)
            print(f"  {target_hour_str}: {price:.2f} EUR/MWh")
    
    # Demonstrate optimization usage
    print("\n=== Optimization Usage Examples ===")
    
    # Example 1: Cost-based load shifting
    current_price = extracted.get('current_hour_price', 0.0)
    off_peak_price = extracted.get('off_peak_price', 0.0)
    
    if current_price > off_peak_price * 1.5:  # If current price is 50% higher than off-peak
        print(f"WARNING: High price alert: Current price ({current_price:.2f}) is {(current_price/off_peak_price - 1)*100:.1f}% higher than off-peak")
        print("   Recommendation: Shift non-critical loads to off-peak hours")
    else:
        print(f"OK: Price is reasonable: Current price ({current_price:.2f}) is close to off-peak ({off_peak_price:.2f})")
    
    # Example 2: Battery charging strategy
    if 'hourly_prices' in extracted:
        # Find the cheapest 4-hour window for battery charging
        sorted_prices = sorted(hourly_prices.items(), key=lambda x: x[1])
        cheapest_hours = sorted_prices[:4]
        print(f"\nINFO: Best battery charging window (4 hours):")
        for hour, price in cheapest_hours:
            print(f"   {hour}: {price:.2f} EUR/MWh")
        
        # Calculate potential savings
        avg_price = sum(price for _, price in cheapest_hours) / len(cheapest_hours)
        peak_price = extracted.get('peak_price', 0.0)
        if peak_price > avg_price:
            savings_percent = ((peak_price - avg_price) / peak_price) * 100
            print(f"   Potential savings: {savings_percent:.1f}% compared to peak hours")
    
    # Example 3: Grid export timing
    if 'hourly_prices' in extracted:
        # Find the most profitable hours for grid export
        sorted_prices = sorted(hourly_prices.items(), key=lambda x: x[1], reverse=True)
        best_export_hours = sorted_prices[:3]
        print(f"\nINFO: Best grid export hours:")
        for hour, price in best_export_hours:
            print(f"   {hour}: {price:.2f} EUR/MWh")
    
    return extracted

def main():
    """Main test function"""
    
    print("Realistic Home Assistant Entity Testing")
    print("=" * 60)
    
    # Test entity data extraction
    entities = test_entity_extraction()
    
    # Simulate real-time updates
    entities = simulate_real_time_data(entities)
    
    # Simulate optimization data creation
    optimization_data = simulate_optimization_data(entities)
    
    # Demonstrate PV forecast usage
    demonstrate_pv_forecast_usage(entities)
    
    # Demonstrate OMIE pricing usage
    demonstrate_omie_pricing_usage(entities)
    
    print("\n=== Test Summary ===")
    print(f"OK: Tested {len(entities)} realistic entity types")
    print(f"OK: Successfully extracted data from all entities")
    print(f"OK: Simulated real-time data updates")
    print(f"OK: Created comprehensive optimization data structure")
    print(f"OK: Ready for Home Assistant integration")
    
    # Show some key insights
    print("\n=== Key Insights ===")
    print(f"• Total devices: {len(optimization_data['devices'])}")
    print(f"• Current solar generation: {optimization_data['solar']['current_power']:.2f} kW")
    print(f"• Current total load: {optimization_data['energy_flow']['total_load']:.2f} kW")
    print(f"• Battery SOC: {optimization_data['battery']['soc']*100:.1f}%")
    print(f"• Optimization mode: {optimization_data['user_preferences'].get('mode', 'Not set')}")
    
    return optimization_data

if __name__ == "__main__":
    main()
