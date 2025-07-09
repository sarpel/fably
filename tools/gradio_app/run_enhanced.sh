#!/bin/bash

echo "Starting Enhanced Fably Web Interface..."

# Check if virtual environment exists
if [ ! -d "../../.venv" ]; then
    echo "Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source ../../.venv/bin/activate

# Install/update requirements
pip install -r requirements.txt

# Launch the enhanced app
echo "Launching on http://localhost:7860"
python enhanced_app.py
