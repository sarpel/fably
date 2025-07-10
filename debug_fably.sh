#!/bin/bash

# Fably Debug Script
# Use this to diagnose why Fably says "bye come back soon"

echo "🔍 Fably Debug Diagnostics"
echo "=========================="

# Check virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not active"
    if [[ -d ".venv" ]]; then
        echo "   Activating .venv..."
        source .venv/bin/activate
    fi
fi

# Check API key
if [[ -f ".env" ]]; then
    if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        echo "✅ OpenAI API key found in .env"
    else
        echo "❌ OpenAI API key missing or invalid in .env"
        echo "   Expected format: OPENAI_API_KEY=sk-..."
        exit 1
    fi
else
    echo "❌ .env file not found"
    exit 1
fi

# Check Fably installation
if command -v fably >/dev/null 2>&1; then
    echo "✅ Fably command available"
else
    echo "❌ Fably command not found"
    echo "   Try: pip install --editable ."
    exit 1
fi

# Test CLI options
echo ""
echo "📋 Available CLI options:"
fably --help | grep -E "(web-app|debug|loop)" || echo "   CLI options check failed"

# Test simple story generation with maximum debugging
echo ""
echo "🧪 Testing story generation with full debugging:"
echo "Running: fably --debug 'test'"
echo "----------------------------------------"

# Set maximum logging
export PYTHONPATH="$(pwd):$PYTHONPATH"
python -c "import logging; logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')"

fably --debug "test"

echo "----------------------------------------"
echo "🔍 Debug complete. Check output above for errors."
