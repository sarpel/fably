# 🎭 Fably All-in-One Setup

**One script to rule them all!** This consolidated setup script replaces all the individual `.sh` files and provides a comprehensive solution for Fably installation, configuration, and troubleshooting.

## 🚀 Quick Start

```bash
# Clone and run
git clone https://github.com/sarpel/fably.git
cd fably
chmod +x fably-setup.sh

# Complete installation (recommended)
./fably-setup.sh install

# Or fix audio issues only
./fably-setup.sh audio-fix
```

## 📋 All Available Commands

### **Main Commands**
- `./fably-setup.sh install` - Complete Fably installation
- `./fably-setup.sh audio-fix` - Quick audio configuration fix  
- `./fably-setup.sh diagnose` - Run comprehensive diagnostics
- `./fably-setup.sh test` - Test installation and functionality

### **Development Commands**
- `./fably-setup.sh format` - Format code with Black
- `./fably-setup.sh check` - Run code quality checks
- `./fably-setup.sh update` - Update project from repository
- `./fably-setup.sh clean` - Clean temporary files

### **Web Interface**
- `./fably-setup.sh web` - Start web interface
- `./fably-setup.sh web-deps` - Install web dependencies only

### **Diagnostics**
- `./fably-setup.sh audio-test` - Test audio system only
- `./fably-setup.sh system-info` - Show system information

## 🎯 What This Script Replaces

This single script consolidates functionality from all these files:
- `setup.sh` - Main installation
- `fix_iqaudio_codec.sh` - IQaudio fixes
- `quick_fix_iqaudio.sh` - Quick audio fixes
- `diagnose_iqaudio.py` - Audio diagnostics
- `system-fixes.sh` - System-specific fixes
- `audio-tools.sh` - Audio generation tools
- `dev-tools.sh` - Development utilities
- `install_web_deps.sh` - Web interface setup

## 🔧 Special Hardware Support

### **IQaudio Codec Zero** (User Tested)
- Automatic detection of "IQaudIO Limited www.iqaudio.com" version
- Uses proven `plughw:0,0` configuration
- Handles device tree overlay setup
- Creates working `.asoundrc` configuration

### **reSpeaker HAT**
- Automatic driver installation
- Optimized ALSA configuration
- LED and button support

### **USB Audio Devices**
- Automatic detection and configuration
- Fallback support for various USB audio cards

## 🖥️ Platform Support

- **Raspberry Pi Zero 2W** - Full support with optimizations
- **Raspberry Pi 4/5** - Complete functionality
- **Generic Linux** - Core features
- **macOS** - Development support

## ⚡ Quick Examples

```bash
# First time setup on Pi Zero 2W
./fably-setup.sh install

# Fix audio issues after changes
./fably-setup.sh audio-fix

# Check if everything works
./fably-setup.sh diagnose

# Start web interface for story management
./fably-setup.sh web

# Update to latest version
./fably-setup.sh update

# Clean up development files
./fably-setup.sh clean
```

## 🔍 Troubleshooting

If you encounter issues:

1. **Run diagnostics first**: `./fably-setup.sh diagnose`
2. **Check audio**: `./fably-setup.sh audio-test`
3. **Get system info**: `./fably-setup.sh system-info`
4. **Try audio fix**: `./fably-setup.sh audio-fix`

## 📝 After Installation

1. **Edit .env file**: `nano .env`
2. **Add OpenAI API key**: `OPENAI_API_KEY=sk-your-key-here`
3. **Test Fably**: `fably --debug "test hikayesi"`
4. **Start web interface**: `fably --web-app` or `./fably-setup.sh web`

---

**One script, all solutions!** 🎉
