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
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    UNIQUE NOT NULL,
                password   TEXT    NOT NULL,
                points     INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        columns = {
            str(row["name"])
            for row in conn.execute("PRAGMA table_info(users)").fetchall()
        }
        if "points" not in columns:
            conn.execute(
                "ALTER TABLE users ADD COLUMN points INTEGER NOT NULL DEFAULT 0"
            )
