from typing import List, Optional, Dict, Any, cast
from tinydb import Query
from database.database_base import DatabaseBase

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
        doc = self.table.get(doc_id=tour_id)
        if doc is None:
            return None
        # Document is a dict subclass, cast to Dict for type checker
        return cast(Dict[str, Any], doc)

    def get_tour_by_uuid(self, tour_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get a tour by its UUID.
        """
        Tour = Query()
        results = self.table.search(Tour.id == tour_uuid)
        if not results:
            return None
        # Return the first matching tour
        return cast(Dict[str, Any], results[0])

    def list_tours(self) -> List[Dict[str, Any]]:
        """
        List all tours in the database.
        """
        # Document is a dict subclass, cast to Dict for type checker
        return [cast(Dict[str, Any], doc) for doc in self.table.all()]
    
    def update_tour(self, tour_id: int, updates: Dict[str, Any]) -> None:
        """
        Update a tour by its ID.
        """
        self.table.update(updates, doc_ids=[tour_id])

    def update_tour_by_uuid(self, tour_uuid: str, updates: Dict[str, Any]) -> bool:
        """
        Update a tour by its UUID.
        Returns True if updated, False if tour not found.
        """
        Tour = Query()
        results = self.table.search(Tour.id == tour_uuid)
        if not results:
            return False
        # Update using the document ID
        doc_id = results[0].doc_id
        self.table.update(updates, doc_ids=[doc_id])
        return True
