from typing import Optional
from tinydb import Query
from .database_base import DatabaseBase

class TTSRepository:
    def __init__(self, db_base: DatabaseBase):
        self.db = db_base.get_db()
        self.table = self.db.table('tts_cache')

    def get_audio_path(self, text_hash: str) -> Optional[str]:
        """
        Retrieve the file path for a given text hash.
        """
        TTS = Query()
        result = self.table.search(TTS.text_hash == text_hash)
        if result:
            return result[0].get('file_path')
        return None

    def save_audio_path(self, text_hash: str, file_path: str) -> int:
        """
        Save the mapping of text hash to audio file path.
        Returns the inserted document ID.
        """
        # Check if it already exists to avoid duplicates
        TTS = Query()
        existing = self.table.search(TTS.text_hash == text_hash)
        if existing:
            self.table.update({'file_path': file_path}, doc_ids=[existing[0].doc_id])
            return existing[0].doc_id
        
        return self.table.insert({
            'text_hash': text_hash,
            'file_path': file_path
        })
