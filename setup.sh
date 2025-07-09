#!/bin/bash

# ================================================================================
# Fably Project - Complete Installation and Setup Script
# ================================================================================
# This script handles the complete installation of Fably from zero to production
# It consolidates all installation requirements, dependencies, and configuration
# ================================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log function with colors
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

# ================================================================================
# SYSTEM DETECTION AND REQUIREMENTS
# ================================================================================

detect_system() {
    header "System Detection"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
            SYSTEM="raspberry_pi"
            log "Detected: Raspberry Pi OS"
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
        warn "Proceeding with generic Linux installation..."
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
# PACKAGE INSTALLATION FUNCTIONS
# ================================================================================

install_system_packages() {
    header "Installing System Dependencies"
    
    case $SYSTEM in
        "raspberry_pi"|"linux")
            log "Updating package lists..."
            sudo apt update
            
            log "Installing system packages..."
            sudo apt install -y \
                git \
                curl \
                wget \
                build-essential \
                python3 \
                python3-pip \
                python3-venv \
                python3-dev \
                python3-setuptools \
                python3-wheel \
                python3-numpy \
                python3-scipy \
                python3-yaml \
                libportaudio2 \
                portaudio19-dev \
                libsndfile1 \
                libsndfile1-dev \
                mpg123 \
                alsa-utils \
                ffmpeg \
                espeak \
                espeak-data \
                libespeak1 \
                libespeak-dev \
                libjack-jackd2-dev
            
            if [[ $SYSTEM == "raspberry_pi" ]]; then
                log "Installing Raspberry Pi specific packages..."
                sudo apt install -y \
                    python3-gpiozero \
                    python3-rpi.gpio \
                    python3-bluez \
                    raspi-config
            fi
            ;;
        "macos")
            if ! command -v brew &> /dev/null; then
                error "Homebrew not found. Please install Homebrew first:"
                error "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            
            log "Installing macOS packages via Homebrew..."
            brew install \
                git \
                python3 \
                portaudio \
                libsndfile \
                mpg123 \
                ffmpeg \
                espeak
            ;;
    esac
    
    log "System packages installed successfully"
}

setup_python_environment() {
    header "Setting up Python Environment"
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log "Python version: $PYTHON_VERSION"
    
    if [[ $(echo "$PYTHON_VERSION 3.8" | awk '{print ($1 >= $2)}') == 1 ]]; then
        log "Python version is compatible (>= 3.8)"
    else
        error "Python 3.8 or higher is required, found $PYTHON_VERSION"
        exit 1
    fi
    
    # Create virtual environment
    if [[ $SYSTEM == "raspberry_pi" ]]; then
        log "Creating Python virtual environment with system packages..."
        python3 -m venv --system-site-packages .venv
    else
        log "Creating Python virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    log "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    log "Python environment setup complete"
}

install_python_dependencies() {
    header "Installing Python Dependencies"
    
    # Ensure virtual environment is active
    source .venv/bin/activate
    
    log "Installing core dependencies..."
    pip install \
        openai>=1.0.0 \
        requests \
        click \
        python-dotenv \
        pyyaml \
        numpy \
        sounddevice \
        soundfile \
        vosk \
        pydub \
        aiohttp
    
    # Install platform-specific packages
    case $SYSTEM in
        "raspberry_pi")
            log "Installing Raspberry Pi specific packages..."
            pip install \
                apa102-pi \
                gpiozero \
                RPi.GPIO
            ;;
        "linux")
            log "Installing Linux audio packages..."
            pip install pyaudio
            ;;
        "macos")
            log "Installing macOS audio packages..."
            pip install pyaudio
            ;;
    esac
    
    # Install Fably in development mode
    log "Installing Fably in development mode..."
    pip install --editable .
    
    log "Python dependencies installed successfully"
}

# ================================================================================
# RASPBERRY PI SPECIFIC SETUP
# ================================================================================

setup_raspberry_pi_hardware() {
    if [[ $SYSTEM != "raspberry_pi" ]]; then
        return
    fi
    
    header "Raspberry Pi Hardware Setup"
    
    # Check if reSpeaker HAT is connected
    log "Checking for reSpeaker HAT..."
    if lsmod | grep -q "snd_soc_seeed_voicecard"; then
        log "reSpeaker HAT drivers already installed"
    else
        warn "reSpeaker HAT not detected or drivers not installed"
        read -p "Do you want to install reSpeaker HAT drivers? (y/N): " install_respeaker
        
        if [[ $install_respeaker == "y" || $install_respeaker == "Y" ]]; then
            install_respeaker_drivers
        fi
    fi
    
    # Enable SPI and I2C
    log "Enabling SPI and I2C interfaces..."
    sudo raspi-config nonint do_spi 0
    sudo raspi-config nonint do_i2c 0
    
    # Configure audio settings
    configure_audio_settings
}

install_respeaker_drivers() {
    log "Installing reSpeaker HAT drivers..."
    
    # Clone the driver repository
    if [[ ! -d "seeed-voicecard" ]]; then
        git clone https://github.com/HinTak/seeed-voicecard
    fi
    
    cd seeed-voicecard
    
    # Get kernel version and switch to appropriate branch
    KERNEL_VERSION=$(uname -r | sed 's/\([0-9]*\.[0-9]*\).*/\1/')
    log "Kernel version: $KERNEL_VERSION"
    
    if git show-ref --verify --quiet "refs/remotes/origin/v$KERNEL_VERSION"; then
        log "Switching to branch v$KERNEL_VERSION"
        git checkout "v$KERNEL_VERSION"
    else
        warn "No specific branch for kernel $KERNEL_VERSION, using master"
    fi
    
    # Compile and install drivers
    make clean
    make
    sudo ./install.sh
    
    cd ..
    
    log "reSpeaker HAT drivers installed. Reboot required."
    REBOOT_REQUIRED=true
}

configure_audio_settings() {
    log "Configuring audio settings..."
    
    # Create ALSA configuration for optimal audio
    cat > ~/.asoundrc << 'EOF'
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
    
    # Set audio levels
    if command -v amixer &> /dev/null; then
        log "Setting optimal audio levels..."
        amixer -c seeed2micvoicec set 'Headphone' 80%
        amixer -c seeed2micvoicec set 'Speaker' 80%
    fi
}

# ================================================================================
# CONFIGURATION AND SETUP
# ================================================================================

setup_environment_file() {
    header "Setting up Environment Configuration"
    
    if [[ ! -f ".env" ]]; then
        log "Creating .env file from example..."
        cp env.example .env
        
        warn "Please edit .env file and add your API keys:"
        warn "  - OPENAI_API_KEY (required)"
        warn "  - ELEVENLABS_API_KEY (optional)"
        warn "  - GEMINI_API_KEY (optional)"
        warn "  - DEEPSEEK_API_KEY (optional)"
        
        read -p "Press Enter to continue after editing .env file..."
    else
        log ".env file already exists"
    fi
}

create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p fably/stories
    mkdir -p fably/sounds
    mkdir -p logs
    mkdir -p backups
    
    log "Directories created successfully"
}

setup_systemd_service() {
    if [[ $SYSTEM != "raspberry_pi" ]]; then
        return
    fi
    
    header "Setting up Systemd Service"
    
    read -p "Do you want to enable Fably to start automatically on boot? (y/N): " enable_service
    
    if [[ $enable_service == "y" || $enable_service == "Y" ]]; then
        log "Installing systemd service..."
        
        # Create service file with current user and path
        USER_NAME=$(whoami)
        FABLY_PATH=$(pwd)
        
        sudo tee /etc/systemd/system/fably.service > /dev/null << EOF
[Unit]
Description=Fably AI Storyteller
After=network.target sound.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$FABLY_PATH
Environment=PATH=$FABLY_PATH/.venv/bin
ExecStart=$FABLY_PATH/.venv/bin/fably --noise-reduction --auto-calibrate --loop
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable fably.service
        
        log "Fably service installed and enabled"
        log "Use 'sudo systemctl start fably.service' to start manually"
        log "Use 'sudo systemctl status fably.service' to check status"
    fi
}

# ================================================================================
# TESTING AND VERIFICATION
# ================================================================================

test_installation() {
    header "Testing Installation"
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Test basic import
    log "Testing Python imports..."
    python3 -c "
import fably
import openai
import sounddevice
import vosk
print('All imports successful')
"
    
    # Test CLI
    log "Testing CLI functionality..."
    fably --help > /dev/null
    
    # Test audio devices
    log "Testing audio devices..."
    python3 -c "
import sounddevice as sd
devices = sd.query_devices()
print(f'Found {len(devices)} audio devices')
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f'  Input device {i}: {device[\"name\"]}')
    if device['max_output_channels'] > 0:
        print(f'  Output device {i}: {device[\"name\"]}')
"
    
    log "Installation test completed successfully"
}

# ================================================================================
# DEVELOPMENT AND MAINTENANCE FUNCTIONS
# ================================================================================

format_code() {
    header "Code Formatting"
    
    # Activate virtual environment if it exists
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    fi
    
    # Check if black is installed, if not install it
    if ! command -v black &> /dev/null; then
        log "Black not found, installing..."
        pip install black
    fi
    
    log "Formatting Python code with Black..."
    black fably tools servers
    
    log "Code formatting completed"
}

check_code() {
    header "Code Quality Check"
    
    # Activate virtual environment if it exists
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    fi
    
    # Check if pylint is installed, if not install it
    if ! command -v pylint &> /dev/null; then
        log "Pylint not found, installing..."
        pip install pylint
    fi
    
    log "Running Pylint code quality checks..."
    pylint fably tools/*.py servers/stt_server/*.py servers/tts_server/*.py
    
    log "Code quality check completed"
}

update_project() {
    header "Project Update"
    
    log "Pulling latest changes from repository..."
    git pull
    
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
        log "Updating Python dependencies..."
        pip install --editable .
    fi
    
    log "Project update completed"
}

clean_project() {
    header "Project Cleanup"
    
    log "Removing Python cache files..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    log "Removing temporary files..."
    rm -rf .pytest_cache/ 2>/dev/null || true
    rm -rf build/ 2>/dev/null || true
    rm -rf dist/ 2>/dev/null || true
    rm -rf *.egg-info/ 2>/dev/null || true
    
    log "Project cleanup completed"
}

show_usage() {
    echo "Fably Setup and Maintenance Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Complete installation setup (default)"
    echo "  format      Format code with Black"
    echo "  check       Run code quality checks with Pylint"
    echo "  update      Update project from repository"
    echo "  clean       Clean temporary and cache files"
    echo "  test        Run installation tests"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Run complete installation"
    echo "  $0 install     # Run complete installation"
    echo "  $0 format      # Format code"
    echo "  $0 check       # Check code quality"
    echo "  $0 update      # Update project"
    echo ""
}

# ================================================================================
# MAIN INSTALLATION SEQUENCE
# ================================================================================

main_install() {
    header "Fably Complete Setup Script"
    
    # Initialize variables
    REBOOT_REQUIRED=false
    
    # Check prerequisites
    check_root
    detect_system
    
    # Main installation sequence
    install_system_packages
    setup_python_environment
    install_python_dependencies
    
    # Platform-specific setup
    setup_raspberry_pi_hardware
    
    # Configuration
    create_directories
    setup_environment_file
    setup_systemd_service
    
    # Verification
    test_installation
    
    # Final instructions
    header "Installation Complete!"
    
    log "Fably has been successfully installed!"
    log ""
    log "Quick Start Commands:"
    log "  source .venv/bin/activate    # Activate virtual environment"
    log "  fably --help                 # Show all available options"
    log "  fably --loop                 # Start in interactive mode"
    log "  fably 'Tell me a story'      # Generate a single story"
    log ""
    log "Advanced Commands:"
    log "  fably --noise-reduction --auto-calibrate --loop  # Best quality"
    log "  fably --voice-cycle --loop                       # Cycle voices"
    log "  fably --web-app                                  # Start web interface"
    log ""
    log "Configuration Files:"
    log "  .env                         # API keys and settings"
    log "  .venv/                       # Python virtual environment"
    log "  fably/stories/              # Generated stories"
    log "  fably/sounds/               # Audio files"
    log ""
    
    if [[ $REBOOT_REQUIRED == "true" ]]; then
        warn "REBOOT REQUIRED for hardware drivers to take effect"
        read -p "Reboot now? (y/N): " do_reboot
        if [[ $do_reboot == "y" || $do_reboot == "Y" ]]; then
            sudo reboot
        fi
    fi
    
    log "Setup completed successfully!"
}

# ================================================================================
# COMMAND-LINE ARGUMENT HANDLING
# ================================================================================

# Handle command-line arguments
case "${1:-install}" in
    "install")
        main_install
        ;;
    "format")
        format_code
        ;;
    "check")
        check_code
        ;;
    "update")
        update_project
        ;;
    "clean")
        clean_project
        ;;
    "test")
        # Activate virtual environment if it exists
        if [[ -f ".venv/bin/activate" ]]; then
            source .venv/bin/activate
        fi
        test_installation
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
