#!/usr/bin/env python3
"""
Test script to verify all required modules can be imported
"""

def test_imports():
    """Test importing all required modules"""
    try:
        print("Testing imports...")
        
        import flask
        print("✓ Flask imported successfully")
        
        import requests
        print("✓ Requests imported successfully")
        
        import numpy
        print("✓ NumPy imported successfully")
        
        import apscheduler
        print("✓ APScheduler imported successfully")
        
        import deap
        print("✓ DEAP imported successfully")
        
        import scipy
        print("✓ SciPy imported successfully")
        
        import pandas
        print("✓ Pandas imported successfully")
        
        import dotenv
        print("✓ Python-dotenv imported successfully")
        
        print("\n✅ All imports successful! The environment is ready.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports() 