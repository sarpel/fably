#!/bin/bash

# Quick Fably Test Script

echo "Testing Fably setup..."

# Check if .env exists and has API key
if [ ! -f .env ]; then
    echo "❌ .env file missing!"
    echo "Please create .env file with your OpenAI API key"
    exit 1
fi

if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  OpenAI API key not found in .env file"
    echo "Please edit .env and add your API key: OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Test basic Fably functionality
echo "Testing Fably with a simple story request..."
fably "bana bir köpek hakkında hikaye anlat"

echo "If you saw a story generated above, Fably is working!"
echo ""
echo "To use Fably interactively:"
echo "  fably --loop                          # Use with button/wakeword"
echo "  fably --web-app                       # Start web interface"
echo "  fably 'uzay macerası hikayesi'        # Generate specific story"
