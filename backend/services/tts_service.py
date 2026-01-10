import logging
import os
import hashlib
import uuid
import wave
from google import genai
from google.genai import types
from typing import Optional
from database.database_base import DatabaseBase
from database.tts_storage import TTSRepository


class TTSService:
    def __init__(self, tts_repo: TTSRepository, audio_dir: str = "audio"):
        self.tts_repo = tts_repo
        self.audio_dir = audio_dir
        self._ensure_audio_dir()

    def _ensure_audio_dir(self):
        """Ensure the audio directory exists."""
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)

    def _wave_file(self, filename: str, pcm: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2):
        """Save PCM audio data to a WAV file."""
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)

    def get_existing_audio(self, text: str) -> Optional[str]:
        """
        Check if audio for the given text already exists.
        
        Args:
            text: The text to check
            
        Returns:
            Filename if audio exists, None otherwise
        """
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        existing_filename = self.tts_repo.get_audio_path(text_hash)
        
        if existing_filename:
            file_path = os.path.join(self.audio_dir, existing_filename)
            if os.path.exists(file_path):
                return existing_filename
        return None

    def generate_audio(self, text: str) -> str:
        """
        Generate audio from text using Gemini TTS API.
        """
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(self.audio_dir, filename)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
            
        client = genai.Client(api_key=api_key)

        model_id = 'gemini-2.5-flash-preview-tts' 
        
        logging.info(f"Generating audio with model: {model_id} \n text: {text}")

        try:
            response = client.models.generate_content(
                model=model_id,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name='Puck',
                            )
                        )
                    ),
                )
            )
        except Exception as e:
            logging.error(f"Gemini API request failed: {e}")
            raise

        if not response.candidates or not response.candidates[0].content:
            raise Exception("No content in response")
        
        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            raise Exception("No parts in response content")
        
        part = candidate.content.parts[0]
        if not part.inline_data:
            raise Exception("No inline_data found in response")
        
        # Extract the audio data directly (as per recommended approach)
        data = part.inline_data.data
        
        if not data:
            raise Exception("No audio data found in response")
        
        logging.info(f"Audio data extracted: type={type(data)}, length={len(data)} bytes")

        # Save audio as WAV file
        try:
            self._wave_file(output_path, data)
            logging.info(f"Audio successfully saved to {output_path}")
        except Exception as e:
            logging.error(f"Failed to save audio data: {e}")
            raise Exception(f"Failed to save audio data: {e}")

        # Save to repository
        self.tts_repo.save_audio_path(text_hash, filename)

        return filename
    
    def get_audio_path(self, filename: str) -> str:
        """
        Get the full path to an audio file.
        
        Args:
            filename: The audio filename
            
        Returns:
            Full path to the audio file
        """
        return os.path.join(self.audio_dir, filename)
