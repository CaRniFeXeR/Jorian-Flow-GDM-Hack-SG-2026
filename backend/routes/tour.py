from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import logging
from services.gemini_service import generate_theme_options, generate_pois, validate_user_request_guardrail, order_pois_for_tour
from services.maps_service import get_address_from_coordinates, verify_multiple_pois, get_place_details, calculate_route_metrics
from database.database_base import DatabaseBase
from database.tour import TourRepository

# Configure logger
logger = logging.getLogger(__name__)


router = APIRouter()

# Initialize Repository
db_base = DatabaseBase("database/db.json")
tour_repo = TourRepository(db_base)


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
        logger.info(f"🚀 Starting background tour generation for transaction {transaction_id}")

        # Update status: geocoding
        tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={"status_code": "geocoding"}
        )

        # Step 1: Geocode address to get coordinates
        from services.maps_service import get_coordinates_from_address

        logger.info(f"📍 Geocoding address: {user_address}")
        latitude, longitude = get_coordinates_from_address(user_address)
        logger.info(f"✅ Coordinates obtained: {latitude}, {longitude}")

        # Update status: generating POIs
        tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={"status_code": "generating_pois"}
        )

        # Step 2: Generate POIs using Gemini
        logger.info(f"🤖 Generating POIs with Gemini...")
        pois_data = await generate_pois(
            address=user_address,
            time_constraint=max_time,
            distance_constraint=distance,
            user_custom_info=custom_message
        )
        logger.info(f"✅ Generated {len(pois_data)} POIs")

        # Update status: filtering POIs
        tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={"status_code": "filtering_pois"}
        )

        # Step 3: Filter POIs using Google Maps verification
        logger.info(f"🔍 Verifying POIs with Google Maps...")
        verified_pois_dict = verify_multiple_pois(pois_data)
        logger.info(f"✅ Verified {len(verified_pois_dict)} out of {len(pois_data)} POIs")

        # Store filtered POIs in database
        tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={"filtered_candidate_poi_list": verified_pois_dict}
        )

        # If no POIs were verified, mark as failed
        if not verified_pois_dict:
            logger.error(f"❌ No POIs were verified for transaction {transaction_id}")
            tour_repo.update_tour_by_uuid(
                tour_uuid=transaction_id,
                updates={
                    "status_code": "failed",
                    "error_message": "No POIs could be verified in the specified area"
                }
            )
            return

        # Update status: generating tour
        tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={"status_code": "generating_tour"}
        )

        # Step 4: Order POIs and generate tour
        logger.info(f"🗺️ Ordering POIs for optimal tour...")

        # Get tour data to retrieve theme
        tour_data = tour_repo.get_tour_by_uuid(transaction_id)
        if tour_data is None:
            logger.error(f"❌ Tour {transaction_id} not found during background generation")
            return
        theme = tour_data.get('theme', custom_message)

        # Use retry logic similar to generate_tour endpoint
        max_retries = 3
        current_pois = verified_pois_dict
        feedback = None
        ordered_pois = []

        for attempt in range(max_retries):
            logger.info(f"🔄 Tour generation attempt {attempt + 1}/{max_retries}")

            # Use Gemini to order the POIs optimally
            ordered_pois = await order_pois_for_tour(
                pois=current_pois,
                user_address=user_address,
                max_time=max_time,
                distance=distance,
                theme=theme,
                feedback=feedback
            )

            # Prepare waypoints for route calculation (tour should start and end at user_address)
            waypoints = []
            for poi in ordered_pois:
                waypoints.append(poi.get('poi_address', ''))

            # Calculate route metrics (origin and destination are both user_address)
            metrics = calculate_route_metrics(user_address, waypoints)
            total_distance_km = metrics.get('total_distance_km', float('inf'))
            total_duration_min = metrics.get('total_duration_minutes', float('inf'))

            logger.info(f"📊 Route metrics: {total_distance_km:.2f} km, {total_duration_min:.0f} min")

            # Parse constraints
            limit_distance = float(distance.split()[0]) if isinstance(distance, str) and ' ' in distance else 5.0
            limit_time = 120  # Default
            if isinstance(max_time, str):
                if 'hour' in max_time:
                    limit_time = float(max_time.split()[0]) * 60
                elif 'min' in max_time:
                    limit_time = float(max_time.split()[0])

            # Check if constraints are met (with 10% buffer)
            if total_distance_km <= limit_distance * 1.1 and total_duration_min <= limit_time * 1.1:
                logger.info("✅ Tour constraints met!")
                break
            else:
                logger.warning(f"⚠️ Constraints exceeded (attempt {attempt + 1})")
                feedback = f"Previous plan exceeded constraints. Distance: {total_distance_km:.2f}km (limit: {limit_distance}km), Duration: {total_duration_min:.0f}min (limit: {limit_time}min). Reduce POIs or choose closer ones."

                if attempt == max_retries - 1:
                    logger.warning("⚠️ Max retries reached, using best effort result")

        # Step 5: Enrich POIs with Google Maps details
        logger.info(f"📍 Enriching {len(ordered_pois)} POIs with Google Maps details...")
        enriched_pois = []

        for ordered_poi in ordered_pois:
            poi_title = ordered_poi.get('poi_title', '')
            poi_address = ordered_poi.get('poi_address', '')
            order = ordered_poi.get('order', 0)

            # Get Google Maps details
            place_details = get_place_details(poi_title, poi_address)

            if place_details:
                gps_location = place_details.get('gps_location')
                photo_url = place_details.get('photo_url')

                poi_entry = {
                    "order": order,
                    "google_place_id": place_details.get('google_place_id', ''),
                    "google_place_img_url": photo_url if photo_url else None,
                    "address": place_details.get('formatted_address', poi_address),
                    "google_maps_name": place_details.get('google_maps_name', poi_title),
                    "story": None,
                    "pin_image_url": None,
                    "story_keywords": None,
                    "gps_location": gps_location if gps_location else None
                }
            else:
                poi_entry = {
                    "order": order,
                    "google_place_id": "",
                    "google_place_img_url": None,
                    "address": poi_address,
                    "google_maps_name": poi_title,
                    "story": None,
                    "pin_image_url": None,
                    "story_keywords": None,
                    "gps_location": None
                }

            enriched_pois.append(poi_entry)

        # Update tour with final POIs and mark as completed
        tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={
                "pois": enriched_pois,
                "status_code": "completed"
            }
        )

        logger.info(f"✅ Tour generation completed successfully for transaction {transaction_id}")
        logger.info(f"   Final tour has {len(enriched_pois)} POIs")

    except Exception as e:
        logger.error(f"❌ Error in background tour generation for {transaction_id}: {str(e)}")
        logger.exception(e)  # Log full stack trace

        # Update tour status to failed with error message
        tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={
                "status_code": "failed",
                "error_message": str(e)
            }
        )


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
    themes: Dict[str, str]
    address: str

    class Config:
        json_schema_extra = {
            "example": {
                "themes": {
                    "Historical Heritage Tour": "Explore the colonial architecture and historical landmarks along this iconic street",
                    "Shopping & Fashion Tour": "Discover luxury brands and modern shopping centers in Singapore's premier retail district",
                    "Cultural Fusion Tour": "Experience the blend of traditional and contemporary Asian culture"
                },
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
                themes={
                    "🏛️ Historical Heritage Tour": "Explore the colonial architecture and historical landmarks along this iconic street",
                    "🛍️ Shopping & Fashion Tour": "Discover luxury brands and modern shopping centers in Singapore's premier retail district",
                    "🎨 Cultural Fusion Tour": "Experience the blend of traditional and contemporary Asian culture"
                },
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
        pois_data = await generate_pois(
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
        verified_pois_dict = verify_multiple_pois(pois_dict)

        # Convert verified POIs back to POI model objects
        verified_pois = [POI(**poi) for poi in verified_pois_dict]

        # Get total verified count
        total_verified = len(verified_pois)

        # Update tour with filtered POIs
        tour_repo.update_tour_by_uuid(
            tour_uuid=request.transaction_id,
            updates={"filtered_candidate_poi_list": [poi.model_dump() for poi in verified_pois]}
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

        # Helper function to parse time to minutes
        def parse_time_to_minutes(time_str: str) -> int:
            time_lower = time_str.lower()
            if 'hour' in time_lower:
                hours = float(''.join(filter(lambda x: x.isdigit() or x == '.', time_lower.split('hour')[0])))
                return int(hours * 60)
            elif 'min' in time_lower:
                return int(''.join(filter(str.isdigit, time_lower)))
            elif 'day' in time_lower:
                days = float(''.join(filter(lambda x: x.isdigit() or x == '.', time_lower.split('day')[0])))
                return int(days * 24 * 60)
            return 120  # Default 2 hours

        # Helper function to parse distance to km
        def parse_distance_to_km(distance_str: str) -> float:
            distance_lower = distance_str.lower()
            if 'km' in distance_lower or 'kilometer' in distance_lower:
                return float(''.join(filter(lambda x: x.isdigit() or x == '.', distance_lower.split('km')[0])))
            elif 'mile' in distance_lower:
                miles = float(''.join(filter(lambda x: x.isdigit() or x == '.', distance_lower.split('mile')[0])))
                return miles * 1.60934
            elif 'm' in distance_lower and 'km' not in distance_lower:
                meters = float(''.join(filter(str.isdigit, distance_lower)))
                return meters / 1000
            return 5.0  # Default 5 km

        # Prepare tour data for database (address is now part of constraints)
        tour_data = {
            "id": transaction_id,
            "theme": request.constraints.custom,
            "status_code": "valid" if is_valid else "invalid",
            "max_distance_km": parse_distance_to_km(request.constraints.distance),
            "max_duration_minutes": parse_time_to_minutes(request.constraints.max_time),
            "introduction": f"Tour request at {user_address}",
            "pois": [],
            "storyline_keywords": user_address,
            "constraints": request.constraints.model_dump()  # This now includes address
        }

        # Store in tours table
        tour_repo.add_tour(tour_data)

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
        tour_data = tour_repo.get_tour_by_uuid(request.transaction_id)

        if tour_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Tour with transaction_id {request.transaction_id} not found"
            )

        # Get the user address from the tour
        user_address = tour_data.get('storyline_keywords', '')
        
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
            
        # Convert POI models to dictionaries if they aren't already
        pois_dict = filtered_pois

        # Use Gemini to order the POIs optimally
        max_retries = 3
        current_pois = pois_dict
        feedback = None
        
        ordered_pois = []
        
        for attempt in range(max_retries):
            print(f"🔄 Tour generation attempt {attempt + 1}/{max_retries}")
            
            # Use Gemini to order the POIs optimally
            ordered_pois = await order_pois_for_tour(
                pois=current_pois,
                user_address=user_address,
                max_time=max_time,
                distance=distance,
                theme=theme,
                feedback=feedback
            )
            
            # Prepare waypoints for route calculation (tour should start and end at user_address)
            waypoints = []
            for poi in ordered_pois:
                waypoints.append(poi.get('poi_address', ''))
            
            # Calculate route metrics (origin and destination are both user_address)
            metrics = calculate_route_metrics(user_address, waypoints)
            total_distance_km = metrics.get('total_distance_km', float('inf'))
            total_duration_min = metrics.get('total_duration_minutes', float('inf'))
            
            print(f"   📊 Metrics: {total_distance_km:.2f} km, {total_duration_min:.0f} min")
            
            # Check constraints
            # Parse limits (assuming they are stored as strings like "5 km" or numbers in DB)
            # Helper to parse limit from string if needed, or use the value if already float/int
            limit_distance = float(distance.split()[0]) if isinstance(distance, str) and ' ' in distance else (float(distance) if distance else 5.0)
            limit_time = 120 # Default
            if isinstance(max_time, str):
                 if 'hour' in max_time:
                     limit_time = float(max_time.split()[0]) * 60
                 elif 'min' in max_time:
                     limit_time = float(max_time.split()[0])
            else:
                limit_time = int(max_time) if max_time else 120

            # Allow some buffer (e.g. 10%)
            if total_distance_km <= limit_distance * 1.1 and total_duration_min <= limit_time * 1.1:
                print("   ✅ Constraints met!")
                break
            else:
                print("   ❌ Constraints exceeded.")
                feedback = f"The previous plan was too long. Actual distance: {total_distance_km:.2f} km (Limit: {limit_distance} km). Actual duration: {total_duration_min:.0f} min (Limit: {limit_time} min). Please reduce the number of stops or choose closer ones."
                
                # If this was the last attempt, we still use the result but maybe log/warn
                if attempt == max_retries - 1:
                    print("   ⚠️ Max retries reached. Returning best effort.")

        # Enrich each POI with Google Maps details
        enriched_pois = []
        for ordered_poi in ordered_pois:
            poi_title = ordered_poi.get('poi_title', '')
            poi_address = ordered_poi.get('poi_address', '')
            order = ordered_poi.get('order', 0)

            # Get Google Maps details (place_id, name, GPS location, photo URL)
            place_details = get_place_details(poi_title, poi_address)

            if place_details:
                # Extract GPS location and photo URL if available
                gps_location = place_details.get('gps_location')
                photo_url = place_details.get('photo_url')
                
                poi_entry = {
                    "order": order,
                    "google_place_id": place_details.get('google_place_id', ''),
                    "google_place_img_url": photo_url if photo_url else None,
                    "address": place_details.get('formatted_address', poi_address),
                    "google_maps_name": place_details.get('google_maps_name', poi_title),
                    "story": None,  # To be filled later
                    "pin_image_url": None,  # To be filled later
                    "story_keywords": None,  # To be filled later
                    "gps_location": gps_location if gps_location else None
                }
            else:
                # Fallback if place details not found
                poi_entry = {
                    "order": order,
                    "google_place_id": "",
                    "google_place_img_url": None,
                    "address": poi_address,
                    "google_maps_name": poi_title,
                    "story": None,
                    "pin_image_url": None,
                    "story_keywords": None,
                    "gps_location": None
                }

            enriched_pois.append(poi_entry)

        # Update the tour in database with the enriched POIs
        updated = tour_repo.update_tour_by_uuid(
            tour_uuid=request.transaction_id,
            updates={"pois": enriched_pois}
        )

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
