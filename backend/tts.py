from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import hashlib
import uuid
from google import genai
from database.database_base import DatabaseBase
from database.tts_storage import TTSRepository

router = APIRouter()

# Initialize Repository
# Using the same database file as main.py
db_base = DatabaseBase("database/db.json")
tts_repo = TTSRepository(db_base)

AUDIO_DIR = "audio"
# Ensure audio directory exists
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

class TTSRequest(BaseModel):
    text: str

class TTSResponse(BaseModel):
    filename: str
    url: str

@router.post("/tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Hash the text
    text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

    # Check repository for existing audio
    existing_filename = tts_repo.get_audio_path(text_hash)
    if existing_filename:
        # Check if file actually exists on disk
        file_path = os.path.join(AUDIO_DIR, existing_filename)
        if os.path.exists(file_path):
             return TTSResponse(
                filename=existing_filename,
                url=f"/tts/audio/{existing_filename}"
            )

    # Generate Audio if not found
    try:
        filename = f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)

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
        # Assuming the first part contains the audio data as inline_data
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
        tts_repo.save_audio_path(text_hash, filename)

        return TTSResponse(
            filename=filename,
            url=f"/tts/audio/{filename}"
        )

    except Exception as e:
        print(f"TTS Generation Error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS Generation failed: {str(e)}")

@router.get("/audio/{filename}")
async def read_mp3(filename: str):
    """
    Stream the mp3 file.
    """
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(file_path, media_type="audio/mpeg")
