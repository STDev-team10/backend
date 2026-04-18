import os
import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    db_path = os.getenv("DATABASE_PATH")
    if db_path:
        return Path(db_path)
    return Path(__file__).parent.parent / "data.db"


def get_conn() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compounds (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                formula TEXT NOT NULL,
                emoji TEXT NOT NULL,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                elements_json TEXT NOT NULL,
                available_elements_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_compound_unlocks (
                user_id INTEGER NOT NULL,
                compound_id TEXT NOT NULL,
                unlocked_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, compound_id),
                FOREIGN KEY (compound_id) REFERENCES compounds (id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS time_attack_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                play_mode TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                clear_time_ms INTEGER NOT NULL,
                cleared_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
