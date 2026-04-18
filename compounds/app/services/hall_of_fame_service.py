from ..repositories import hall_of_fame_repository
from ..schemas.hall_of_fame import HallOfFameItem, HallOfFameListResponse


def list_items() -> HallOfFameListResponse:
    items = hall_of_fame_repository.list_items_with_discoverers()
    return HallOfFameListResponse(items=[HallOfFameItem(**item) for item in items])


def unlock_item(item_id: str, user_id: int, username: str) -> bool | None:
    if not hall_of_fame_repository.get_item_by_id(item_id):
        return None
    return hall_of_fame_repository.unlock_item_for_user(item_id, user_id, username)
