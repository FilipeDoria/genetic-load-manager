#!/usr/bin/env python3
"""
Simple Test Runner for Genetic Load Manager
Runs all tests and provides a summary
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_test_script(script_name: str, description: str) -> bool:
    """Run a test script and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {description}")
    print(f"📁 Script: {script_name}")
    print(f"{'='*60}")
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        start_time = time.time()
        
        # Run the test script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=script_path.parent
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(f"⚠️  Warnings/Errors:")
            print(result.stderr)
        
        # Check result
        if result.returncode == 0:
            print(f"✅ {description} completed successfully in {duration:.2f}s")
            return True
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Main test runner"""
    print("🚀 Genetic Load Manager - Test Suite Runner")
    print("=" * 60)
    
    # Define test scripts
    tests = [
        ("test_integration_local.py", "Integration Components Test"),
        ("test_real_ha_entities.py", "Real HA Entities Simulation"),
        ("quick_algorithm_test.py", "Algorithm Local Testing")
    ]
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "custom_components").exists():
        print("❌ Error: Must run from project root directory")
        print(f"   Current: {current_dir}")
        print("   Expected: genetic-load-manager/")
        return False
    
    print(f"📍 Running tests from: {current_dir}")
    print(f"🔍 Found custom_components: {(current_dir / 'custom_components').exists()}")
    
    # Run tests
    results = {}
    total_start = time.time()
    
    for script_name, description in tests:
        success = run_test_script(script_name, description)
        results[description] = success
        
        # Small delay between tests
        time.sleep(1)
    
    total_duration = time.time() - total_start
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUITE SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for description, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {description}")
    
    print(f"\nOverall: {passed}/{total} test suites passed ({passed/total*100:.1f}%)")
    print(f"Total time: {total_duration:.2f} seconds")
    
    if passed == total:
        print("\n🎉 All test suites passed! Your integration is ready for testing.")
        print("\nNext steps:")
        print("1. Test in a Home Assistant development environment")
        print("2. Test with real entities and data")
        print("3. Submit to HACS for community testing")
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
