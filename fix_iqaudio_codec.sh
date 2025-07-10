#!/bin/bash

# ================================================================================
# IQaudio Codec Zero Sound Card Fix for Fably
# ================================================================================
# This script configures ALSA specifically for IQaudio Codec Zero on Pi Zero 2W
# Usage: ./fix_iqaudio_codec.sh
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

header "IQaudio Codec Zero Configuration Fix"

# Check if we're on a Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    error "This script is designed for Raspberry Pi systems only"
    exit 1
fi

log "Detected Raspberry Pi - proceeding with IQaudio Codec Zero setup"

# Step 1: Check current audio devices
log "Current audio devices:"
aplay -l 2>/dev/null || warn "No audio devices found via aplay"
echo

# Step 2: Enable I2S and configure device tree
log "Configuring device tree for IQaudio Codec Zero..."

# Backup config.txt
sudo cp /boot/config.txt /boot/config.txt.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || \
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || \
warn "Could not backup config.txt - continuing anyway"

# Determine config.txt location
CONFIG_TXT=""
if [[ -f "/boot/firmware/config.txt" ]]; then
    CONFIG_TXT="/boot/firmware/config.txt"
elif [[ -f "/boot/config.txt" ]]; then
    CONFIG_TXT="/boot/config.txt"
else
    error "Could not find config.txt file"
    exit 1
fi

log "Using config file: $CONFIG_TXT"

# Remove conflicting audio settings
log "Removing conflicting audio settings..."
sudo sed -i '/dtparam=audio/d' "$CONFIG_TXT"
sudo sed -i '/dtoverlay=vc4-kms-v3d/d' "$CONFIG_TXT"
sudo sed -i '/dtoverlay=iqaudio/d' "$CONFIG_TXT"

# Add IQaudio Codec Zero configuration
log "Adding IQaudio Codec Zero device tree overlay..."
cat << 'EOF' | sudo tee -a "$CONFIG_TXT"

# IQaudio Codec Zero configuration
dtparam=audio=off
dtoverlay=iqaudio-codec
EOF

# Step 3: Configure ALSA for IQaudio Codec Zero
log "Creating ALSA configuration for IQaudio Codec Zero..."

ASOUND_PATH="$HOME/.asoundrc"

# Backup existing .asoundrc
if [[ -f "$ASOUND_PATH" ]]; then
    cp "$ASOUND_PATH" "$ASOUND_PATH.backup.$(date +%Y%m%d_%H%M%S)"
    log "Backed up existing .asoundrc"
fi

# Create optimized ALSA config for IQaudio Codec Zero (black PCB version)
cat > "$ASOUND_PATH" << 'EOF'
# ALSA configuration for IQaudio Codec Zero 
# Optimized for "IQaudIO Limited www.iqaudio.com" version (black PCB)
# Compatible with Fably on Raspberry Pi Zero 2W

pcm.!default {
    type asym
    playback.pcm "iqaudio_playback"
    capture.pcm "iqaudio_capture"
}

pcm.iqaudio_playback {
    type plug
    slave {
        pcm "hw:IQaudIOCODEC,0"
        rate 44100
        channels 2
        format S16_LE
        period_size 1024
        buffer_size 4096
    }
}

pcm.iqaudio_capture {
    type plug
    slave {
        pcm "hw:IQaudIOCODEC,0"
        rate 44100
        channels 1
        format S16_LE
        period_size 1024
        buffer_size 4096
    }
}

# Control interface
ctl.!default {
    type hw
    card "IQaudIOCODEC"
}

# Alternative simple configuration
pcm.iqaudio_simple {
    type hw
    card "IQaudIOCODEC"
    device 0
}

# Dmix configuration for audio mixing
pcm.dmixer {
    type dmix
    ipc_key 1024
    slave {
        pcm "hw:IQaudIOCODEC,0"
        rate 44100
        period_time 0
        period_size 1024
        buffer_size 8192
        channels 2
    }
    bindings {
        0 0
        1 1
    }
}

# Dsnoop configuration for audio capture sharing
pcm.dsnooper {
    type dsnoop
    ipc_key 816357492
    ipc_key_add_uid 0
    ipc_perm 0666
    slave {
        pcm "hw:IQaudIOCODEC,0"
        channels 1
        rate 44100
    }
}
EOF

chmod 644 "$ASOUND_PATH"
log "Created ALSA configuration file: $ASOUND_PATH"

# Step 4: Set up module loading
log "Configuring kernel modules for IQaudio Codec Zero..."

# Create modprobe configuration
sudo tee /etc/modprobe.d/iqaudio-codec.conf > /dev/null << 'EOF'
# IQaudio Codec Zero module configuration
options snd-soc-iqaudio-codec dai_fmt=i2s
EOF

# Step 5: Configure system audio settings for IQaudio Codec Zero
log "Configuring system audio settings..."

# Create systemd service to set audio levels on boot
sudo tee /etc/systemd/system/iqaudio-setup.service > /dev/null << 'EOF'
[Unit]
Description=IQaudio Codec Zero Setup
After=sound.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'sleep 5 && amixer -c IQaudIOCODEC set "Headphone" 80% 2>/dev/null || true && amixer -c IQaudIOCODEC set "Lineout" 80% 2>/dev/null || true && amixer -c IQaudIOCODEC set "Mic 1" 50% 2>/dev/null || true'
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable iqaudio-setup.service

# Step 6: Test the configuration (without reboot)
log "Testing current audio configuration..."

# Check if IQaudio device is detected
if aplay -l 2>/dev/null | grep -q "IQaudIOCODEC"; then
    log "✅ IQaudio Codec Zero detected in ALSA"
else
    warn "⚠️ IQaudio Codec Zero not yet detected - reboot required"
fi

# Step 7: Create a Fably-specific audio test
log "Creating Fably audio test script..."

cat > test_iqaudio.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for IQaudio Codec Zero with Fably
"""

import sys
import logging

# Test sounddevice import
try:
    import sounddevice as sd
    print("✅ sounddevice imported successfully")
    
    # List audio devices
    devices = sd.query_devices()
    print(f"\n📊 Found {len(devices)} audio devices:")
    
    iqaudio_found = False
    for i, device in enumerate(devices):
        if "IQaudIOCODEC" in device['name'] or "iqaudio" in device['name'].lower():
            iqaudio_found = True
            print(f"🎵 IQaudio device {i}: {device['name']}")
            if device['max_input_channels'] > 0:
                print(f"   - Input channels: {device['max_input_channels']}")
            if device['max_output_channels'] > 0:
                print(f"   - Output channels: {device['max_output_channels']}")
        else:
            print(f"   Device {i}: {device['name']}")
    
    if not iqaudio_found:
        print("\n⚠️ IQaudio Codec Zero not found in sounddevice list")
        print("   This may be normal before reboot")
    
except Exception as e:
    print(f"❌ sounddevice import failed: {e}")
    print("   Fably will use ALSA-only mode")

# Test ALSA directly
print("\n🔧 Testing ALSA configuration:")
import subprocess

try:
    # Test aplay
    result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
    if "IQaudIOCODEC" in result.stdout:
        print("✅ IQaudio Codec Zero detected in ALSA")
    else:
        print("⚠️ IQaudio Codec Zero not detected in ALSA yet")
        
except Exception as e:
    print(f"❌ ALSA test failed: {e}")

print("\n🎯 Fably compatibility test:")
try:
    # Test Fably audio utilities
    sys.path.insert(0, '.')
    from fably.utils import play_sound
    
    print("✅ Fably audio utilities imported successfully")
    print("   Fably will automatically fall back to ALSA mode if needed")
    
except Exception as e:
    print(f"❌ Fably audio utilities test failed: {e}")

print("\n📋 Next steps:")
print("1. Reboot your Pi: sudo reboot")
print("2. Test Fably: fably 'test hikayesi'")
print("3. Use ALSA mode if needed: fably --debug 'test hikayesi'")
EOF

chmod +x test_iqaudio.py

# Run the test
log "Running compatibility test..."
python3 test_iqaudio.py

echo
header "IQaudio Codec Zero Configuration Complete"

log "Configuration summary:"
log "✅ Device tree overlay configured: iqaudio-codec"
log "✅ ALSA configuration created: $ASOUND_PATH"
log "✅ Kernel module configuration: /etc/modprobe.d/iqaudio-codec.conf"
log "✅ System service created: iqaudio-setup.service"
log "✅ Audio test script created: test_iqaudio.py"

echo
warn "🔄 REBOOT REQUIRED for hardware changes to take effect"
warn "   After reboot, run: ./test_iqaudio.py"

echo
log "🚀 Quick test commands after reboot:"
log "   fably --debug 'test hikayesi'           # Debug mode"
log "   fably 'bana bir hikaye anlat'           # Normal mode"
log "   aplay /usr/share/sounds/alsa/Front_Left.wav  # ALSA test"

echo
log "💡 If audio still doesn't work after reboot:"
log "   1. Check: aplay -l | grep IQaudio"
log "   2. Run: amixer -c IQaudIOCODEC"
log "   3. Try: fably --help  # Use built-in fallbacks"

log "Configuration completed successfully! 🎉"
