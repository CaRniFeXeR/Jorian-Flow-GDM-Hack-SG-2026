import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath("/root/git/Jorian-Flow-GDM-Hack-SG-2026/backend"))

try:
    from database.database_base import DatabaseBase
    from database.tour import TourRepository
    from database.tts_storage import TTSRepository
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

# Test database creation
try:
    db_base = DatabaseBase("test_db.json")
    tour_repo = TourRepository(db_base)
    tts_repo = TTSRepository(db_base)
    print("Database initialization successful.")
    
    # Test Tour Repo
    tour_id = tour_repo.add_tour({"name": "Test Tour", "stops": []})
    tours = tour_repo.list_tours()
    assert len(tours) == 1
    assert tours[0]['name'] == 'Test Tour'
    print("TourRepository operations successful.")

    # Test TTS Repo
    tts_id = tts_repo.save_audio_path("hash123", "/path/to/audio.mp3")
    path = tts_repo.get_audio_path("hash123")
    assert path == "/path/to/audio.mp3"
    print("TTSRepository operations successful.")

    # Cleanup
    import shutil
    if os.path.exists("test_db.json"):
        os.remove("test_db.json")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
