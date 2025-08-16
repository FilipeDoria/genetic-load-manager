#!/usr/bin/env python3
"""
Basic Functionality Test for Genetic Load Manager
This script tests the basic components without requiring Home Assistant
"""

import sys
import os

def test_file_structure():
    """Test if all required files exist."""
    print("🔍 Testing file structure...")
    
    required_files = [
        "custom_components/genetic-load-manager/__init__.py",
        "custom_components/genetic-load-manager/const.py",
        "custom_components/genetic-load-manager/manifest.json",
        "custom_components/genetic-load-manager/config_flow.py",
        "custom_components/genetic-load-manager/sensor.py",
        "custom_components/genetic-load-manager/switch.py",
        "custom_components/genetic-load-manager/binary_sensor.py",
        "custom_components/genetic-load-manager/services.yaml",
        "custom_components/genetic-load-manager/translations/en.json",
        "hacs.json",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({file_size} bytes)")
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    else:
        print("  ✅ All required files present")
        return True

def test_python_syntax():
    """Test Python syntax for all Python files."""
    print("\n🐍 Testing Python syntax...")
    
    python_files = [
        "custom_components/genetic-load-manager/__init__.py",
        "custom_components/genetic-load-manager/const.py",
        "custom_components/genetic-load-manager/config_flow.py",
        "custom_components/genetic-load-manager/sensor.py",
        "custom_components/genetic-load-manager/switch.py",
        "custom_components/genetic-load-manager/binary_sensor.py"
    ]
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, file_path, 'exec')
            print(f"  ✅ {file_path} - Syntax OK")
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
            print(f"  ❌ {file_path} - Syntax Error: {e}")
        except Exception as e:
            syntax_errors.append(f"{file_path}: {e}")
            print(f"  ❌ {file_path} - Error: {e}")
    
    if syntax_errors:
        print(f"  ❌ Syntax errors found: {len(syntax_errors)}")
        return False
    else:
        print("  ✅ All Python files have valid syntax")
        return True

def test_imports():
    """Test if basic imports work (without Home Assistant)."""
    print("\n📦 Testing basic imports...")
    
    try:
        # Test basic Python imports
        import logging
        import asyncio
        import datetime
        import typing
        print("  ✅ Standard Python imports OK")
        
        # Test if we can read the files
        with open("custom_components/genetic-load-manager/const.py", 'r') as f:
            content = f.read()
            if "DOMAIN" in content:
                print("  ✅ Constants file readable and contains DOMAIN")
            else:
                print("  ❌ Constants file missing DOMAIN")
                return False
        
        with open("custom_components/genetic-load-manager/manifest.json", 'r') as f:
            content = f.read()
            if "genetic-load-manager" in content:
                print("  ✅ Manifest file readable and contains domain")
            else:
                print("  ❌ Manifest file missing domain")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import test failed: {e}")
        return False

def test_hacs_compliance():
    """Test HACS compliance."""
    print("\n🏠 Testing HACS compliance...")
    
    try:
        # Check hacs.json
        with open("hacs.json", 'r') as f:
            content = f.read()
            if "Genetic Load Manager" in content:
                print("  ✅ hacs.json contains correct name")
            else:
                print("  ❌ hacs.json missing name")
                return False
        
        # Check directory structure
        if os.path.exists("custom_components/genetic-load-manager"):
            print("  ✅ custom_components directory structure correct")
        else:
            print("  ❌ custom_components directory missing")
            return False
        
        # Check manifest.json
        with open("custom_components/genetic-load-manager/manifest.json", 'r') as f:
            content = f.read()
            if '"domain": "genetic-load-manager"' in content:
                print("  ✅ manifest.json contains correct domain")
            else:
                print("  ❌ manifest.json domain mismatch")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ HACS compliance test failed: {e}")
        return False

def test_mock_optimizer():
    """Test the mock optimizer functionality."""
    print("\n🤖 Testing mock optimizer...")
    
    try:
        # Read the __init__.py file to check mock optimizer
        with open("custom_components/genetic-load-manager/__init__.py", 'r') as f:
            content = f.read()
        
        if "MockOptimizer" in content:
            print("  ✅ MockOptimizer class found")
        else:
            print("  ❌ MockOptimizer class missing")
            return False
        
        if "get_status" in content:
            print("  ✅ get_status method found")
        else:
            print("  ❌ get_status method missing")
            return False
        
        if "is_running" in content:
            print("  ✅ is_running attribute found")
        else:
            print("  ❌ is_running attribute missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Mock optimizer test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Genetic Load Manager - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_python_syntax),
        ("Basic Imports", test_imports),
        ("HACS Compliance", test_hacs_compliance),
        ("Mock Optimizer", test_mock_optimizer)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The project appears to be functioning correctly.")
        print("\n🚀 Next steps:")
        print("1. Deploy to GitHub")
        print("2. Install via HACS in Home Assistant")
        print("3. Test integration setup")
        print("4. Verify sensors appear")
        return True
    else:
        print("⚠️  Some tests failed. Please fix the issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 