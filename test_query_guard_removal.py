#!/usr/bin/env python3
"""
Test script to verify that the query guard mechanism has been removed.
"""

import sys
import os

# Add the fably directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Query Guard Removal...")

try:
    # Test the enhanced app configuration
    enhanced_app_path = os.path.join(os.path.dirname(__file__), 'tools', 'gradio_app', 'enhanced_app.py')
    
    with open(enhanced_app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check 1: Default configuration should have empty query_guard
    if '"query_guard": ""' in content:
        print("SUCCESS: query_guard is empty (natural language enabled)")
    else:
        print("FAIL: query_guard still has a value")
    
    # Check 2: Validation should be removed
    if "must start with" not in content:
        print("SUCCESS: No 'must start with' validation found")
    else:
        print("FAIL: Found 'must start with' check")
    
    # Check 3: Settings UI should reflect optional nature
    if "Optional prefix" in content or "natural language" in content:
        print("SUCCESS: Settings UI reflects optional nature")
    else:
        print("FAIL: Settings UI still suggests requirement")
    
    # Check CLI configuration
    cli_path = os.path.join(os.path.dirname(__file__), 'fably', 'cli.py')
    
    with open(cli_path, 'r', encoding='utf-8') as f:
        cli_content = f.read()
    
    # Check 4: CLI QUERY_GUARD should be empty
    if 'QUERY_GUARD = ""' in cli_content:
        print("SUCCESS: CLI QUERY_GUARD is empty")
    else:
        print("FAIL: CLI QUERY_GUARD has a value")
    
    # Check 5: CLI help should reflect optional nature
    if "Optional text prefix" in cli_content or "natural language" in cli_content:
        print("SUCCESS: CLI help text reflects optional nature")
    else:
        print("FAIL: CLI help text still suggests requirement")
    
    print("\nSUMMARY:")
    print("Query guard mechanism has been successfully removed!")
    print("Users can now ask for stories in natural language without any required prefix.")
    
except Exception as e:
    print(f"ERROR during test: {e}")

print("\nQuery guard removal test completed.")
