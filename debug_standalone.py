#!/usr/bin/env python3
"""Standalone debugging script that analyzes code structure without importing Home Assistant."""

import os
import sys
import ast
import re
from pathlib import Path

def analyze_python_file(file_path):
    """Analyze a Python file for imports, classes, and methods."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Extract information
        imports = []
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    'line': node.lineno
                })
            elif isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line': node.lineno
                })
        
        return {
            'imports': imports,
            'classes': classes,
            'functions': functions,
            'content': content
        }
    except Exception as e:
        return {'error': str(e)}

def check_homeassistant_dependencies():
    """Check which files have Home Assistant dependencies."""
    print("🔍 Checking Home Assistant Dependencies")
    print("=" * 60)
    
    custom_components_dir = Path("custom_components/genetic_load_manager")
    
    if not custom_components_dir.exists():
        print("❌ custom_components/genetic_load_manager directory not found")
        return
    
    python_files = list(custom_components_dir.glob("*.py"))
    
    print(f"Found {len(python_files)} Python files:")
    
    for py_file in python_files:
        print(f"\n📁 {py_file.name}:")
        analysis = analyze_python_file(py_file)
        
        if 'error' in analysis:
            print(f"   ❌ Error analyzing: {analysis['error']}")
            continue
        
        # Check for Home Assistant imports
        ha_imports = [imp for imp in analysis['imports'] if 'homeassistant' in imp]
        if ha_imports:
            print(f"   ⚠️  Home Assistant imports: {ha_imports}")
        else:
            print(f"   ✅ No Home Assistant imports")
        
        # Show classes
        if analysis['classes']:
            print(f"   🏗️  Classes:")
            for cls in analysis['classes']:
                print(f"      - {cls['name']} (line {cls['line']})")
                if cls['methods']:
                    print(f"        Methods: {', '.join(cls['methods'])}")
        
        # Show functions
        if analysis['functions']:
            print(f"   🔧 Functions: {', '.join([f['name'] for f in analysis['functions']])}")

def analyze_code_structure():
    """Analyze the overall code structure."""
    print("\n🔍 Analyzing Code Structure")
    print("=" * 60)
    
    # Check file sizes and complexity
    custom_components_dir = Path("custom_components/genetic_load_manager")
    
    if not custom_components_dir.exists():
        print("❌ custom_components/genetic_load_manager directory not found")
        return
    
    total_lines = 0
    total_files = 0
    
    for py_file in custom_components_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                total_files += 1
                
                print(f"📄 {py_file.name}: {lines} lines")
                
                # Check for common patterns
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Count async functions
                    async_count = len(re.findall(r'async def', content))
                    if async_count > 0:
                        print(f"   🔄 Async functions: {async_count}")
                    
                    # Count await statements
                    await_count = len(re.findall(r'await ', content))
                    if await_count > 0:
                        print(f"   ⏳ Await statements: {await_count}")
                    
                    # Check for logging
                    if 'import logging' in content or 'from logging' in content:
                        print(f"   📝 Has logging")
                    
                    # Check for constants
                    if 'CONF_' in content:
                        print(f"   ⚙️  Has configuration constants")
                        
        except Exception as e:
            print(f"❌ Error reading {py_file.name}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Total files: {total_files}")
    print(f"   Total lines: {total_lines}")
    print(f"   Average lines per file: {total_lines // total_files if total_files > 0 else 0}")

def check_import_issues():
    """Check for potential import issues."""
    print("\n🔍 Checking Import Issues")
    print("=" * 60)
    
    custom_components_dir = Path("custom_components/genetic_load_manager")
    
    if not custom_components_dir.exists():
        print("❌ custom_components/genetic_load_manager directory not found")
        return
    
    # Check __init__.py for imports
    init_file = custom_components_dir / "__init__.py"
    if init_file.exists():
        print("📁 __init__.py analysis:")
        analysis = analyze_python_file(init_file)
        
        if 'error' not in analysis:
            print(f"   Imports: {analysis['imports']}")
            print(f"   Functions: {[f['name'] for f in analysis['functions']]}")
        else:
            print(f"   ❌ Error: {analysis['error']}")
    
    # Check for circular imports
    print("\n🔄 Checking for potential circular imports...")
    
    # Look for files that import each other
    for py_file in custom_components_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        analysis = analyze_python_file(py_file)
        if 'error' not in analysis:
            local_imports = [imp for imp in analysis['imports'] 
                           if not imp.startswith('homeassistant') and '.' in imp]
            if local_imports:
                print(f"   {py_file.name} imports: {local_imports}")

def suggest_debugging_approach():
    """Suggest the best debugging approach."""
    print("\n💡 Suggested Debugging Approach")
    print("=" * 60)
    
    print("Since the integration has Home Assistant dependencies, here are your options:")
    
    print("\n1️⃣ **Code Analysis (Current Script)**")
    print("   ✅ What we can do:")
    print("   - Analyze file structure and dependencies")
    print("   - Check for syntax errors")
    print("   - Identify import patterns")
    print("   - Count functions and classes")
    
    print("\n2️⃣ **Mock Home Assistant Environment**")
    print("   🔧 What you can do:")
    print("   - Create mock objects for Home Assistant classes")
    print("   - Test individual functions in isolation")
    print("   - Verify data parsing logic")
    
    print("\n3️⃣ **Test in Home Assistant**")
    print("   🏠 What you should do:")
    print("   - Test the actual integration in Home Assistant")
    print("   - Check Home Assistant logs for errors")
    print("   - Verify entity data structures")
    
    print("\n4️⃣ **Data Validation**")
    print("   📊 What we can verify:")
    print("   - Check your entity data matches expected format")
    print("   - Validate Solcast PV forecast structure")
    print("   - Verify OMIE price data format")
    
    print("\n🎯 **Recommended Next Steps:**")
    print("   1. Run this analysis to understand the code structure")
    print("   2. Use the data validation script to check your entities")
    print("   3. Test the integration in Home Assistant")
    print("   4. Check Home Assistant logs for specific error messages")

def main():
    """Run all analysis functions."""
    print("🚀 Starting Standalone Code Analysis")
    print("=" * 60)
    
    # Check dependencies
    check_homeassistant_dependencies()
    
    # Analyze structure
    analyze_code_structure()
    
    # Check import issues
    check_import_issues()
    
    # Suggest approach
    suggest_debugging_approach()
    
    print("\n🎉 Analysis completed!")
    print("\n💡 **Key Insight:** The integration can't run locally because it depends on Home Assistant.")
    print("   This is normal for Home Assistant custom integrations.")
    print("   Use Home Assistant itself to test the integration.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Error during analysis: {e}")
        import traceback
        traceback.print_exc()
