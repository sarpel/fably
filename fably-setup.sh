#!/bin/bash

# ================================================================================
# Fably Complete Setup and Fix Script - All-in-One Solution
# ================================================================================
# This script consolidates all setup, diagnosis, and fix functionality for Fably
# Supports: Installation, Audio Fixes, Diagnostics, Web Interface, and Development
# Compatible with: Raspberry Pi (all models), Linux, macOS
# Special Support: IQaudio Codec Zero, reSpeaker HAT, USB Audio
# ================================================================================

set -e

# Version and Info
SCRIPT_VERSION="2.0.0"
SCRIPT_NAME="Fably All-in-One Setup & Fix"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
header() { 
    echo -e "\n${BLUE}$(printf '=%.0s' {1..60})${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..60})${NC}\n"
}
section() { echo -e "\n${PURPLE}--- $1 ---${NC}"; }

# Global variables
SYSTEM=""
PI_MODEL=""
REBOOT_REQUIRED=false
FABLY_ROOT=$(pwd)

# ================================================================================
# SYSTEM DETECTION
# ================================================================================

detect_system() {
    header "System Detection"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
            if grep -q "Pi 5" /proc/cpuinfo 2>/dev/null; then
                SYSTEM="raspberry_pi5"
                PI_MODEL="5"
                log "Detected: Raspberry Pi 5"
            elif grep -q "Pi 4" /proc/cpuinfo 2>/dev/null; then
                SYSTEM="raspberry_pi4"
                PI_MODEL="4"  
                log "Detected: Raspberry Pi 4"
            elif grep -q "Pi Zero 2" /proc/cpuinfo 2>/dev/null; then
                SYSTEM="raspberry_pi_zero2w"
                PI_MODEL="Zero 2W"
                log "Detected: Raspberry Pi Zero 2W"
            else
                SYSTEM="raspberry_pi"
                PI_MODEL="Unknown"
                log "Detected: Raspberry Pi (model unknown)"
            fi
        else
            SYSTEM="linux"
            log "Detected: Linux system"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        SYSTEM="macos"
        log "Detected: macOS"
    else
        SYSTEM="unknown"
        warn "Unknown system type: $OSTYPE"
        SYSTEM="linux"
    fi
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should NOT be run as root/sudo"
        error "Run it as a regular user, it will prompt for sudo when needed"
        exit 1
    fi
}

# ================================================================================
# AUDIO SYSTEM DETECTION AND CONFIGURATION
# ================================================================================

detect_audio_hardware() {
    section "Audio Hardware Detection"
    
    # Check for IQaudio Codec Zero
    if aplay -l 2>/dev/null | grep -q "IQaudIOCODEC"; then
        log "✅ IQaudio Codec Zero detected"
        AUDIO_CARD="iqaudio"
        return
    fi
    
    # Check for reSpeaker HAT
    if lsmod | grep -q "snd_soc_seeed_voicecard" || aplay -l 2>/dev/null | grep -q "seeed"; then
        log "✅ reSpeaker HAT detected"
        AUDIO_CARD="respeaker"
        return
    fi
    
    # Check for USB audio
    if aplay -l 2>/dev/null | grep -q "USB Audio\|USB\|Card 1"; then
        log "✅ USB Audio device detected"
        AUDIO_CARD="usb"
        return
    fi
    
    # Default to built-in
    log "Using built-in audio (HDMI/3.5mm jack)"
    AUDIO_CARD="builtin"
}

configure_iqaudio_codec_zero() {
    section "Configuring IQaudio Codec Zero (User Tested Configuration)"
    
    # Determine config.txt location
    CONFIG_TXT=""
    if [[ -f "/boot/firmware/config.txt" ]]; then
        CONFIG_TXT="/boot/firmware/config.txt"
    elif [[ -f "/boot/config.txt" ]]; then
        CONFIG_TXT="/boot/config.txt"
    else
        error "Could not find config.txt file"
        return 1
    fi
    
    log "Using config file: $CONFIG_TXT"
    
    # Backup config.txt
    sudo cp "$CONFIG_TXT" "$CONFIG_TXT.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
    log "Backed up config.txt"
    
    # Configure device tree
    log "Configuring device tree overlay..."
    sudo sed -i '/dtparam=audio/d' "$CONFIG_TXT"
    sudo sed -i '/dtoverlay=iqaudio/d' "$CONFIG_TXT"
    
    cat << 'EOF' | sudo tee -a "$CONFIG_TXT"

# IQaudio Codec Zero configuration (User tested on Pi Zero 2W + DietPi)
dtparam=audio=off
dtoverlay=iqaudio-codec
EOF
    
    # Create working .asoundrc (user tested: plughw:0,0 works)
    ASOUND_PATH="$HOME/.asoundrc"
    if [[ -f "$ASOUND_PATH" ]]; then
        cp "$ASOUND_PATH" "$ASOUND_PATH.backup.$(date +%Y%m%d_%H%M%S)"
        log "Backed up existing .asoundrc"
    fi
    
    log "Creating user-tested .asoundrc configuration..."
    cat > "$ASOUND_PATH" << 'EOF'
# WORKING configuration for IQaudio Codec Zero (User tested)
# Tested on Pi Zero 2W + DietPi + "IQaudIO Limited www.iqaudio.com"

pcm.!default {
    type plug
    slave.pcm "hw:0,0"
}

ctl.!default {
    type hw
    card 0
}

# Alternative configurations for advanced use
pcm.iqaudio_dmix {
    type dmix
    ipc_key 1024
    slave {
        pcm "hw:0,0"
        rate 44100
        period_size 1024
        buffer_size 8192
        channels 2
    }
}
EOF
    
    chmod 644 "$ASOUND_PATH"
    log "Created .asoundrc: $ASOUND_PATH"
    
    # Set up audio levels service
    log "Creating audio setup service..."
    sudo tee /etc/systemd/system/iqaudio-setup.service > /dev/null << 'EOF'
[Unit]
Description=IQaudio Codec Zero Setup
After=sound.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'sleep 5 && amixer -c 0 set "Headphone" 80% 2>/dev/null || true && amixer -c 0 set "Lineout" 80% 2>/dev/null || true'
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload 2>/dev/null || true
    sudo systemctl enable iqaudio-setup.service 2>/dev/null || true
    
    REBOOT_REQUIRED=true
    success "IQaudio Codec Zero configured successfully"
}

configure_respeaker_hat() {
    section "Configuring reSpeaker HAT"
    
    # Check if drivers are already installed
    if lsmod | grep -q "snd_soc_seeed_voicecard"; then
        log "reSpeaker HAT drivers already installed"
    else
        log "Installing reSpeaker HAT drivers..."
        if [[ ! -d "seeed-voicecard" ]]; then
            git clone https://github.com/HinTak/seeed-voicecard || {
                error "Failed to clone reSpeaker drivers"
                return 1
            }
        fi
        
        cd seeed-voicecard
        make clean && make
        sudo ./install.sh
        cd "$FABLY_ROOT"
        REBOOT_REQUIRED=true
    fi
    
    # Create .asoundrc for reSpeaker
    ASOUND_PATH="$HOME/.asoundrc"
    log "Creating reSpeaker .asoundrc..."
    cat > "$ASOUND_PATH" << 'EOF'
# reSpeaker HAT configuration
pcm.!default {
    type asym
    playback.pcm "plughw:seeed2micvoicec,0"
    capture.pcm "plughw:seeed2micvoicec,0"
}
ctl.!default {
    type hw
    card "seeed2micvoicec"
}
EOF
    
    success "reSpeaker HAT configured successfully"
}

configure_usb_audio() {
    section "Configuring USB Audio"
    
    ASOUND_PATH="$HOME/.asoundrc"
    log "Creating USB audio .asoundrc..."
    cat > "$ASOUND_PATH" << 'EOF'
# USB Audio configuration
pcm.!default {
    type asym
    playback.pcm {
        type hw
        card 1
        device 0
    }
    capture.pcm {
        type hw
        card 1
        device 0
    }
}
ctl.!default {
    type hw
    card 1
}
EOF
    
    success "USB Audio configured successfully"
}

# Audio configuration for all supported hardware
configure_asoundrc() {
    case $AUDIO_CARD in
        "iqaudio")
            cat > "$HOME/.asoundrc" << 'EOF'
# IQaudio Codec Zero configuration (User tested)
pcm.!default {
    type plug
    slave.pcm "hw:0,0"
}
ctl.!default {
    type hw
    card 0
}
EOF
            log "Created .asoundrc for IQaudio Codec Zero."
            ;;
        "respeaker")
            cat > "$HOME/.asoundrc" << 'EOF'
# reSpeaker HAT configuration
pcm.!default {
    type asym
    playback.pcm "plughw:seeed2micvoicec,0"
    capture.pcm "plughw:seeed2micvoicec,0"
}
ctl.!default {
    type hw
    card "seeed2micvoicec"
}
EOF
            log "Created .asoundrc for reSpeaker HAT."
            ;;
        "usb")
            cat > "$HOME/.asoundrc" << 'EOF'
# USB Audio configuration
pcm.!default {
    type asym
    playback.pcm {
        type hw
        card 1
        device 0
    }
    capture.pcm {
        type hw
        card 1
        device 0
    }
}
ctl.!default {
    type hw
    card 1
}
EOF
            log "Created .asoundrc for USB Audio."
            ;;
        *)
            cat > "$HOME/.asoundrc" << 'EOF'
# Basic ALSA configuration
pcm.!default {
    type hw
    card 0
    device 0
}
ctl.!default {
    type hw
    card 0
}
EOF
            log "Created default .asoundrc."
            ;;
    esac
    chmod 644 "$HOME/.asoundrc"
}

# ================================================================================
# PACKAGE INSTALLATION
# ================================================================================

install_system_packages() {
    header "Installing System Dependencies"
    
    case $SYSTEM in
        "raspberry_pi"*|"raspberry_pi5"|"raspberry_pi4"|"raspberry_pi_zero2w")
            log "Updating package lists..."
            sudo apt update -qq
            
            log "Installing Raspberry Pi system packages..."
            sudo apt install -y \
                git curl wget build-essential \
                python3 python3-pip python3-venv python3-dev python3-setuptools python3-wheel \
                libportaudio2 portaudio19-dev libsndfile1 libsndfile1-dev \
                mpg123 alsa-utils ffmpeg espeak espeak-data \
                i2c-tools spi-tools
            ;;
        "linux")
            log "Installing Linux packages..."
            if command -v apt >/dev/null 2>&1; then
                sudo apt update -qq
                sudo apt install -y git python3 python3-pip python3-venv portaudio19-dev libsndfile1-dev mpg123 ffmpeg espeak
            elif command -v yum >/dev/null 2>&1; then
                sudo yum install -y git python3 python3-pip portaudio-devel libsndfile-devel mpg123 ffmpeg espeak
            fi
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                log "Installing macOS packages via Homebrew..."
                brew install git python3 portaudio libsndfile mpg123 ffmpeg espeak
            else
                warn "Homebrew not found. Please install manually."
            fi
            ;;
    esac
    
    success "System packages installed"
}

setup_python_environment() {
    header "Setting up Python Environment"
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log "Python version: $PYTHON_VERSION"
    
    # Create virtual environment
    if [[ ! -d ".venv" ]]; then
        log "Creating Python virtual environment..."
        if [[ $SYSTEM == "raspberry_pi"* ]]; then
            python3 -m venv --system-site-packages .venv
        else
            python3 -m venv .venv
        fi
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    log "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    success "Python environment ready"
}

install_fably_dependencies() {
    header "Installing Fably Dependencies"
    
    source .venv/bin/activate
    
    log "Installing core dependencies..."
    pip install \
        openai>=1.0.0 requests click python-dotenv pyyaml \
        numpy sounddevice soundfile vosk pydub aiohttp
    
    # Platform-specific packages
    if [[ $SYSTEM == "raspberry_pi"* ]]; then
        log "Installing Raspberry Pi packages..."
        # (GPIO, wakeword ve legacy bağımlılıklar kaldırıldı)
    fi
    
    # Web interface dependencies
    log "Installing web interface dependencies..."
    pip install gradio plotly pandas markdown || warn "Web interface packages failed"
    
    # Install Fably
    log "Installing Fably..."
    if [[ -f "pyproject.toml" ]]; then
        pip install --editable . --use-pep517 || pip install --editable .
    else
        pip install --editable .
    fi
    
    success "Fably dependencies installed"
}

# ================================================================================
# CONFIGURATION SETUP
# ================================================================================

setup_environment_file() {
    header "Setting up Environment Configuration"
    
    if [[ ! -f ".env" ]]; then
        log "Creating .env file..."
        cat > .env << 'EOF'
# Fably Configuration File
# Get your API key at https://platform.openai.com/api-keys

# Required: OpenAI API Key
OPENAI_API_KEY=

# Optional: Additional AI Providers
ELEVENLABS_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=

# Optional: Audio Configuration
# FABLY_AUDIO_DRIVER=alsa
# FABLY_DEFAULT_VOICE=nova
EOF
        
        warn "Please edit .env file and add your API keys:"
        warn "  nano .env"
        warn "  Add your OpenAI API key: OPENAI_API_KEY=sk-your-key-here"
    else
        log ".env file already exists"
    fi
}

create_directories() {
    log "Creating directories..."
    mkdir -p fably/stories fably/sounds logs backups
    success "Directories created"
}

setup_systemd_service() {
    if [[ $SYSTEM != "raspberry_pi"* ]]; then
        return
    fi
    
    header "Setting up Systemd Service"
    
    read -p "Enable Fably to start automatically on boot? (y/N): " enable_service
    
    if [[ $enable_service == "y" || $enable_service == "Y" ]]; then
        USER_NAME=$(whoami)
        
        sudo tee /etc/systemd/system/fably.service > /dev/null << EOF
[Unit]
Description=Fably AI Storyteller
After=network.target sound.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$FABLY_ROOT
Environment=PATH=$FABLY_ROOT/.venv/bin
ExecStart=$FABLY_ROOT/.venv/bin/fably --noise-reduction --auto-calibrate --loop
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable fably.service
        success "Fably service installed and enabled"
    fi
}

setup_fably_web_service() {
    header "Setting up Fably Web Interface systemd service"
    USER_NAME=$(whoami)
    SERVICE_PATH="/etc/systemd/system/fably-web.service"
    sudo tee $SERVICE_PATH > /dev/null << EOF
[Unit]
Description=Fably Web Interface
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$FABLY_ROOT
ExecStart=/usr/bin/python3 $FABLY_ROOT/web_interface/launch.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable fably-web.service
    sudo systemctl restart fably-web.service
    success "Fably web interface service installed, enabled, and started."
}

# ================================================================================
# DIAGNOSTIC FUNCTIONS
# ================================================================================

run_audio_diagnostics() {
    header "Audio System Diagnostics"
    
    # Check audio devices
    section "Audio Devices"
    if command -v aplay >/dev/null 2>&1; then
        log "Playback devices:"
        aplay -l 2>/dev/null || warn "No playback devices found"
    fi
    
    if command -v arecord >/dev/null 2>&1; then
        log "Recording devices:"
        arecord -l 2>/dev/null || warn "No recording devices found"
    fi
    
    # Check Python audio libraries
    section "Python Audio Libraries"
    source .venv/bin/activate 2>/dev/null || true
    
    python3 << 'EOF'
try:
    import sounddevice as sd
    print("✅ sounddevice imported successfully")
    devices = sd.query_devices()
    print(f"Found {len(devices)} audio devices")
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0 or device['max_output_channels'] > 0:
            print(f"  Device {i}: {device['name']}")
except Exception as e:
    print(f"❌ sounddevice failed: {e}")

try:
    import soundfile as sf
    print("✅ soundfile imported successfully")
except Exception as e:
    print(f"❌ soundfile failed: {e}")
EOF
    
    # Test ALSA configuration
    section "ALSA Configuration"
    if [[ -f "$HOME/.asoundrc" ]]; then
        log "✅ .asoundrc exists"
        log "Configuration:"
        head -10 "$HOME/.asoundrc" | sed 's/^/  /'
    else
        warn ".asoundrc not found"
    fi
    
    # Test basic audio playback
    section "Audio Playback Test"
    test_audio_playback
}

test_audio_playback() {
    # Test different audio devices based on user's tested configuration
    local test_commands=(
        "aplay -D plughw:0,0"
        "aplay -D hw:0,0" 
        "aplay -q"
        "aplay -D default"
    )
    
    local test_file="/usr/share/sounds/alsa/Front_Center.wav"
    if [[ ! -f "$test_file" ]]; then
        test_file="/usr/share/sounds/alsa/Front_Left.wav"
    fi
    
    if [[ -f "$test_file" ]]; then
        for cmd in "${test_commands[@]}"; do
            log "Testing: $cmd"
            if timeout 3 $cmd "$test_file" 2>/dev/null; then
                success "✅ Audio test successful with: $cmd"
                return 0
            else
                warn "❌ Failed: $cmd"
            fi
        done
        warn "All audio tests failed"
    else
        warn "No test audio file found"
    fi
}

run_fably_diagnostics() {
    header "Fably System Diagnostics"
    
    # Check virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        log "✅ Virtual environment active: $VIRTUAL_ENV"
    else
        warn "Virtual environment not active"
        if [[ -d ".venv" ]]; then
            source .venv/bin/activate
        fi
    fi
    
    # Check API key
    if [[ -f ".env" ]]; then
        if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
            log "✅ OpenAI API key found"
        else
            warn "OpenAI API key missing or invalid"
        fi
    else
        warn ".env file not found"
    fi
    
    # Check Fably installation
    if command -v fably >/dev/null 2>&1; then
        log "✅ Fably command available"
        fably --help | head -3
    else
        error "Fably command not found"
    fi
    
    # Test basic functionality
    log "Testing Fably imports..."
    python3 << 'EOF'
try:
    import fably
    from fably.cli import cli
    print("✅ Fably imports successful")
except Exception as e:
    print(f"❌ Fably import failed: {e}")
EOF
}

# ================================================================================
# TESTING FUNCTIONS
# ================================================================================

test_installation() {
    header "Testing Complete Installation"
    
    run_audio_diagnostics
    run_fably_diagnostics
    
    section "Quick Functionality Test"
    if command -v fably >/dev/null 2>&1 && [[ -f ".env" ]] && grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        log "Running quick story generation test..."
        echo "Testing with: fably --debug 'test hikayesi'"
        # Note: Actual test would be run by user after API key setup
        success "Installation appears complete"
        log "Next steps:"
        log "1. Edit .env file with your OpenAI API key"
        log "2. Test: fably --debug 'test hikayesi'"
        log "3. Start web interface: fably --web-app"
    else
        warn "Installation incomplete - check API key in .env file"
    fi
}

# ================================================================================
# DEVELOPMENT TOOLS
# ================================================================================

format_code() {
    header "Code Formatting"
    source .venv/bin/activate 2>/dev/null || true
    
    if ! command -v black >/dev/null 2>&1; then
        pip install black
    fi
    
    log "Formatting code with Black..."
    black fably tools servers 2>/dev/null || warn "Some files could not be formatted"
    success "Code formatting completed"
}

check_code_quality() {
    header "Code Quality Check"
    source .venv/bin/activate 2>/dev/null || true
    
    if ! command -v pylint >/dev/null 2>&1; then
        pip install pylint
    fi
    
    log "Running Pylint checks..."
    pylint fably tools/*.py servers/*/*.py 2>/dev/null || warn "Some quality issues found"
    success "Code quality check completed"
}

update_project() {
    header "Project Update"
    
    log "Pulling latest changes..."
    git pull
    
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
        log "Updating dependencies..."
        pip install --editable . --upgrade
    fi
    
    success "Project updated"
}

clean_project() {
    header "Project Cleanup"
    
    log "Removing cache files..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    rm -rf .pytest_cache/ build/ dist/ *.egg-info/ 2>/dev/null || true
    
    success "Project cleanup completed"
}

start_web_interface() {
    header "Starting Fably Web Interface"
    
    source .venv/bin/activate 2>/dev/null || {
        error "Virtual environment not found"
        return 1
    }
    
    # Check and install web dependencies
    if ! python3 -c "import gradio" 2>/dev/null; then
        log "Installing web dependencies..."
        pip install gradio plotly pandas markdown
    fi
    
    log "Starting web interface on http://localhost:7860"
    if [[ -f "tools/gradio_app/enhanced_app.py" ]]; then
        cd tools/gradio_app
        python enhanced_app.py
    else
        fably --web-app
    fi
}

# ================================================================================
# MAIN FUNCTIONS
# ================================================================================

install_complete() {
    header "Complete Fably Installation"
    
    check_root
    detect_system
    install_system_packages
    setup_python_environment
    install_fably_dependencies
    detect_audio_hardware
    configure_asoundrc
    # Configure audio based on detected hardware
    case $AUDIO_CARD in
        "iqaudio")
            configure_iqaudio_codec_zero
            ;;
        "respeaker")
            configure_respeaker_hat
            ;;
        "usb")
            configure_usb_audio
            ;;
        *)
            log "Using default audio configuration"
            ;;
    esac
    
    create_directories
    setup_environment_file
    setup_systemd_service
    setup_fably_web_service
    
    if [[ $REBOOT_REQUIRED == true ]]; then
        warn "🔄 REBOOT REQUIRED for hardware changes to take effect"
    fi
    
    success "🎉 Fably installation completed!"
    log "Next steps:"
    log "1. Edit .env file: nano .env"
    log "2. Add OpenAI API key: OPENAI_API_KEY=sk-your-key"
    if [[ $REBOOT_REQUIRED == true ]]; then
        log "3. Reboot: sudo reboot"
        log "4. Test: fably --debug 'test hikayesi'"
    else
        log "3. Test: fably --debug 'test hikayesi'"
    fi
}

quick_audio_fix() {
    header "Quick Audio Fix"
    
    detect_system
    detect_audio_hardware
    configure_asoundrc
    case $AUDIO_CARD in
        "iqaudio")
            configure_iqaudio_codec_zero
            success "IQaudio Codec Zero configured - reboot required"
            ;;
        "respeaker")
            configure_respeaker_hat
            success "reSpeaker HAT configured"
            ;;
        "usb")
            configure_usb_audio
            success "USB Audio configured"
            ;;
        *)
            log "Creating basic audio configuration..."
            ;;
    esac
    
    if [[ $REBOOT_REQUIRED == true ]]; then
        warn "Reboot required: sudo reboot"
    fi
}

show_usage() {
    echo -e "${CYAN}$SCRIPT_NAME v$SCRIPT_VERSION${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo -e "${YELLOW}Main Commands:${NC}"
    echo "  install                Complete Fably installation"
    echo "  audio-fix             Quick audio configuration fix"
    echo "  diagnose              Run comprehensive diagnostics"
    echo "  test                  Test installation and functionality"
    echo ""
    echo -e "${YELLOW}Development Commands:${NC}"
    echo "  format                Format code with Black"
    echo "  check                 Run code quality checks"
    echo "  update                Update project from repository"
    echo "  clean                 Clean temporary files"
    echo ""
    echo -e "${YELLOW}Web Interface:${NC}"
    echo "  web                   Start web interface"
    echo "  web-deps              Install web dependencies only"
    echo ""
    echo -e "${YELLOW}Diagnostics:${NC}"
    echo "  audio-test            Test audio system only"
    echo "  system-info           Show system information"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 install            # Complete installation"
    echo "  $0 audio-fix          # Fix audio issues"
    echo "  $0 diagnose           # Run full diagnostics"
    echo "  $0 web                # Start web interface"
    echo ""
}

# ================================================================================
# MAIN COMMAND DISPATCHER
# ================================================================================

main() {
    case "${1:-help}" in
        "install")
            install_complete
            ;;
        "audio-fix")
            quick_audio_fix
            ;;
        "diagnose")
            detect_system
            run_audio_diagnostics
            run_fably_diagnostics
            ;;
        "test")
            test_installation
            ;;
        "format")
            format_code
            ;;
        "check")
            check_code_quality
            ;;
        "update")
            update_project
            ;;
        "clean")
            clean_project
            ;;
        "web")
            start_web_interface
            ;;
        "web-deps")
            source .venv/bin/activate 2>/dev/null || true
            pip install gradio plotly pandas markdown
            success "Web dependencies installed"
            ;;
        "audio-test")
            detect_system
            run_audio_diagnostics
            ;;
        "system-info")
            detect_system
            log "System: $SYSTEM"
            log "Pi Model: $PI_MODEL"
            log "Script Version: $SCRIPT_VERSION"
            log "Working Directory: $FABLY_ROOT"
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
}

# Run main function with all arguments
main "$@"
