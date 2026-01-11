from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class GPSLocation(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")


class POI(BaseModel):
    order: Optional[int] = Field(None, description="Order of the POI in the tour")
    poi_title: Optional[str] = Field(None, description="Title of the POI")
    google_place_id: Optional[str] = Field(None, description="Google Place ID for this POI")
    google_place_img_url: Optional[str] = Field(None, description="Image URL from Google Places")
    address: Optional[str] = Field(None, description="Address of the POI")
    google_maps_name: Optional[str] = Field(None, description="Name from Google Maps")
    story: Optional[str] = Field(None, description="Story or description for this POI")
    pin_image_url: Optional[str] = Field(None, description="URL for the pin image")
    story_keywords: Optional[str] = Field(None, description="Keywords related to the story")
    gps_location: Optional[GPSLocation] = Field(None, description="GPS location with latitude and longitude")

    class Config:
        json_schema_extra = {
            "example": {
                "order": 1,
                "google_place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
                "google_place_img_url": "https://example.com/image.jpg",
                "address": "1 Cluny Rd, Singapore 259569",
                "google_maps_name": "Singapore Botanic Gardens",
                "story": "A beautiful botanical garden with rich history",
                "pin_image_url": "https://example.com/pin.png",
                "story_keywords": "nature, history, gardens",
                "gps_location": {
                    "lat": 1.3147,
                    "lng": 103.8159
                }
            }
        }


class Tour(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the tour")
    user_address: str = Field(..., description="User's starting location address")
    user_location: Optional[GPSLocation] = Field(None, description="User's starting location GPS coordinates")
    theme: str = Field(..., description="Theme of the tour")
    status_code: str = Field(..., description="Status code of the tour")
    max_distance_km: float = Field(..., description="Maximum distance in kilometers")
    max_duration_minutes: int = Field(..., description="Maximum duration in minutes")
    introduction: Optional[str] = Field(None, description="Introduction text for the tour")
    pois: List[POI] = Field(default_factory=list, description="List of Points of Interest")
    storyline_keywords: Optional[str] = Field(None, description="Keywords for the tour storyline")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Constraints used for the tour")
    filtered_candidate_poi_list: Optional[List[POI]] = Field(None, description="List of candidate POIs after filtering")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_address": "Orchard Road, Singapore",
                "theme": "Historical Heritage Tour",
                "status_code": "active",
                "max_distance_km": 5.0,
                "max_duration_minutes": 120,
                "introduction": "Explore the colonial architecture and historical landmarks",
                "pois": [
                    {
                        "order": 1,
                        "google_place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
                        "google_place_img_url": "https://example.com/image.jpg",
                        "address": "1 Cluny Rd, Singapore 259569",
                        "google_maps_name": "Singapore Botanic Gardens",
                        "story": "A beautiful botanical garden",
                        "pin_image_url": "https://example.com/pin.png",
                        "story_keywords": "nature, history",
                        "gps_location": {
                            "lat": 1.3147,
                            "lng": 103.8159
                        }
                    }
                ],
                "storyline_keywords": "",
                "constraints": {
                    "max_time": "3 hours",
                    "distance": "10 km",
                    "custom": "I want a chicken rice food tour",
                    "address": "Orchard Road, Singapore"
                },
                "filtered_candidate_poi_list": [
                     {
                        "order": 1,
                        "google_place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
                        "google_place_img_url": "https://example.com/image.jpg",
                        "address": "1 Cluny Rd, Singapore 259569",
                        "google_maps_name": "Singapore Botanic Gardens",
                        "story": "A beautiful botanical garden",
                        "pin_image_url": "https://example.com/pin.png",
                        "story_keywords": "nature, history",
                        "gps_location": {
                            "lat": 1.3147,
                            "lng": 103.8159
                        }
                    }
                ]
            }
        }
