#!/bin/bash

# ================================================================================
# Fably System Fixes - Consolidated Script
# ================================================================================
# This script combines all system-specific fixes for different platforms
# Usage: ./system-fixes.sh [command] [options]
# ================================================================================

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

header() {
    echo -e "${BLUE}==================== $1 ====================${NC}"
}

show_usage() {
    echo "Fably System Fixes"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  audio               Fix audio configuration issues"
    echo "  rpi5                Apply Raspberry Pi 5 specific fixes"
    echo "  auto                Auto-detect and apply appropriate fixes"
    echo "  test                Test system configuration"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 audio             # Fix audio issues"
    echo "  $0 rpi5              # Apply Pi 5 fixes"
    echo "  $0 auto              # Auto-detect and fix"
    echo ""
}

# ================================================================================
# AUDIO FIXES (from fix_rpi_audio.sh)
# ================================================================================

fix_audio() {
    header "Fixing Audio Configuration"
    
    log "Creating optimized ALSA configuration..."
    ASOUND_PATH="$HOME/.asoundrc"
    
    # Backup existing configuration
    if [[ -f "$ASOUND_PATH" ]]; then
        cp "$ASOUND_PATH" "$ASOUND_PATH.backup"
        log "Backed up existing .asoundrc"
    fi
    
    # Create new optimized configuration
    cat > "$ASOUND_PATH" << 'EOF'
# Optimized ALSA configuration for Raspberry Pi 5
# Handles both USB audio and built-in HDMI audio

pcm.!default {
    type plug
    slave.pcm "dmixer"
}

pcm.dmixer {
    type dmix
    ipc_key 1024
    slave {
        pcm "hw:0,0"
        period_time 0
        period_size 1024
        buffer_size 4096
        channels 2
        rate 44100
    }
    bindings {
        0 0
        1 1
    }
}

pcm.dsnoop {
    type dsnoop
    ipc_key 2048
    slave {
        pcm "hw:0,0"
        channels 2
        rate 44100
    }
}

pcm.duplex {
    type asym
    playback.pcm "dmixer"
    capture.pcm "dsnoop"
}

# Control interface
ctl.!default {
    type hw
    card 0
}

# Alternative configuration for USB audio devices
pcm.usb {
    type hw
    card 1
    device 0
}

ctl.usb {
    type hw
    card 1
}
EOF
    
    chmod 644 "$ASOUND_PATH"
    log "Created optimized ALSA configuration"
    
    # Test audio devices
    log "Testing audio devices..."
    aplay -l 2>/dev/null || warn "No playback devices found"
    arecord -l 2>/dev/null || warn "No recording devices found"
    
    # Set proper audio levels
    log "Setting audio levels..."
    # Set master volume to 80%
    amixer set Master 80% 2>/dev/null || warn "Could not set Master volume"
    # Set PCM volume to 80%
    amixer set PCM 80% 2>/dev/null || warn "Could not set PCM volume"
    # Unmute if muted
    amixer set Master unmute 2>/dev/null || warn "Could not unmute Master"
    
    # Test with a simple beep
    log "Testing audio playback..."
    if command -v speaker-test >/dev/null 2>&1; then
        timeout 3 speaker-test -t sine -f 1000 -l 1 >/dev/null 2>&1 || warn "Audio test failed"
        log "Audio test completed"
    else
        warn "speaker-test not available, skipping audio test"
    fi
    
    # Show current audio configuration
    log "Current audio configuration:"
    echo "ALSA version: $(cat /proc/asound/version 2>/dev/null || echo 'Unknown')"
    echo "Audio cards:"
    cat /proc/asound/cards 2>/dev/null || echo "No audio cards found"
    
    log "Audio configuration fix completed!"
    log "If you still have issues, try:"
    log "  1. Restart your Pi: sudo reboot"
    log "  2. Use USB audio device instead of HDMI"
    log "  3. Check audio with: aplay /usr/share/sounds/alsa/Front_Left.wav"
}

# ================================================================================
# RASPBERRY PI 5 FIXES (from rpi5_fix.sh)
# ================================================================================

fix_rpi5() {
    header "Raspberry Pi 5 Quick Fix"
    
    # Check if virtual environment is activated
    if [[ -z "$VIRTUAL_ENV" ]]; then
        if [[ -d ".venv" ]]; then
            log "Activating virtual environment..."
            source .venv/bin/activate
        else
            log "Creating virtual environment..."
            python3 -m venv .venv
            source .venv/bin/activate
        fi
    fi
    
    # Fix file permissions
    log "Fixing file permissions..."
    sudo chown -R $USER:$USER $HOME || true
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
    
    # Try to remove problematic pyproject.toml temporarily
    log "Temporarily backing up pyproject.toml..."
    if [[ -f "pyproject.toml" ]]; then
        mv pyproject.toml pyproject.toml.backup
    fi
    
    # Install with legacy setuptools (more compatible with older pip)
    log "Installing Fably with legacy setuptools..."
    pip install --editable . --no-use-pep517
    
    # Restore pyproject.toml
    if [[ -f "pyproject.toml.backup" ]]; then
        mv pyproject.toml.backup pyproject.toml
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
        
        # Try alternative installation method
        warn "Trying alternative installation method..."
        
        # Install dependencies one by one to isolate issues
        log "Installing core dependencies individually..."
        pip install openai requests click python-dotenv pyyaml numpy
        pip install sounddevice soundfile vosk pydub aiohttp
        
        # Install Pi-specific packages
        log "Installing Raspberry Pi packages..."
        pip install gpiozero RPi.GPIO || warn "GPIO packages failed (normal if not on Pi)"
        pip install apa102-pi || warn "APA102 LED package failed (normal without hardware)"
        
        # Install wakeword engines
        log "Installing wakeword engines..."
        pip install pvporcupine || warn "Picovoice failed (check platform)"
        pip install onnxruntime || warn "ONNX Runtime failed"
        
        # Manual setup.py install
        log "Running manual setup.py install..."
        python setup.py develop || python setup.py install
        
        # Final test
        if fably --help > /dev/null 2>&1; then
            log "✅ Alternative installation succeeded!"
        else
            error "❌ All installation methods failed"
            error "Please check error messages above and report to developers"
            exit 1
        fi
    fi
    
    log "🎉 RPi5 quick fix completed!"
}

# ================================================================================
# AUTO-DETECTION AND SYSTEM TESTING
# ================================================================================

auto_fix() {
    header "Auto-detecting System and Applying Fixes"
    
    # Detect system type
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
            if grep -q "Pi 5" /proc/cpuinfo 2>/dev/null; then
                log "Detected: Raspberry Pi 5"
                fix_rpi5
            else
                log "Detected: Raspberry Pi (applying general audio fixes)"
                fix_audio
            fi
        else
            log "Detected: Linux system (applying audio fixes)"
            fix_audio
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log "Detected: macOS (no specific fixes needed)"
    else
        warn "Unknown system type: $OSTYPE"
        log "Applying general audio fixes..."
        fix_audio
    fi
}

test_system() {
    header "Testing System Configuration"
    
    log "Checking Python installation..."
    python3 --version
    
    log "Checking virtual environment..."
    if [[ -n "$VIRTUAL_ENV" ]]; then
        log "✅ Virtual environment active: $VIRTUAL_ENV"
    else
        warn "⚠️  Virtual environment not active"
    fi
    
    log "Checking audio devices..."
    if command -v aplay >/dev/null 2>&1; then
        aplay -l 2>/dev/null || warn "No playback devices found"
    fi
    
    if command -v arecord >/dev/null 2>&1; then
        arecord -l 2>/dev/null || warn "No recording devices found"
    fi
    
    log "Checking Fably installation..."
    if command -v fably >/dev/null 2>&1; then
        log "✅ Fably command available"
        fably --help | head -5
    else
        error "❌ Fably command not found"
    fi
    
    log "System test completed"
}

# ================================================================================
# MAIN COMMAND DISPATCHER
# ================================================================================

case "${1:-help}" in
    "audio")
        fix_audio
        ;;
    "rpi5")
        fix_rpi5
        ;;
    "auto")
        auto_fix
        ;;
    "test")
        test_system
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
