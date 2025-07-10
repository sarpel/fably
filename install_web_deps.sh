#!/bin/bash

# ================================================================================
# Install Fably Web Interface Dependencies
# ================================================================================
# This script installs the required packages for the Fably web interface
# ================================================================================

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INSTALL]${NC} $1"
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

header "Installing Fably Web Interface Dependencies"

# Check if virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ -d ".venv" ]]; then
        log "Activating virtual environment..."
        source .venv/bin/activate
    else
        error "Virtual environment not found. Please run ./setup.sh first"
        exit 1
    fi
fi

log "Virtual environment active: $VIRTUAL_ENV"

# Install web interface dependencies
log "Installing gradio and web dependencies..."
pip install gradio

log "Installing plotting and data analysis libraries..."
pip install plotly pandas

log "Installing additional web interface dependencies..."
pip install markdown

# Check if installation was successful
log "Testing gradio installation..."
python3 -c "import gradio; print(f'Gradio version: {gradio.__version__}')" || {
    error "Gradio installation failed"
    exit 1
}

log "Testing plotly installation..."
python3 -c "import plotly; print('Plotly installed successfully')" || {
    warn "Plotly installation failed - charts may not work"
}

# Test the web app
log "Testing Fably web app..."
if [[ -f "tools/gradio_app/enhanced_app.py" ]]; then
    python3 -c "
import sys
sys.path.insert(0, 'tools/gradio_app')
try:
    import enhanced_app
    print('✅ Enhanced web app imports successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    if [[ $? -eq 0 ]]; then
        log "✅ Web interface dependencies installed successfully!"
    else
        error "Web interface test failed"
        exit 1
    fi
else
    warn "Enhanced web app not found - basic web app will be used"
fi

header "Installation Complete"

log "You can now run:"
log "  fably --web-app                    # Start web interface"
log "  ./dev-tools.sh web-enhanced        # Alternative way to start"
log ""
log "Web interface will be available at: http://localhost:7860"

if command -v hostname >/dev/null 2>&1; then
    HOSTNAME=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "your-pi-ip")
    if [[ -n "$HOSTNAME" && "$HOSTNAME" != "your-pi-ip" ]]; then
        log "Or from other devices: http://$HOSTNAME:7860"
    fi
fi
