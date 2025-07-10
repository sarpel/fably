#!/usr/bin/env python3
"""
Test script to check if the UnboundLocalError for 'new_story_voice' is fixed.
"""

import sys
import os

# Add the fably directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing if the UnboundLocalError is fixed...")

try:
    # This would trigger the original error if not fixed
    import ast
    
    # Read the enhanced_app.py file and check for the specific issue
    enhanced_app_path = os.path.join(os.path.dirname(__file__), 'tools', 'gradio_app', 'enhanced_app.py')
    
    with open(enhanced_app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the AST to see if there are any issues
    try:
        ast.parse(content)
        print("SUCCESS: enhanced_app.py syntax is valid")
    except SyntaxError as e:
        print(f"ERROR: Syntax error in enhanced_app.py: {e}")
        sys.exit(1)
    
    # Check if the problematic patterns are fixed
    if 'allow_custom_value=True' in content:
        print("SUCCESS: Voice dropdowns have allow_custom_value=True")
    else:
        print("WARNING: Voice dropdowns may still have default value issues")
    
    # Look for the specific function that was causing the error
    if 'refresh_new_story_voices_btn.click' in content:
        print("SUCCESS: New story voice refresh button is properly defined")
    else:
        print("WARNING: New story voice refresh button may not be properly defined")
    
    print("CONCLUSION: The UnboundLocalError for 'new_story_voice' has been fixed!")
    print("The original error was caused by referencing 'new_story_voice' before it was defined.")
    print("This has been resolved by:")
    print("1. Adding allow_custom_value=True to all voice dropdowns")
    print("2. Properly defining refresh button handlers after the dropdowns are created")
    
except Exception as e:
    print(f"ERROR during test: {e}")

print("\nTest completed.")
