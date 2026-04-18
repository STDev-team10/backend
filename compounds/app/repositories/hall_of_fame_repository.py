from ..database import get_conn


def list_items_with_discoverers() -> list[dict]:
    with get_conn() as conn:
        items = conn.execute(
            "SELECT id, title, subtitle, image_filename FROM hall_of_fame_items ORDER BY id"
        ).fetchall()

        result = []
        for item in items:
            unlocks = conn.execute(
                """
                SELECT username, unlocked_at
                FROM hall_of_fame_unlocks
                WHERE item_id = ?
                ORDER BY unlocked_at
                """,
                (item["id"],),
            ).fetchall()

            discoverers = [row["username"] for row in unlocks]
            first_discovered_at = unlocks[0]["unlocked_at"] if unlocks else None

            result.append({
                "id": item["id"],
                "title": item["title"],
                "subtitle": item["subtitle"],
                "image_filename": item["image_filename"],
                "discoverers": discoverers,
                "first_discovered_at": first_discovered_at,
            })

    return result


def get_item_by_id(item_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM hall_of_fame_items WHERE id = ?", (item_id,)
        ).fetchone()
    return dict(row) if row else None


def unlock_item_for_user(item_id: str, user_id: int, username: str) -> bool:
    with get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO hall_of_fame_unlocks (item_id, user_id, username)
            VALUES (?, ?, ?)
            """,
            (item_id, user_id, username),
        )
    return cursor.rowcount > 0
