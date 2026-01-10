import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from routes import tts, tour

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

# Create API v1 router
api_v1_router = APIRouter(prefix="/api/v1")

# Register routers under /api/v1
api_v1_router.include_router(tts.router, prefix="/tts", tags=["TTS"])
api_v1_router.include_router(tour.router, tags=["Tour"])

# Mount the v1 API router
app.include_router(api_v1_router)

# Expose OpenAPI schema at /api/v1/openapi.json
@app.get("/api/v1/openapi.json", include_in_schema=False)
async def openapi_json():
    from fastapi.openapi.utils import get_openapi
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema


@app.get("/")
async def root():
    return {
        "message": "Welcome to Jorian Flow Tour API",
        "version": "1.0.0",
        "endpoints": {
            "/api/v1/theme_options": "POST - Generate thematic tour options for a location",
            "/api/v1/generate_poi": "POST - Generate POIs based on coordinates and constraints",
            "/api/v1/filter_poi": "POST - Filter and verify POIs using Google Maps Places API",
            "/api/v1/tts/tts": "POST - Generate text-to-speech audio",
            "/api/v1/tts/audio/{filename}": "GET - Stream audio file",
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level = "debug", access_log=True)
