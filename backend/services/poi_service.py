"""
POI (Point of Interest) Management Service.

This service handles all POI-related operations including:
- Generation of POIs using AI
- Verification of POIs using Google Maps
- Enrichment of POIs with Google Maps details
"""
from typing import Dict, List
import logging
from services.gemini_service import generate_pois
from services.maps_service import verify_multiple_pois, get_place_details

logger = logging.getLogger(__name__)


class POIService:
    """Service for managing POI operations."""

    def __init__(self):
        """Initialize the POI service."""
        pass

    async def generate_pois(
        self,
        address: str,
        time_constraint: str,
        distance_constraint: str,
        user_custom_info: str
    ) -> List[Dict]:
        """
        Generate POIs using Gemini based on user constraints.

        Args:
            address: User's starting location
            time_constraint: Maximum time constraint
            distance_constraint: Maximum distance constraint
            user_custom_info: User's custom preferences/theme

        Returns:
            List of generated POI dictionaries
        """
        logger.info(f"🔍 Generating POIs for address: {address}")
        logger.info(f"🤖 Generating POIs with Gemini...")

        pois_data = await generate_pois(
            address=address,
            time_constraint=time_constraint,
            distance_constraint=distance_constraint,
            user_custom_info=user_custom_info
        )
        logger.info(f"✅ Generated {len(pois_data)} POIs")

        return pois_data

    def verify_pois(self, pois_data: List[Dict]) -> List[Dict]:
        """
        Verify POIs using Google Maps.

        Args:
            pois_data: List of POI dictionaries to verify

        Returns:
            List of verified POI dictionaries (may be empty if none are verified)
        """
        logger.info(f"🔍 Verifying POIs with Google Maps...")

        verified_pois_list = verify_multiple_pois(pois_data)
        logger.info(f"✅ Verified {len(verified_pois_list)} out of {len(pois_data)} POIs")

        return verified_pois_list

    def enrich_poi_with_details(self, ordered_poi: Dict) -> Dict:
        """
        Enrich a single POI with Google Maps details.

        Args:
            ordered_poi: Dictionary containing POI information with keys:
                         'poi_title', 'poi_address', 'order', 'story_keywords'

        Returns:
            Dictionary with enriched POI data including Google Maps details
        """
        poi_title = ordered_poi.get('poi_title', '')
        poi_address = ordered_poi.get('poi_address', '')
        order = ordered_poi.get('order', 0)
        story_keywords = ordered_poi.get('story_keywords', None)

        # Get Google Maps details
        place_details = get_place_details(poi_title, poi_address)

        if place_details:
            gps_location = place_details.get('gps_location')
            photo_url = place_details.get('photo_url')

            return {
                "order": order,
                "google_place_id": place_details.get('google_place_id', ''),
                "google_place_img_url": photo_url if photo_url else None,
                "address": place_details.get('formatted_address', poi_address),
                "google_maps_name": place_details.get('google_maps_name', poi_title),
                "story": None,
                "pin_image_url": None,
                "story_keywords": story_keywords,
                "gps_location": gps_location if gps_location else None
            }
        else:
            return {
                "order": order,
                "google_place_id": "",
                "google_place_img_url": None,
                "address": poi_address,
                "google_maps_name": poi_title,
                "story": None,
                "pin_image_url": None,
                "story_keywords": story_keywords,
                "gps_location": None
            }

    def enrich_pois_with_details(self, ordered_pois: List[Dict]) -> List[Dict]:
        """
        Enrich all ordered POIs with Google Maps details.

        Args:
            ordered_pois: List of ordered POI dictionaries

        Returns:
            List of enriched POI dictionaries
        """
        logger.info(f"📍 Enriching {len(ordered_pois)} POIs with Google Maps details...")
        enriched_pois = [self.enrich_poi_with_details(poi) for poi in ordered_pois]
        return enriched_pois
