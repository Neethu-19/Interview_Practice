"""
Voice Mode Diagnostic Script
Checks all requirements for voice mode and provides fix instructions
"""
import sys
import subprocess
import shutil


def check_ffmpeg():
    """Check if ffmpeg is installed"""
    print("\n1. Checking ffmpeg...")
    ffmpeg_path = shutil.which("ffmpeg")
    
    if ffmpeg_path:
        print(f"   ✓ ffmpeg found at: {ffmpeg_path}")
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_line = result.stdout.split('\n')[0]
            print(f"   ✓ {version_line}")
            return True
        except Exception as e:
            print(f"   ✗ ffmpeg found but error running it: {e}")
            return False
    else:
        print("   ✗ ffmpeg NOT FOUND - THIS IS THE PROBLEM!")
        print("\n   ⚠ This is why voice mode isn't working!")
        print("\n   QUICK FIX (2 minutes):")
        print("   1. Open PowerShell as Administrator")
        print("   2. Run: choco install ffmpeg")
        print("   3. Restart this terminal")
        print("   4. Restart backend server")
        print("\n   See INSTALL_FFMPEG_WINDOWS.md for detailed instructions")
        return False


def check_whisper():
    """Check if Whisper is installed"""
    print("\n2. Checking Whisper...")
    try:
        import whisper
        print(f"   ✓ Whisper installed (version: {whisper.__version__ if hasattr(whisper, '__version__') else 'unknown'})")
        return True
    except ImportError:
        print("   ✗ Whisper NOT INSTALLED")
        print("\n   SOLUTION:")
        print("   pip install openai-whisper")
        return False


def check_torch():
    """Check if PyTorch is installed (required by Whisper)"""
    print("\n3. Checking PyTorch...")
    try:
        import torch
        print(f"   ✓ PyTorch installed (version: {torch.__version__})")
        return True
    except ImportError:
        print("   ✗ PyTorch NOT INSTALLED")
        print("\n   SOLUTION:")
        print("   pip install torch")
        return False


def check_tts():
    """Check if TTS is available (optional)"""
    print("\n4. Checking TTS (optional)...")
    
    # Check Piper
    piper_path = shutil.which("piper")
    if piper_path:
        print(f"   ✓ Piper TTS found at: {piper_path}")
        return True
    
    # Check Coqui
    try:
        import TTS
        print("   ✓ Coqui TTS installed")
        return True
    except ImportError:
        pass
    
    print("   ⚠ No TTS engine found (this is OK!)")
    print("   Voice mode will work for recording your voice")
    print("   TTS is only for AI speaking questions back to you")
    print("\n   Note: Coqui TTS doesn't support Python 3.12 yet")
    print("   You can use voice mode without TTS!")
    return False


def test_voice_service():
    """Test if VoiceService can be initialized"""
    print("\n5. Testing VoiceService...")
    try:
        from services.voice_service import VoiceService
        
        # Try to initialize (TTS is optional)
        service = VoiceService(require_tts=False)
        print("   ✓ VoiceService initialized successfully")
        return True
    except Exception as e:
        print(f"   ✗ VoiceService initialization failed: {e}")
        return False


def main():
    """Run all diagnostic checks"""
    print("=" * 60)
    print("Voice Mode Diagnostic Tool")
    print("=" * 60)
    
    results = {
        "ffmpeg": check_ffmpeg(),
        "whisper": check_whisper(),
        "torch": check_torch(),
        "tts": check_tts(),
        "service": False
    }
    
    # Only test service if basic requirements are met
    if results["ffmpeg"] and results["whisper"] and results["torch"]:
        results["service"] = test_voice_service()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    required_checks = ["ffmpeg", "whisper", "torch"]
    required_passed = all(results[check] for check in required_checks)
    
    if required_passed and results["service"]:
        print("\n✓ ALL REQUIRED COMPONENTS WORKING!")
        print("\nVoice mode should work now. Try:")
        print("1. Restart your backend server")
        print("2. Open the frontend")
        print("3. Click 'Voice Mode' button")
        print("4. Try recording")
        
        if not results["tts"]:
            print("\nNote: TTS not available, but speech-to-text will work")
    else:
        print("\n✗ SOME COMPONENTS MISSING")
        print("\nRequired components:")
        for check in required_checks:
            status = "✓" if results[check] else "✗"
            print(f"  {status} {check}")
        
        print("\nPlease install missing components and run this script again.")
        print("\nFor detailed instructions, see:")
        print("  - VOICE_MODE_FIX.md (for ffmpeg)")
        print("  - VOICE_MODE_SETUP.md (for complete setup)")
    
    print("\n" + "=" * 60)
    
    return 0 if required_passed else 1


if __name__ == "__main__":
    sys.exit(main())
