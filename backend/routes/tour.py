from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import logging
from services.gemini_service import generate_theme_options, validate_user_request_guardrail, generate_narrative_stories
from services.maps_service import get_address_from_coordinates
from database.database_base import DatabaseBase
from database.tour import TourRepository
from services.poi_service import POIService
from services.tour_service import TourService
from services.tour_orchestration_service import TourOrchestrationService

# Configure logger
logger = logging.getLogger(__name__)


router = APIRouter()

# Initialize Repository and Services
db_base = DatabaseBase("database/db.json")
tour_repo = TourRepository(db_base)
tour_service = TourService(tour_repo)
poi_service = POIService()
tour_orchestration_service = TourOrchestrationService(poi_service, tour_service)


async def process_tour_generation_background(
    transaction_id: str,
    user_address: str,
    max_time: str,
    distance: str,
    custom_message: str
):
    """
    Background task to automatically generate a complete tour after guardrail validation.

    This function orchestrates the following steps:
    1. Geocode user address to coordinates
    2. Generate POIs based on constraints
    3. Filter/verify POIs using Google Maps
    4. Order POIs optimally and enrich with details

    Args:
        transaction_id: UUID of the tour
        user_address: User's starting location
        max_time: Maximum time constraint
        distance: Maximum distance constraint
        custom_message: User's custom preferences/theme
    """
    try:
        await tour_orchestration_service.process_tour_generation(
            transaction_id=transaction_id,
            user_address=user_address,
            max_time=max_time,
            distance=distance,
            custom_message=custom_message
        )
    except Exception as e:
        logger.error(f"❌ Error in background tour generation for {transaction_id}: {str(e)}")
        logger.exception(e)
        tour_service.mark_tour_failed(transaction_id, str(e))


class ThemeOptionsRequest(BaseModel):
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    use_dummy_data: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "address": "Orchard Road, Singapore",
                "latitude": 1.3048,
                "longitude": 103.8318
            }
        }


class ThemeOptionsResponse(BaseModel):
    themes: List[str]
    address: str

    class Config:
        json_schema_extra = {
            "example": {
                "themes": [
                    "🏛️ Historical Heritage Walk",
                    "🛍️ Shopping & Fashion Tour",
                    "🎨 Cultural Fusion Experience",
                    "🍜 Foodie's Paradise Tour"
                ],
                "address": "Orchard Road, Singapore"
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


from schemas.tour import Tour, POI


class IntermediatePOI(BaseModel):
    """Simplified POI model for intermediate representations before enrichment"""
    poi_title: str
    address: str

    class Config:
        json_schema_extra = {
            "example": {
                "poi_title": "Singapore Botanic Gardens",
                "address": "1 Cluny Rd, Singapore 259569"
            }
        }


class GeneratePOIResponse(BaseModel):
    user_address: str
    pois: List[IntermediatePOI]

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
    transaction_id: str
    pois: List[POI]

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
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


class GuardrailConstraints(BaseModel):
    max_time: str
    distance: str
    custom: str
    address: str

    class Config:
        json_schema_extra = {
            "example": {
                "max_time": "3 hours",
                "distance": "10 km",
                "custom": "I want a chicken rice food tour",
                "address": "Orchard Road, Singapore"
            }
        }


class GuardrailRequest(BaseModel):
    constraints: GuardrailConstraints

    class Config:
        json_schema_extra = {
            "example": {
                "constraints": {
                    "max_time": "3 hours",
                    "distance": "10 km",
                    "custom": "I want a chicken rice food tour",
                    "address": "Orchard Road, Singapore"
                }
            }
        }


class GuardrailResponse(BaseModel):
    transaction_id: str
    valid: bool

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                "valid": True
            }
        }





class GenerateTourRequest(BaseModel):
    transaction_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "e3d6b790-4604-4570-8fde-c7d278c1ad9e"
            }
        }


class GenerateTourResponse(BaseModel):
    transaction_id: str
    success: bool
    message: str
    pois_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                "success": True,
                "message": "Tour successfully generated and stored",
                "pois_count": 5
            }
        }


class GenerateStoryRequest(BaseModel):
    transaction_id: str
    pois: List[POI]

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                "pois": [
                    {
                        "order": 1,
                        "poi_title": "Singapore Botanic Gardens",
                        "google_place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
                        "address": "1 Cluny Rd, Singapore 259569"
                    }
                ]
            }
        }


class GenerateStoryResponse(BaseModel):
    transaction_id: str
    success: bool
    stories_generated: int
    updated_pois: List[POI]

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                "success": True,
                "stories_generated": 5,
                "updated_pois": []
            }
        }


@router.post("/theme_options", response_model=ThemeOptionsResponse)
async def get_theme_options(request: ThemeOptionsRequest):
    """
    Generate thematic tour options for a given location address or coordinates.

    Args:
        request: ThemeOptionsRequest containing either address or latitude/longitude

    Returns:
        ThemeOptionsResponse with suggested tour themes

    Raises:
        HTTPException: If there's an error generating themes
    """
    try:
        # Get geocoded address (either from request or by converting coordinates)
        geocoded_address = None
        if request.address:
            geocoded_address = request.address
        elif request.latitude is not None and request.longitude is not None:
            geocoded_address = get_address_from_coordinates(request.latitude, request.longitude)
        else:
            raise ValueError("Either address or coordinates must be provided")
        
        if request.use_dummy_data:
            return ThemeOptionsResponse(
                themes=[
                    "🏛️ Historical Heritage Walk",
                    "🛍️ Shopping & Fashion Tour",
                    "🎨 Cultural Fusion Experience",
                    "🍜 Foodie's Paradise Tour"
                ],
                address=geocoded_address or "Orchard Road, Singapore"
            )

        # Generate themes using the geocoded address (service will use it directly since we provide it)
        themes = await generate_theme_options(
            address=geocoded_address,
            latitude=None,
            longitude=None
        )
        return ThemeOptionsResponse(themes=themes, address=geocoded_address)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
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
        pois_data = await poi_service.generate_pois(
            address=user_address,
            time_constraint=request.constraints.time,
            distance_constraint=request.constraints.distance,
            user_custom_info=request.constraints.user_custom_info
        )

        # Convert to intermediate POI model objects
        # Note: generate_pois returns dicts with 'poi_title' and 'address' keys
        pois = []
        for poi_data_item in pois_data:
            # Handle both 'address' and 'poi_address' keys for compatibility
            address = poi_data_item.get('address') or poi_data_item.get('poi_address', '')
            pois.append(IntermediatePOI(
                poi_title=poi_data_item.get('poi_title', ''),
                address=address
            ))

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
        verified_pois_dict = poi_service.verify_pois(pois_dict)

        # Convert verified POIs back to POI model objects
        verified_pois = [POI(**poi) for poi in verified_pois_dict]

        # Get total verified count
        total_verified = len(verified_pois)

        # Update tour with filtered POIs
        tour_service.update_filtered_pois(
            request.transaction_id,
            [poi.model_dump() for poi in verified_pois]
        )

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


@router.post("/guardrail", response_model=GuardrailResponse)
async def guardrail_validation(request: GuardrailRequest, background_tasks: BackgroundTasks):
    """
    Validate if a user's tour request is legitimate for their current location.

    This endpoint uses Gemini AI to check if the user's custom tour preferences
    make sense given their location. For example, a "chicken rice tour" in Singapore
    would be valid, but the same request in New York would be invalid.

    The validation result is stored in the tours table with status_code indicating
    whether the request passed validation. The address is stored as part of the constraints.

    If the request is valid, a background process is automatically started to:
    1. Generate POIs based on the address and constraints
    2. Filter/verify the POIs using Google Maps
    3. Order the POIs optimally and create the tour

    You can check the tour status by calling GET /{transaction_id}/{is_dummy}

    Args:
        request: GuardrailRequest containing constraints (including address)
        background_tasks: FastAPI background tasks handler

    Returns:
        GuardrailResponse with transaction_id and validation result

    Raises:
        HTTPException: If there's an error during validation
    """
    try:
        # Generate a unique transaction ID (tour UUID)
        transaction_id = str(uuid4())

        # Get address from constraints
        user_address = request.constraints.address
        
        # Validate the request using Gemini
        is_valid = await validate_user_request_guardrail(
            user_address=user_address,
            max_time=request.constraints.max_time,
            distance=request.constraints.distance,
            custom_message=request.constraints.custom
        )

        # Store in tours table
        tour_service.create_tour(
            transaction_id=transaction_id,
            user_address=user_address,
            theme=request.constraints.custom,
            status_code="valid" if is_valid else "invalid",
            max_time=request.constraints.max_time,
            distance=request.constraints.distance,
            constraints=request.constraints.model_dump()
        )

        # If validation passed, start background tour generation process
        if is_valid:
            logger.info(f"✅ Guardrail passed, starting background tour generation for {transaction_id}")
            background_tasks.add_task(
                process_tour_generation_background,
                transaction_id=transaction_id,
                user_address=user_address,
                max_time=request.constraints.max_time,
                distance=request.constraints.distance,
                custom_message=request.constraints.custom
            )
        else:
            logger.info(f"❌ Guardrail failed for {transaction_id}, skipping tour generation")

        return GuardrailResponse(
            transaction_id=transaction_id,
            valid=is_valid
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating request: {str(e)}"
        )


@router.post("/generate_tour", response_model=GenerateTourResponse)
async def generate_tour(request: GenerateTourRequest):
    """
    Generate and plan the routing of a tour.

    This endpoint takes filtered POIs and orders them optimally for a tour.
    It updates the database with:
    - order: Sequence in which POIs should be visited
    - poi_title: Name of the POI
    - address: Location address
    - google_place_id: Google Maps Place ID
    - google_maps_name: Official name from Google Maps

    Args:
        request: GenerateTourRequest with transaction_id, POIs, and constraints

    Returns:
        GenerateTourResponse with success status and POI count

    Raises:
        HTTPException: If tour not found or error during generation
    """
    try:
        # Look up the tour in database using transaction_id
        tour_data = tour_service.get_tour(request.transaction_id)

        if tour_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Tour with transaction_id {request.transaction_id} not found"
            )

        # Get the user address from the tour
        user_address = tour_data.get('user_address', '')
        
        # Retrieve constraints from tour data
        constraints = tour_data.get('constraints', {})
        theme = tour_data.get('theme', constraints.get('custom', ''))
        max_time = constraints.get('max_time', '2 hours')
        distance = constraints.get('distance', '5 km')

        # Retrieve filtered POIs from tour data
        filtered_pois = tour_data.get('filtered_candidate_poi_list', [])
        if not filtered_pois:
             raise HTTPException(
                status_code=400,
                detail="No filtered POIs found for this tour. Please call /filter_poi first."
            )

        # Generate tour from filtered POIs (order, enrich, and finalize)
        enriched_pois = await tour_orchestration_service.generate_tour_from_filtered_pois(
            transaction_id=request.transaction_id,
            filtered_pois=filtered_pois,
            user_address=user_address,
            max_time=max_time,
            distance=distance,
            theme=theme
        )

        # Update the tour in database with the enriched POIs
        updated = tour_service.update_tour_pois(request.transaction_id, enriched_pois)

        if not updated:
            raise HTTPException(
                status_code=500,
                detail="Failed to update tour in database"
            )

        return GenerateTourResponse(
            transaction_id=request.transaction_id,
            success=True,
            message="Tour successfully generated and stored",
            pois_count=len(enriched_pois)
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating tour: {str(e)}"
        )


@router.post("/generate_story", response_model=GenerateStoryResponse)
async def generate_story_endpoint(request: GenerateStoryRequest):
    """
    Generate narrative stories for POIs in a tour.

    This endpoint takes a list of POIs, generates a coherent story for each,
    and updates the database with the stories.
    
    It serves as the next process after /generate_tour.
    
    Args:
        request: GenerateStoryRequest with transaction_id and POI list

    Returns:
        GenerateStoryResponse with updated POIs containing stories
    """
    try:
        # Get tour to retrieve context/theme
        tour_data = tour_service.get_tour(request.transaction_id)
        if not tour_data:
             raise HTTPException(
                 status_code=404, 
                 detail=f"Tour with transaction_id {request.transaction_id} not found"
             )
             
        # Extract theme or constraints for context
        constraints = tour_data.get('constraints', {})
        theme = tour_data.get('theme', constraints.get('custom', 'Standard Tour'))
        
        # Convert POIs to dicts for processing
        pois_dicts = [poi.model_dump() for poi in request.pois]
        
        # Generate stories using Gemini
        # The service handles removing sensitive fields (gps_location, etc.) before prompt
        updated_pois_dicts = await generate_narrative_stories(
            pois=pois_dicts,
            user_custom_info=theme
        )
        
        # Update the tour in database with the enriched POIs (now with stories)
        success = tour_service.update_tour_pois(request.transaction_id, updated_pois_dicts)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update tour in database"
            )
            
        # Convert back to POI models
        updated_pois = [POI(**p) for p in updated_pois_dicts]
        
        return GenerateStoryResponse(
            transaction_id=request.transaction_id,
            success=True,
            stories_generated=len(updated_pois),
            updated_pois=updated_pois
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating stories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating stories: {str(e)}"
        )


@router.get("/{tour_id}/{is_dummy}", response_model=Tour)
async def get_tour_by_id(tour_id: UUID, is_dummy: bool = False):
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
        tour_data = tour_service.get_tour(tour_uuid_str)
        
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
        
        # If is_dummy is True, replace POIs with dummy Singapore POIs
        if is_dummy:
            tour_data['pois'] = [
                {
                    "order": 1,
                    "poi_title": "Marina Bay Sands",
                    "google_place_id": "ChIJt1rLykIW2jER5iQeQJONKzY",
                    "google_place_img_url": None,
                    "address": "10 Bayfront Ave, Singapore 018956",
                    "google_maps_name": "Marina Bay Sands",
                    "story": "An iconic integrated resort featuring a hotel, casino, shopping mall, and the famous SkyPark with an infinity pool overlooking Singapore's skyline.",
                    "pin_image_url": None,
                    "story_keywords": "architecture, luxury, skyline, iconic",
                    "gps_location": {
                        "lat": 1.2839,
                        "lng": 103.8608
                    }
                },
                {
                    "order": 2,
                    "poi_title": "Gardens by the Bay",
                    "google_place_id": "ChIJ-1rLykIW2jER5iQeQJONKzY",
                    "google_place_img_url": None,
                    "address": "18 Marina Gardens Dr, Singapore 018953",
                    "google_maps_name": "Gardens by the Bay",
                    "story": "A nature park spanning 101 hectares of reclaimed land, featuring the stunning Supertree Grove and climate-controlled conservatories showcasing plants from around the world.",
                    "pin_image_url": None,
                    "story_keywords": "nature, gardens, architecture, sustainability",
                    "gps_location": {
                        "lat": 1.2816,
                        "lng": 103.8636
                    }
                },
                {
                    "order": 3,
                    "poi_title": "Merlion Park",
                    "google_place_id": "ChIJt1rLykIW2jER5iQeQJONKzY",
                    "google_place_img_url": None,
                    "address": "1 Fullerton Rd, Singapore 049213",
                    "google_maps_name": "Merlion Park",
                    "story": "Home to Singapore's iconic Merlion statue, a mythical creature with the head of a lion and body of a fish, symbolizing Singapore's origin as a fishing village.",
                    "pin_image_url": None,
                    "story_keywords": "iconic, symbol, history, culture",
                    "gps_location": {
                        "lat": 1.2868,
                        "lng": 103.8545
                    }
                },
                {
                    "order": 4,
                    "poi_title": "Singapore Flyer",
                    "google_place_id": "ChIJt1rLykIW2jER5iQeQJONKzY",
                    "google_place_img_url": None,
                    "address": "30 Raffles Ave, Singapore 039803",
                    "google_maps_name": "Singapore Flyer",
                    "story": "One of the world's largest observation wheels, offering breathtaking 360-degree views of Singapore's cityscape, Marina Bay, and the surrounding islands.",
                    "pin_image_url": None,
                    "story_keywords": "observation, views, architecture, experience",
                    "gps_location": {
                        "lat": 1.2893,
                        "lng": 103.8631
                    }
                }
            ]
        
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
