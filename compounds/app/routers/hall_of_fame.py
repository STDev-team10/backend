from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import current_user
from ..schemas.hall_of_fame import HallOfFameListResponse, HallOfFameUnlockResponse
from ..services import hall_of_fame_service

router = APIRouter(prefix="/api/hall-of-fame", tags=["hall-of-fame"])


@router.get("", response_model=HallOfFameListResponse)
def list_hall_of_fame() -> HallOfFameListResponse:
    return hall_of_fame_service.list_items()


@router.post("/{item_id}/unlock", response_model=HallOfFameUnlockResponse)
def unlock_item(item_id: str, user: dict = Depends(current_user)) -> HallOfFameUnlockResponse:
    result = hall_of_fame_service.unlock_item(
        item_id=item_id,
        user_id=int(user["sub"]),
        username=str(user["username"]),
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return HallOfFameUnlockResponse(item_id=item_id, unlocked=result)
