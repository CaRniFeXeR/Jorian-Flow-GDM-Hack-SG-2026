from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import os
from dotenv import load_dotenv

from gemini_service import generate_theme_options
from database.database_base import DatabaseBase
from database.tour import TourRepository
from database.tts_storage import TTSRepository
from gemini_service import generate_theme_options, generate_pois
from maps_service import get_address_from_coordinates, verify_multiple_pois

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


class POIConstraints(BaseModel):
    time: str
    distance: str
    user_custom_info: str

    class Config:
        json_schema_extra = {
            "example": {
                "time": "2 hours",
                "distance": "5 km",
                "user_custom_info": "I love historical sites and local food"
            }
        }


class GeneratePOIRequest(BaseModel):
    latitude: float
    longitude: float
    constraints: POIConstraints

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 1.3048,
                "longitude": 103.8318,
                "constraints": {
                    "time": "2 hours",
                    "distance": "5 km",
                    "user_custom_info": "I love historical sites and local food"
                }
            }
        }


class POI(BaseModel):
    poi_title: str
    poi_address: str


class GeneratePOIResponse(BaseModel):
    user_address: str
    pois: List[POI]

    class Config:
        json_schema_extra = {
            "example": {
                "user_address": "Orchard Road, Singapore",
                "pois": [
                    {
                        "poi_title": "Singapore Botanic Gardens",
                        "poi_address": "1 Cluny Rd, Singapore 259569"
                    },
                    {
                        "poi_title": "ION Orchard",
                        "poi_address": "2 Orchard Turn, Singapore 238801"
                    }
                ]
            }
        }


class FilterPOIRequest(BaseModel):
    pois: List[POI]

    class Config:
        json_schema_extra = {
            "example": {
                "pois": [
                    {
                        "poi_title": "Singapore Botanic Gardens",
                        "poi_address": "1 Cluny Rd, Singapore 259569"
                    },
                    {
                        "poi_title": "Fake Museum",
                        "poi_address": "123 Nonexistent St, Singapore"
                    },
                    {
                        "poi_title": "ION Orchard",
                        "poi_address": "2 Orchard Turn, Singapore 238801"
                    }
                ]
            }
        }


class FilterPOIResponse(BaseModel):
    verified_pois: List[POI]
    total_input: int
    total_verified: int

    class Config:
        json_schema_extra = {
            "example": {
                "verified_pois": [
                    {
                        "poi_title": "Singapore Botanic Gardens",
                        "poi_address": "1 Cluny Rd, Singapore 259569"
                    },
                    {
                        "poi_title": "ION Orchard",
                        "poi_address": "2 Orchard Turn, Singapore 238801"
                    }
                ],
                "total_input": 3,
                "total_verified": 2
            }
        }


@app.get("/")
async def root():
    return {
        "message": "Welcome to Jorian Flow Tour API",
        "version": "1.0.0",
        "endpoints": {
            "/theme_options": "POST - Generate thematic tour options for a location",
            "/generate_poi": "POST - Generate POIs based on coordinates and constraints",
            "/filter_poi": "POST - Filter and verify POIs using Google Maps Places API"
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


@app.post("/generate_poi", response_model=GeneratePOIResponse)
async def generate_poi_endpoint(request: GeneratePOIRequest):
    """
    Generate Points of Interest (POIs) based on user coordinates and constraints.

    This endpoint performs two steps:
    1. Converts latitude/longitude to address using Google Maps Geocoding API
    2. Generates relevant POIs using Gemini API based on the address and constraints

    Args:
        request: GeneratePOIRequest containing coordinates and constraints

    Returns:
        GeneratePOIResponse with user address and list of POIs

    Raises:
        HTTPException: If there's an error in geocoding or POI generation
    """
    try:
        # Step 1: Convert coordinates to address using Google Maps API
        user_address = get_address_from_coordinates(
            request.latitude,
            request.longitude
        )

        # Step 2: Generate POIs using Gemini API
        pois_data = await generate_pois(
            address=user_address,
            time_constraint=request.constraints.time,
            distance_constraint=request.constraints.distance,
            user_custom_info=request.constraints.user_custom_info
        )

        # Convert to POI model objects
        pois = [POI(**poi) for poi in pois_data]

        return GeneratePOIResponse(
            user_address=user_address,
            pois=pois
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating POIs: {str(e)}"
        )


@app.post("/filter_poi", response_model=FilterPOIResponse)
async def filter_poi_endpoint(request: FilterPOIRequest):
    """
    Filter and verify POIs to check if they actually exist in reality.

    This endpoint uses Google Maps Places API to verify each POI.
    Only POIs that are found and verified are included in the response.

    Args:
        request: FilterPOIRequest containing a list of POIs to verify

    Returns:
        FilterPOIResponse with verified POIs and statistics

    Raises:
        HTTPException: If there's an error during verification
    """
    try:
        # Convert POI models to dictionaries for verification
        pois_dict = [poi.model_dump() for poi in request.pois]

        # Get total input count
        total_input = len(pois_dict)

        # Verify POIs using Google Maps Places API
        verified_pois_dict = verify_multiple_pois(pois_dict)

        # Convert verified POIs back to POI model objects
        verified_pois = [POI(**poi) for poi in verified_pois_dict]

        # Get total verified count
        total_verified = len(verified_pois)

        return FilterPOIResponse(
            verified_pois=verified_pois,
            total_input=total_input,
            total_verified=total_verified
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error filtering POIs: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level = "debug", access_log=True)
