#!/usr/bin/env python3
"""
IQaudio Codec Zero (Black PCB) Diagnostic and Quick Fix
Specifically for "IQaudIO Limited www.iqaudio.com" version
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
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_status(success, message):
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def main():
    print_header("IQaudio Codec Zero (Black PCB) Diagnostic & Quick Fix")
    print("For 'IQaudIO Limited www.iqaudio.com' version")
    
    # Check Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        if "Raspberry Pi" in cpuinfo:
            print("✅ Running on Raspberry Pi")
            if "Pi Zero 2" in cpuinfo:
                print("✅ Detected Pi Zero 2W - Perfect for IQaudio Codec Zero")
        else:
            print("❌ Not running on Raspberry Pi")
            return
    except:
        print("❌ Could not detect system type")
        return
    
    print_header("Step 1: Hardware Detection")
    
    # Check for IQaudio board version
    success, stdout, stderr = run_command("cat /proc/device-tree/hat/vendor 2>/dev/null")
    if success and "IQaudIO Limited" in stdout:
        print("✅ IQaudio Codec Zero (Black PCB) detected")
        print("   Vendor: IQaudIO Limited www.iqaudio.com")
    else:
        print("❌ IQaudio vendor string not found")
        print("   This might be expected before configuration")
    
    # Check ALSA detection
    success, stdout, stderr = run_command("aplay -l")
    if success and "IQaudIOCODEC" in stdout:
        print("✅ IQaudio Codec Zero detected in ALSA as 'IQaudIOCODEC'")
        print("   Card name: IQaudIOCODEC")
    else:
        print("❌ IQaudio Codec Zero not detected in ALSA")
        print("   Available devices:")
        if stdout:
            for line in stdout.split('\n'):
                if 'card' in line.lower():
                    print(f"   {line}")
    
    print_header("Step 2: Configuration Check")
    
    # Check config.txt
    config_files = ["/boot/firmware/config.txt", "/boot/config.txt"]
    config_found = False
    config_file = None
    
    for cf in config_files:
        if os.path.exists(cf):
            config_found = True
            config_file = cf
            print(f"✅ Found config file: {cf}")
            break
    
    if config_found:
        try:
            with open(config_file, 'r') as f:
                config_content = f.read()
            
            audio_disabled = "dtparam=audio=off" in config_content or "#dtparam=audio=on" in config_content
            iqaudio_enabled = "dtoverlay=iqaudio-codec" in config_content
            
            print_status(audio_disabled, "Built-in audio disabled")
            print_status(iqaudio_enabled, "IQaudio overlay configured (dtoverlay=iqaudio-codec)")
            
            if not audio_disabled:
                print("   🔧 Need to disable built-in audio")
            if not iqaudio_enabled:
                print("   🔧 Need to add dtoverlay=iqaudio-codec")
                
        except Exception as e:
            print(f"❌ Could not read {config_file}: {e}")
    else:
        print("❌ No config.txt file found")
    
    # Check .asoundrc
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
    
    print_header("Step 3: Quick Audio Test")
    
    # Test amixer
    success, stdout, stderr = run_command("amixer -c IQaudIOCODEC info 2>/dev/null")
    if success:
        print("✅ IQaudio Codec Zero mixer accessible")
        
        # Show available controls
        success, stdout, stderr = run_command("amixer -c IQaudIOCODEC | head -10")
        if success:
            print("   Available mixer controls:")
            for line in stdout.split('\n')[:5]:
                if line.strip():
                    print(f"   {line}")
    else:
        print("❌ Cannot access IQaudio mixer")
    
    print_header("Step 4: Automatic Quick Fix")
    
    needs_fix = False
    fix_actions = []
    
    # Determine what needs fixing
    if not config_found:
        print("❌ Cannot proceed - no config.txt found")
        return
    
    try:
        with open(config_file, 'r') as f:
            config_content = f.read()
        
        if "dtparam=audio=off" not in config_content and "#dtparam=audio=on" not in config_content:
            needs_fix = True
            fix_actions.append("Disable built-in audio")
        
        if "dtoverlay=iqaudio-codec" not in config_content:
            needs_fix = True
            fix_actions.append("Enable IQaudio overlay")
            
    except:
        print("❌ Could not check config.txt")
        return
    
    if not os.path.exists(asoundrc_path):
        needs_fix = True
        fix_actions.append("Create .asoundrc file")
    
    if needs_fix:
        print(f"🔧 Need to apply {len(fix_actions)} fixes:")
        for action in fix_actions:
            print(f"   - {action}")
        
        print("\n" + "="*60)
        print("QUICK FIX COMMANDS - Run these manually:")
        print("="*60)
        
        # Config.txt fixes
        if "Disable built-in audio" in fix_actions or "Enable IQaudio overlay" in fix_actions:
            print(f"\n1. Edit config.txt:")
            print(f"   sudo nano {config_file}")
            print("   Add these lines at the end:")
            if "Disable built-in audio" in fix_actions:
                print("   dtparam=audio=off")
            if "Enable IQaudio overlay" in fix_actions:
                print("   dtoverlay=iqaudio-codec")
        
        # .asoundrc fix
        if "Create .asoundrc file" in fix_actions:
            print(f"\n2. Create .asoundrc file (USER TESTED - WORKS):")
            print(f"   cat > {asoundrc_path} << 'EOF'")
            print("pcm.!default {")
            print("    type plug")
            print("    slave.pcm \"hw:0,0\"")
            print("}")
            print("ctl.!default {")
            print("    type hw")
            print("    card 0")
            print("}")
            print("EOF")
        
        print("\n3. Reboot:")
        print("   sudo reboot")
        
        print("\n4. Test after reboot:")
        print("   aplay -l | grep IQaudio")
        print("   aplay -D plughw:0,0 /usr/share/sounds/alsa/Front_Left.wav")
        print("   fably --debug 'test hikayesi'")
        
    else:
        print("✅ Configuration looks good!")
        
        # Test if Fably works
        print("\nTesting Fably compatibility...")
        try:
            sys.path.insert(0, '.')
            from fably.utils import play_sound
            print("✅ Fably audio system should work")
            print("\nTry running:")
            print("   fably --debug 'bana cesur bir fare hakkında hikaye anlat'")
        except Exception as e:
            print(f"❌ Fably import test failed: {e}")
    
    print_header("Diagnostic Complete")

if __name__ == "__main__":
    main()
