"""Entity creation utilities for EMS Testing integration."""

import yaml
from typing import List, Dict, Any

def generate_ha_configuration() -> str:
    """Generate Home Assistant configuration for EMS testing entities."""
    
    config = {
        'input_boolean': {
            'ev_charger': {
                'name': 'EV Charger',
                'icon': 'mdi:ev-station'
            },
            'water_heater': {
                'name': 'Water Heater', 
                'icon': 'mdi:water-boiler'
            },
            'dehumidifier': {
                'name': 'Dehumidifier',
                'icon': 'mdi:air-humidifier'
            }
        },
        
        'input_number': {
            'ev_target_soc': {
                'name': 'EV Target SOC',
                'min': 50,
                'max': 100,
                'step': 5,
                'unit_of_measurement': '%',
                'icon': 'mdi:battery-charging'
            },
            'battery_soc': {
                'name': 'Battery SOC',
                'min': 0,
                'max': 100,
                'step': 1,
                'unit_of_measurement': '%',
                'icon': 'mdi:battery'
            }
        },
        
        'input_select': {
            'optimization_mode': {
                'name': 'Optimization Mode',
                'options': [
                    'cost_savings',
                    'comfort', 
                    'battery_health',
                    'grid_stability'
                ],
                'icon': 'mdi:tune'
            }
        },
        
        'sensor': {
            'grid_import_power': {
                'platform': 'template',
                'sensors': {
                    'grid_import_power': {
                        'friendly_name': 'Grid Import Power',
                        'unit_of_measurement': 'kW',
                        'icon': 'mdi:transmission-tower',
                        'value_template': '{{ states("input_number.grid_import") | float }}'
                    }
                }
            },
            'grid_export_power': {
                'platform': 'template',
                'sensors': {
                    'grid_export_power': {
                        'friendly_name': 'Grid Export Power',
                        'unit_of_measurement': 'kW',
                        'icon': 'mdi:transmission-tower',
                        'value_template': '{{ states("input_number.grid_export") | float }}'
                    }
                }
            },
            'solar_power': {
                'platform': 'template',
                'sensors': {
                    'solar_power': {
                        'friendly_name': 'Solar Power',
                        'unit_of_measurement': 'kW',
                        'icon': 'mdi:solar-power',
                        'value_template': '{{ states("input_number.solar_power") | float }}'
                    }
                }
            }
        },
        
        'input_number': {
            'grid_import': {
                'name': 'Grid Import Power',
                'min': 0,
                'max': 10,
                'step': 0.1,
                'unit_of_measurement': 'kW',
                'icon': 'mdi:transmission-tower'
            },
            'grid_export': {
                'name': 'Grid Export Power',
                'min': 0,
                'max': 10,
                'step': 0.1,
                'unit_of_measurement': 'kW',
                'icon': 'mdi:transmission-tower'
            },
            'solar_power': {
                'name': 'Solar Power',
                'min': 0,
                'max': 10,
                'step': 0.1,
                'unit_of_measurement': 'kW',
                'icon': 'mdi:solar-power'
            }
        },
        
        'climate': {
            'platform': 'generic_thermostat',
            'name': 'Living Room AC',
            'heater': 'input_boolean.ac_heating',
            'target_sensor': 'input_number.room_temperature',
            'min_temp': 16,
            'max_temp': 30,
            'ac_mode': True,
            'target_temp': 22,
            'cold_tolerance': 0.5,
            'hot_tolerance': 0.5,
            'min_cycle_duration': '00:05:00'
        },
        
        'input_boolean': {
            'ac_heating': {
                'name': 'AC Heating',
                'icon': 'mdi:air-conditioner'
            }
        },
        
        'input_number': {
            'room_temperature': {
                'name': 'Room Temperature',
                'min': 10,
                'max': 40,
                'step': 0.5,
                'unit_of_measurement': '°C',
                'icon': 'mdi:thermometer'
            }
        }
    }
    
    # Convert to YAML string
    yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    return yaml_str

def generate_automation_examples() -> str:
    """Generate example automations for EMS testing."""
    
    automations = {
        'automation': [
            {
                'alias': 'Update Grid Import from Smart Meter',
                'description': 'Update grid import power from your smart meter',
                'trigger': {
                    'platform': 'time_pattern',
                    'minutes': '/5'  # Every 5 minutes
                },
                'action': {
                    'service': 'input_number.set_value',
                    'target': {
                        'entity_id': 'input_number.grid_import'
                    },
                    'data': {
                        'value': '{{ states("sensor.smart_meter_power") | float }}'
                    }
                }
            },
            {
                'alias': 'Update Solar Power from Inverter',
                'description': 'Update solar power from your inverter',
                'trigger': {
                    'platform': 'time_pattern',
                    'minutes': '/5'
                },
                'action': {
                    'service': 'input_number.set_value',
                    'target': {
                        'entity_id': 'input_number.solar_power'
                    },
                    'data': {
                        'value': '{{ states("sensor.solar_inverter_power") | float }}'
                    }
                }
            }
        ]
    }
    
    yaml_str = yaml.dump(automations, default_flow_style=False, sort_keys=False)
    return yaml_str

def create_setup_guide() -> str:
    """Create a setup guide for users."""
    
    guide = """
# EMS Testing Integration Setup Guide

## Step 1: Add Required Entities

Copy the following configuration to your `configuration.yaml`:

```yaml
# Add this to your configuration.yaml
{config}
```

## Step 2: Add Example Automations (Optional)

If you have smart meters or solar inverters, add these automations:

```yaml
# Add to your automations.yaml
{automations}
```

## Step 3: Restart Home Assistant

After adding the configuration, restart Home Assistant to create the entities.

## Step 4: Configure EMS Testing Integration

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "EMS Testing Integration"
4. Configure with your new entities

## Entity Mapping

The integration will automatically detect and use these entities:

- **EV Charger**: `input_boolean.ev_charger`
- **Water Heater**: `input_boolean.water_heater`
- **Battery SOC**: `input_number.battery_soc`
- **Grid Import**: `sensor.grid_import_power`
- **Grid Export**: `sensor.grid_export_power`
- **Solar Power**: `sensor.solar_power`
- **Room Temperature**: `input_number.room_temperature`
- **AC Control**: `climate.living_room_ac`

## Testing Your Setup

1. **Check Entities**: Go to Developer Tools > States to see all entities
2. **Test Controls**: Use the entities in your dashboard to simulate device states
3. **Monitor Logs**: Check the logs for EMS optimization results

## Customization

You can modify the entity names, ranges, and icons in the configuration above.
For real devices, replace the `input_*` entities with your actual device entities.
"""
    
    config = generate_ha_configuration()
    automations = generate_automation_examples()
    
    return guide.format(config=config, automations=automations)

if __name__ == "__main__":
    """Generate configuration files when run directly."""
    
    print("=== EMS Testing Integration Configuration Generator ===\n")
    
    # Generate configuration
    config = generate_ha_configuration()
    print("Configuration to add to configuration.yaml:")
    print("=" * 50)
    print(config)
    
    print("\n" + "=" * 50)
    print("Example automations (add to automations.yaml):")
    print("=" * 50)
    automations = generate_automation_examples()
    print(automations)
    
    print("\n" + "=" * 50)
    print("Setup Guide:")
    print("=" * 50)
    guide = create_setup_guide()
    print(guide)
    
    # Save to files
    with open('ha_configuration.yaml', 'w') as f:
        f.write(config)
    
    with open('ha_automations.yaml', 'w') as f:
        f.write(automations)
    
    with open('setup_guide.md', 'w') as f:
        f.write(guide)
    
    print("\nFiles saved:")
    print("- ha_configuration.yaml (add to configuration.yaml)")
    print("- ha_automations.yaml (add to automations.yaml)")
    print("- setup_guide.md (complete setup instructions)")
