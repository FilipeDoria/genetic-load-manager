#!/usr/bin/env python3
"""
Local testing script to simulate fetching data from Home Assistant entities.
This helps understand the data structure before integrating with Home Assistant.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Simulate Home Assistant entity states
class MockHAEntity:
    """Mock Home Assistant entity for testing"""
    
    def __init__(self, entity_id: str, state: str, attributes: Dict[str, Any]):
        self.entity_id = entity_id
        self.state = state
        self.attributes = attributes
    
    def __str__(self):
        return f"{self.entity_id}: {self.state}"

def create_mock_entities():
    """Create mock Home Assistant entities for testing"""
    
    entities = {
        # Climate entities (AC, thermostats)
        'climate.living_room': MockHAEntity(
            'climate.living_room',
            'heat',
            {
                'temperature': 22.0,
                'target_temp_high': 25.0,
                'target_temp_low': 20.0,
                'current_temperature': 23.5,
                'hvac_modes': ['heat', 'cool', 'off'],
                'hvac_action': 'heating',
                'fan_mode': 'auto',
                'preset_mode': 'eco'
            }
        ),
        
        # Switch entities (simple on/off devices)
        'switch.ev_charger': MockHAEntity(
            'switch.ev_charger',
            'on',
            {
                'friendly_name': 'EV Charger',
                'icon': 'mdi:ev-station',
                'assumed_state': False,
                'power': 3.7,  # kW
                'current': 16.0,  # A
                'voltage': 230.0  # V
            }
        ),
        
        'switch.water_heater': MockHAEntity(
            'switch.water_heater',
            'off',
            {
                'friendly_name': 'Water Heater',
                'icon': 'mdi:water-boiler',
                'assumed_state': False,
                'power': 0.0,  # kW
                'temperature': 45.0  # °C
            }
        ),
        
        # Sensor entities (measurements)
        'sensor.battery_soc': MockHAEntity(
            'sensor.battery_soc',
            '65.2',
            {
                'friendly_name': 'Battery State of Charge',
                'unit_of_measurement': '%',
                'icon': 'mdi:battery',
                'device_class': 'battery',
                'state_class': 'measurement'
            }
        ),
        
        'sensor.grid_import_power': MockHAEntity(
            'sensor.grid_import_power',
            '2.1',
            {
                'friendly_name': 'Grid Import Power',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:transmission-tower',
                'device_class': 'power',
                'state_class': 'measurement'
            }
        ),
        
        'sensor.grid_export_power': MockHAEntity(
            'sensor.grid_export_power',
            '0.0',
            {
                'friendly_name': 'Grid Export Power',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:transmission-tower',
                'device_class': 'power',
                'state_class': 'measurement'
            }
        ),
        
        'sensor.solar_power': MockHAEntity(
            'sensor.solar_power',
            '3.2',
            {
                'friendly_name': 'Solar Power',
                'unit_of_measurement': 'kW',
                'icon': 'mdi:solar-power',
                'device_class': 'power',
                'state_class': 'measurement'
            }
        ),
        
        # More complex entities
        'climate.bedroom': MockHAEntity(
            'climate.bedroom',
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
                'swing_mode': 'off'
            }
        ),
        
        'switch.dehumidifier': MockHAEntity(
            'switch.dehumidifier',
            'on',
            {
                'friendly_name': 'Dehumidifier',
                'icon': 'mdi:air-humidifier',
                'assumed_state': False,
                'power': 0.2,  # kW
                'humidity': 45.0,  # %
                'target_humidity': 50.0  # %
            }
        ),
        
        # Numeric input entities (user-configurable values)
        'input_number.ev_target_soc': MockHAEntity(
            'input_number.ev_target_soc',
            '80.0',
            {
                'friendly_name': 'EV Target SOC',
                'unit_of_measurement': '%',
                'icon': 'mdi:battery-charging',
                'min': 50.0,
                'max': 100.0,
                'step': 5.0,
                'mode': 'slider'
            }
        ),
        
        # Select entities (choice-based)
        'select.optimization_mode': MockHAEntity(
            'select.optimization_mode',
            'cost_savings',
            {
                'friendly_name': 'Optimization Mode',
                'icon': 'mdi:tune',
                'options': ['cost_savings', 'comfort', 'battery_health', 'grid_stability']
            }
        ),
        
        # Binary sensor entities (on/off states)
        'binary_sensor.motion_living_room': MockHAEntity(
            'binary_sensor.motion_living_room',
            'off',
            {
                'friendly_name': 'Motion Living Room',
                'icon': 'mdi:motion-sensor',
                'device_class': 'motion',
                'off_delay': 30
            }
        ),
        
        # Weather entities
        'weather.home': MockHAEntity(
            'weather.home',
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
                'forecast': [
                    {
                        'datetime': '2025-01-20T12:00:00+00:00',
                        'condition': 'partlycloudy',
                        'temperature': 18.0,
                        'humidity': 65
                    }
                ]
            }
        )
    }
    
    return entities

def extract_entity_data(entity: MockHAEntity) -> Dict[str, Any]:
    """Extract relevant data from a Home Assistant entity"""
    
    entity_id = entity.entity_id
    entity_type = entity_id.split('.')[0]
    
    extracted_data = {
        'entity_id': entity_id,
        'state': entity.state,
        'entity_type': entity_type,
        'attributes': entity.attributes.copy()
    }
    
    # Handle different entity types
    if entity_type == 'climate':
        extracted_data.update({
            'current_temp': entity.attributes.get('current_temperature'),
            'target_temp': entity.attributes.get('temperature'),
            'hvac_mode': entity.state,
            'hvac_action': entity.attributes.get('hvac_action'),
            'fan_mode': entity.attributes.get('fan_mode'),
            'preset_mode': entity.attributes.get('preset_mode')
        })
        
        # Calculate if AC is needed (simplified logic)
        current_temp = entity.attributes.get('current_temperature', 0)
        target_temp = entity.attributes.get('temperature', 0)
        if current_temp > target_temp + 1:  # 1°C buffer
            extracted_data['ac_needed'] = True
            extracted_data['cooling_power'] = min(2.0, (current_temp - target_temp) * 0.5)  # kW
        else:
            extracted_data['ac_needed'] = False
            extracted_data['cooling_power'] = 0.0
    
    elif entity_type == 'switch':
        extracted_data.update({
            'is_on': entity.state == 'on',
            'power': entity.attributes.get('power', 0.0),
            'current': entity.attributes.get('current', 0.0),
            'voltage': entity.attributes.get('voltage', 230.0)
        })
        
        # Calculate actual power consumption
        if entity.state == 'on':
            extracted_data['actual_power'] = entity.attributes.get('power', 0.0)
        else:
            extracted_data['actual_power'] = 0.0
    
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
            'state_class': entity.attributes.get('state_class')
        })
        
        # Handle specific sensor types
        if 'battery' in entity_id:
            extracted_data['battery_level'] = extracted_data.get('numeric_value')
        elif 'power' in entity_id:
            extracted_data['power_value'] = extracted_data.get('numeric_value')
    
    elif entity_type == 'input_number':
        extracted_data.update({
            'value': float(entity.state),
            'min': entity.attributes.get('min'),
            'max': entity.attributes.get('max'),
            'step': entity.attributes.get('step')
        })
    
    elif entity_type == 'select':
        extracted_data.update({
            'selected_option': entity.state,
            'available_options': entity.attributes.get('options', [])
        })
    
    elif entity_type == 'binary_sensor':
        extracted_data.update({
            'is_detected': entity.state == 'on',
            'device_class': entity.attributes.get('device_class')
        })
    
    elif entity_type == 'weather':
        extracted_data.update({
            'temperature': entity.attributes.get('temperature'),
            'humidity': entity.attributes.get('humidity'),
            'pressure': entity.attributes.get('pressure'),
            'wind_speed': entity.attributes.get('wind_speed'),
            'condition': entity.state
        })
    
    return extracted_data

def test_entity_data_extraction():
    """Test extracting data from different entity types"""
    
    print("=== Testing Home Assistant Entity Data Extraction ===\n")
    
    # Create mock entities
    entities = create_mock_entities()
    
    # Test each entity type
    for entity_id, entity in entities.items():
        print(f"Testing: {entity_id}")
        print(f"Raw state: {entity.state}")
        print(f"Raw attributes: {json.dumps(entity.attributes, indent=2)}")
        
        # Extract data
        extracted = extract_entity_data(entity)
        
        print(f"Extracted data:")
        for key, value in extracted.items():
            if key != 'attributes':  # Skip raw attributes for readability
                print(f"  {key}: {value}")
        
        print("-" * 50)
    
    return entities

def simulate_optimization_data(entities: Dict[str, MockHAEntity]) -> Dict[str, Any]:
    """Simulate creating optimization data from entity data"""
    
    print("\n=== Simulating Optimization Data Creation ===\n")
    
    optimization_data = {
        'timestamp': datetime.now(),
        'devices': {},
        'battery': {},
        'grid': {},
        'weather': {},
        'user_preferences': {}
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
                'ac_needed': extracted.get('ac_needed', False),
                'cooling_power': extracted.get('cooling_power', 0.0),
                'hvac_mode': extracted.get('hvac_mode'),
                'power_levels': [0.0, 0.5, 1.0, 1.5, 2.0]  # kW
            }
        
        elif 'switch' in entity_id:
            # Handle switch devices
            device_name = entity_id.split('.')[-1]
            optimization_data['devices'][device_name] = {
                'type': 'switch',
                'is_on': extracted.get('is_on', False),
                'current_power': extracted.get('actual_power', 0.0),
                'max_power': extracted.get('power', 0.0),
                'power_levels': [0.0, extracted.get('power', 1.0)]
            }
        
        elif 'battery' in entity_id:
            # Handle battery
            optimization_data['battery'] = {
                'soc': extracted.get('battery_level', 50.0) / 100.0,  # Convert % to fraction
                'capacity': 20.0,  # kWh (you'd get this from device config)
                'max_charge_rate': 5.0,  # kW
                'max_discharge_rate': 5.0,  # kW
                'efficiency': 0.95
            }
        
        elif 'grid' in entity_id:
            # Handle grid data
            if 'import' in entity_id:
                optimization_data['grid']['import_power'] = extracted.get('power_value', 0.0)
            elif 'export' in entity_id:
                optimization_data['grid']['export_power'] = extracted.get('power_value', 0.0)
        
        elif 'solar' in entity_id:
            # Handle solar data
            optimization_data['solar'] = {
                'current_power': extracted.get('power_value', 0.0),
                'max_power': 5.0  # kWp (you'd get this from device config)
            }
        
        elif 'weather' in entity_id:
            # Handle weather data
            optimization_data['weather'] = {
                'temperature': extracted.get('temperature'),
                'humidity': extracted.get('humidity'),
                'condition': extracted.get('condition')
            }
        
        elif 'input_number' in entity_id:
            # Handle user preferences
            if 'ev_target_soc' in entity_id:
                optimization_data['user_preferences']['ev_target_soc'] = extracted.get('value', 80.0) / 100.0
        
        elif 'select' in entity_id:
            # Handle optimization mode
            if 'optimization_mode' in entity_id:
                optimization_data['user_preferences']['mode'] = extracted.get('selected_option', 'cost_savings')
    
    # Print the final optimization data
    print("Final optimization data structure:")
    print(json.dumps(optimization_data, indent=2, default=str))
    
    return optimization_data

def main():
    """Main test function"""
    
    print("Home Assistant Entity Data Extraction Test")
    print("=" * 50)
    
    # Test entity data extraction
    entities = test_entity_data_extraction()
    
    # Simulate optimization data creation
    optimization_data = simulate_optimization_data(entities)
    
    print("\n=== Test Summary ===")
    print(f"✓ Tested {len(entities)} different entity types")
    print(f"✓ Successfully extracted data from all entities")
    print(f"✓ Created optimization data structure")
    print(f"✓ Ready for Home Assistant integration")
    
    return optimization_data

if __name__ == "__main__":
    main()
