#!/bin/bash

# Quick fix for RPi5 installation issues
# Run this script if setup.sh fails

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[FIX]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log "Fably RPi5 Quick Fix Script"

# Fix file permissions
log "Fixing file permissions..."
sudo chown -R $USER:$USER $HOME
chmod 755 $HOME

# Fix .asoundrc creation
log "Creating ALSA configuration..."
ASOUND_PATH="$HOME/.asoundrc"
if [[ -f "$ASOUND_PATH" ]]; then
    rm -f "$ASOUND_PATH"
fi

cat > "$ASOUND_PATH" << 'EOF'
# ALSA configuration for Fably
# Works with USB microphones and built-in audio

pcm.!default {
    type asym
    playback.pcm {
        type hw
        card 0
        device 0
    }
    capture.pcm {
        type hw
        card 0
        device 0
    }
}

ctl.!default {
    type hw
    card 0
}
EOF

chmod 644 "$ASOUND_PATH"

# Install missing dependencies if needed
log "Installing any missing Python dependencies..."
pip install --upgrade pip setuptools wheel

# Install with modern setuptools
if [[ -f "pyproject.toml" ]]; then
    log "Installing Fably with modern setuptools..."
    pip install --editable . --use-pep517
else
    log "Installing Fably with legacy setuptools..."
    pip install --editable .
fi

# Test audio devices
log "Testing audio devices..."
python3 -c "
import sounddevice as sd
try:
    devices = sd.query_devices()
    print(f'Found {len(devices)} audio devices:')
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f'  Input device {i}: {device[\"name\"]}')
        if device['max_output_channels'] > 0:
            print(f'  Output device {i}: {device[\"name\"]}')
except Exception as e:
    print(f'Audio test failed: {e}')
"

# Test Fably installation
log "Testing Fably installation..."
if fably --help > /dev/null 2>&1; then
    log "✅ Fably installed successfully!"
    log ""
    log "Quick start commands:"
    log "  fably --gpio-button --loop          # Use GPIO button"
    log "  fably --story-request \"space story\"  # Generate specific story"
    log "  fably --web-app                     # Start web interface"
else
    error "❌ Fably installation test failed"
    exit 1
fi

log "🎉 RPi5 quick fix completed!"
