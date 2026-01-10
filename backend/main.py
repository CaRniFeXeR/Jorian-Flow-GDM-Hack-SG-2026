from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes import tts, tour

load_dotenv()

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

# Register routers
app.include_router(tts.router, prefix="/tts", tags=["TTS"])
app.include_router(tour.router, tags=["Tour"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Jorian Flow Tour API",
        "version": "1.0.0",
        "endpoints": {
            "/theme_options": "POST - Generate thematic tour options for a location",
            "/generate_poi": "POST - Generate POIs based on coordinates and constraints",
            "/filter_poi": "POST - Filter and verify POIs using Google Maps Places API",
            "/guardrail": "POST - Validate if tour request is legitimate for user location",
            "/tts/tts": "POST - Generate text-to-speech audio",
            "/tts/audio/{filename}": "GET - Stream audio file"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level = "debug", access_log=True)
