# Hardware Setup Guide

This guide covers all hardware-related setup and configuration for Fably, including wakeword detection, GPIO controls, audio configuration, and server deployment.

## 🎙️ Wakeword and GPIO Button Systems

### Wakeword Detection

Raspberry Pi Zero 2W için optimize edilmiş wakeword sistemi:

#### Desteklenen Formatlar:
1. **PPN (Picovoice)** - Profesyonel, düşük RAM kullanımı (ÖNERİLEN)
2. **ONNX** - Kendi eğitilmiş model
3. **TFLite** - TensorFlow Lite model (opsiyonel)

#### Kurulum:
```bash
# Picovoice PPN için
pip install pvporcupine

# ONNX için  
pip install onnxruntime

# TFLite için (opsiyonel)
pip install tflite-runtime
```

#### Kullanım:
```bash
# PPN wakeword ile (önerilen)
fably --wakeword-engine ppn --wakeword-model "path/to/fably.ppn" --loop

# ONNX wakeword ile
fably --wakeword-engine onnx --wakeword-model "path/to/fably.onnx" --loop

# GPIO button alternatif olarak
fably --gpio-button --loop
```

### GPIO Button Sistemi

Wakeword alternatifi olarak fiziksel button:

- **Tek basış**: Ses kaydı başlat
- **Çift basış**: Ses değiştir (voice-cycle aktifse)  
- **Uzun basış**: Sistem kapatma

#### Avantajlar:
- Sıfır RAM kullanımı
- %100 güvenilir tetikleme
- Çocuklar için basit kullanım

#### GPIO Configuration:
```bash
# GPIO button kullanımı
fably --gpio-button --loop

# GPIO button + ses değiştirme
fably --gpio-button --voice-cycle --loop

# Button pin değiştir
fably --gpio-button --button-gpio-pin 18 --loop
```

## 🔊 Audio Configuration

### Supported Audio Interfaces

#### 1. **reSpeaker 2-Mic HAT** (Recommended for Pi)
- Best audio quality for voice recognition
- Built-in noise reduction
- Optimized for Pi Zero 2W

#### 2. **USB Audio Adapters**
- Universal compatibility
- Good quality alternatives
- Waveshare USB Audio Adapter recommended

#### 3. **Built-in Audio** 
- HDMI audio output
- 3.5mm jack (where available)
- Basic functionality

### ALSA Configuration

The system automatically creates optimized ALSA configurations:

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

**For USB Audio:**
```bash
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
```

### Audio Troubleshooting

#### Common Issues:

1. **No audio devices found**
   ```bash
   # Check available devices
   aplay -l    # Playback devices
   arecord -l  # Recording devices
   
   # Fix permissions
   sudo usermod -a -G audio $USER
   ```

2. **Audio crackling or distortion**
   ```bash
   # Adjust buffer sizes in .asoundrc
   period_size 1024
   buffer_size 4096
   ```

3. **Microphone not working**
   ```bash
   # Test microphone
   arecord -d 5 test.wav
   aplay test.wav
   
   # Adjust input levels
   alsamixer
   ```

4. **USB audio not detected**
   ```bash
   # Force USB audio recognition
   sudo modprobe snd-usb-audio
   
   # Check USB devices
   lsusb
   ```

## 🖥️ Server Configuration

This section covers running local AI servers for privacy and performance.

### Available Servers

#### STT Server (Speech-to-Text)
- **Technology**: faster-whisper model
- **Performance**: Fast and accurate
- **Default Port**: 5000

#### LLM Server (Language Model)
- **Technology**: [Ollama](https://ollama.com/)
- **Performance**: Fast on both GPU and CPU
- **Default Port**: 11434 (Ollama's default)

#### TTS Server (Text-to-Speech)
- **Technology**: WhisperSpeech
- **Performance**: Very fast on GPU, slower on CPU
- **Default Port**: 5001

### Server Setup

#### Prerequisites
```bash
# Install Docker (recommended)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Or install directly
sudo apt update
sudo apt install python3 python3-pip
```

#### Installing Ollama (LLM Server)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download a model
ollama pull llama3:latest
ollama pull gemma2:9b

# Start Ollama service
systemctl enable ollama
systemctl start ollama
```

#### Running STT Server
```bash
cd servers/stt_server
pip install -r requirements.txt
python stt_server.py
```

#### Running TTS Server
```bash
cd servers/tts_server
pip install -r requirements.txt
python tts_server.py
```

### Server Usage

#### Multiple Machine Setup
You can run servers on different machines for distributed processing:

```bash
# Machine 1: STT Server (port 5000)
cd servers/stt_server && python stt_server.py

# Machine 2: LLM Server (port 11434)
ollama serve

# Machine 3: TTS Server (port 5001)
cd servers/tts_server && python tts_server.py
```

#### Using Local Servers
```bash
# Configure Fably to use local servers
fably --loop \
  --stt-url=http://192.168.1.100:5000/v1 \
  --llm-url=http://192.168.1.101:11434/v1 \
  --llm-model=llama3:latest \
  --tts-url=http://192.168.1.102:5001/v1
```

#### Single Machine Setup
```bash
# All servers on localhost
fably --loop \
  --stt-url=http://localhost:5000/v1 \
  --llm-url=http://localhost:11434/v1 \
  --llm-model=gemma2:9b \
  --tts-url=http://localhost:5001/v1
```

### Performance Optimization

#### For Raspberry Pi Deployment
```bash
# Use lightweight models
ollama pull gemma2:2b     # Smaller model for Pi 4+
ollama pull tinyllama     # Tiny model for Pi Zero 2W

# Optimize for low memory
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
```

#### For GPU Acceleration
```bash
# NVIDIA GPU support for TTS
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# AMD GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2
```

## 🔧 Hardware-Specific Configurations

### Raspberry Pi Zero 2W
- **Memory**: 512MB RAM limit
- **CPU**: Quad-core ARM Cortex-A53
- **Recommended**: PPN wakeword engine, GPIO button
- **Audio**: USB microphone + USB speaker/headphones

### Raspberry Pi 4/5
- **Memory**: 2GB-8GB RAM available
- **CPU**: Higher performance ARM cores
- **Recommended**: ONNX wakeword engine, reSpeaker HAT
- **Audio**: HDMI + USB audio combination

### Generic Linux
- **Audio**: PulseAudio or ALSA
- **Wakeword**: ONNX engine recommended
- **GPIO**: Not available (use keyboard shortcuts)

### macOS
- **Audio**: CoreAudio (automatic)
- **Wakeword**: ONNX engine
- **Controls**: Keyboard shortcuts only

## 🚨 Troubleshooting Hardware Issues

### Audio Problems
```bash
# Run audio diagnostics
./system-fixes.sh audio

# Test audio generation
./audio-tools.sh test-audio
```

### GPIO/Button Issues
```bash
# Check GPIO permissions
sudo usermod -a -G gpio $USER

# Test GPIO functionality
python3 -c "
import gpiozero
led = gpiozero.LED(18)
led.on()
led.off()
print('GPIO test successful')
"
```

### Wakeword Detection Issues
```bash
# Test microphone sensitivity
./dev-tools.sh debug

# Calibrate noise reduction
fably --auto-calibrate --noise-reduction --loop
```

### Performance Issues
```bash
# Monitor system resources
htop

# Check temperature (Pi only)
vcgencmd measure_temp

# Optimize for low memory
sudo systemctl stop unnecessary-services
```

## 📋 Hardware Checklist

### Required Components
- [ ] Raspberry Pi Zero 2W (or higher)
- [ ] MicroSD card (32GB+, Class 10)
- [ ] USB microphone or reSpeaker HAT
- [ ] USB speaker/headphones or HDMI display
- [ ] GPIO button (optional, for wakeword alternative)
- [ ] LED strip (optional, for status indicators)

### Optional Enhancements
- [ ] Active cooling (for Pi 4/5)
- [ ] Power management HAT
- [ ] Case with audio ports
- [ ] External USB hub
- [ ] Ethernet adapter

### Software Requirements
- [ ] Raspberry Pi OS (64-bit recommended)
- [ ] Python 3.8+
- [ ] Virtual environment activated
- [ ] OpenAI API key configured
- [ ] Audio drivers installed
- [ ] GPIO permissions configured

This hardware setup guide provides comprehensive coverage of all hardware-related aspects of Fably deployment. Follow the specific sections relevant to your hardware configuration for optimal performance.
