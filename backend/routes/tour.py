from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from uuid import UUID
from services.gemini_service import generate_theme_options, generate_pois
from services.maps_service import get_address_from_coordinates, verify_multiple_pois
from database.database_base import DatabaseBase
from database.tour import TourRepository
from schemas.tour import Tour

router = APIRouter()

# Initialize Repository
db_base = DatabaseBase("database/db.json")
tour_repo = TourRepository(db_base)


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


@router.post("/theme_options", response_model=ThemeOptionsResponse)
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


@router.post("/generate_poi", response_model=GeneratePOIResponse)
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


@router.post("/filter_poi", response_model=FilterPOIResponse)
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


@router.get("/{tour_id}", response_model=Tour)
async def get_tour_by_id(tour_id: UUID):
    """
    Get a tour by its UUID.

    This endpoint retrieves a fully typed tour object including all POIs
    associated with the tour.

    Args:
        tour_id: UUID of the tour to retrieve

    Returns:
        Tour object with all details including POIs

    Raises:
        HTTPException: If the tour is not found or there's an error retrieving it
    """
    try:
        # Convert UUID to string for database lookup
        tour_uuid_str = str(tour_id)
        
        # Get tour from database
        tour_data = tour_repo.get_tour_by_uuid(tour_uuid_str)
        
        if tour_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Tour with ID {tour_id} not found"
            )
        
        # Convert database dict to Pydantic model
        # The database might store UUID as string, so we ensure proper conversion
        if 'id' in tour_data:
            tour_data['id'] = UUID(tour_data['id']) if isinstance(tour_data['id'], str) else tour_data['id']
        
        # Ensure pois is a list if it exists
        if 'pois' not in tour_data:
            tour_data['pois'] = []
        elif tour_data['pois'] is None:
            tour_data['pois'] = []
        
        return Tour(**tour_data)
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tour ID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving tour: {str(e)}"
        )
