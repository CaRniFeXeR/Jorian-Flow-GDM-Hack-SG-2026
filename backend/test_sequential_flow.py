import httpx
import json
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    print("🚀 Starting Sequential API Test...")
    
    with httpx.Client(timeout=30.0) as client:
        # Step 1: Guardrail
        print("\n1️⃣  Testing /guardrail...")
        guardrail_payload = {
            "user_address": "Orchard Road, Singapore",
            "constraints": {
                "max_time": "2 hours",
                "distance": "5 km",
                "custom": "Historical tour"
            }
        }
        
        try:
            response = client.post(f"{BASE_URL}/guardrail", json=guardrail_payload)
            response.raise_for_status()
            data = response.json()
            transaction_id = data["transaction_id"]
            is_valid = data["valid"]
            print(f"✅ Guardrail Success! Transaction ID: {transaction_id}")
            print(f"   Valid: {is_valid}")
            
            if not is_valid:
                print("❌ Tour request was invalid according to Guardrail. Stopping.")
                return

        except httpx.HTTPError as e:
            print(f"❌ Guardrail Failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)
            return

        # Step 2: Filter POI
        print("\n2️⃣  Testing /filter_poi...")
        # Dummy POIs for testing
        pois_input = [
            {
                "poi_title": "Singapore Botanic Gardens",
                "poi_address": "1 Cluny Rd, Singapore 259569",
                "order": 0,
                "google_place_id": "", # Let backend fill/verify if needed, or provide if known
                "google_place_img_url": None,
                "address": "1 Cluny Rd, Singapore 259569",
                "google_maps_name": "Singapore Botanic Gardens",
                "story": "History",
                "pin_image_url": None,
                "story_keywords": "nature"
            },
             {
                "poi_title": "ION Orchard",
                "poi_address": "2 Orchard Turn, Singapore 238801",
                "order": 0,
                "google_place_id": "", 
                "google_place_img_url": None,
                "address": "2 Orchard Turn, Singapore 238801",
                "google_maps_name": "ION Orchard",
                "story": "Shopping",
                "pin_image_url": None,
                "story_keywords": "shopping"
            }
        ]
        
        filter_payload = {
            "transaction_id": transaction_id,
            "pois": pois_input
        }

        try:
            response = client.post(f"{BASE_URL}/filter_poi", json=filter_payload)
            response.raise_for_status()
            data = response.json()
            verified_count = data["total_verified"]
            print(f"✅ Filter POI Success! Verified POIs: {verified_count}")
        except httpx.HTTPError as e:
            print(f"❌ Filter POI Failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)
            return

        # Step 3: Generate Tour
        print("\n3️⃣  Testing /generate_tour...")
        generate_payload = {
            "transaction_id": transaction_id
        }

        try:
            response = client.post(f"{BASE_URL}/generate_tour", json=generate_payload)
            response.raise_for_status()
            data = response.json()
            success = data["success"]
            poi_count = data["pois_count"]
            print(f"✅ Generate Tour Success! Status: {success}")
            print(f"   Final POI Count: {poi_count}")
        except httpx.HTTPError as e:
            print(f"❌ Generate Tour Failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)
            return

    print("\n🎉 Test Complete!")

if __name__ == "__main__":
    run_test()
