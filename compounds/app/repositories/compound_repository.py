import json
from typing import Any

from ..database import get_conn


def _serialize(compound: dict[str, Any]) -> tuple[Any, ...]:
    return (
        compound["id"],
        compound["name"],
        compound["formula"],
        compound["emoji"],
        compound["description"],
        compound["difficulty"],
        json.dumps(compound["elements"], ensure_ascii=False, sort_keys=True),
        json.dumps(compound["available_elements"], ensure_ascii=False),
    )


def _deserialize(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "formula": row["formula"],
        "emoji": row["emoji"],
        "description": row["description"],
        "difficulty": row["difficulty"],
        "elements": json.loads(row["elements_json"]),
        "available_elements": json.loads(row["available_elements_json"]),
    }


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

    merged = {**current, **updates, "id": compound_id}

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
