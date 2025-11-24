"""
SQLite database connection and schema management for Interview Practice Partner.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


class Database:
    """Manages SQLite database connection and schema initialization."""
    
    def __init__(self, db_path: str = "interview_practice.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file and initialize schema if it doesn't exist."""
        db_file = Path(self.db_path)
        is_new = not db_file.exists()
        
        if is_new:
            self.initialize_schema()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def initialize_schema(self):
        """Create database tables if they don't exist."""
        schema = """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            mode TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            current_question_index INTEGER DEFAULT 0,
            followup_count INTEGER DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        );
        
        CREATE TABLE IF NOT EXISTS feedback (
            session_id TEXT PRIMARY KEY,
            communication_score INTEGER NOT NULL,
            technical_score INTEGER NOT NULL,
            structure_score INTEGER NOT NULL,
            strengths TEXT NOT NULL,
            improvements TEXT NOT NULL,
            overall_feedback TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id);
        
        CREATE INDEX IF NOT EXISTS idx_sessions_status 
            ON sessions(status);
        
        CREATE INDEX IF NOT EXISTS idx_sessions_created 
            ON sessions(created_at);
        """
        
        with self.get_connection() as conn:
            conn.executescript(schema)
    
    def reset_database(self):
        """Drop all tables and recreate schema. Use with caution!"""
        drop_schema = """
        DROP TABLE IF EXISTS feedback;
        DROP TABLE IF EXISTS messages;
        DROP TABLE IF EXISTS sessions;
        """
        
        with self.get_connection() as conn:
            conn.executescript(drop_schema)
        
        self.initialize_schema()
