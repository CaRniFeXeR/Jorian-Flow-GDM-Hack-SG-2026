"""
Tour Generation Orchestration Service.

This service orchestrates the complete tour generation workflow including:
- POI generation and verification
- Optimal ordering with retry logic
- Enrichment and finalization
"""
from typing import Dict, List
import logging
from services.poi_service import POIService
from services.tour_service import TourService
from services.gemini_service import order_pois_for_tour
from services.maps_service import calculate_route_metrics
from helpers.tour_helpers import parse_time_to_minutes, parse_distance_to_km

logger = logging.getLogger(__name__)


class TourOrchestrationService:
    """Service for orchestrating tour generation workflows."""

    def __init__(self, poi_service: POIService, tour_service: TourService):
        """
        Initialize the tour orchestration service.

        Args:
            poi_service: POIService instance for POI operations
            tour_service: TourService instance for tour database operations
        """
        self.poi_service = poi_service
        self.tour_service = tour_service

    async def generate_pois_step(
        self,
        transaction_id: str,
        user_address: str,
        max_time: str,
        distance: str,
        custom_message: str
    ) -> List[Dict]:
        """
        Generate POIs using Gemini based on user constraints.

        Args:
            transaction_id: UUID of the tour
            user_address: User's starting location
            max_time: Maximum time constraint
            distance: Maximum distance constraint
            custom_message: User's custom preferences/theme

        Returns:
            List of generated POI dictionaries
        """
        logger.info(f"🔍 Geocoding address: {user_address}")
        self.tour_service.update_tour_status(transaction_id, "geocoding")

        self.tour_service.update_tour_status(transaction_id, "generating_pois")
        logger.info(f"🤖 Generating POIs with Gemini...")

        pois_data = await self.poi_service.generate_pois(
            address=user_address,
            time_constraint=max_time,
            distance_constraint=distance,
            user_custom_info=custom_message
        )
        logger.info(f"✅ Generated {len(pois_data)} POIs")

        return pois_data

    def verify_and_store_pois(
        self,
        transaction_id: str,
        pois_data: List[Dict]
    ) -> List[Dict]:
        """
        Verify POIs using Google Maps and store them in the database.

        Args:
            transaction_id: UUID of the tour
            pois_data: List of POI dictionaries to verify

        Returns:
            List of verified POI dictionaries

        Raises:
            ValueError: If no POIs were verified
        """
        self.tour_service.update_tour_status(transaction_id, "filtering_pois")
        logger.info(f"🔍 Verifying POIs with Google Maps...")

        verified_pois_list = self.poi_service.verify_pois(pois_data)
        logger.info(f"✅ Verified {len(verified_pois_list)} out of {len(pois_data)} POIs")

        # Store filtered POIs in database
        self.tour_service.update_filtered_pois(transaction_id, verified_pois_list)

        if not verified_pois_list:
            logger.error(f"❌ No POIs were verified for transaction {transaction_id}")
            self.tour_service.update_tour_status(transaction_id, "failed")
            self.tour_service.mark_tour_failed(
                transaction_id,
                "No POIs could be verified in the specified area"
            )
            raise ValueError("No POIs could be verified in the specified area")

        return verified_pois_list

    async def order_pois_with_retry(
        self,
        transaction_id: str,
        verified_pois_list: List[Dict],
        user_address: str,
        max_time: str,
        distance: str,
        theme: str
    ) -> List[Dict]:
        """
        Order POIs optimally with retry logic to meet constraints.

        Args:
            transaction_id: UUID of the tour
            verified_pois_list: List of verified POI dictionaries
            user_address: User's starting location
            max_time: Maximum time constraint
            distance: Maximum distance constraint
            theme: Tour theme

        Returns:
            List of ordered POI dictionaries
        """
        self.tour_service.update_tour_status(transaction_id, "generating_tour")
        logger.info(f"🗺️ Ordering POIs for optimal tour...")

        max_retries = 4
        current_pois = verified_pois_list
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

            # Prepare waypoints for route calculation
            waypoints = [poi.get('poi_address', '') for poi in ordered_pois]

            # Calculate route metrics
            metrics = calculate_route_metrics(user_address, waypoints)
            total_distance_km = metrics.get('total_distance_km', float('inf'))
            total_duration_min = metrics.get('total_duration_minutes', float('inf'))

            logger.info(f"📊 Route metrics: {total_distance_km:.2f} km, {total_duration_min:.0f} min")

            # Parse constraints
            limit_distance = parse_distance_to_km(distance)
            limit_time = parse_time_to_minutes(max_time)

            # Check if constraints are met (with 10% buffer)
            if total_distance_km <= limit_distance * 1.1 and total_duration_min <= limit_time * 1.1:
                logger.info("✅ Tour constraints met!")
                break
            else:
                logger.warning(f"⚠️ Constraints exceeded (attempt {attempt + 1})")
                feedback = (
                    f"Previous plan exceeded constraints. "
                    f"Distance: {total_distance_km:.2f}km (limit: {limit_distance}km), "
                    f"Duration: {total_duration_min:.0f}min (limit: {limit_time}min). "
                    f"Reduce POIs or choose closer ones."
                )

                if attempt == max_retries - 1:
                    logger.warning("⚠️ Max retries reached, using best effort result")

        return ordered_pois

    async def process_tour_generation(
        self,
        transaction_id: str,
        user_address: str,
        max_time: str,
        distance: str,
        custom_message: str
    ) -> None:
        """
        Process complete tour generation workflow.

        This function orchestrates the following steps:
        1. Generate POIs based on constraints
        2. Filter/verify POIs using Google Maps
        3. Order POIs optimally and enrich with details
        4. Generate tour introduction
        5. Generate narrative stories for each POI

        Args:
            transaction_id: UUID of the tour
            user_address: User's starting location
            max_time: Maximum time constraint
            distance: Maximum distance constraint
            custom_message: User's custom preferences/theme
        """
        try:
            logger.info(f"🚀 Starting tour generation for transaction {transaction_id}")

            # Step 1: Generate POIs using Gemini
            pois_data = await self.generate_pois_step(
                transaction_id=transaction_id,
                user_address=user_address,
                max_time=max_time,
                distance=distance,
                custom_message=custom_message
            )

            # Step 2: Verify POIs using Google Maps
            verified_pois_list = self.verify_and_store_pois(transaction_id, pois_data)

            # Step 3: Get tour theme
            tour_data = self.tour_service.get_tour(transaction_id)
            if tour_data is None:
                raise ValueError(f"Tour {transaction_id} not found during generation")
            theme = tour_data.get('theme', custom_message)

            # Step 4: Order POIs optimally with retry logic
            ordered_pois = await self.order_pois_with_retry(
                transaction_id=transaction_id,
                verified_pois_list=verified_pois_list,
                user_address=user_address,
                max_time=max_time,
                distance=distance,
                theme=theme
            )

            # Step 5: Enrich POIs with Google Maps details
            enriched_pois = self.poi_service.enrich_pois_with_details(ordered_pois)

            # Step 6: Generate introduction for the tour
            logger.info(f"📝 Generating tour introduction...")
            from services.gemini_service import generate_tour_introduction
            introduction = await generate_tour_introduction(
                pois=enriched_pois,
                user_custom_info=theme
            )
            
            # Update tour with introduction
            self.tour_service.tour_repo.update_tour_by_uuid(
                tour_uuid=transaction_id,
                updates={"introduction": introduction}
            )
            logger.info(f"✅ Introduction generated: {introduction[:50]}...")

            # Step 7: Generate narrative stories for each POI
            logger.info(f"📖 Generating narrative stories for POIs...")
            from services.gemini_service import generate_narrative_stories
            pois_with_stories = await generate_narrative_stories(
                pois=enriched_pois,
                user_custom_info=theme
            )
            logger.info(f"✅ Stories generated for {len(pois_with_stories)} POIs")

            # Step 8: Finalize tour with stories
            self.tour_service.finalize_tour(transaction_id, pois_with_stories)

        except ValueError as e:
            # Handle validation errors (e.g., no POIs verified)
            logger.error(f"❌ Validation error in tour generation for {transaction_id}: {str(e)}")
            error_message = str(e)
            if "No POIs could be verified" not in error_message:
                self.tour_service.mark_tour_failed(transaction_id, error_message)
            raise
        except Exception as e:
            # Handle other errors
            logger.error(f"❌ Error in tour generation for {transaction_id}: {str(e)}")
            logger.exception(e)
            self.tour_service.mark_tour_failed(transaction_id, str(e))
            raise

    async def generate_tour_from_filtered_pois(
        self,
        transaction_id: str,
        filtered_pois: List[Dict],
        user_address: str,
        max_time: str,
        distance: str,
        theme: str
    ) -> List[Dict]:
        """
        Generate tour from already filtered POIs (manual flow).

        This method orders existing filtered POIs and enriches them.
        Used for the /generate_tour endpoint when POIs are already filtered.

        Args:
            transaction_id: UUID of the tour
            filtered_pois: List of already filtered POI dictionaries
            user_address: User's starting location
            max_time: Maximum time constraint
            distance: Maximum distance constraint
            theme: Tour theme

        Returns:
            List of enriched POI dictionaries
        """
        logger.info(f"🗺️ Ordering {len(filtered_pois)} filtered POIs for tour...")

        max_retries = 3
        current_pois = filtered_pois
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

            # Prepare waypoints for route calculation
            waypoints = [poi.get('poi_address', '') for poi in ordered_pois]

            # Calculate route metrics
            metrics = calculate_route_metrics(user_address, waypoints)
            total_distance_km = metrics.get('total_distance_km', float('inf'))
            total_duration_min = metrics.get('total_duration_minutes', float('inf'))

            logger.info(f"📊 Route metrics: {total_distance_km:.2f} km, {total_duration_min:.0f} min")

            # Parse constraints
            limit_distance = parse_distance_to_km(distance)
            limit_time = parse_time_to_minutes(max_time)

            # Check if constraints are met (with 10% buffer)
            if total_distance_km <= limit_distance * 1.1 and total_duration_min <= limit_time * 1.1:
                logger.info("✅ Constraints met!")
                break
            else:
                logger.warning("⚠️ Constraints exceeded.")
                feedback = (
                    f"The previous plan was too long. "
                    f"Actual distance: {total_distance_km:.2f} km (Limit: {limit_distance} km). "
                    f"Actual duration: {total_duration_min:.0f} min (Limit: {limit_time} min). "
                    f"Please reduce the number of stops or choose closer ones."
                )

                if attempt == max_retries - 1:
                    logger.warning("⚠️ Max retries reached. Returning best effort.")

        # Enrich POIs with Google Maps details
        enriched_pois = self.poi_service.enrich_pois_with_details(ordered_pois)

        return enriched_pois
