#!/usr/bin/env python3
"""
Fably Web Interface Launcher
Professional story management system entry point.
"""

import sys
from pathlib import Path

# Add parent directory to path for Fably imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and launch the web interface
from web_interface.app import main

if __name__ == "__main__":
    main()
