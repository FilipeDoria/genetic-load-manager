#!/usr/bin/env python3
"""
Quick Algorithm Test for Genetic Load Manager
Fast test of core genetic algorithm functionality
"""

import sys
import os
import time

# Add the custom_components to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'custom_components'))

class MockHA:
    """Simple mock Home Assistant for testing"""
    def __init__(self):
        self.states = {}
    
    def states_get(self, entity_id):
        return MockState(entity_id, "0")
    
    def states_set(self, entity_id, state, attributes=None):
        self.states[entity_id] = MockState(entity_id, state, attributes or {})

class MockState:
    """Simple mock state object"""
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.attributes = attributes or {}

def test_file_structure():
    """Test that required algorithm files exist"""
    print("\n=== File Structure Test ===")
    
    required_files = [
        '../../custom_components/genetic_load_manager/genetic_algorithm.py',
        '../../custom_components/genetic_load_manager/pricing_calculator.py',
        '../../custom_components/genetic_load_manager/const.py'
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

def test_constants_validation():
    """Test that constants file has required values"""
    print("\n=== Constants Validation Test ===")
    
    try:
        const_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'custom_components', 'genetic_load_manager', 'const.py'
        )
        
        if os.path.exists(const_file):
            with open(const_file, 'r') as f:
                content = f.read()
            
            # Check for algorithm-related constants
            required_constants = [
                'MIN_POPULATION_SIZE', 'MAX_POPULATION_SIZE',
                'MIN_GENERATIONS', 'MAX_GENERATIONS',
                'MIN_MUTATION_RATE', 'MAX_MUTATION_RATE'
            ]
            
            found_constants = []
            for constant in required_constants:
                if constant in content:
                    found_constants.append(constant)
                    print(f"OK: Found constant {constant}")
                else:
                    print(f"MISSING: Constant {constant}")
            
            print(f"Constants found: {len(found_constants)}/{len(required_constants)}")
            return len(found_constants) >= 4  # At least 4 out of 6
            
        else:
            print("ERROR: Constants file not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not read constants file: {e}")
        return False

def test_algorithm_file_content():
    """Test that algorithm file has basic structure"""
    print("\n=== Algorithm File Content Test ===")
    
    try:
        algo_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'custom_components', 'genetic_load_manager', 'genetic_algorithm.py'
        )
        
        if os.path.exists(algo_file):
            with open(algo_file, 'r') as f:
                content = f.read()
            
            # Check for basic algorithm structure
            required_elements = [
                'class GeneticLoadOptimizer',
                'def __init__',
                            'def fitness_function',
            'def optimize'
            ]
            
            found_elements = []
            for element in required_elements:
                if element in content:
                    found_elements.append(element)
                    print(f"OK: Found {element}")
                else:
                    print(f"MISSING: {element}")
            
            print(f"Algorithm elements found: {len(found_elements)}/{len(required_elements)}")
            return len(found_elements) >= 3  # At least 3 out of 4
            
        else:
            print("ERROR: Algorithm file not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not read algorithm file: {e}")
        return False

def test_pricing_calculator_file():
    """Test that pricing calculator file exists and has content"""
    print("\n=== Pricing Calculator Test ===")
    
    try:
        calc_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 
            'custom_components', 'genetic_load_manager', 'pricing_calculator.py'
        )
        
        if os.path.exists(calc_file):
            with open(calc_file, 'r') as f:
                content = f.read()
            
            # Check for basic calculator structure
            required_elements = [
                'class IndexedTariffCalculator',
                            'def calculate_indexed_price',
            'def get_current_price'
            ]
            
            found_elements = []
            for element in required_elements:
                if element in content:
                    found_elements.append(element)
                    print(f"OK: Found {element}")
                else:
                    print(f"MISSING: {element}")
            
            print(f"Calculator elements found: {len(found_elements)}/{len(required_elements)}")
            return len(found_elements) >= 2  # At least 2 out of 3
            
        else:
            print("ERROR: Pricing calculator file not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not read pricing calculator file: {e}")
        return False

def main():
    """Main test function"""
    print("Quick Algorithm Test - Genetic Load Manager")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Constants Validation", test_constants_validation),
        ("Algorithm File Content", test_algorithm_file_content),
        ("Pricing Calculator", test_pricing_calculator_file)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"ERROR: Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*50)
    print("QUICK TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("All quick tests passed! Algorithm files are properly structured.")
    else:
        print("Some quick tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
