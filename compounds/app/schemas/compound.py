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
