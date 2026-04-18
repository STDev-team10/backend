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


_HALL_OF_FAME_ITEMS = [
    ("guigeumseok", "귀금속", "빛나는 금속의 가치", "guigeumseok.png"),
    ("dynamite", "다이너마이트", "폭발의 과학", "dynamite.png"),
    ("radium", "라듐", "방사성 원소의 발견", "radium.png"),
    ("lax", "락스", "강력한 세정의 화학", "lax.png"),
    ("biso", "비소", "독성의 원소", "biso.png"),
    ("salchungje", "살충제", "해충을 막는 화학", "salchungje.png"),
    ("seokmyeon", "석면", "금지된 광물", "seokmyeon.png"),
    ("alcohol", "알콜", "발효와 증류의 산물", "alcohol.png"),
    ("sueun", "수은", "액체 금속의 비밀", "sueun.png"),
    ("haber", "하버", "공기에서 빵을, 그리고 독가스를", "haber.png"),
]


def _seed_hall_of_fame_items(conn: sqlite3.Connection) -> None:
    conn.executemany(
        """
        INSERT INTO hall_of_fame_items (id, title, subtitle, image_filename)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            subtitle = excluded.subtitle,
            image_filename = excluded.image_filename
        """,
        _HALL_OF_FAME_ITEMS,
    )


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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hall_of_fame_items (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                subtitle TEXT NOT NULL DEFAULT '',
                image_filename TEXT NOT NULL DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hall_of_fame_unlocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL REFERENCES hall_of_fame_items(id),
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                unlocked_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(item_id, user_id)
            )
        """)
        # migration: add hall_of_fame_item_id to compounds if not exists
        existing = {row[1] for row in conn.execute("PRAGMA table_info(compounds)")}
        if "hall_of_fame_item_id" not in existing:
            conn.execute("ALTER TABLE compounds ADD COLUMN hall_of_fame_item_id TEXT")
        _seed_hall_of_fame_items(conn)
