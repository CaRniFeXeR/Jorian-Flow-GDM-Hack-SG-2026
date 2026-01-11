"""
Tour Database and Status Management Service.

This service handles tour database operations and status management.
"""
from typing import Dict, Optional
import logging
from database.tour import TourRepository
from helpers.tour_helpers import parse_time_to_minutes, parse_distance_to_km

logger = logging.getLogger(__name__)


class TourService:
    """Service for managing tour database operations and status."""

    def __init__(self, tour_repo: TourRepository):
        """
        Initialize the tour service.

        Args:
            tour_repo: TourRepository instance for database operations
        """
        self.tour_repo = tour_repo

    def update_tour_status(self, transaction_id: str, status_code: str) -> None:
        """
        Update tour status in the database.

        Args:
            transaction_id: UUID of the tour
            status_code: New status code to set
        """
        self.tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={"status_code": status_code}
        )

    def get_tour(self, transaction_id: str) -> Optional[Dict]:
        """
        Get tour by UUID.

        Args:
            transaction_id: UUID of the tour

        Returns:
            Tour data dictionary or None if not found
        """
        return self.tour_repo.get_tour_by_uuid(transaction_id)

    def create_tour(self, transaction_id: str, user_address: str, theme: str, status_code: str,
                    max_time: str, distance: str, constraints: Dict) -> None:
        """
        Create a new tour in the database.

        Args:
            transaction_id: UUID of the tour
            user_address: User's starting location
            theme: Tour theme
            status_code: Initial status code
            max_time: Maximum time constraint
            distance: Maximum distance constraint
            constraints: Full constraints dictionary
        """
        # Geocode user address to get coordinates
        user_location = None
        try:
            from services.maps_service import get_coordinates_from_address
            lat, lng = get_coordinates_from_address(user_address)
            user_location = {"lat": lat, "lng": lng}
            logger.info(f"📍 Geocoded user location: {lat}, {lng}")
        except Exception as e:
            logger.warning(f"⚠️ Could not geocode user address '{user_address}': {str(e)}")
        
        tour_data = {
            "id": transaction_id,
            "user_address": user_address,
            "user_location": user_location,
            "theme": theme,
            "status_code": status_code,
            "max_distance_km": parse_distance_to_km(distance),
            "max_duration_minutes": parse_time_to_minutes(max_time),
            "pois": [],
            "storyline_keywords": "",
            "constraints": constraints
        }
        self.tour_repo.add_tour(tour_data)

    def update_filtered_pois(self, transaction_id: str, filtered_pois: list) -> None:
        """
        Update tour with filtered POI list.

        Args:
            transaction_id: UUID of the tour
            filtered_pois: List of filtered POI dictionaries
        """
        self.tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={"filtered_candidate_poi_list": filtered_pois}
        )

    def finalize_tour(self, transaction_id: str, enriched_pois: list) -> None:
        """
        Finalize tour by updating database with enriched POIs and marking as completed.

        Args:
            transaction_id: UUID of the tour
            enriched_pois: List of enriched POI dictionaries
        """
        self.tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={
                "pois": enriched_pois,
                "status_code": "completed"
            }
        )

        logger.info(f"✅ Tour generation completed successfully for transaction {transaction_id}")
        logger.info(f"   Final tour has {len(enriched_pois)} POIs")

    def mark_tour_failed(self, transaction_id: str, error_message: str) -> None:
        """
        Mark tour as failed with error message.

        Args:
            transaction_id: UUID of the tour
            error_message: Error message to store
        """
        self.tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={
                "status_code": "failed",
                "error_message": error_message
            }
        )

    def update_tour_pois(self, transaction_id: str, pois: list) -> bool:
        """
        Update tour with POIs.

        Args:
            transaction_id: UUID of the tour
            pois: List of POI dictionaries

        Returns:
            True if updated successfully, False otherwise
        """
        return self.tour_repo.update_tour_by_uuid(
            tour_uuid=transaction_id,
            updates={"pois": pois}
        )
