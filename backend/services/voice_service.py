"""
Voice service for speech-to-text and text-to-speech functionality.

Provides integration with:
- Whisper for speech-to-text transcription
- Piper/Coqui TTS for text-to-speech synthesis
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Union
import base64


class VoiceServiceError(Exception):
    """Base exception for voice service errors"""
    pass


class SpeechToTextError(VoiceServiceError):
    """Exception for speech-to-text errors"""
    pass


class TextToSpeechError(VoiceServiceError):
    """Exception for text-to-speech errors"""
    pass


class VoiceService:
    """
    Service for handling voice interactions.
    
    Provides speech-to-text transcription using Whisper and
    text-to-speech synthesis using Piper or Coqui TTS.
    """
    
    def __init__(
        self,
        whisper_model: str = "base",
        tts_engine: str = "piper",
        piper_voice: str = "en_US-lessac-medium",
        require_tts: bool = False
    ):
        """
        Initialize voice service.
        
        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large)
            tts_engine: TTS engine to use (piper or coqui)
            piper_voice: Voice model for Piper TTS
            require_tts: If True, raise error if TTS is not available
        """
        self.whisper_model = whisper_model
        self.tts_engine = tts_engine
        self.piper_voice = piper_voice
        self.tts_available = False
        
        # Check if whisper is available (required for STT)
        self._check_whisper_available()
        
        # Check if TTS engine is available (optional)
        try:
            if tts_engine == "piper":
                self._check_piper_available()
                self.tts_available = True
            elif tts_engine == "coqui":
                self._check_coqui_available()
                self.tts_available = True
        except TextToSpeechError as e:
            if require_tts:
                raise
            # TTS is optional, continue without it
            print(f"Warning: TTS not available - {e}")
    
    def _check_whisper_available(self) -> bool:
        """
        Check if Whisper is installed and available.
        
        Returns:
            True if Whisper is available
            
        Raises:
            SpeechToTextError: If Whisper is not available
        """
        try:
            import whisper
            return True
        except ImportError:
            raise SpeechToTextError(
                "Whisper is not installed. Install with: pip install openai-whisper"
            )
    
    def _check_piper_available(self) -> bool:
        """
        Check if Piper TTS is installed and available.
        
        Returns:
            True if Piper is available
            
        Raises:
            TextToSpeechError: If Piper is not available
        """
        try:
            result = subprocess.run(
                ["piper", "--help"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise TextToSpeechError(
                "Piper TTS is not installed. Download from: https://github.com/rhasspy/piper"
            )
    
    def _check_coqui_available(self) -> bool:
        """
        Check if Coqui TTS is installed and available.
        
        Returns:
            True if Coqui is available
            
        Raises:
            TextToSpeechError: If Coqui is not available
        """
        try:
            import TTS
            return True
        except ImportError:
            raise TextToSpeechError(
                "Coqui TTS is not installed. Install with: pip install TTS"
            )
    
    def transcribe_audio(
        self,
        audio_data: Union[bytes, str],
        language: str = "en"
    ) -> str:
        """
        Transcribe audio to text using Whisper.
        
        Args:
            audio_data: Audio data as bytes or base64 string
            language: Language code (default: en)
            
        Returns:
            Transcribed text
            
        Raises:
            SpeechToTextError: If transcription fails
        """
        temp_audio_path = None
        
        try:
            import whisper
            
            # Decode base64 if needed
            if isinstance(audio_data, str):
                try:
                    audio_bytes = base64.b64decode(audio_data)
                except Exception as e:
                    raise SpeechToTextError(f"Failed to decode base64 audio: {e}")
            else:
                audio_bytes = audio_data
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            # Load Whisper model (cached after first load)
            if not hasattr(self, '_whisper_model_cache'):
                self._whisper_model_cache = whisper.load_model(self.whisper_model)
            
            model = self._whisper_model_cache
            
            # Transcribe audio using Python API
            result = model.transcribe(
                temp_audio_path,
                language=language,
                fp16=False  # Disable FP16 for CPU compatibility
            )
            
            transcription = result["text"].strip()
            
            if not transcription:
                raise SpeechToTextError("No speech detected in audio")
            
            return transcription
            
        except ImportError:
            raise SpeechToTextError("Whisper is not installed. Install with: pip install openai-whisper")
        except Exception as e:
            if isinstance(e, SpeechToTextError):
                raise
            raise SpeechToTextError(f"Transcription failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
    
    def synthesize_speech(
        self,
        text: str,
        output_format: str = "wav"
    ) -> bytes:
        """
        Synthesize speech from text using configured TTS engine.
        
        Args:
            text: Text to synthesize
            output_format: Audio format (wav, mp3)
            
        Returns:
            Audio data as bytes
            
        Raises:
            TextToSpeechError: If synthesis fails
        """
        if not self.tts_available:
            raise TextToSpeechError("TTS engine is not available. Please install Piper or Coqui TTS.")
        
        if self.tts_engine == "piper":
            return self._synthesize_with_piper(text, output_format)
        elif self.tts_engine == "coqui":
            return self._synthesize_with_coqui(text, output_format)
        else:
            raise TextToSpeechError(f"Unknown TTS engine: {self.tts_engine}")
    
    def _synthesize_with_piper(
        self,
        text: str,
        output_format: str = "wav"
    ) -> bytes:
        """
        Synthesize speech using Piper TTS.
        
        Args:
            text: Text to synthesize
            output_format: Audio format
            
        Returns:
            Audio data as bytes
            
        Raises:
            TextToSpeechError: If synthesis fails
        """
        temp_output_path = None
        
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(
                suffix=f".{output_format}",
                delete=False
            ) as temp_output:
                temp_output_path = temp_output.name
            
            # Run Piper TTS
            # Note: Piper reads from stdin and writes to stdout
            result = subprocess.run(
                [
                    "piper",
                    "--model", self.piper_voice,
                    "--output_file", temp_output_path
                ],
                input=text,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise TextToSpeechError(
                    f"Piper TTS failed: {result.stderr}"
                )
            
            # Read audio data
            with open(temp_output_path, "rb") as f:
                audio_data = f.read()
            
            return audio_data
            
        except subprocess.TimeoutExpired:
            raise TextToSpeechError("Speech synthesis timed out after 30 seconds")
        except Exception as e:
            if isinstance(e, TextToSpeechError):
                raise
            raise TextToSpeechError(f"Speech synthesis failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_output_path and os.path.exists(temp_output_path):
                try:
                    os.unlink(temp_output_path)
                except:
                    pass
    
    def _synthesize_with_coqui(
        self,
        text: str,
        output_format: str = "wav"
    ) -> bytes:
        """
        Synthesize speech using Coqui TTS.
        
        Args:
            text: Text to synthesize
            output_format: Audio format
            
        Returns:
            Audio data as bytes
            
        Raises:
            TextToSpeechError: If synthesis fails
        """
        temp_output_path = None
        
        try:
            from TTS.api import TTS
            
            # Initialize TTS
            tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(
                suffix=f".{output_format}",
                delete=False
            ) as temp_output:
                temp_output_path = temp_output.name
            
            # Synthesize speech
            tts.tts_to_file(text=text, file_path=temp_output_path)
            
            # Read audio data
            with open(temp_output_path, "rb") as f:
                audio_data = f.read()
            
            return audio_data
            
        except Exception as e:
            if isinstance(e, TextToSpeechError):
                raise
            raise TextToSpeechError(f"Speech synthesis failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_output_path and os.path.exists(temp_output_path):
                try:
                    os.unlink(temp_output_path)
                except:
                    pass
    
    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported languages for speech-to-text.
        
        Returns:
            List of language codes
        """
        # Whisper supports these languages
        return [
            "en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr",
            "pl", "ca", "nl", "ar", "sv", "it", "id", "hi", "fi", "vi",
            "he", "uk", "el", "ms", "cs", "ro", "da", "hu", "ta", "no"
        ]
