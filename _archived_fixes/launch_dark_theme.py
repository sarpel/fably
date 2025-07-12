#!/usr/bin/env python3
"""
Fably Dark Theme Launcher
"""

import os
import sys
from pathlib import Path

def main():
    print("Fably Dark Theme Web Interface")
    print("=" * 40)
    print("Duzeltilen Component ID'ler: 11, 16, 54, 63, 82, 87")
    print()
    
    # Enhanced app kontrolu
    enhanced_app = Path("tools/gradio_app/enhanced_app_dark_theme.py")
    if enhanced_app.exists():
        print("Enhanced Dark Theme App baslatiliyor...")
        os.system(f"python {enhanced_app}")
    else:
        print("Enhanced app bulunamadi!")
        print("Lutfen once: python simple_dark_patch.py")

if __name__ == "__main__":
    main()
