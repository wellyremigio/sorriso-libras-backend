from fastapi import HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.repositories.video_repository import VideoRepository
from app.schemas.video_schema import VideoCreate, VideoUpdate

class VideoService:
    def __init__(self, database: AsyncDatabase):
        self.repository = VideoRepository(database)

    async def create_video(self, video_data: VideoCreate) -> dict:
        return await self.repository.create(video_data)

    async def get_all_videos(self) -> list[dict]:
        return await self.repository.find_all()

    async def get_video_by_id(self, video_id: str) -> dict:
        video = await self.repository.find_by_id(video_id)

        if video is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vídeo não encontrado.",
            )
        return video

    async def get_videos_by_module(self, module: str) -> list[dict]:
        if module not in ["children", "dentist"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Módulo inválido. Use 'children' ou 'dentist'.",
            )

        return await self.repository.find_by_module(module)

    async def update_video(self, video_id: str, video_data: VideoUpdate) -> dict:
        video = await self.repository.update(video_id, video_data)

        if video is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vídeo não encontrado.",
            )

        return video

    async def delete_video(self, video_id: str) -> dict:
        was_deleted = await self.repository.deactivate(video_id)

        if not was_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vídeo não encontrado.",
            )

        return {
            "message": "Vídeo removido com sucesso."
        }