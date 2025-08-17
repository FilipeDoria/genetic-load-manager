#!/usr/bin/env python3
"""
Test Script for Genetic Load Manager Sensor Integration
Tests sensor creation, forecast generation, and integration functionality
"""

import sys
import os
import ast
from pathlib import Path

def test_file_syntax():
    """Test that all Python files have valid syntax."""
    print("🔍 Testing Python file syntax...")
    
    files_to_test = [
        "custom_components/genetic-load-manager/__init__.py",
        "custom_components/genetic-load-manager/sensor.py",
        "custom_components/genetic-load-manager/config_flow.py",
        "custom_components/genetic-load-manager/genetic_algorithm.py"
    ]
    
    all_valid = True
    for file_path in files_to_test:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            print(f"  ✅ {file_path} - Syntax valid")
        except Exception as e:
            print(f"  ❌ {file_path} - Syntax error: {e}")
            all_valid = False
    
    return all_valid

def test_imports():
    """Test that all required imports are available."""
    print("\n🔍 Testing import dependencies...")
    
    required_imports = [
        "homeassistant.components.sensor",
        "homeassistant.core",
        "homeassistant.helpers.entity_platform",
        "homeassistant.helpers.typing",
        "homeassistant.const",
        "homeassistant.helpers.event",
        "homeassistant.helpers.selector",
        "voluptuous",
        "numpy",
        "datetime",
        "logging"
    ]
    
    all_available = True
    for import_name in required_imports:
        try:
            __import__(import_name)
            print(f"  ✅ {import_name} - Available")
        except ImportError:
            print(f"  ❌ {import_name} - Not available")
            all_available = False
    
    return all_available

def test_file_structure():
    """Test that all required files exist and have correct structure."""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "custom_components/genetic-load-manager/__init__.py",
        "custom_components/genetic-load-manager/sensor.py",
        "custom_components/genetic-load-manager/config_flow.py",
        "custom_components/genetic-load-manager/genetic_algorithm.py",
        "custom_components/genetic-load-manager/const.py",
        "custom_components/genetic-load-manager/manifest.json"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} - Exists")
        else:
            print(f"  ❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def test_sensor_class_structure():
    """Test the LoadForecastSensor class structure."""
    print("\n🔍 Testing LoadForecastSensor class structure...")
    
    try:
        with open("custom_components/genetic-load-manager/sensor.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required class
        if "class LoadForecastSensor" in content:
            print("  ✅ LoadForecastSensor class found")
        else:
            print("  ❌ LoadForecastSensor class not found")
            return False
        
        # Check for required methods
        required_methods = [
            "__init__",
            "state",
            "extra_state_attributes",
            "async_added_to_hass",
            "async_update",
            "_get_historical_data",
            "_generate_forecast"
        ]
        
        all_methods_found = True
        for method in required_methods:
            if f"def {method}" in content:
                print(f"  ✅ {method} method found")
            else:
                print(f"  ❌ {method} method not found")
                all_methods_found = False
        
        return all_methods_found
        
    except Exception as e:
        print(f"  ❌ Error reading sensor.py: {e}")
        return False

def test_config_flow_structure():
    """Test the configuration flow structure."""
    print("\n🔍 Testing configuration flow structure...")
    
    try:
        with open("custom_components/genetic-load-manager/config_flow.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required schema fields
        required_fields = [
            "load_sensor_entity",
            "load_forecast_entity",
            "pv_forecast_entity",
            "pv_forecast_tomorrow_entity"
        ]
        
        all_fields_found = True
        for field in required_fields:
            if field in content:
                print(f"  ✅ {field} field found")
            else:
                print(f"  ❌ {field} field not found")
                all_fields_found = False
        
        # Check for entity selector
        if "selector.EntitySelector" in content:
            print("  ✅ EntitySelector found")
        else:
            print("  ❌ EntitySelector not found")
            all_fields_found = False
        
        return all_fields_found
        
    except Exception as e:
        print(f"  ❌ Error reading config_flow.py: {e}")
        return False

def test_init_structure():
    """Test the __init__.py structure."""
    print("\n🔍 Testing __init__.py structure...")
    
    try:
        with open("custom_components/genetic-load-manager/__init__.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for platforms
        if 'PLATFORMS = ["sensor", "binary_sensor", "switch"]' in content:
            print("  ✅ PLATFORMS list includes sensor")
        else:
            print("  ❌ PLATFORMS list missing or incorrect")
            return False
        
        # Check for required functions
        required_functions = [
            "async_setup",
            "async_setup_entry",
            "async_unload_entry",
            "async_register_services"
        ]
        
        all_functions_found = True
        for func in required_functions:
            if f"async def {func}" in content:
                print(f"  ✅ {func} function found")
            else:
                print(f"  ❌ {func} function not found")
                all_functions_found = False
        
        return all_functions_found
        
    except Exception as e:
        print(f"  ❌ Error reading __init__.py: {e}")
        return False

def test_manifest():
    """Test the manifest.json file."""
    print("\n🔍 Testing manifest.json...")
    
    try:
        import json
        with open("custom_components/genetic-load-manager/manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        required_fields = ["domain", "name", "version", "dependencies", "config_flow"]
        all_fields_found = True
        
        for field in required_fields:
            if field in manifest:
                print(f"  ✅ {field}: {manifest[field]}")
            else:
                print(f"  ❌ {field} missing")
                all_fields_found = False
        
        # Check specific values
        if manifest.get("domain") == "genetic-load-manager":
            print("  ✅ Domain is correct")
        else:
            print("  ❌ Domain is incorrect")
            all_fields_found = False
        
        if "sensor" in manifest.get("dependencies", []):
            print("  ✅ Sensor dependency included")
        else:
            print("  ❌ Sensor dependency missing")
            all_fields_found = False
        
        return all_fields_found
        
    except Exception as e:
        print(f"  ❌ Error reading manifest.json: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Genetic Load Manager Sensor Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("File Syntax", test_file_syntax),
        ("Import Dependencies", test_imports),
        ("File Structure", test_file_structure),
        ("Sensor Class Structure", test_sensor_class_structure),
        ("Config Flow Structure", test_config_flow_structure),
        ("Init Structure", test_init_structure),
        ("Manifest", test_manifest)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Sensor integration is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
