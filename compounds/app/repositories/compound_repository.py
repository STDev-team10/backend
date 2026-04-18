import json
from typing import Any

from ..database import get_conn


def _normalize_available_elements(compound: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(compound)
    required_elements = [str(symbol) for symbol in normalized["elements"].keys()]
    existing_elements = [str(symbol) for symbol in normalized["available_elements"]]

    seen: set[str] = set()
    merged: list[str] = []
    for symbol in [*existing_elements, *required_elements]:
        if symbol in seen:
            continue
        seen.add(symbol)
        merged.append(symbol)

    normalized["available_elements"] = merged
    return normalized


def _serialize(compound: dict[str, Any]) -> tuple[Any, ...]:
    normalized = _normalize_available_elements(compound)
    return (
        normalized["id"],
        normalized["name"],
        normalized["formula"],
        normalized["emoji"],
        normalized["description"],
        normalized["difficulty"],
        json.dumps(normalized["elements"], ensure_ascii=False, sort_keys=True),
        json.dumps(normalized["available_elements"], ensure_ascii=False),
    )


def _deserialize(row: Any) -> dict[str, Any]:
    return _normalize_available_elements({
        "id": row["id"],
        "name": row["name"],
        "formula": row["formula"],
        "emoji": row["emoji"],
        "description": row["description"],
        "difficulty": row["difficulty"],
        "elements": json.loads(row["elements_json"]),
        "available_elements": json.loads(row["available_elements_json"]),
    })


def count_compounds() -> int:
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM compounds").fetchone()
    return int(row["count"])


def list_compounds(difficulty: str | None = None) -> list[dict[str, Any]]:
    query = "SELECT * FROM compounds"
    params: tuple[Any, ...] = ()

    if difficulty:
        query += " WHERE difficulty = ?"
        params = (difficulty,)

    query += " ORDER BY name"

    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()

    return [_deserialize(row) for row in rows]


def get_compound_by_id(compound_id: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM compounds WHERE id = ?", (compound_id,)).fetchone()
    if not row:
        return None
    return _deserialize(row)


def upsert_compounds(compounds: list[dict[str, Any]]) -> int:
    with get_conn() as conn:
        conn.executemany(
            """
            INSERT INTO compounds (
                id, name, formula, emoji, description, difficulty, elements_json, available_elements_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                formula = excluded.formula,
                emoji = excluded.emoji,
                description = excluded.description,
                difficulty = excluded.difficulty,
                elements_json = excluded.elements_json,
                available_elements_json = excluded.available_elements_json,
                updated_at = datetime('now')
            """,
            [_serialize(compound) for compound in compounds],
        )
    return len(compounds)


def create_compound(compound: dict[str, Any]) -> dict[str, Any]:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO compounds (
                id, name, formula, emoji, description, difficulty, elements_json, available_elements_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            _serialize(compound),
        )
    return get_compound_by_id(compound["id"])


def update_compound(compound_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    current = get_compound_by_id(compound_id)
    if not current:
        return None

    merged = _normalize_available_elements({**current, **updates, "id": compound_id})

    with get_conn() as conn:
        conn.execute(
            """
            UPDATE compounds
            SET name = ?, formula = ?, emoji = ?, description = ?, difficulty = ?,
                elements_json = ?, available_elements_json = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                merged["name"],
                merged["formula"],
                merged["emoji"],
                merged["description"],
                merged["difficulty"],
                json.dumps(merged["elements"], ensure_ascii=False, sort_keys=True),
                json.dumps(merged["available_elements"], ensure_ascii=False),
                compound_id,
            ),
        )
    return get_compound_by_id(compound_id)


def list_unlocked_compound_ids(user_id: int) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT compound_id
            FROM user_compound_unlocks
            WHERE user_id = ?
            ORDER BY unlocked_at, compound_id
            """,
            (user_id,),
        ).fetchall()
    return [str(row["compound_id"]) for row in rows]


def unlock_compound_for_user(user_id: int, compound_id: str) -> bool | None:
    compound = get_compound_by_id(compound_id)
    if not compound:
        return None

    with get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO user_compound_unlocks (user_id, compound_id)
            VALUES (?, ?)
            """,
            (user_id, compound_id),
        )
    return cursor.rowcount > 0


def create_time_attack_record(user_id: int, username: str, play_mode: str, difficulty: str, clear_time_ms: int) -> int:
    with get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO time_attack_records (user_id, username, play_mode, difficulty, clear_time_ms)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, username, play_mode, difficulty, clear_time_ms),
        )
    return int(cursor.lastrowid)


def _time_attack_leaderboard_cte() -> str:
    return """
        WITH ranked AS (
            SELECT
                id,
                user_id,
                username,
                play_mode,
                difficulty,
                clear_time_ms,
                cleared_at,
                ROW_NUMBER() OVER (
                    PARTITION BY user_id, play_mode, difficulty
                    ORDER BY clear_time_ms ASC, cleared_at ASC, id ASC
                ) AS user_best_order
            FROM time_attack_records
            WHERE play_mode = ? AND difficulty = ?
        ),
        best_per_user AS (
            SELECT
                id,
                user_id,
                username,
                play_mode,
                difficulty,
                clear_time_ms,
                cleared_at
            FROM ranked
            WHERE user_best_order = 1
        ),
        leaderboard AS (
            SELECT
                id,
                user_id,
                username,
                play_mode,
                difficulty,
                clear_time_ms,
                cleared_at,
                ROW_NUMBER() OVER (
                    ORDER BY clear_time_ms ASC, cleared_at ASC, user_id ASC
                ) AS rank
            FROM best_per_user
        )
    """


def list_time_attack_rankings(play_mode: str, difficulty: str, limit: int) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            {_time_attack_leaderboard_cte()}
            SELECT *
            FROM leaderboard
            ORDER BY rank
            LIMIT ?
            """,
            (play_mode, difficulty, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_time_attack_personal_best(user_id: int, play_mode: str, difficulty: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            f"""
            {_time_attack_leaderboard_cte()}
            SELECT *
            FROM leaderboard
            WHERE user_id = ?
            """,
            (play_mode, difficulty, user_id),
        ).fetchone()
    return dict(row) if row else None


def count_time_attack_rankings(play_mode: str, difficulty: str) -> int:
    with get_conn() as conn:
        row = conn.execute(
            f"""
            {_time_attack_leaderboard_cte()}
            SELECT COUNT(*) AS count
            FROM leaderboard
            """,
            (play_mode, difficulty),
        ).fetchone()
    return int(row["count"])
