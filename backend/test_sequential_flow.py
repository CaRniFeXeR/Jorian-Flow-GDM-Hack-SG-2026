import httpx
import json
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"


def run_happy_path():
    print("\n🚀 Starting Happy Path API Test...")
    
    with httpx.Client(timeout=60.0) as client:
        # Step 1: Guardrail
        print("\n1️⃣  Testing /guardrail (Normal)...")
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
            
            if not is_valid:
                print("❌ Tour request was invalid according to Guardrail. Stopping.")
                return

        except httpx.HTTPError as e:
            print(f"❌ Guardrail Failed: {e}")
            return

        # Step 2: Filter POI
        print("\n2️⃣  Testing /filter_poi...")
        pois_input = [
            {
                "poi_title": "Singapore Botanic Gardens",
                "address": "1 Cluny Rd, Singapore 259569",
                "order": 0,
                "google_place_id": "",
                "google_place_img_url": None,
                "google_maps_name": "Singapore Botanic Gardens",
                "story": "History",
                "pin_image_url": None,
                "story_keywords": "nature"
            },
             {
                "poi_title": "ION Orchard",
                "address": "2 Orchard Turn, Singapore 238801",
                "order": 0,
                "google_place_id": "", 
                "google_place_img_url": None,
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
                 print(f"Server Response: {e.response.text}")
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
            return

def run_strict_constraints_test():
    print("\n🚀 Starting Strict Constraints (Retry Logic) Test...")
    print("   Goal: Force the backend to optimize/remove POIs because they are too far apart for the time limit.")

    with httpx.Client(timeout=120.0) as client: # Longer timeout for retries
        # Step 1: Guardrail with STRICT constraints
        print("\n1️⃣  Testing /guardrail (Strict: 30 mins, 2 km)...")
        guardrail_payload = {
            "user_address": "Marina Bay Sands, Singapore",
            "constraints": {
                "max_time": "30 mins",
                "distance": "2 km",
                "custom": "Quick sightseeing"
            }
        }
        
        try:
            response = client.post(f"{BASE_URL}/guardrail", json=guardrail_payload)
            response.raise_for_status()
            data = response.json()
            transaction_id = data["transaction_id"]
            print(f"✅ Guardrail Success! Transaction ID: {transaction_id}")
        except httpx.HTTPError as e:
            print(f"❌ Guardrail Failed: {e}")
            return

        # Step 2: Filter POI with FAR APART locations
        # MBS, Sentosa (far), Changi Airport (very far)
        print("\n2️⃣  Testing /filter_poi (Inputting far apart POIs)...")
        pois_input = [
            {
                "poi_title": "ArtScience Museum",
                "address": "6 Bayfront Ave, Singapore 018974", # Near MBS
                "order": 0, "google_place_id": "", "google_place_img_url": None, "google_maps_name": "", "story": "", "pin_image_url": None, "story_keywords": ""
            },
            {
                "poi_title": "Universal Studios Singapore",
                "address": "8 Sentosa Gateway, Singapore 098269", # Far (Sentosa)
                "order": 0, "google_place_id": "", "google_place_img_url": None, "google_maps_name": "", "story": "", "pin_image_url": None, "story_keywords": ""
            },
            {
                "poi_title": "Jewel Changi Airport",
                "address": "78 Airport Blvd., Singapore 819666", # Very Far
                "order": 0, "google_place_id": "", "google_place_img_url": None, "google_maps_name": "", "story": "", "pin_image_url": None, "story_keywords": ""
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
            print(f"✅ Filter POI Success! Verified POIs: {data['total_verified']}")
        except httpx.HTTPError as e:
            print(f"❌ Filter POI Failed: {e}")
            if hasattr(e, 'response') and e.response:
                 print(f"Server Response: {e.response.text}")
            return

        # Step 3: Generate Tour (Should trigger retries)
        print("\n3️⃣  Testing /generate_tour (Expect backend to filter out far POIs)...")
        generate_payload = {
            "transaction_id": transaction_id
        }

        try:
            start_time = time.time()
            response = client.post(f"{BASE_URL}/generate_tour", json=generate_payload)
            response.raise_for_status()
            duration = time.time() - start_time
            
            data = response.json()
            success = data["success"]
            poi_count = data["pois_count"]
            print(f"✅ Generate Tour Success! Status: {success}")
            print(f"   Time taken: {duration:.2f}s (Longer time implies retries occurred)")
            print(f"   Final POI Count: {poi_count}")
            
            if poi_count < 3:
                print("   ✅ SUCCESS: POI count reduced to meet strict constraints!")
            else:
                print("   ⚠️ WARNING: POI count equals input. Check if constraints were actually met.")

        except httpx.HTTPError as e:
            print(f"❌ Generate Tour Failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Server Response: {e.response.text}")
            return
            
        # Step 4: Verify details
        print("\n4️⃣  Fetching Final Tour Details...")
        try:
            response = client.get(f"{BASE_URL}/{transaction_id}")
            response.raise_for_status()
            tour_data = response.json()
            print(f"   Tour Theme: {tour_data.get('theme')}")
            print("   Final POIs:")
            for p in tour_data.get('pois', []):
                 print(f"   - {p.get('google_maps_name')} ({p.get('address')})")
        except httpx.HTTPError as e:
            print(f"❌ Get Tour Failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Server Response: {e.response.text}")

if __name__ == "__main__":
    run_happy_path()
    run_strict_constraints_test()
