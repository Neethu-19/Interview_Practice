"""
Test script for voice service functionality.

This script tests the voice service without requiring the full API to be running.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.voice_service import (
    VoiceService,
    VoiceServiceError,
    SpeechToTextError,
    TextToSpeechError
)


def test_voice_service_initialization():
    """Test that voice service can be initialized."""
    print("Testing voice service initialization...")
    
    try:
        voice_service = VoiceService(
            whisper_model="base",
            tts_engine="piper"
        )
        print("✓ Voice service initialized successfully")
        return voice_service
    except VoiceServiceError as e:
        print(f"✗ Voice service initialization failed: {e}")
        print("\nTo enable voice mode, install dependencies:")
        print("  pip install openai-whisper")
        print("  Download Piper from: https://github.com/rhasspy/piper")
        return None


def test_supported_languages(voice_service):
    """Test getting supported languages."""
    print("\nTesting supported languages...")
    
    try:
        languages = voice_service.get_supported_languages()
        print(f"✓ Supported languages: {len(languages)} languages")
        print(f"  Sample: {', '.join(languages[:10])}")
        return True
    except Exception as e:
        print(f"✗ Failed to get supported languages: {e}")
        return False


def test_text_to_speech(voice_service):
    """Test text-to-speech synthesis."""
    print("\nTesting text-to-speech...")
    
    test_text = "Hello, this is a test of the text to speech system."
    
    try:
        audio_data = voice_service.synthesize_speech(test_text)
        print(f"✓ Text-to-speech successful")
        print(f"  Generated {len(audio_data)} bytes of audio")
        
        # Optionally save to file for manual testing
        output_file = "test_tts_output.wav"
        with open(output_file, "wb") as f:
            f.write(audio_data)
        print(f"  Audio saved to: {output_file}")
        
        return True
    except TextToSpeechError as e:
        print(f"✗ Text-to-speech failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_speech_to_text_with_sample(voice_service):
    """Test speech-to-text with a sample audio file if available."""
    print("\nTesting speech-to-text...")
    
    # Check if we have a test audio file
    test_audio_file = "test_audio.wav"
    
    if not os.path.exists(test_audio_file):
        print(f"⚠ No test audio file found ({test_audio_file})")
        print("  To test STT, create a test_audio.wav file with speech")
        return None
    
    try:
        with open(test_audio_file, "rb") as f:
            audio_data = f.read()
        
        transcription = voice_service.transcribe_audio(audio_data)
        print(f"✓ Speech-to-text successful")
        print(f"  Transcription: {transcription}")
        
        return True
    except SpeechToTextError as e:
        print(f"✗ Speech-to-text failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Run all voice service tests."""
    print("=" * 60)
    print("Voice Service Test Suite")
    print("=" * 60)
    
    # Test initialization
    voice_service = test_voice_service_initialization()
    
    if voice_service is None:
        print("\n" + "=" * 60)
        print("Voice service not available - tests skipped")
        print("=" * 60)
        return
    
    # Run tests
    results = []
    
    results.append(("Supported Languages", test_supported_languages(voice_service)))
    results.append(("Text-to-Speech", test_text_to_speech(voice_service)))
    results.append(("Speech-to-Text", test_speech_to_text_with_sample(voice_service)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP"
        
        print(f"{status:10} {test_name}")
    
    print("=" * 60)
    
    # Cleanup
    if os.path.exists("test_tts_output.wav"):
        print("\nNote: Test audio file 'test_tts_output.wav' created")
        print("You can play it to verify TTS quality")


if __name__ == "__main__":
    main()
