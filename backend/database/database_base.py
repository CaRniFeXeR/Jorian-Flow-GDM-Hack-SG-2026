from tinydb import TinyDB
import os

class DatabaseBase:
    def __init__(self, db_path: str = "db.json"):
        # Ensure the directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self.db = TinyDB(db_path)

    def get_db(self):
        return self.db
