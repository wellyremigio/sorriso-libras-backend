from pydantic import BaseModel, ConfigDict, Field

class StickerBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    module: str = Field(..., pattern="^(children|dentist)$")
    image_url: str
    unlock_condition: str = Field(..., min_length=3, max_length=100)
    video_id: str | None = None
    is_special: bool = False
    order: int = Field(default=0, ge=0)
    is_active: bool = True

class StickerCreate(StickerBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Dente campeão",
                "description": "Adesivo conquistado ao finalizar o vídeo de escovação.",
                "module": "children",
                "image_url": "https://url-do-cloudflare/stickers/dente-campeao.png",
                "unlock_condition": "finish_video",
                "video_id": "ID_DO_VIDEO_AQUI",
                "is_special": False,
                "order": 1,
                "is_active": True
            }
        }
    )
class StickerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    module: str | None = Field(default=None, pattern="^(children|dentist)$")
    image_url: str | None = None
    unlock_condition: str | None = Field(
        default=None,
        pattern="^(finish_video|finish_module)$"
    )
    video_id: str | None = None
    is_special: bool | None = None
    order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Dente campeão atualizado"
            }
        }
    )
class StickerResponse(StickerBase):
    id: str