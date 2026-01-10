from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class POI(BaseModel):
    order: int = Field(..., description="Order of the POI in the tour")
    filtered_candidate_poi_list: Optional[List[str]] = Field(
        None, description="List of filtered candidate POIs"
    )
    poi_title: Optional[str] = Field(None, description="Title of the POI")
    google_place_id: str = Field(..., description="Google Place ID for this POI")
    google_place_img_url: Optional[str] = Field(None, description="Image URL from Google Places")
    address: Optional[str] = Field(None, description="Address of the POI")
    google_maps_name: Optional[str] = Field(None, description="Name from Google Maps")
    story: Optional[str] = Field(None, description="Story or description for this POI")
    pin_image_url: Optional[str] = Field(None, description="URL for the pin image")
    story_keywords: Optional[str] = Field(None, description="Keywords related to the story")

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
                "story_keywords": "nature, history, gardens"
            }
        }


class Tour(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the tour")
    theme: str = Field(..., description="Theme of the tour")
    status_code: str = Field(..., description="Status code of the tour")
    max_distance_km: float = Field(..., description="Maximum distance in kilometers")
    max_duration_minutes: int = Field(..., description="Maximum duration in minutes")
    introduction: str = Field(..., description="Introduction text for the tour")
    pois: List[POI] = Field(default_factory=list, description="List of Points of Interest")
    storyline_keywords: str = Field(..., description="Keywords for the tour storyline")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
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
                        "story_keywords": "nature, history"
                    }
                ],
                "storyline_keywords": "history, architecture, culture"
            }
        }
