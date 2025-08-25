#!/usr/bin/env python3
"""
Local Error Reproduction Script for Genetic Load Manager
This script simulates Home Assistant integration errors locally for debugging
"""

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional

class MockHomeAssistant:
    """Mock Home Assistant environment for local testing."""
    
    def __init__(self):
        self.states = {}
        self.services = {}
        self.logs = []
        self.errors = []
        
    def log(self, level: str, message: str, **kwargs):
        """Mock logging function."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level.upper()}: {message}"
        self.logs.append(log_entry)
        print(log_entry)
        
        if level == "error":
            self.errors.append(message)
    
    def get_state(self, entity_id: str) -> Optional[Dict]:
        """Mock state retrieval."""
        return self.states.get(entity_id)
    
    def set_state(self, entity_id: str, state: str, attributes: Dict = None):
        """Mock state setting."""
        self.states[entity_id] = {
            "state": state,
            "attributes": attributes or {},
            "last_updated": datetime.now().isoformat()
        }

class MockGeneticLoadOptimizer:
    """Mock genetic algorithm optimizer that reproduces common errors."""
    
    def __init__(self, hass: MockHomeAssistant):
        self.hass = hass
        self.is_running = False
        self.error_mode = None  # Set to reproduce specific errors
        
    def set_error_mode(self, error_type: str):
        """Set error mode to reproduce specific failures."""
        self.error_mode = error_type
        self.hass.log("info", f"Error mode set to: {error_type}")
    
    def fetch_pv_forecast(self) -> List[float]:
        """Mock PV forecast fetching with error reproduction."""
        if self.error_mode == "no_pv_data":
            self.hass.log("error", "No Solcast PV forecast data available, using zeros")
            return [0.0] * 96  # 24 hours * 4 (15-min intervals)
        
        if self.error_mode == "pv_parsing_error":
            self.hass.log("error", "Failed to parse PV forecast data structure")
            return []
        
        # Normal operation
        self.hass.log("info", "PV forecast data fetched successfully")
        return [0.0, 0.0, 0.1, 0.3, 0.8, 1.2, 1.8, 2.1, 2.3, 2.1, 1.8, 1.2, 0.8, 0.3, 0.1, 0.0] * 6
    
    def fetch_pricing_data(self) -> List[float]:
        """Mock pricing data fetching with error reproduction."""
        if self.error_mode == "no_pricing_data":
            self.hass.log("error", "No hourly prices found in OMIE entity attributes")
            return []
        
        if self.error_mode == "pricing_parsing_error":
            self.hass.log("error", "Failed to parse pricing data structure")
            return []
        
        # Normal operation
        self.hass.log("info", "Pricing data fetched successfully")
        return [100.0, 95.0, 90.0, 85.0, 80.0, 75.0, 70.0, 65.0, 60.0, 55.0, 50.0, 45.0, 40.0, 35.0, 30.0, 25.0] * 6
    
    def start_optimization(self) -> bool:
        """Mock optimization start with error reproduction."""
        if self.error_mode == "startup_failure":
            self.hass.log("error", "Failed to start optimizer: missing required attributes")
            return False
        
        if self.error_mode == "missing_entities":
            self.hass.log("error", "Required entities not configured")
            return False
        
        self.is_running = True
        self.hass.log("info", "Optimization started successfully")
        return True
    
    def run_optimization_step(self) -> Dict[str, Any]:
        """Mock optimization step execution."""
        if not self.is_running:
            return {"status": "not_running"}
        
        if self.error_mode == "algorithm_error":
            self.hass.log("error", "Genetic algorithm encountered numerical error")
            return {"status": "error", "message": "Algorithm failed"}
        
        # Simulate optimization progress
        return {
            "status": "running",
            "generation": 25,
            "best_fitness": 0.85,
            "population_diversity": 0.72
        }
    
    def stop_optimization(self):
        """Mock optimization stop."""
        self.is_running = False
        self.hass.log("info", "Optimization stopped")

class ErrorReproductionTester:
    """Main class for testing error reproduction."""
    
    def __init__(self):
        self.hass = MockHomeAssistant()
        self.optimizer = MockGeneticLoadOptimizer(self.hass)
        
    def test_normal_operation(self):
        """Test normal operation without errors."""
        print("\n" + "="*60)
        print("🧪 TESTING NORMAL OPERATION")
        print("="*60)
        
        # Set up mock entities
        self.hass.set_state("sensor.solcast_pv_forecast", "available", {
            "DetailedForecast": [
                {"period_start": "2025-08-25T00:00:00+01:00", "pv_estimate": 0.0},
                {"period_start": "2025-08-25T00:15:00+01:00", "pv_estimate": 0.1}
            ]
        })
        
        self.hass.set_state("sensor.omie_spot_price_pt", "available", {
            "Today hours": {
                "2025-08-25T00:00:00+01:00": 100.0,
                "2025-08-25T01:00:00+01:00": 95.0
            }
        })
        
        # Test normal flow
        self.optimizer.start_optimization()
        for i in range(5):
            result = self.optimizer.run_optimization_step()
            print(f"Step {i+1}: {result}")
            time.sleep(0.1)
        self.optimizer.stop_optimization()
        
        print("✅ Normal operation test completed")
    
    def test_pv_forecast_error(self):
        """Test PV forecast data error reproduction."""
        print("\n" + "="*60)
        print("🧪 TESTING PV FORECAST ERROR")
        print("="*60)
        
        self.optimizer.set_error_mode("no_pv_data")
        
        # Test PV forecast fetching
        pv_data = self.optimizer.fetch_pv_forecast()
        print(f"PV data length: {len(pv_data)}")
        print(f"First 10 values: {pv_data[:10]}")
        
        print("✅ PV forecast error test completed")
    
    def test_pricing_error(self):
        """Test pricing data error reproduction."""
        print("\n" + "="*60)
        print("🧪 TESTING PRICING ERROR")
        print("="*60)
        
        self.optimizer.set_error_mode("no_pricing_data")
        
        # Test pricing data fetching
        pricing_data = self.optimizer.fetch_pricing_data()
        print(f"Pricing data length: {len(pricing_data)}")
        
        print("✅ Pricing error test completed")
    
    def test_startup_failure(self):
        """Test optimizer startup failure."""
        print("\n" + "="*60)
        print("🧪 TESTING STARTUP FAILURE")
        print("="*60)
        
        self.optimizer.set_error_mode("startup_failure")
        
        # Test startup
        success = self.optimizer.start_optimization()
        print(f"Startup success: {success}")
        
        print("✅ Startup failure test completed")
    
    def test_algorithm_error(self):
        """Test algorithm execution error."""
        print("\n" + "="*60)
        print("🧪 TESTING ALGORITHM ERROR")
        print("="*60)
        
        self.optimizer.set_error_mode("algorithm_error")
        
        # Start optimization
        self.optimizer.start_optimization()
        
        # Run steps until error
        for i in range(3):
            result = self.optimizer.run_optimization_step()
            print(f"Step {i+1}: {result}")
            if result.get("status") == "error":
                break
            time.sleep(0.1)
        
        self.optimizer.stop_optimization()
        print("✅ Algorithm error test completed")
    
    def test_missing_entities(self):
        """Test missing entity configuration error."""
        print("\n" + "="*60)
        print("🧪 TESTING MISSING ENTITIES")
        print("="*60)
        
        self.optimizer.set_error_mode("missing_entities")
        
        # Test startup with missing entities
        success = self.optimizer.start_optimization()
        print(f"Startup success: {success}")
        
        print("✅ Missing entities test completed")
    
    def run_all_tests(self):
        """Run all error reproduction tests."""
        print("🚀 STARTING ERROR REPRODUCTION TESTS")
        print("="*60)
        
        tests = [
            self.test_normal_operation,
            self.test_pv_forecast_error,
            self.test_pricing_error,
            self.test_startup_failure,
            self.test_algorithm_error,
            self.test_missing_entities
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total logs: {len(self.hass.logs)}")
        print(f"Total errors: {len(self.hass.errors)}")
        
        if self.hass.errors:
            print("\n🚨 ERRORS ENCOUNTERED:")
            for i, error in enumerate(self.hass.errors, 1):
                print(f"  {i}. {error}")
        
        print("\n💡 To reproduce these errors in Home Assistant:")
        print("   1. Check the logs above for error patterns")
        print("   2. Look for similar errors in Home Assistant logs")
        print("   3. Use the error modes to debug specific issues")
        print("   4. Compare local behavior with Home Assistant behavior")

def main():
    """Main function to run error reproduction tests."""
    tester = ErrorReproductionTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
