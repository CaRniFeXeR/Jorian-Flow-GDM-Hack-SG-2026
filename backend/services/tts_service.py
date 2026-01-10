import os
import hashlib
import uuid
from google import genai
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
        
        Args:
            text: The text to convert to speech
            
        Returns:
            Filename of the generated audio file
            
        Raises:
            ValueError: If API key is not found
            Exception: If audio generation fails
        """
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(self.audio_dir, filename)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
            
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash-tts',
            contents=text,
            config={
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Puck"
                        }
                    }
                }
            }
        )
        
        if not response.candidates or not response.candidates[0].content.parts:
            raise Exception("No audio content generated")

        # Save the audio content
        audio_saved = False
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with open(output_path, "wb") as out:
                    out.write(part.inline_data.data)
                audio_saved = True
                break
        
        if not audio_saved:
            raise Exception("No inline audio data found in response")

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
