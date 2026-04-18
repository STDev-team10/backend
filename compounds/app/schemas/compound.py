from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CompoundBase(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    formula: str = Field(min_length=1)
    emoji: str = Field(min_length=1)
    description: str = Field(min_length=1)
    difficulty: str = Field(min_length=1)
    elements: dict[str, int]
    available_elements: list[str]


class CompoundCreate(CompoundBase):
    pass


class CompoundPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    formula: str | None = None
    emoji: str | None = None
    description: str | None = None
    difficulty: str | None = None
    elements: dict[str, int] | None = None
    available_elements: list[str] | None = None


class CompoundDetail(CompoundBase):
    pass


class CompoundListResponse(BaseModel):
    items: list[CompoundDetail]
    total: int


class CompoundSeedResponse(BaseModel):
    imported: int


class CompoundUnlockResponse(BaseModel):
    compound_id: str
    unlocked: bool


class CompoundUnlockListResponse(BaseModel):
    items: list[str]
    total: int


PlayMode = Literal["normal", "hardcore"]
Difficulty = Literal["easy", "medium", "hard", "mimic"]


class TimeAttackRecordCreate(BaseModel):
    play_mode: PlayMode
    difficulty: Difficulty
    clear_time_ms: int = Field(gt=0)


class TimeAttackRecordResponse(BaseModel):
    record_id: int
    play_mode: PlayMode
    difficulty: Difficulty
    clear_time_ms: int
    rank: int
    is_personal_best: bool


class TimeAttackRankingEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    play_mode: PlayMode
    difficulty: Difficulty
    clear_time_ms: int
    cleared_at: str


class TimeAttackRankingListResponse(BaseModel):
    items: list[TimeAttackRankingEntry]
    total: int


class TimeAttackPersonalBestResponse(BaseModel):
    item: TimeAttackRankingEntry | None


class TimeAttackLeaderboardResponse(BaseModel):
    items: list[TimeAttackRankingEntry]
    total: int
    my_item: TimeAttackRankingEntry | None
