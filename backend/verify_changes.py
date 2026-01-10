import asyncio
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath("backend"))

from main import app
from database.database_base import DatabaseBase
from database.tour import TourRepository

client = TestClient(app)

# Mock external services to avoid API calls
@pytest.fixture
def mock_external_services():
    with patch("routes.tour.validate_user_request_guardrail", new_callable=AsyncMock) as mock_guardrail, \
         patch("routes.tour.verify_multiple_pois", new_callable=MagicMock) as mock_verify_pois, \
         patch("routes.tour.order_pois_for_tour", new_callable=AsyncMock) as mock_order_pois, \
         patch("routes.tour.get_place_details", new_callable=MagicMock) as mock_place_details, \
         patch("routes.tour.calculate_route_metrics", new_callable=MagicMock) as mock_route_metrics:

        mock_guardrail.return_value = True
        
        # Mock verify_multiple_pois to return the input POIs
        def side_effect_verify(pois):
            return pois
        mock_verify_pois.side_effect = side_effect_verify

        # Mock order_pois_for_tour to return the input POIs with an order field
        async def side_effect_order(pois, **kwargs):
            ordered = []
            for i, p in enumerate(pois):
                p_copy = p.copy()
                p_copy['order'] = i + 1
                ordered.append(p_copy)
            return ordered
        mock_order_pois.side_effect = side_effect_order

        mock_place_details.return_value = {
            "google_place_id": "test_place_id",
            "formatted_address": "Test Address",
            "google_maps_name": "Test Name"
        }

        mock_route_metrics.return_value = {
            "total_distance_km": 1.0,
            "total_duration_minutes": 30.0
        }

        yield {
            "guardrail": mock_guardrail,
            "verify_pois": mock_verify_pois,
            "order_pois": mock_order_pois,
            "place_details": mock_place_details,
            "route_metrics": mock_route_metrics
        }

def test_tour_flow(mock_external_services):
    # Setup test database
    db_path = "test_db_flow.json"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Patch the database path in the router
    # Note: This is tricky because the router initializes the DB at module level.
    # For this test script, we rely on the fact that we can manipulate the repository used by the router if we could access it,
    # or we can just let it use the default DB but cleaned up.
    # However, since the code hardcodes "database/db.json", we might affect dev data.
    # Ideally, dependency injection should be used.
    # For this hackathon scope, we will patch TourRepository in the routes module.
    
    with patch("routes.tour.db_base", DatabaseBase(db_path)) as mock_db_base:
        # We need to re-initialize the repo with the new db_base
        # But the route uses `tour_repo` instance. We patch that instance.
        new_repo = TourRepository(mock_db_base)
        with patch("routes.tour.tour_repo", new_repo):
            
            # Step 1: Guardrail
            print("\nTesting /guardrail...")
            guardrail_payload = {
                "user_address": "Orchard Road",
                "constraints": {
                    "max_time": "2 hours",
                    "distance": "5 km",
                    "custom": "Test Theme"
                }
            }
            response = client.post("/api/v1/guardrail", json=guardrail_payload)
            if response.status_code != 200:
                print(f"Guardrail Failed: {response.text}")
            assert response.status_code == 200
            data = response.json()
            transaction_id = data["transaction_id"]
            assert data["valid"] is True
            print(f"Guardrail passed. Transaction ID: {transaction_id}")

            # Verify DB state
            tour = new_repo.get_tour_by_uuid(transaction_id)
            assert tour is not None
            assert tour["constraints"]["custom"] == "Test Theme"
            print("DB verification for Guardrail passed.")

            # Step 2: Filter POI
            print("\nTesting /filter_poi...")
            pois_input = [
                    "google_place_id": "id2"
                }
            ]
            filter_payload = {
                "transaction_id": transaction_id,
                "pois": pois_input
            }
            response = client.post("/api/v1/filter_poi", json=filter_payload)
            assert response.status_code == 200
            data = response.json()
            assert data["total_verified"] == 2
            print("Filter POI passed.")

            # Verify DB state
            tour = new_repo.get_tour_by_uuid(transaction_id)
            assert "filtered_candidate_poi_list" in tour
            assert len(tour["filtered_candidate_poi_list"]) == 2
            print("DB verification for Filter POI passed.")

            # Step 3: Generate Tour
            print("\nTesting /generate_tour...")
            generate_payload = {
                "transaction_id": transaction_id
            }
            response = client.post("/api/v1/generate_tour", json=generate_payload)
            if response.status_code != 200:
                print(f"Generate Tour Failed: {response.json()}")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            print("Generate Tour passed.")

            # Verify DB state
            tour = new_repo.get_tour_by_uuid(transaction_id)
            assert len(tour["pois"]) == 2
            assert tour["pois"][0]["google_place_id"] == "test_place_id"
            print("DB verification for Generate Tour passed.")

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    # Run pytest manually from script
    sys.exit(pytest.main(["-v", __file__]))
