from pydantic import BaseModel, Field, ConfigDict

class VideoBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    module: str = Field(..., pattern="^(children|dentist)$")
    video_url: str
    thumbnail_url: str | None = None
    order: int = Field(default=0, ge=0)
    is_active: bool = True
    
class VideoCreate(VideoBase):
    pass
class VideoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    module: str | None = Field(default=None, pattern="^(children|dentist)$")
    video_url: str | None = None
    thumbnail_url: str | None = None
    order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Novo título do vídeo"
            }
        }
    )
    
class VideoResponse(VideoBase):
    id: str
    
