from pydantic import BaseModel


class HallOfFameItem(BaseModel):
    id: str
    title: str
    subtitle: str
    image_filename: str
    discoverers: list[str]
    first_discovered_at: str | None


class HallOfFameListResponse(BaseModel):
    items: list[HallOfFameItem]


class HallOfFameUnlockResponse(BaseModel):
    item_id: str
    unlocked: bool
