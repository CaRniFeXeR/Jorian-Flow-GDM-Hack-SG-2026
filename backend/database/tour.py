from typing import List, Optional, Dict, Any
from tinydb import Query
from .database_base import DatabaseBase

class TourRepository:
    def __init__(self, db_base: DatabaseBase):
        self.db = db_base.get_db()
        self.table = self.db.table('tours')

    def add_tour(self, tour_data: Dict[str, Any]) -> int:
        """
        Add a new tour to the database.
        Returns the inserted document ID.
        """
        return self.table.insert(tour_data)

    def get_tour(self, tour_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a tour by its document ID.
        """
        return self.table.get(doc_id=tour_id)

    def list_tours(self) -> List[Dict[str, Any]]:
        """
        List all tours in the database.
        """
        return self.table.all()
    
    def update_tour(self, tour_id: int, updates: Dict[str, Any]) -> None:
        """
        Update a tour by its ID.
        """
        self.table.update(updates, doc_ids=[tour_id])
