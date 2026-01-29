#!/usr/bin/env python3
"""
Setup script for Voice Input Feature
"""

import subprocess
import sys
import platform

def setup_voice():
    """Setup voice input dependencies."""
    
    print("\n" + "="*60)
    print("🎤 Voice Input Setup for English Speaking Guide")
    print("="*60 + "\n")
    
    os_type = platform.system()
    
    print(f"📌 Detected OS: {os_type}\n")
    
    # Check if SpeechRecognition is installed
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition is already installed")
    except ImportError:
        print("❌ SpeechRecognition not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "SpeechRecognition"])
        print("✅ SpeechRecognition installed")
    
    # Check if PyAudio is installed
    try:
        import pyaudio
        print("✅ PyAudio is already installed")
    except ImportError:
        print("⚠️  PyAudio not found. Installing...\n")
        
        if os_type == "Windows":
            print("📌 For Windows, trying pipwin (recommended)...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pipwin"])
                subprocess.check_call([sys.executable, "-m", "pipwin", "install", "pyaudio"])
                print("✅ PyAudio installed via pipwin")
            except:
                print("⚠️  pipwin method failed. Trying pip directly...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
                    print("✅ PyAudio installed via pip")
                except:
                    print("❌ Could not install PyAudio automatically")
                    print("   Manual installation required:")
                    print("   1. Download pre-built wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
                    print("   2. Install: pip install PyAudio-X.X-cpXX-cpXX-winXX.whl")
        
        elif os_type == "Darwin":  # macOS
            print("📌 For macOS, installing via brew...")
            try:
                subprocess.check_call(["brew", "install", "portaudio"])
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
                print("✅ PyAudio installed on macOS")
            except:
                print("❌ Could not install PyAudio on macOS")
                print("   Try: brew install portaudio && pip install pyaudio")
        
        elif os_type == "Linux":
            print("📌 For Linux, installing dependencies...")
            try:
                subprocess.check_call(["sudo", "apt-get", "install", "portaudio19-dev"])
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
                print("✅ PyAudio installed on Linux")
            except:
                print("❌ Could not install PyAudio on Linux")
                print("   Try: sudo apt-get install portaudio19-dev && pip install pyaudio")
    
    print("\n" + "="*60)
    print("✅ Voice Setup Complete!")
    print("="*60)
    print("\n📌 **How to Use Voice Feature:**")
    print("   1. Open the Streamlit app: http://localhost:8501")
    print("   2. Go to Settings → Input Method")
    print("   3. Select 'Voice' instead of 'Text'")
    print("   4. Click 'Start Recording'")
    print("   5. Speak your sentence")
    print("   6. Get instant corrections! 🌟\n")
    
    print("🎤 **Voice Tips:**")
    print("   - Speak clearly and at normal speed")
    print("   - Use simple sentences")
    print("   - The app listens for 10 seconds")
    print("   - Make sure your microphone is working\n")

if __name__ == "__main__":
    try:
        setup_voice()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
