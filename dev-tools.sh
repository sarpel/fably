#!/bin/bash

# ================================================================================
# Fably Development Tools - Consolidated Script
# ================================================================================
# This script combines debugging, testing, and web app functionality
# Usage: ./dev-tools.sh [command] [options]
# ================================================================================

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

header() {
    echo -e "${BLUE}==================== $1 ====================${NC}"
}

show_usage() {
    echo "Fably Development Tools"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  debug [query]        Debug Fably with optional test query"
    echo "  test                 Run comprehensive Fably tests"
    echo "  web                  Start basic web interface"
    echo "  web-enhanced         Start enhanced web interface"
    echo "  help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 debug                                   # Debug mode"
    echo "  $0 debug 'uzay macerası'                   # Debug with query"
    echo "  $0 test                                    # Run tests"
    echo "  $0 web                                     # Basic web app"
    echo "  $0 web-enhanced                            # Enhanced web app"
    echo ""
}

# ================================================================================
# DEBUG FUNCTIONALITY (from debug_fably.sh)
# ================================================================================

debug_fably() {
    local test_query="${1:-test}"
    
    header "Fably Debug Diagnostics"
    
    # Check virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        log "✅ Virtual environment active: $VIRTUAL_ENV"
    else
        warn "⚠️  Virtual environment not active"
        if [[ -d ".venv" ]]; then
            log "Activating .venv..."
            source .venv/bin/activate
        fi
    fi
    
    # Check API key
    if [[ -f ".env" ]]; then
        if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
            log "✅ OpenAI API key found in .env"
        else
            error "❌ OpenAI API key missing or invalid in .env"
            error "   Expected format: OPENAI_API_KEY=sk-..."
            exit 1
        fi
    else
        error "❌ .env file not found"
        exit 1
    fi
    
    # Check Fably installation
    if command -v fably >/dev/null 2>&1; then
        log "✅ Fably command available"
    else
        error "❌ Fably command not found"
        error "   Try: pip install --editable ."
        exit 1
    fi
    
    # Test CLI options
    log ""
    log "📋 Available CLI options:"
    fably --help | grep -E "(web-app|debug|loop)" || log "   CLI options check failed"
    
    # Test simple story generation with maximum debugging
    log ""
    log "🧪 Testing story generation with full debugging:"
    log "Running: fably --debug '$test_query'"
    log "----------------------------------------"
    
    # Set maximum logging
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    python -c "import logging; logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')"
    
    fably --debug "$test_query"
    
    log "----------------------------------------"
    log "🔍 Debug complete. Check output above for errors."
}

# ================================================================================
# TEST FUNCTIONALITY (from test_fably.sh)
# ================================================================================

test_fably() {
    header "Fably Testing Suite"
    
    log "Testing Fably setup..."
    
    # Check if .env exists and has API key
    if [ ! -f .env ]; then
        error "❌ .env file missing!"
        error "Please create .env file with your OpenAI API key"
        exit 1
    fi
    
    if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        warn "⚠️  OpenAI API key not found in .env file"
        warn "Please edit .env and add your API key: OPENAI_API_KEY=sk-your-key-here"
        exit 1
    fi
    
    # Activate virtual environment if it exists
    if [ -d ".venv" ]; then
        log "Activating virtual environment..."
        source .venv/bin/activate
    fi
    
    # Test basic Fably functionality with debug mode
    log "Testing Fably with debug mode to see what's happening..."
    log "Running: fably --debug 'bana bir köpek hakkında hikaye anlat'"
    fably --debug "bana bir köpek hakkında hikaye anlat"
    
    log ""
    log "Testing web app option..."
    log "Running: fably --help | grep web-app"
    fably --help | grep web-app
    
    log ""
    log "If you saw a story generated above, Fably is working!"
    log ""
    log "Available commands:"
    log "  fably --loop                          # Use with button/wakeword"
    log "  fably --web-app                       # Start web interface"
    log "  fably 'uzay macerası hikayesi'        # Generate specific story"
    log "  fably --debug 'test hikayesi'         # Debug mode"
}

# ================================================================================
# WEB INTERFACE FUNCTIONALITY (from run scripts)
# ================================================================================

start_basic_web() {
    header "Starting Basic Fably Web Interface"
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        error "Virtual environment not found. Please run setup first."
        exit 1
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Navigate to gradio app directory
    cd tools/gradio_app
    
    # Install requirements if needed
    if [ -f "requirements.txt" ]; then
        log "Installing/updating requirements..."
        pip install -r requirements.txt
    fi
    
    # Launch basic app
    log "Launching basic app on http://localhost:7860"
    if [ -f "app.py" ]; then
        gradio app.py
    else
        python app.py
    fi
}

start_enhanced_web() {
    header "Starting Enhanced Fably Web Interface"
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        error "Virtual environment not found. Please run setup first."
        exit 1
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Navigate to gradio app directory
    cd tools/gradio_app
    
    # Install/update requirements
    if [ -f "requirements.txt" ]; then
        log "Installing/updating requirements..."
        pip install -r requirements.txt
    fi
    
    # Launch the enhanced app
    log "Launching enhanced app on http://localhost:7860"
    if [ -f "enhanced_app.py" ]; then
        python enhanced_app.py
    else
        error "Enhanced app not found at tools/gradio_app/enhanced_app.py"
        exit 1
    fi
}

# ================================================================================
# MAIN COMMAND DISPATCHER
# ================================================================================

case "${1:-help}" in
    "debug")
        debug_fably "${2:-test}"
        ;;
    "test")
        test_fably
        ;;
    "web")
        start_basic_web
        ;;
    "web-enhanced")
        start_enhanced_web
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
