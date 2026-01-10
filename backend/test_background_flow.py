import httpx
import json
import time

BASE_URL = "http://localhost:8000/api/v1"


def test_background_tour_generation():
    """
    Test the background tour generation flow:
    1. Call /guardrail with valid request
    2. Get transaction_id immediately
    3. Background process automatically runs: generate_poi -> filter_poi -> generate_tour
    4. Poll the tour status until completed
    """
    print("\n🚀 Testing Background Tour Generation Flow...")
    print("=" * 80)

    with httpx.Client(timeout=120.0) as client:
        # Step 1: Call /guardrail
        print("\n1️⃣  Calling /guardrail...")
        guardrail_payload = {
            "user_address": "Orchard Road, Singapore",
            "constraints": {
                "max_time": "2 hours",
                "distance": "5 km",
                "custom": "Historical landmarks and cultural sites"
            }
        }

        try:
            response = client.post(f"{BASE_URL}/guardrail", json=guardrail_payload)
            response.raise_for_status()
            data = response.json()
            transaction_id = data["transaction_id"]
            is_valid = data["valid"]

            print(f"✅ Guardrail Response Received!")
            print(f"   Transaction ID: {transaction_id}")
            print(f"   Valid: {is_valid}")

            if not is_valid:
                print("❌ Tour request was invalid. Test stopped.")
                return

            print("\n🔄 Background process started automatically...")
            print("   The backend is now running:")
            print("   - Geocoding address to coordinates")
            print("   - Generating POIs with Gemini")
            print("   - Filtering POIs with Google Maps")
            print("   - Ordering POIs and creating tour")

        except httpx.HTTPError as e:
            print(f"❌ Guardrail Failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Server Response: {e.response.text}")
            return

        # Step 2: Poll tour status
        print("\n2️⃣  Polling tour status...")
        max_poll_attempts = 30  # Poll for up to 30 attempts
        poll_interval = 5  # Wait 5 seconds between polls

        for attempt in range(1, max_poll_attempts + 1):
            try:
                print(f"\n   Poll attempt {attempt}/{max_poll_attempts}...")

                # Call GET /{transaction_id}/false to get tour status
                response = client.get(f"{BASE_URL}/{transaction_id}/false")

                if response.status_code == 200:
                    tour_data = response.json()
                    status = tour_data.get('status_code', 'unknown')
                    pois_count = len(tour_data.get('pois', []))

                    print(f"   Status: {status}")
                    print(f"   POIs count: {pois_count}")

                    if status == "completed":
                        print("\n✅ Tour generation COMPLETED!")
                        print("=" * 80)
                        print(f"📋 Final Tour Details:")
                        print(f"   Transaction ID: {transaction_id}")
                        print(f"   Theme: {tour_data.get('theme')}")
                        print(f"   Status: {status}")
                        print(f"   Number of POIs: {pois_count}")
                        print("\n   POIs:")
                        for poi in tour_data.get('pois', []):
                            print(f"   {poi.get('order')}. {poi.get('google_maps_name')} - {poi.get('address')}")
                        print("=" * 80)
                        return

                    elif status == "failed":
                        error_msg = tour_data.get('error_message', 'Unknown error')
                        print(f"\n❌ Tour generation FAILED!")
                        print(f"   Error: {error_msg}")
                        return

                    elif status in ["geocoding", "generating_pois", "filtering_pois", "generating_tour"]:
                        print(f"   ⏳ Still in progress, waiting {poll_interval} seconds...")
                        time.sleep(poll_interval)

                    else:
                        print(f"   ⏳ Status: {status}, waiting {poll_interval} seconds...")
                        time.sleep(poll_interval)

                elif response.status_code == 404:
                    print(f"   Tour not found yet, waiting {poll_interval} seconds...")
                    time.sleep(poll_interval)

                else:
                    print(f"   Unexpected status code: {response.status_code}")
                    time.sleep(poll_interval)

            except httpx.HTTPError as e:
                print(f"   Poll error: {e}")
                time.sleep(poll_interval)

        print("\n⏰ Polling timeout reached. Tour may still be processing.")
        print(f"   You can manually check the status by calling: GET {BASE_URL}/{transaction_id}/false")


if __name__ == "__main__":
    test_background_tour_generation()
