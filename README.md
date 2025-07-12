# 🎭 Fably - Complete Documentation

**Fably**, 5 yaşındaki çocuklara özel olarak tasarlanmış yapay zeka destekli hikaye anlatıcısıdır. Gelişmiş ses tanıma, doğal dil işleme ve metin-ses teknolojisi kullanarak kişiselleştirilmiş, etkileşimli hikayeler oluşturur.

---

## 📑 Table of Contents

1. [Features & Overview](#-features--overview)
2. [Quick Start](#-quick-start)
3. [Setup & Installation](#-setup--installation)
4. [Hardware Configuration](#-hardware-configuration)
5. [Usage Guide](#-usage-guide)
6. [Web Interface](#-web-interface)
7. [Development Guide](#-development-guide)
8. [Troubleshooting](#-troubleshooting)
9. [Examples](#-examples)

---

## ✨ Features & Overview

### 🎙️ **Advanced Voice Interaction**
- **Multi-STT Support** - OpenAI Whisper, Google Cloud Speech, Local Whisper
- **Noise Reduction** - Advanced audio filtering for home environments
- **Auto Calibration** - Automatic adaptation to room acoustics
- **Voice Switching** - Seamless narrator voice transitions

### 🧠 **Multi-AI Support**
- **OpenAI GPT** - GPT-4o, GPT-4o Mini for high-quality stories
- **Google Gemini** - Gemini 1.5 Pro, Gemini 1.5 Flash
- **DeepSeek** - Cost-effective with excellent Turkish support
- **Local Models** - Privacy-focused Ollama support

### 🔊 **Professional Text-to-Speech**
- **OpenAI Voices** - Nova, Alloy, Echo, Fable, Onyx, Shimmer
- **ElevenLabs** - Premium synthesis with emotional expression
- **Voice Consistency** - Character voice preservation throughout stories

### 📚 **Story Management**
- **Story Continuation** - Expand existing stories with new adventures
- **Smart Organization** - Automatic categorization and metadata tracking
- **Collection Management** - Create and share story collections

### 🌐 **Modern Web Interface**
- **Real-time Generation** - Watch stories develop paragraph by paragraph
- **Interactive Controls** - Play, pause, skip, regenerate
- **Visual Story Browser** - Rich interface with search and filtering

### 🏠 **Raspberry Pi Optimization**
- **Low Power Consumption** - Designed for always-on operation
- **Hardware Controls** - Child-friendly physical buttons
- **LED Status Indicators** - Visual feedback for system status
- **Auto-startup** - Launches automatically with system

---

## 🚀 Quick Start

### One-Command Installation

```bash
# Clone Fably and install (all dependencies included)
git clone https://github.com/sarpel/fably.git
cd fably
chmod +x fably-setup.sh
./fably-setup.sh install
```

### First Story

```bash
# Activate environment
source .venv/bin/activate

# Create your first story
fably "Bana cesur bir fare hakkında hikaye anlat"

# Interactive mode
fably --noise-reduction --auto-calibrate --loop

# Web interface
fably --web-app
```

---

## 🔧 Setup & Installation

### All-in-One Setup Script

The `fably-setup.sh` script consolidates all installation and configuration:

#### **Main Commands**
- `./fably-setup.sh install` - Complete Fably installation
- `./fably-setup.sh audio-fix` - Quick audio configuration fix  
- `./fably-setup.sh diagnose` - Run comprehensive diagnostics
- `./fably-setup.sh test` - Test installation and functionality

#### **Development Commands**
- `./fably-setup.sh format` - Format code with Black
- `./fably-setup.sh check` - Run code quality checks
- `./fably-setup.sh update` - Update project from repository
- `./fably-setup.sh clean` - Clean temporary files

#### **Web Interface**
- `./fably-setup.sh web` - Start web interface
- `./fably-setup.sh web-deps` - Install web dependencies only

#### **Diagnostics**
- `./fably-setup.sh audio-test` - Test audio system only
- `./fably-setup.sh system-info` - Show system information

### Manual Development Setup

```bash
# Clone the repository
git clone https://github.com/sarpel/fably.git
cd fably

# Set up development environment
python3 -m venv .venv
source .venv/bin/activate
pip install --editable .

# Install development dependencies
pip install black pylint pytest

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Environment Configuration

Create a `.env` file with your API keys:

```bash
# Required: OpenAI API key
OPENAI_API_KEY=sk-your-openai-api-key

# Optional: Additional AI providers
ELEVENLABS_API_KEY=your-elevenlabs-key
GEMINI_API_KEY=your-gemini-key
DEEPSEEK_API_KEY=your-deepseek-key
```

---

## 🔊 Hardware Configuration

### Audio Hardware Support

#### **reSpeaker 2-Mic HAT** (Recommended for Pi)
- Best audio quality for voice recognition
- Built-in noise reduction
- Optimized for Pi Zero 2W

#### **IQaudio Codec Zero** (User Tested)
- Automatic detection of "IQaudIO Limited www.iqaudio.com" version
- Uses proven `plughw:0,0` configuration
- Handles device tree overlay setup

#### **USB Audio Adapters**
- Universal compatibility
- Good quality alternatives
- Waveshare USB Audio Adapter recommended

### ALSA Configuration

The system automatically creates optimized audio configurations:

**For reSpeaker HAT:**
```bash
pcm.!default {
    type asym
    playback.pcm "plughw:seeed2micvoicec,0"
    capture.pcm "plughw:seeed2micvoicec,0"
}
ctl.!default {
    type hw
    card "seeed2micvoicec"
}
```

**For IQaudio Codec Zero:**
```bash
pcm.!default {
    type plug
    slave.pcm "hw:0,0"
}
ctl.!default {
    type hw
    card 0
}
```

---

## 📖 Usage Guide

### Command Line Interface

#### **Basic Story Generation**
```bash
# Single story generation
fably "Bana ejder ve prensesler hakkında hikaye anlat"
fably "Bir robot dinozorla karşılaştığında ne olur?"

# Specific settings
fably --voice "elevenlabs:rachel" --paragraphs 5 "Uzay macerası hikayesi"
fably --model "gpt-4o-mini" --voice "openai:nova" "Su hikayesi"
```

#### **Interactive Loop Mode**
```bash
# Start listening for voice commands
fably --loop

# Enhanced quality mode (recommended)
fably --noise-reduction --auto-calibrate --loop

# Voice cycling mode
fably --voice-cycle --loop

# All features combined
fably --noise-reduction --auto-calibrate --voice-cycle --loop
```

#### **Story Continuation**
```bash
# Continue existing story
fably --continue "cesur_sovalye_hakkinda" "Şövalye ejderle karşılaştığında ne olur?"

# Continue with different voice
fably --continue "uzay_macerasi" --voice "elevenlabs:adam" "Uzay gemisi Mars'a iniyor"
```

### Command Line Options

#### **Story Generation**
- `--model` - AI model selection
  - `gpt-4o-mini` - OpenAI GPT-4o Mini (fast, cost-effective) **[DEFAULT]**
  - `gpt-4o` - OpenAI GPT-4o (highest quality)
  - `gemini-1.5-pro` - Google Gemini Pro (creative)
  - `deepseek-chat` - DeepSeek Chat (economical)

- `--voice` - Text-to-speech voice selection
  - OpenAI: `openai:nova`, `openai:alloy`, `openai:echo`
  - ElevenLabs: `elevenlabs:rachel`, `elevenlabs:adam`

- `--paragraphs` - Story paragraph count (1-10, default: 6)

#### **Audio Settings**
- `--noise-reduction` - Advanced noise filtering
- `--noise-sensitivity` - Noise gate sensitivity (0.1-10.0)
- `--auto-calibrate` - Automatic room noise measurement
- `--voice-cycle` - Cycle between different voices for variety

#### **Story Management**
- `--continue STORY_NAME` - Continue existing story
- `--story-request` - Request specific story topic

#### **Wakeword & Controls**
- `--wakeword-engine` - Wakeword engine (ppn, onnx, tflite)
- `--wakeword-model` - Wakeword model file path
- `--wakeword-sensitivity` - Detection sensitivity (0.0-1.0)
- `--gpio-button` - Enable GPIO button as wakeword alternative
- `--button-gpio-pin` - GPIO pin number (default: 17)

#### **System Controls**
- `--loop` - Interactive voice command mode
- `--web-app` - Launch web interface
- `--list-voices` - Show all available voices
- `--list-stories` - Show all saved stories
- `--debug` - Enable detailed logging

---

## 🌐 Web Interface

### Starting the Web Interface

```bash
# Professional web interface
fably --web-app
# Opens at http://localhost:7860

# Or start directly
python web_interface/launch.py
```

### Features

#### **📚 Story Library**
- View and edit existing stories
- Real-time paragraph-level editing
- Regenerate audio content
- Story continuation system

#### **✨ New Story Creation**
- Voice query recording and text input
- Multi-AI provider support (OpenAI, Gemini, ElevenLabs)
- Advanced configuration options
- Real-time audio synthesis

#### **⚙️ System Settings**
- Multi-AI provider management
- Audio quality and hardware controls  
- Dynamic language support (Turkish/English)
- Professional configuration interface

### Web Interface Requirements

```bash
# Install web dependencies
pip install -r web_interface/requirements.txt

# Or use setup script
./fably-setup.sh web-deps
```

---

## 🛠️ Development Guide

### Project Structure
```
fably/
├── fably/                    # Core application package
│   ├── cli.py               # Command-line interface
│   ├── fably.py             # Core story logic
│   ├── utils.py             # Utility functions
│   ├── voice_manager.py     # Voice recognition system
│   ├── tts_service.py       # Text-to-speech service
│   └── sounds/              # Audio files
├── web_interface/           # Modern web interface
├── tools/                   # Development tools
├── servers/                 # Independent servers
├── tests/                   # Test suite
├── fably-setup.sh          # Complete setup script
└── DOCUMENTATION.md        # This guide
```

### Development Tools

```bash
# Code formatting
./fably-setup.sh format
# Or: black fably tools servers

# Code quality checks  
./fably-setup.sh check
# Or: pylint fably tools/*.py servers/*/

# Run tests
./fably-setup.sh test

# Update project
./fably-setup.sh update

# Clean temporary files
./fably-setup.sh clean
```

### Enhancement Roadmap

#### **Quality of Life Improvements**

1. **Advanced Story Continuation**
   - Context preservation across sessions
   - Chapter-based storytelling
   - Interactive story choices
   - Bookmark system

2. **Enhanced Audio Quality**
   - Adaptive noise filtering
   - Environment calibration
   - False trigger prevention
   - Real-time audio monitoring

3. **Voice Character Mapping**
   - Different voices for different characters
   - Voice memory per story type
   - Real-time voice preview

#### **Technical Enhancements**

1. **Containerization Support**
   - Docker deployment
   - Self-hosting capability
   - Simplified distribution

2. **Local AI Integration**
   - Ollama model support
   - Privacy-focused deployment
   - Offline capability

3. **Advanced Error Handling**
   - Voice feedback in Turkish
   - LED status indicators
   - Graceful degradation

### Coding Standards

```bash
# File formatting requirements
black --line-length 120 fably/

# Code quality requirements  
pylint --rcfile=.pylintrc fably/

# Import organization
isort fably/
```

### Git Workflow

```bash
# Feature development
git checkout -b feature/story-continuation
git commit -m "feat: add story continuation system"

# Bug fixes
git checkout -b fix/audio-crackling
git commit -m "fix: resolve audio buffer issues"

# Release preparation
git checkout -b release/v1.1.0
git commit -m "chore: prepare v1.1.0 release"
```

---

## 🔧 Troubleshooting

### Common Issues

#### **"API key not found"**
```bash
# Check .env file existence and format
cat .env
# Should contain: OPENAI_API_KEY=sk-your-key
```

#### **"No audio device found"**
```bash
# List available audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Test microphone
python tools/capture_voice_query.py
```

#### **"Voice commands not recognized"**
```bash
# Test without noise reduction
fably --loop

# Increase noise sensitivity
fably --noise-reduction --noise-sensitivity 3.0 --auto-calibrate --loop
```

#### **"Stories generating slowly"**
```bash
# Use faster model
fably --model gpt-4o-mini "Hızlı hikaye"

# Reduce paragraph count
fably --paragraphs 3 "Kısa hikaye"
```

### Debug Mode
```bash
# Enable detailed logging
fably --debug "test hikayesi"

# Check system status
fably --system-info

# Run comprehensive diagnostics
./fably-setup.sh diagnose
```

### Audio Troubleshooting

#### **IQaudio Codec Zero Issues**
```bash
# Apply user-tested fix
./fably-setup.sh audio-fix

# Manual configuration
sudo nano /boot/firmware/config.txt
# Add: dtparam=audio=off
# Add: dtoverlay=iqaudio-codec
```

#### **reSpeaker HAT Issues**
```bash
# Check driver installation
lsmod | grep seeed

# Reinstall drivers if needed
git clone https://github.com/HinTak/seeed-voicecard
cd seeed-voicecard && sudo ./install.sh
```

#### **USB Audio Issues**
```bash
# Check USB audio detection
lsusb
aplay -l

# Force USB audio recognition
sudo modprobe snd-usb-audio
```

---

## 🎯 Examples

### Typical Daily Usage

```bash
# Morning story
fably "Günaydın hikayesi - neşeli bir hayvan macerası"

# Afternoon continuation
fably --continue "sabah_hikayesi" "Kahramanımız yeni arkadaşlarla ne yapıyor?"

# Bedtime story
fably --voice "openai:echo" --paragraphs 4 "Huzurlu uyku hikayesi"
```

### Web Interface Workflow

1. Start: `fably --web-app`
2. Navigate to "Story Creation" tab
3. Enter: "Bir prenses ve sihirli kedi hikayesi"
4. Select voice: "elevenlabs:rachel"
5. Click "Create Story"
6. Listen and enjoy!

### Hardware Button Usage

```bash
# Enable GPIO button system
fably --gpio-button --voice-cycle --loop

# Button actions:
# - Single press: Start recording
# - Double press: Change voice
# - Long press: Shutdown
```

### Story Request System

```bash
# Specific story requests
fably --story-request "Uzayda yaşayan bir kedi hakkında"
fably --story-request "Sihirli orman macerası"
fably --story-request "Prenses ve ejder dostluğu"
```

### Raspberry Pi Deployment

```bash
# Complete Pi Zero 2W setup
./fably-setup.sh install

# Enable auto-startup service
sudo systemctl enable fably.service
sudo systemctl start fably.service

# Check service status
sudo systemctl status fably.service
```

---

## 📊 Platform Support

- **Raspberry Pi Zero 2W** - Full support with memory optimizations
- **Raspberry Pi 4/5** - Complete functionality
- **Generic Linux** - Core features
- **macOS** - Development support

---

## 🎭 Project Philosophy

Fably is designed with these core principles:

1. **Child-First Design** - Every feature prioritizes simplicity and safety for young users
2. **Hardware Efficiency** - Optimized for resource-constrained devices like Pi Zero 2W
3. **Modular Architecture** - STT, LLM, and TTS components are independently configurable
4. **Async Performance** - Smooth user experience through asyncio-based pipeline

---

**Fably ile hayal dünyası sınırsız! 🎭✨**

*This project is lovingly developed to provide safe technology experiences and enhance creativity for 5-year-old children.*

# mDNS ve masal.local ile Web Arayüzüne Erişim

Fably web arayüzü artık yerel ağda `masal.local` adresiyle otomatik olarak erişilebilir. Bu özellik, python-zeroconf kütüphanesi ile sağlanır ve cihazınızın ağda kolayca bulunmasını sağlar.

## Nasıl Çalışır?
- Web arayüzü başlatıldığında, `masal.local:7860` adresi mDNS ile yayınlanır.
- Aynı ağdaki diğer cihazlar, tarayıcıya `http://masal.local:7860` yazarak arayüze ulaşabilir.

## Desteklenen Platformlar
- **Linux (Raspberry Pi dahil):** Avahi veya benzeri mDNS servisleri otomatik çalışır.
- **MacOS:** Bonjour desteğiyle otomatik çalışır.
- **Windows:** Ek Bonjour kurulumu gerekebilir.

## Sorun Giderme
- Eğer `masal.local` açılmıyorsa:
  - Aynı ağda olduğunuzdan emin olun.
  - Linux'ta `avahi-daemon` servisi çalışıyor olmalı.
  - Windows'ta Bonjour servisi kurulu olmalı.
  - Güvenlik duvarı veya ağ kısıtlamalarını kontrol edin.

## Notlar
- mDNS yayını sadece yerel ağda çalışır, internetten erişim için DNS ayarı gerekir.
- Port numarası (7860) gereklidir: `http://masal.local:7860`

---

## 🛡️ Production Quality & Codebase Health

- Tüm kod tabanı, rogue/deprecated kodlardan, gereksiz debug/print satırlarından ve eski OpenAI/Whisper/STT referanslarından tamamen arındırılmıştır.
- Kodda hiçbir hardcoded API anahtarı, parola, gizli bilgi veya güvenlik açığı bulunmamaktadır.
- Linter ve kalite araçlarından (Black, Pylint) başarıyla geçmektedir.
- Tüm broad exception blokları sadeleştirilmiş ve logging fonksiyonları Python standartlarına uygun hale getirilmiştir.
- Kodun tamamı üretime hazır, sürdürülebilir ve güvenlidir.
- .gitignore dosyası, gereksiz ve hassas dosyaların git'e gitmesini engelleyecek şekilde güncellenmiştir.

---
