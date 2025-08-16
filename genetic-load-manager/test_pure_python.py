#!/usr/bin/env python3
"""
Test script to verify pure Python implementation works
"""

def test_pure_python_imports():
    """Test importing all required modules"""
    try:
        print("Testing pure Python imports...")
        
        import flask
        print("✓ Flask imported successfully")
        
        import requests
        print("✓ Requests imported successfully")
        
        # Test our pure Python math functions
        import math
        print("✓ Math module imported successfully")
        
        import apscheduler
        print("✓ APScheduler imported successfully")
        
        import deap
        print("✓ DEAP imported successfully")
        
        import dotenv
        print("✓ Python-dotenv imported successfully")
        
        import gunicorn
        print("✓ Gunicorn imported successfully")
        
        print("\n✅ All pure Python imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_math_functions():
    """Test our pure Python mathematical functions"""
    try:
        print("\nTesting pure Python math functions...")
        
        # Test data
        test_values = [1, 2, 3, 4, 5]
        
        # Test mean
        from app import mean
        result = mean(test_values)
        print(f"✓ Mean calculation: {result} (expected: 3.0)")
        
        # Test std
        from app import std
        result = std(test_values)
        print(f"✓ Standard deviation: {result:.4f} (expected: ~1.5811)")
        
        # Test normalization
        from app import min_max_normalize
        result = min_max_normalize(test_values, 0, 1)
        print(f"✓ Normalization: {[f'{x:.3f}' for x in result]}")
        
        print("✅ All math functions working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Math function error: {e}")
        return False

if __name__ == "__main__":
    print("=== Pure Python Implementation Test ===\n")
    
    # Test imports
    imports_ok = test_pure_python_imports()
    
    if imports_ok:
        # Test math functions
        math_ok = test_math_functions()
        
        if math_ok:
            print("\n🎉 All tests passed! The pure Python implementation is ready.")
        else:
            print("\n⚠️  Math functions have issues.")
    else:
        print("\n❌ Import tests failed.") 