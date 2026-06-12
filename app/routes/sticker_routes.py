from fastapi import APIRouter, Depends, status
from pymongo.asynchronous.database import AsyncDatabase

from app.database.mongodb import get_database
from app.schemas.sticker_schema import StickerCreate, StickerResponse, StickerUpdate
from app.services.sticker_service import StickerService

router = APIRouter(
    prefix="/stickers",
    tags=["Stickers"],
)


def get_sticker_service(
    database: AsyncDatabase = Depends(get_database),
) -> StickerService:
    return StickerService(database)


@router.post(
    "",
    response_model=StickerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sticker(
    sticker_data: StickerCreate,
    service: StickerService = Depends(get_sticker_service),
):
    return await service.create_sticker(sticker_data)


@router.get(
    "",
    response_model=list[StickerResponse],
)
async def get_all_stickers(
    service: StickerService = Depends(get_sticker_service),
):
    return await service.get_all_stickers()


@router.get(
    "/module/{module}",
    response_model=list[StickerResponse],
)
async def get_stickers_by_module(
    module: str,
    service: StickerService = Depends(get_sticker_service),
):
    return await service.get_stickers_by_module(module)


@router.get(
    "/{sticker_id}",
    response_model=StickerResponse,
)
async def get_sticker_by_id(
    sticker_id: str,
    service: StickerService = Depends(get_sticker_service),
):
    return await service.get_sticker_by_id(sticker_id)


@router.patch(
    "/{sticker_id}",
    response_model=StickerResponse,
)
async def update_sticker(
    sticker_id: str,
    sticker_data: StickerUpdate,
    service: StickerService = Depends(get_sticker_service),
):
    return await service.update_sticker(sticker_id, sticker_data)


@router.delete(
    "/{sticker_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_sticker(
    sticker_id: str,
    service: StickerService = Depends(get_sticker_service),
):
    return await service.delete_sticker(sticker_id)