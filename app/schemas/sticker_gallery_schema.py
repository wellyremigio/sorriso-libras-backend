from pydantic import BaseModel


class EarnedStickerResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    module: str
    image_url: str
    unlock_condition: str
    video_id: str | None = None
    is_special: bool = False
    earned_at: str
    earned_reason: str
    earned_from_video_id: str | None = None


class CompleteVideoResponse(BaseModel):
    message: str
    already_completed: bool
    module_completed: bool
    earned_stickers: list[EarnedStickerResponse]