from fastapi.testclient import TestClient
from main import app
from schemas.tour import POI
from uuid import uuid4
import json

client = TestClient(app)

def test_generate_introduction_endpoint():
    print("\n🚀 Testing /generate_introduction endpoint...")

    # 1. Create a tour first to get a valid transaction_id
    print("1️⃣ Creating a tour context...")
    guardrail_response = client.post("/api/v1/guardrail", json={
        "constraints": {
            "max_time": "3 hours",
            "distance": "10 km",
            "custom": "Food and Culture in Singapore",
            "address": "Chinatown, Singapore"
        }
    })
    
    if guardrail_response.status_code != 200:
        print(f"❌ Guardrail failed: {guardrail_response.text}")
        return

    transaction_id = guardrail_response.json()["transaction_id"]
    print(f"   ✓ Transaction ID: {transaction_id}")

    # 2. Call /generate_introduction
    print("2️⃣ Calling /generate_introduction...")
    
    # Mock POIs
    pois = [
        {
            "order": 1,
            "poi_title": "Chinatown Food Street",
            "google_place_id": "dummy_id_1",
            "address": "Smith St, Singapore 058938",
            "google_maps_name": "Chinatown Food Street",
             "story_keywords": "food, street, satay"
        },
        {
            "order": 2,
            "poi_title": "Buddha Tooth Relic Temple",
            "google_place_id": "dummy_id_2",
            "address": "288 South Bridge Rd, Singapore 058840",
            "google_maps_name": "Buddha Tooth Relic Temple",
            "story_keywords": "temple, culture, history"
        }
    ]

    payload = {
        "transaction_id": transaction_id,
        "pois": pois
    }

    response = client.post("/api/v1/generate_introduction", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Response 200 OK")
        intro = data['introduction']
        print(f"   Introduction ({len(intro)} chars):")
        print(f"   \"{intro}\"")
        
        if not intro:
             print("❌ Introduction empty!")
        else:
             print("   ✓ Introduction present")
             
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_generate_introduction_endpoint()
