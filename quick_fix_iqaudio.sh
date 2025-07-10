#!/bin/bash

# ================================================================================
# Quick Fix for IQaudio Codec Zero (Black PCB) - "IQaudIO Limited www.iqaudio.com"
# ================================================================================
# Based on official Raspberry Pi documentation and community solutions
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

header "IQaudio Codec Zero Quick Fix"
log "For 'IQaudIO Limited www.iqaudio.com' version (Black PCB)"

# Step 1: Find and configure config.txt
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

# Backup config.txt
sudo cp "$CONFIG_TXT" "$CONFIG_TXT.backup.$(date +%Y%m%d_%H%M%S)"
log "Backed up config.txt"

# Remove conflicting settings and add IQaudio configuration
log "Configuring device tree overlay..."
sudo sed -i '/dtparam=audio/d' "$CONFIG_TXT"
sudo sed -i '/dtoverlay=iqaudio/d' "$CONFIG_TXT"

# Add IQaudio configuration
cat << 'EOF' | sudo tee -a "$CONFIG_TXT"

# IQaudio Codec Zero configuration (for black PCB version)
dtparam=audio=off
dtoverlay=iqaudio-codec
EOF

log "Added IQaudio overlay to config.txt"

# Step 2: Create .asoundrc for the current user
ASOUND_PATH="$HOME/.asoundrc"

if [[ -f "$ASOUND_PATH" ]]; then
    cp "$ASOUND_PATH" "$ASOUND_PATH.backup.$(date +%Y%m%d_%H%M%S)"
    log "Backed up existing .asoundrc"
fi

log "Creating .asoundrc configuration..."

# Create simple, working .asoundrc based on community solutions
cat > "$ASOUND_PATH" << 'EOF'
# Simple ALSA configuration for IQaudio Codec Zero (Black PCB)
# Based on community solutions and official documentation

pcm.!default {
    type hw
    card "IQaudIOCODEC"
    device 0
}

ctl.!default {
    type hw
    card "IQaudIOCODEC"
}
EOF

chmod 644 "$ASOUND_PATH"
log "Created .asoundrc file: $ASOUND_PATH"

# Step 3: Download official ALSA state files (optional)
log "Downloading official ALSA state files..."

if [[ ! -d "Pi-Codec" ]]; then
    git clone https://github.com/raspberrypi/Pi-Codec.git 2>/dev/null || {
        warn "Could not download Pi-Codec repository"
        warn "You can manually download from: https://github.com/raspberrypi/Pi-Codec"
    }
fi

# Step 4: Test current configuration
log "Testing current configuration..."

if aplay -l 2>/dev/null | grep -q "IQaudIOCODEC"; then
    log "✅ IQaudio Codec Zero already detected!"
    log "No reboot needed for basic functionality"
    
    # Test basic audio
    if command -v speaker-test >/dev/null 2>&1; then
        log "Testing audio output..."
        timeout 3 speaker-test -D hw:IQaudIOCODEC,0 -t sine -f 1000 -l 1 >/dev/null 2>&1 && {
            log "✅ Audio test successful!"
        } || {
            warn "Audio test failed - may need speaker connected or volume adjustment"
        }
    fi
else
    warn "IQaudio Codec Zero not detected yet - reboot required"
fi

header "Configuration Complete"

log "Summary of changes:"
log "✅ Added dtparam=audio=off to $CONFIG_TXT"
log "✅ Added dtoverlay=iqaudio-codec to $CONFIG_TXT"
log "✅ Created .asoundrc for IQaudio Codec Zero"
log "✅ Downloaded official ALSA state files (if available)"

echo
warn "🔄 REBOOT REQUIRED for hardware changes to take effect"
echo
log "After reboot, test with:"
log "  aplay -l | grep IQaudio"
log "  fably --debug 'test hikayesi'"
log "  speaker-test -D hw:IQaudIOCODEC,0 -t sine -f 1000 -l 1"

echo
log "If you need specific audio configurations, use:"
log "  sudo alsactl restore -f Pi-Codec/IQaudIO_Codec_OnboardMIC_record_and_SPK_playback.state"

echo
log "🎉 Quick fix completed! Reboot to activate changes."
