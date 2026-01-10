import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database_base import DatabaseBase
from database.tour import TourRepository

def test_db_read():
    db_path = "database/db.json"
    print(f"Checking DB at: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ DB File not found!")
        return

    db_base = DatabaseBase(db_path)
    repo = TourRepository(db_base)
    
    target_id = "59063a1b-efad-4b2e-a0df-16c443930924"
    print(f"Searching for ID: {target_id}")
    
    result = repo.get_tour_by_uuid(target_id)
    
    if result:
        print("✅ Found Tour!")
        print(f"Theme: {result.get('theme')}")
    else:
        print("❌ Tour NOT FOUND in DB via Repository.")
        
        # List all IDs
        print("Listing all IDs in DB:")
        all_tours = repo.tours_table.all()
        for t in all_tours:
            print(f" - {t.get('id')}")

if __name__ == "__main__":
    test_db_read()
