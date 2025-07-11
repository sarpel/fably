#!/usr/bin/env python3
"""
Fably Comprehensive Diagnostic Tool
Consolidates all diagnostic functionality for audio, system, and Fably components
"""

import os
import sys
import subprocess
import logging
import yaml
from pathlib import Path
import time

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_status(success, message):
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def detect_system_info():
    """Detect system and hardware information"""
    print_header("System Detection")
    
    system_info = {
        'platform': sys.platform,
        'is_raspberry_pi': False,
        'pi_model': None,
        'has_iqaudio': False,
        'has_respeaker': False,
        'has_usb_audio': False
    }
    
    # Check if we're on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        if "Raspberry Pi" in cpuinfo:
            system_info['is_raspberry_pi'] = True
            print("✅ Running on Raspberry Pi")
            
            if "Pi Zero 2" in cpuinfo:
                system_info['pi_model'] = "Zero 2W"
                print("✅ Detected Pi Zero 2W")
            elif "Pi 5" in cpuinfo:
                system_info['pi_model'] = "5"
                print("✅ Detected Pi 5")
            elif "Pi 4" in cpuinfo:
                system_info['pi_model'] = "4"
                print("✅ Detected Pi 4")
            else:
                system_info['pi_model'] = "Unknown"
                print("✅ Detected Raspberry Pi (model unknown)")
        else:
            print(f"✅ Running on {sys.platform}")
    except FileNotFoundError:
        print(f"✅ Running on {sys.platform}")
    except Exception as e:
        print(f"❌ Could not detect system type: {e}")
    
    return system_info

def check_audio_hardware(system_info):
    """Check for audio hardware and drivers"""
    print_header("Audio Hardware Detection")
    
    # Check ALSA devices
    success, stdout, stderr = run_command("aplay -l")
    if success:
        if "IQaudIOCODEC" in stdout:
            system_info['has_iqaudio'] = True
            print("✅ IQaudio Codec Zero detected")
            print("   Card name: IQaudIOCODEC")
        
        if "seeed" in stdout.lower() or "respeaker" in stdout.lower():
            system_info['has_respeaker'] = True
            print("✅ reSpeaker HAT detected")
        
        if "USB Audio" in stdout or "Card 1" in stdout:
            system_info['has_usb_audio'] = True
            print("✅ USB Audio device detected")
        
        if not any([system_info['has_iqaudio'], system_info['has_respeaker'], system_info['has_usb_audio']]):
            print("✅ Using built-in audio (HDMI/3.5mm jack)")
        
        print("\nAvailable audio devices:")
        for line in stdout.split('\n'):
            if 'card' in line.lower():
                print(f"  {line}")
    else:
        print("❌ Could not detect audio devices")
    
    # Check for IQaudio vendor string (specific to IQaudio boards)
    if system_info['has_iqaudio']:
        success, stdout, stderr = run_command("cat /proc/device-tree/hat/vendor 2>/dev/null")
        if success and "IQaudIO Limited" in stdout:
            print("✅ IQaudio Codec Zero (Black PCB) confirmed")
            print("   Vendor: IQaudIO Limited www.iqaudio.com")

def check_configuration_files(system_info):
    """Check system configuration files"""
    print_header("Configuration Check")
    
    # Check config.txt (Raspberry Pi)
    if system_info['is_raspberry_pi']:
        config_files = ["/boot/firmware/config.txt", "/boot/config.txt"]
        config_found = False
        
        for config_file in config_files:
            if os.path.exists(config_file):
                config_found = True
                print(f"✅ Found config file: {config_file}")
                
                try:
                    with open(config_file, 'r') as f:
                        config_content = f.read()
                    
                    audio_disabled = "dtparam=audio=off" in config_content or "#dtparam=audio=on" in config_content
                    iqaudio_enabled = "dtoverlay=iqaudio-codec" in config_content
                    
                    print_status(audio_disabled, "Built-in audio disabled")
                    print_status(iqaudio_enabled, "IQaudio overlay configured")
                    
                    if system_info['has_iqaudio'] and not iqaudio_enabled:
                        print("   🔧 Need to add: dtoverlay=iqaudio-codec")
                    if not audio_disabled and system_info['has_iqaudio']:
                        print("   🔧 Need to add: dtparam=audio=off")
                        
                except Exception as e:
                    print(f"❌ Could not read {config_file}: {e}")
                break
        
        if not config_found:
            print("❌ No config.txt file found")
    
    # Check .asoundrc
    asoundrc_path = os.path.expanduser("~/.asoundrc")
    if os.path.exists(asoundrc_path):
        print("✅ .asoundrc file exists")
        try:
            with open(asoundrc_path, 'r') as f:
                asound_content = f.read()
            
            if system_info['has_iqaudio'] and "IQaudIOCODEC" in asound_content:
                print("✅ .asoundrc configured for IQaudio Codec Zero")
            elif system_info['has_respeaker'] and "seeed" in asound_content:
                print("✅ .asoundrc configured for reSpeaker HAT")
            else:
                print("✅ .asoundrc exists (generic configuration)")
        except Exception as e:
            print(f"❌ Could not read .asoundrc: {e}")
    else:
        print("❌ .asoundrc file does not exist")

def test_audio_functionality():
    """Test audio playback functionality"""
    print_header("Audio Functionality Test")
    
    # Test amixer access
    success, stdout, stderr = run_command("amixer info 2>/dev/null")
    if success:
        print("✅ ALSA mixer accessible")
    else:
        print("❌ Cannot access ALSA mixer")
    
    # Test basic audio playback
    test_commands = [
        "aplay -D plughw:0,0",
        "aplay -D hw:0,0",
        "aplay -D default",
        "aplay"
    ]
    
    test_files = [
        "/usr/share/sounds/alsa/Front_Center.wav",
        "/usr/share/sounds/alsa/Front_Left.wav",
        "/usr/share/sounds/alsa/Front_Right.wav"
    ]
    
    test_file = None
    for tf in test_files:
        if os.path.exists(tf):
            test_file = tf
            break
    
    if test_file:
        print(f"Testing audio playback with: {test_file}")
        for cmd in test_commands:
            print(f"  Trying: {cmd}")
            success, stdout, stderr = run_command(f"timeout 3 {cmd} '{test_file}' 2>/dev/null")
            if success:
                print(f"  ✅ Audio test successful with: {cmd}")
                break
            else:
                print(f"  ❌ Failed: {cmd}")
        else:
            print("  ❌ All audio tests failed")
    else:
        print("❌ No test audio file found")

def check_python_environment():
    """Check Python environment and Fably installation"""
    print_header("Python Environment Check")
    
    # Check Python version
    print(f"✅ Python version: {sys.version}")
    
    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment active")
        print(f"   Environment: {sys.prefix}")
    else:
        print("❌ Virtual environment not active")
        if os.path.exists(".venv"):
            print("   Found .venv directory - activate with: source .venv/bin/activate")
    
    # Check required Python packages
    required_packages = [
        'openai', 'requests', 'click', 'python-dotenv', 'pyyaml',
        'numpy', 'sounddevice', 'soundfile', 'vosk', 'pydub', 'aiohttp'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} missing")
    
    # Check Fably installation
    try:
        import fably
        print("✅ Fably package imported successfully")
        
        # Check if Fably command is available
        success, stdout, stderr = run_command("fably --help")
        if success:
            print("✅ Fably command available")
        else:
            print("❌ Fably command not found")
            print("   Try: pip install --editable .")
            
    except ImportError:
        print("❌ Fably package not found")
        print("   Install with: pip install --editable .")

def check_api_configuration():
    """Check API keys and configuration"""
    print_header("API Configuration Check")
    
    # Check .env file
    if os.path.exists(".env"):
        print("✅ .env file exists")
        
        try:
            with open(".env", 'r') as f:
                env_content = f.read()
            
            if "OPENAI_API_KEY=sk-" in env_content:
                print("✅ OpenAI API key found")
            else:
                print("❌ OpenAI API key missing or invalid")
                print("   Expected format: OPENAI_API_KEY=sk-...")
            
            if "ELEVENLABS_API_KEY=" in env_content:
                elevenlabs_key = [line for line in env_content.split('\n') if line.startswith('ELEVENLABS_API_KEY=')]
                if elevenlabs_key and elevenlabs_key[0].split('=')[1].strip():
                    print("✅ ElevenLabs API key found")
                else:
                    print("⚠️  ElevenLabs API key empty (optional)")
            
            if "GEMINI_API_KEY=" in env_content:
                gemini_key = [line for line in env_content.split('\n') if line.startswith('GEMINI_API_KEY=')]
                if gemini_key and gemini_key[0].split('=')[1].strip():
                    print("✅ Gemini API key found")
                else:
                    print("⚠️  Gemini API key empty (optional)")
                    
        except Exception as e:
            print(f"❌ Could not read .env file: {e}")
    else:
        print("❌ .env file not found")
        print("   Create with: cp env.example .env")

def test_fably_functionality():
    """Test basic Fably functionality"""
    print_header("Fably Functionality Test")
    
    # Check if we can import Fably components
    try:
        from fably import utils, cli
        from fably.voice_manager import voice_manager
        from fably.tts_service import initialize_tts_service
        print("✅ Fably components imported successfully")
    except Exception as e:
        print(f"❌ Fably import failed: {e}")
        return
    
    # Check stories directory
    stories_path = Path("./fably/stories")
    if stories_path.exists():
        story_count = len(list(stories_path.glob("*/info.yaml")))
        print(f"✅ Stories directory exists ({story_count} stories)")
    else:
        print("⚠️  Stories directory not found (will be created when needed)")
    
    # Check examples directory
    examples_path = Path("./fably/examples")
    if examples_path.exists():
        example_count = len(list(examples_path.glob("*/*/info.yaml")))
        print(f"✅ Examples directory exists ({example_count} examples)")
    else:
        print("⚠️  Examples directory not found")

def generate_recommendations(system_info):
    """Generate specific recommendations based on findings"""
    print_header("Recommendations & Quick Fixes")
    
    recommendations = []
    
    # Audio-specific recommendations
    if system_info['has_iqaudio']:
        recommendations.append("IQaudio Codec Zero detected:")
        recommendations.append("  1. Run: ./fably-setup.sh audio-fix")
        recommendations.append("  2. Or manually add to config.txt:")
        recommendations.append("     dtparam=audio=off")
        recommendations.append("     dtoverlay=iqaudio-codec")
        recommendations.append("  3. Create working .asoundrc (user-tested):")
        recommendations.append("     cat > ~/.asoundrc << 'EOF'")
        recommendations.append("pcm.!default {")
        recommendations.append("    type plug")
        recommendations.append("    slave.pcm \"hw:0,0\"")
        recommendations.append("}")
        recommendations.append("ctl.!default {")
        recommendations.append("    type hw")
        recommendations.append("    card 0")
        recommendations.append("}")
        recommendations.append("EOF")
        recommendations.append("  4. Reboot: sudo reboot")
    
    # General setup recommendations
    if not os.path.exists(".env"):
        recommendations.append("\nMissing configuration:")
        recommendations.append("  1. Copy example config: cp env.example .env")
        recommendations.append("  2. Edit .env and add your OpenAI API key")
    
    # Virtual environment recommendations
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        recommendations.append("\nVirtual environment setup:")
        recommendations.append("  1. Run: ./fably-setup.sh install")
        recommendations.append("  2. Or manually: source .venv/bin/activate")
    
    # Testing recommendations
    recommendations.append("\nTest Fably functionality:")
    recommendations.append("  1. Basic test: fably --debug 'test hikayesi'")
    recommendations.append("  2. Web interface: fably --web-app")
    recommendations.append("  3. Enhanced web: python tools/gradio_app/enhanced_app.py")
    
    for rec in recommendations:
        print(rec)

def main():
    """Main diagnostic function"""
    print_header("Fably Comprehensive Diagnostic Tool")
    print("This tool will check your Fably installation and configuration")
    
    # Run all diagnostic checks
    system_info = detect_system_info()
    check_audio_hardware(system_info)
    check_configuration_files(system_info)
    test_audio_functionality()
    check_python_environment()
    check_api_configuration()
    test_fably_functionality()
    generate_recommendations(system_info)
    
    print_header("Diagnostic Complete")
    print("If you see any ❌ errors above, follow the recommendations to fix them.")
    print("For comprehensive setup, run: ./fably-setup.sh install")

if __name__ == "__main__":
    main()
