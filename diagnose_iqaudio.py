#!/usr/bin/env python3
"""
Quick diagnostic script for IQaudio Codec Zero audio issues
Run this to diagnose and temporarily fix audio problems
"""

import os
import sys
import subprocess
import logging

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}")

def print_status(success, message):
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def main():
    print_header("Fably IQaudio Codec Zero Diagnostic")
    
    # Check if we're on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        if "Raspberry Pi" in cpuinfo:
            print("✅ Running on Raspberry Pi")
            if "Pi Zero 2" in cpuinfo:
                print("✅ Detected Pi Zero 2W")
        else:
            print("❌ Not running on Raspberry Pi")
            return
    except:
        print("❌ Could not detect system type")
        return
    
    print_header("Audio Device Detection")
    
    # Check ALSA devices
    success, stdout, stderr = run_command("aplay -l")
    if success and "IQaudIOCODEC" in stdout:
        print("✅ IQaudio Codec Zero detected in ALSA")
    else:
        print("❌ IQaudio Codec Zero not detected in ALSA")
        print("   Available devices:")
        if stdout:
            for line in stdout.split('\n'):
                if 'card' in line.lower():
                    print(f"   {line}")
    
    # Check for config.txt settings
    print_header("Configuration Check")
    
    config_files = ["/boot/firmware/config.txt", "/boot/config.txt"]
    config_found = False
    
    for config_file in config_files:
        if os.path.exists(config_file):
            config_found = True
            print(f"✅ Found config file: {config_file}")
            
            try:
                with open(config_file, 'r') as f:
                    config_content = f.read()
                
                if "iqaudio-codec" in config_content:
                    print("✅ IQaudio Codec Zero overlay configured")
                else:
                    print("❌ IQaudio Codec Zero overlay NOT configured")
                    print("   Need to add: dtoverlay=iqaudio-codec")
                
                if "dtparam=audio=off" in config_content:
                    print("✅ Built-in audio disabled")
                else:
                    print("❌ Built-in audio not disabled")
                    print("   Need to add: dtparam=audio=off")
                    
            except Exception as e:
                print(f"❌ Could not read {config_file}: {e}")
            break
    
    if not config_found:
        print("❌ No config.txt file found")
    
    # Check ALSA configuration
    print_header("ALSA Configuration Check")
    
    asoundrc_path = os.path.expanduser("~/.asoundrc")
    if os.path.exists(asoundrc_path):
        print("✅ .asoundrc file exists")
        try:
            with open(asoundrc_path, 'r') as f:
                asound_content = f.read()
            if "IQaudIOCODEC" in asound_content:
                print("✅ .asoundrc configured for IQaudio Codec Zero")
            else:
                print("❌ .asoundrc not configured for IQaudio Codec Zero")
        except Exception as e:
            print(f"❌ Could not read .asoundrc: {e}")
    else:
        print("❌ .asoundrc file does not exist")
    
    # Test Python audio libraries
    print_header("Python Audio Library Test")
    
    try:
        import sounddevice as sd
        print("✅ sounddevice imported successfully")
        
        try:
            devices = sd.query_devices()
            iqaudio_found = False
            for i, device in enumerate(devices):
                if "IQaudIOCODEC" in device['name'] or "iqaudio" in device['name'].lower():
                    iqaudio_found = True
                    print(f"✅ IQaudio device found: {device['name']}")
                    break
            
            if not iqaudio_found:
                print("❌ IQaudio device not found in sounddevice")
                
        except Exception as e:
            print(f"❌ sounddevice device query failed: {e}")
            
    except Exception as e:
        print(f"❌ sounddevice import failed: {e}")
        print("   This is expected - Fably will use ALSA mode")
    
    # Test ALSA directly
    print_header("Direct ALSA Test")
    
    # Try to play a simple tone
    test_commands = [
        "speaker-test -D hw:IQaudIOCODEC,0 -t sine -f 1000 -c 2 -l 1",
        "speaker-test -D default -t sine -f 1000 -c 2 -l 1",
        "speaker-test -t sine -f 1000 -c 2 -l 1"
    ]
    
    for cmd in test_commands:
        print(f"Trying: {cmd}")
        success, stdout, stderr = run_command(f"timeout 3 {cmd} 2>/dev/null")
        if success:
            print(f"✅ Audio test successful with: {cmd}")
            break
        else:
            print(f"❌ Failed: {cmd}")
    else:
        print("❌ All audio tests failed")
    
    # Quick fix recommendations
    print_header("Quick Fix Recommendations")
    
    print("To fix IQaudio Codec Zero issues:")
    print("1. Run the comprehensive fix script:")
    print("   chmod +x fix_iqaudio_codec.sh")
    print("   ./fix_iqaudio_codec.sh")
    print("")
    print("2. Or manually add to config.txt:")
    print("   sudo nano /boot/firmware/config.txt  (or /boot/config.txt)")
    print("   Add these lines:")
    print("   dtparam=audio=off")
    print("   dtoverlay=iqaudio-codec")
    print("")
    print("3. Create basic .asoundrc:")
    print(f"   cat > {asoundrc_path} << 'EOF'")
    print("pcm.!default {")
    print("    type hw")
    print("    card \"IQaudIOCODEC\"")
    print("    device 0")
    print("}")
    print("ctl.!default {")
    print("    type hw") 
    print("    card \"IQaudIOCODEC\"")
    print("}")
    print("EOF")
    print("")
    print("4. Reboot: sudo reboot")
    print("")
    print("5. Test Fably with debug mode:")
    print("   fably --debug 'test hikayesi'")
    
    print_header("Diagnostic Complete")

if __name__ == "__main__":
    main()
