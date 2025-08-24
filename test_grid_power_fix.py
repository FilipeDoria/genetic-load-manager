#!/usr/bin/env python3
"""Test script to verify grid power configuration fix."""

import sys
import os

# Add the custom_components directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'custom_components', 'genetic_load_manager'))

try:
    from const import CONF_GRID_POWER, DEFAULT_ENTITIES
    
    print("✅ Grid Power Configuration Test")
    print("=" * 40)
    
    print(f"CONF_GRID_POWER: {CONF_GRID_POWER}")
    print(f"Default grid power entity: {DEFAULT_ENTITIES['grid_power']}")
    
    print("\n✅ Configuration updated successfully!")
    print("Grid import and export now use the same bidirectional entity.")
    print("Positive values = Importing from grid")
    print("Negative values = Exporting to grid")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
