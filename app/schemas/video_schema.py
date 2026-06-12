from pydantic import BaseModel, Field

class VideoBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    module: str = Field(..., pattern="^(children|dentist)$")
    category: str = Field(..., min_length=2, max_length=50)
    video_url: str
    thumbnail: str | None = None
    order: int = Field(default=0, ge=0)
    is_active: bool = True
    
class VideoCreate(VideoBase):
    pass

class VideoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    module: str | None = Field(default=None, pattern="^(children|dentist)$")
    category: str | None = Field(default=None, min_length=2, max_length=50)
    video_url: str | None = None
    thumbnail_url: str | None = None
    order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    
class VideoResponse(VideoBase):
    id: str
    
