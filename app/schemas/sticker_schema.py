from pydantic import BaseModel, ConfigDict, Field

class StickerBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    module: str = Field(..., pattern="^(children|dentist)$")
    image_url: str
    unlock_condition: str = Field(..., min_length=3, max_length=100)
    order: int = Field(default=0, ge=0)
    is_active: bool = True

class StickerCreate(StickerBase):
    pass

class StickerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    module: str | None = Field(default=None, pattern="^(children|dentist)$")
    image_url: str | None = None
    unlock_condition: str | None = Field(default=None, min_length=3, max_length=100)
    order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Dente campeão"
            }
        }
    )

class StickerResponse(StickerBase):
    id: str