import logging
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services.tts_service import TTSService
from database.database_base import DatabaseBase
from database.tts_storage import TTSRepository

router = APIRouter()

# Initialize Repository and Service
db_base = DatabaseBase("database/db.json")
tts_repo = TTSRepository(db_base)
tts_service = TTSService(tts_repo, audio_dir="audio")


class TTSRequest(BaseModel):
    text: str


class TTSResponse(BaseModel):
    filename: str
    url: str


@router.post("/tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    """
    Generate text-to-speech audio from the given text.
    
    Args:
        request: TTSRequest containing the text to convert
        
    Returns:
        TTSResponse with filename and URL
        
    Raises:
        HTTPException: If text is empty or generation fails
    """
    logging.info(f"Generating TTS for text: {request.text}")
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # Check if audio already exists
        existing_filename = tts_service.get_existing_audio(text)
        if existing_filename:
            return TTSResponse(
                filename=existing_filename,
                url=f"/tts/audio/{existing_filename}"
            )

        # Generate new audio
        filename = tts_service.generate_audio(text)

        return TTSResponse(
            filename=filename,
            url=f"/tts/audio/{filename}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS Generation failed: {str(e)}")


@router.get("/audio/{filename}")
async def read_audio(filename: str):
    """
    Stream the audio file (WAV format).
    
    Args:
        filename: The audio filename
        
    Returns:
        FileResponse with the audio file
        
    Raises:
        HTTPException: If file not found
    """
    file_path = tts_service.get_audio_path(filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(file_path, media_type="audio/wav")
