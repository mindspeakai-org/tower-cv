import sqlite3
import json
import os
from typing import Dict, Any

class EventLogger:
    """
    Logs contextual events to a local SQLite database for historical queries.
    """
    def __init__(self, db_path: str = "tower_events.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                object_id TEXT,
                description TEXT,
                payload JSON
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def log_event(self, event: Dict[str, Any]):
        """
        Inserts an event into the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (timestamp, event_type, object_id, description, payload)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            event.get("timestamp"),
            event.get("type"),
            event.get("object_id"),
            event.get("description"),
            json.dumps(event)
        ))
        
        conn.commit()
        conn.close()
