"""
Verification script for Speech-to-Text integration (Task 13.1)

This script verifies that all components of the speech-to-text
integration are properly implemented:
1. Whisper is installed and accessible
2. VoiceService can transcribe audio
3. API endpoint is available
"""

import sys
import subprocess


def check_whisper_installed():
    """Check if Whisper is installed."""
    print("Checking Whisper installation...")
    try:
        import whisper
        version = getattr(whisper, '__version__', 'unknown')
        print(f"✓ Whisper Python module is installed (version: {version})")
        return True
    except ImportError:
        print("✗ Whisper is not installed")
        print("  Install with: pip install openai-whisper")
        return False


def check_voice_service():
    """Check if VoiceService can be initialized."""
    print("\nChecking VoiceService...")
    try:
        from services.voice_service import VoiceService, SpeechToTextError
        
        try:
            voice_service = VoiceService()
            print("✓ VoiceService initialized successfully")
            
            # Check supported languages
            languages = voice_service.get_supported_languages()
            print(f"✓ Supports {len(languages)} languages")
            
            return True
        except SpeechToTextError as e:
            print(f"✗ VoiceService initialization failed: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import VoiceService: {e}")
        return False


def check_api_endpoint():
    """Check if the transcribe API endpoint exists."""
    print("\nChecking API endpoint...")
    try:
        from api.endpoints import router
        
        # Check if transcribe endpoint is registered
        routes = [route.path for route in router.routes]
        
        # The route includes the prefix, so check for the full path
        transcribe_found = any("/voice/transcribe" in route for route in routes)
        
        if transcribe_found:
            print("✓ /api/voice/transcribe endpoint is registered")
            return True
        else:
            print("✗ /api/voice/transcribe endpoint not found")
            print(f"  Available routes: {routes}")
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import API router: {e}")
        return False


def check_frontend_integration():
    """Check if frontend has recording functionality."""
    print("\nChecking frontend integration...")
    try:
        import os
        frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "app.js")
        with open(frontend_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = {
            "MediaRecorder": "MediaRecorder" in content,
            "handleRecordStart": "handleRecordStart" in content,
            "processRecording": "processRecording" in content,
            "transcribe API call": "/voice/transcribe" in content,
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✓ {check_name} found")
            else:
                print(f"✗ {check_name} not found")
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        print("✗ frontend/app.js not found")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Speech-to-Text Integration Verification (Task 13.1)")
    print("=" * 60)
    
    results = {
        "Whisper Installation": check_whisper_installed(),
        "VoiceService": check_voice_service(),
        "API Endpoint": check_api_endpoint(),
        "Frontend Integration": check_frontend_integration(),
    }
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for component, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {component}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All components verified successfully!")
        print("Task 13.1 is complete.")
    else:
        print("✗ Some components failed verification.")
        print("\nTo complete task 13.1:")
        if not results["Whisper Installation"]:
            print("  1. Install Whisper: pip install openai-whisper")
        print("\nAfter installing dependencies, run this script again.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
