from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class BrushingGoalCheckUpdate(BaseModel):
    day: str = Field(..., examples=["Seg"])
    shift: str = Field(..., examples=["morning"])
    checked: bool = Field(..., examples=[True])


class WeeklyBrushingGoalResponse(BaseModel):
    id: str
    child_id: str
    week_start_date: date
    week_end_date: date
    checks: dict[str, bool]
    total_completed: int
    total_goal: int
    is_completed: bool
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class EarnedBrushingGoalStickerResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    module: str
    image_url: str
    unlock_condition: str
    video_id: str | None = None
    is_special: bool
    order: int | None = None
    is_active: bool
    earned_at: datetime
    earned_reason: str
    earned_from_video_id: str | None = None


class BrushingGoalCompleteResponse(BaseModel):
    completed: bool
    message: str
    earned_stickers: list[EarnedBrushingGoalStickerResponse] = []
    goal: WeeklyBrushingGoalResponse | None = None