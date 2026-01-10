#!/usr/bin/env python3
"""
Quick test for background tour generation.
Run this after starting the server with: python main.py
"""

import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"

def test():
    print("\n" + "="*60)
    print("Testing Background Tour Generation")
    print("="*60)

    client = httpx.Client(timeout=120.0)

    # Step 1: Call guardrail
    print("\n1. Calling /guardrail...")
    response = client.post(f"{BASE_URL}/guardrail", json={
        "user_address": "Marina Bay, Singapore",
        "constraints": {
            "max_time": "2 hours",
            "distance": "3 km",
            "custom": "Sightseeing tour"
        }
    })

    data = response.json()
    transaction_id = data["transaction_id"]
    print(f"   ✓ Got transaction_id: {transaction_id}")
    print(f"   ✓ Valid: {data['valid']}")

    if not data['valid']:
        print("\n❌ Request invalid, stopping test")
        return

    print("\n2. Background process started! Waiting for completion...")

    # Step 2: Poll for completion
    for i in range(20):  # Poll up to 20 times (100 seconds max)
        time.sleep(5)

        response = client.get(f"{BASE_URL}/{transaction_id}/false")
        if response.status_code == 200:
            tour = response.json()
            status = tour.get('status_code', 'unknown')
            pois = tour.get('pois', [])

            print(f"   [{i+1}] Status: {status}, POIs: {len(pois)}")

            if status == "completed":
                print("\n" + "="*60)
                print("✅ SUCCESS! Tour generated in background")
                print("="*60)
                print(f"Theme: {tour.get('theme')}")
                print(f"POIs Generated: {len(pois)}")
                for poi in pois:
                    print(f"  {poi['order']}. {poi['google_maps_name']}")
                print("="*60)
                return

            elif status == "failed":
                print(f"\n❌ FAILED: {tour.get('error_message')}")
                return

    print("\n⏰ Timeout - tour still processing")
    print(f"Check manually: GET {BASE_URL}/{transaction_id}/false")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"\n❌ Error: {e}")
