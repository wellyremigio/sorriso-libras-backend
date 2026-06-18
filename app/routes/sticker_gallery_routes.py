from fastapi import APIRouter, Depends, status
from pymongo.asynchronous.database import AsyncDatabase

from app.database.mongodb import get_database
from app.schemas.sticker_gallery_schema import (
    CompleteVideoResponse,
    EarnedStickerResponse,
)
from app.services.sticker_gallery_services import StickerGalleryService

router = APIRouter(
    prefix="/children",
    tags=["Children Progress"],
)

def get_sticker_gallery_service(
    database: AsyncDatabase = Depends(get_database),
) -> StickerGalleryService:
    return StickerGalleryService(database)

@router.post(
    "/{child_id}/videos/{video_id}/complete",
    response_model=CompleteVideoResponse,
    status_code=status.HTTP_200_OK,
)
async def complete_video(
    child_id: str,
    video_id: str,
    service: StickerGalleryService = Depends(get_sticker_gallery_service),
):
    return await service.complete_video_and_unlock_stickers(
        child_id=child_id,
        video_id=video_id,
    )


@router.get(
    "/{child_id}/stickers",
    response_model=list[EarnedStickerResponse],
)
async def get_child_sticker_gallery(
    child_id: str,
    service: StickerGalleryService = Depends(get_sticker_gallery_service),
):
    return await service.get_child_sticker_gallery(child_id)