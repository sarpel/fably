#!/bin/bash

# Fix RPi5 audio configuration issues
# Run this script to fix ALSA audio problems

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[AUDIO-FIX]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log "Fixing Raspberry Pi 5 Audio Configuration"

# Create proper .asoundrc for Raspberry Pi 5
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
