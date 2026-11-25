import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).with_name("focus_data.db")

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                focus_score INTEGER NOT NULL,
                posture_events INTEGER NOT NULL,
                eye_alerts INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def save_session(self, duration, score, posture_events, eye_alerts):
        self.conn.execute(
            "INSERT INTO sessions (created_at, duration_seconds, focus_score, posture_events, eye_alerts) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), duration, score, posture_events, eye_alerts)
        )
        self.conn.commit()

    def get_sessions(self, limit=30):
        query = "SELECT created_at, duration_seconds, focus_score, posture_events, eye_alerts FROM sessions ORDER BY id DESC"
        if limit is not None:
            query += " LIMIT ?"
            cur = self.conn.execute(query, (limit,))
        else:
            cur = self.conn.execute(query)
        return cur.fetchall()
