from fastapi import APIRouter, Depends, status
from pymongo.asynchronous.database import AsyncDatabase

from app.database.mongodb import get_database
from app.schemas.video_schema import VideoCreate, VideoResponse, VideoUpdate
from app.services.video_services import VideoService

router = APIRouter(
    prefix="/videos",
    tags=["Videos"],
)

def get_video_service(
    database: AsyncDatabase = Depends(get_database),
) -> VideoService:
    return VideoService(database)


@router.post(
    "",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_video(
    video_data: VideoCreate,
    service: VideoService = Depends(get_video_service),
):
    return await service.create_video(video_data)


@router.get(
    "",
    response_model=list[VideoResponse],
)
async def get_all_videos(
    service: VideoService = Depends(get_video_service),
):
    return await service.get_all_videos()


@router.get(
    "/module/{module}",
    response_model=list[VideoResponse],
)
async def get_videos_by_module(
    module: str,
    service: VideoService = Depends(get_video_service),
):
    return await service.get_videos_by_module(module)


@router.get(
    "/{video_id}",
    response_model=VideoResponse,
)
async def get_video_by_id(
    video_id: str,
    service: VideoService = Depends(get_video_service),
):
    return await service.get_video_by_id(video_id)


@router.patch(
    "/{video_id}",
    response_model=VideoResponse,
)
async def update_video(
    video_id: str,
    video_data: VideoUpdate,
    service: VideoService = Depends(get_video_service),
):
    return await service.update_video(video_id, video_data)


@router.delete(
    "/{video_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_video(
    video_id: str,
    service: VideoService = Depends(get_video_service),
):
    return await service.delete_video(video_id)