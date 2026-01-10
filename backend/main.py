from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import os
from dotenv import load_dotenv

from gemini_service import generate_theme_options
from database.database_base import DatabaseBase
from database.tour import TourRepository
from database.tts_storage import TTSRepository

load_dotenv()

# __Initialize Database__
db_base = DatabaseBase("database/db.json")
tour_repo = TourRepository(db_base)
tts_repo = TTSRepository(db_base)

app = FastAPI(
    title="Jorian Flow Tour API",
    description="API for generating thematic tour options based on location",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ThemeOptionsRequest(BaseModel):
    address: str

    class Config:
        json_schema_extra = {
            "example": {
                "address": "Orchard Road, Singapore"
            }
        }


class ThemeOptionsResponse(BaseModel):
    themes: Dict[str, str]

    class Config:
        json_schema_extra = {
            "example": {
                "themes": {
                    "Historical Heritage Tour": "Explore the colonial architecture and historical landmarks along this iconic street",
                    "Shopping & Fashion Tour": "Discover luxury brands and modern shopping centers in Singapore's premier retail district",
                    "Cultural Fusion Tour": "Experience the blend of traditional and contemporary Asian culture"
                }
            }
        }


@app.get("/")
async def root():
    return {
        "message": "Welcome to Jorian Flow Tour API",
        "version": "1.0.0",
        "endpoints": {
            "/theme_options": "POST - Generate thematic tour options for a location"
        }
    }


@app.post("/theme_options", response_model=ThemeOptionsResponse)
async def get_theme_options(request: ThemeOptionsRequest):
    """
    Generate thematic tour options for a given location address.

    Args:
        request: ThemeOptionsRequest containing the address

    Returns:
        ThemeOptionsResponse with suggested tour themes

    Raises:
        HTTPException: If there's an error generating themes
    """
    try:
        themes = await generate_theme_options(request.address)
        return ThemeOptionsResponse(themes=themes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating theme options: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
