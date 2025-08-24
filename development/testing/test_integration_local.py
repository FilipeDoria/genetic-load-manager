#!/usr/bin/env python3
"""
Local Testing Script for Genetic Load Manager Integration
Tests all components without requiring Home Assistant
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add the custom_components to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'custom_components'))

class MockHomeAssistant:
    """Mock Home Assistant instance for testing"""
    
    def __init__(self):
        self.states = {}
        self.services = {}
        self.config = {}
        self.logger = MockLogger()
    
    def states_get(self, entity_id: str):
        """Mock state getter"""
        return self.states.get(entity_id, MockState(entity_id, "unknown"))
    
    def states_set(self, entity_id: str, state: str, attributes: Dict[str, Any] = None):
        """Mock state setter"""
        self.states[entity_id] = MockState(entity_id, state, attributes or {})
    
    def service_call(self, domain: str, service: str, data: Dict[str, Any] = None):
        """Mock service caller"""
        service_key = f"{domain}.{service}"
        if service_key in self.services:
            return self.services[service_key](data or {})
        return None

class MockState:
    """Mock Home Assistant state object"""
    
    def __init__(self, entity_id: str, state: str, attributes: Dict[str, Any] = None):
        self.entity_id = entity_id
        self.state = state
        self.attributes = attributes or {}
    
    def get(self, key: str, default=None):
        """Get attribute value"""
        return self.attributes.get(key, default)

class MockLogger:
    """Mock logger for testing"""
    
    def info(self, msg: str):
        print(f"INFO: {msg}")
    
    def warning(self, msg: str):
        print(f"WARNING: {msg}")
    
    def error(self, msg: str):
        print(f"ERROR: {msg}")
    
    def debug(self, msg: str):
        print(f"DEBUG: {msg}")

def create_test_entities() -> Dict[str, MockState]:
    """Create test entities for integration testing"""
    
    entities = {}
    
    # PV Forecast Entity
    entities['sensor.solcast_pv_forecast'] = MockState(
        'sensor.solcast_pv_forecast',
        '3.2',
        {
            'friendly_name': 'Solcast PV Forecast',
            'unit_of_measurement': 'kW',
            'Estimate': 25.5,
            'DetailedHourly': [
                {'period_start': '2025-01-20T12:00:00+00:00', 'pv_estimate': 3.2},
                {'period_start': '2025-01-20T13:00:00+00:00', 'pv_estimate': 3.1},
                {'period_start': '2025-01-20T14:00:00+00:00', 'pv_estimate': 2.8}
            ]
        }
    )
    
    # Battery SOC Entity
    entities['sensor.battery_soc'] = MockState(
        'sensor.battery_soc',
        '65.0',
        {
            'friendly_name': 'Battery State of Charge',
            'unit_of_measurement': '%',
            'device_class': 'battery'
        }
    )
    
    # Grid Import Entity
    entities['sensor.grid_import_power'] = MockState(
        'sensor.grid_import_power',
        '2.1',
        {
            'friendly_name': 'Grid Import Power',
            'unit_of_measurement': 'kW',
            'device_class': 'power'
        }
    )
    
    return entities

def test_file_structure():
    """Test that all required files exist"""
    print("\n=== Testing File Structure ===")
    
    required_files = [
        '../../custom_components/genetic_load_manager/__init__.py',
        '../../custom_components/genetic_load_manager/manifest.json',
        '../../custom_components/genetic_load_manager/const.py',
        '../../custom_components/genetic_load_manager/config_flow.py',
        '../../custom_components/genetic_load_manager/services.yaml',
        '../../custom_components/genetic_load_manager/translations/en.json'
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"OK: {file_path}")
        else:
            print(f"MISSING: {file_path}")
            all_exist = False
    
    return all_exist

def test_constants_file():
    """Test that constants file can be loaded"""
    print("\n=== Testing Constants File ===")
    
    try:
        const_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'custom_components', 'genetic_load_manager', 'const.py'
        )
        
        if os.path.exists(const_file):
            with open(const_file, 'r') as f:
                content = f.read()
            
            # Check for basic constants
            required_constants = ['DOMAIN', 'CONF_POPULATION_SIZE', 'CONF_GENERATIONS']
            found_constants = []
            
            for constant in required_constants:
                if constant in content:
                    found_constants.append(constant)
                    print(f"OK: Found constant {constant}")
                else:
                    print(f"MISSING: Constant {constant}")
            
            print(f"Constants found: {len(found_constants)}/{len(required_constants)}")
            return len(found_constants) >= 2  # At least 2 out of 3
            
        else:
            print("ERROR: Constants file not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not read constants file: {e}")
        return False

def test_services_file():
    """Test that services file can be loaded"""
    print("\n=== Testing Services File ===")
    
    try:
        services_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'custom_components', 'genetic_load_manager', 'services.yaml'
        )
        
        if os.path.exists(services_file):
            with open(services_file, 'r') as f:
                content = f.read()
            
            # Check for required services
            required_services = [
                'start_optimization',
                'stop_optimization',
                'run_single_optimization'
            ]
            
            found_services = []
            for service in required_services:
                if service in content:
                    found_services.append(service)
                    print(f"OK: Found service {service}")
                else:
                    print(f"MISSING: Service {service}")
            
            print(f"Services found: {len(found_services)}/{len(required_services)}")
            return len(found_services) >= 2  # At least 2 out of 3
            
        else:
            print("ERROR: Services file not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not read services file: {e}")
        return False

def test_translations_file():
    """Test that translations file can be loaded"""
    print("\n=== Testing Translations File ===")
    
    try:
        translations_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'custom_components', 'genetic_load_manager', 'translations', 'en.json'
        )
        
        if os.path.exists(translations_file):
            with open(translations_file, 'r') as f:
                translations = json.load(f)
            
            # Check for required translation keys
            required_keys = ['config', 'options', 'entity', 'services']
            found_keys = []
            
            for key in required_keys:
                if key in translations:
                    found_keys.append(key)
                    print(f"OK: Found translation key {key}")
                else:
                    print(f"MISSING: Translation key {key}")
            
            print(f"Translation keys found: {len(found_keys)}/{len(required_keys)}")
            return len(found_keys) >= 3  # At least 3 out of 4
            
        else:
            print("ERROR: Translations file not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not read translations file: {e}")
        return False

def test_entity_processing():
    """Test entity data processing"""
    print("\n=== Testing Entity Processing ===")
    
    try:
        # Create test entities
        entities = create_test_entities()
        
        # Test entity data extraction
        for entity_id, entity in entities.items():
            print(f"OK: Processing entity: {entity_id}")
            print(f"   State: {entity.state}")
            print(f"   Attributes: {entity.attributes}")
        
        # Test data aggregation
        pv_forecast = entities['sensor.solcast_pv_forecast']
        battery_soc = entities['sensor.battery_soc']
        grid_import = entities['sensor.grid_import_power']
        
        # Create optimization data structure
        optimization_data = {
            'timestamp': datetime.now(),
            'pv_forecast': {
                'current_power': float(pv_forecast.state),
                'daily_estimate': pv_forecast.attributes.get('Estimate', 0.0),
                'hourly_forecast': pv_forecast.attributes.get('DetailedHourly', [])
            },
            'battery': {
                'soc': float(battery_soc.state) / 100.0,
                'capacity': 10.0,
                'max_charge_rate': 2.0,
                'max_discharge_rate': 2.0
            },
            'grid': {
                'import_power': float(grid_import.state),
                'export_power': 0.0
            }
        }
        
        print(f"OK: Created optimization data structure:")
        print(json.dumps(optimization_data, indent=2, default=str))
        
        return True
        
    except Exception as e:
        print(f"ERROR: Entity processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manifest_file():
    """Test that manifest file is valid"""
    print("\n=== Testing Manifest File ===")
    
    try:
        manifest_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'custom_components', 'genetic_load_manager', 'manifest.json'
        )
        
        if os.path.exists(manifest_file):
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Check for required manifest keys
            required_keys = ['domain', 'name', 'version', 'documentation']
            found_keys = []
            
            for key in required_keys:
                if key in manifest:
                    found_keys.append(key)
                    print(f"OK: Found manifest key {key}: {manifest[key]}")
                else:
                    print(f"MISSING: Manifest key {key}")
            
            print(f"Manifest keys found: {len(found_keys)}/{len(required_keys)}")
            return len(found_keys) >= 3  # At least 3 out of 4
            
        else:
            print("ERROR: Manifest file not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not read manifest file: {e}")
        return False

def main():
    """Main test function"""
    print("Genetic Load Manager - Local Integration Testing")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Constants File", test_constants_file),
        ("Services File", test_services_file),
        ("Translations File", test_translations_file),
        ("Entity Processing", test_entity_processing),
        ("Manifest File", test_manifest_file)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"ERROR: Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\nAll tests passed! Integration files are properly structured.")
    else:
        print(f"\n{total - passed} test(s) failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
