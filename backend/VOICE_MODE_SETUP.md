# Voice Mode Setup Guide

This guide explains how to set up and use the voice mode feature in the Interview Practice Partner.

## Overview

Voice mode allows users to conduct interviews using speech instead of typing. The system uses:
- **Whisper** for speech-to-text (STT) transcription
- **Piper TTS** or **Coqui TTS** for text-to-speech (TTS) synthesis

## Installation

### Option 1: Using Whisper + Piper (Recommended)

#### 1. Install Whisper

```bash
pip install openai-whisper
```

Whisper will automatically download the required model on first use.

#### 2. Install Piper TTS

Download Piper from the official repository:
- GitHub: https://github.com/rhasspy/piper
- Download the appropriate binary for your platform
- Add Piper to your system PATH

Download a voice model (e.g., `en_US-lessac-medium`):
```bash
# Download voice model
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
```

### Option 2: Using Whisper + Coqui TTS

#### 1. Install Whisper

```bash
pip install openai-whisper
```

#### 2. Install Coqui TTS

```bash
pip install TTS
```

## Configuration

The voice service is configured in `backend/services/voice_service.py`:

```python
voice_service = VoiceService(
    whisper_model="base",  # Options: tiny, base, small, medium, large
    tts_engine="piper",    # Options: piper, coqui
    piper_voice="en_US-lessac-medium"  # Voice model for Piper
)
```

### Whisper Model Sizes

- **tiny**: Fastest, lowest quality (~1GB RAM)
- **base**: Good balance (~1GB RAM) - **Recommended**
- **small**: Better accuracy (~2GB RAM)
- **medium**: High accuracy (~5GB RAM)
- **large**: Best accuracy (~10GB RAM)

## API Endpoints

### Check Voice Status

```bash
GET /api/voice/status
```

Returns information about voice service availability.

### Transcribe Audio

```bash
POST /api/voice/transcribe
Content-Type: application/json

{
  "audio_data": "base64_encoded_audio",
  "language": "en"
}
```

Returns transcribed text.

### Synthesize Speech

```bash
POST /api/voice/synthesize
Content-Type: application/json

{
  "text": "Hello, how are you?",
  "format": "wav"
}
```

Returns base64-encoded audio data.

## Frontend Usage

### Starting Voice Mode Interview

1. Select a role from the dropdown
2. Click the "🎤 Voice Mode" button
3. Click "Start Interview"

### Recording Answers

1. Press and hold the "🎤 Hold to Record" button
2. Speak your answer
3. Release the button to stop recording
4. The transcription will appear automatically
5. Click "Send" to submit your answer

### Audio Playback

In voice mode, interview questions are automatically spoken using TTS.

## Troubleshooting

### Voice Mode Not Available

If you see "Voice mode requires additional setup":

1. Check that Whisper is installed: `pip list | grep whisper`
2. Check that Piper or Coqui TTS is installed
3. Restart the backend server
4. Check the console for error messages

### Microphone Access Denied

The browser needs permission to access your microphone:

1. Click the microphone icon in the browser address bar
2. Allow microphone access
3. Refresh the page

### Transcription Errors

If transcription fails:

1. Ensure you're speaking clearly
2. Check your microphone is working
3. Try a different Whisper model size
4. Check the backend logs for errors

### TTS Not Working

If speech synthesis fails:

1. Verify Piper/Coqui is installed correctly
2. Check that voice models are downloaded
3. Try switching TTS engines in the configuration
4. Check the backend logs for errors

## Performance Tips

1. **Use the base Whisper model** for best balance of speed and accuracy
2. **Keep answers under 60 seconds** for faster transcription
3. **Use Piper TTS** for faster speech synthesis
4. **Ensure good microphone quality** for better transcription accuracy

## Supported Languages

Whisper supports 30+ languages including:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- And many more...

To use a different language, pass the language code in the transcribe request.

## System Requirements

### Minimum
- 4GB RAM
- 2 CPU cores
- Microphone access

### Recommended
- 8GB RAM
- 4 CPU cores
- Good quality microphone
- Speakers or headphones

## Notes

- Voice mode is optional and the system works fine without it
- The first transcription may be slower as models are loaded
- Audio is processed locally and never sent to external services
- Voice mode requires more system resources than chat mode
