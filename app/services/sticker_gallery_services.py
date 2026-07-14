from fastapi import HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.repositories.sticker_gallery_repository import StickerGalleryRepository


class StickerGalleryService:
    def __init__(self, database: AsyncDatabase):
        self.repository = StickerGalleryRepository(database)

    async def complete_video_and_unlock_stickers(
        self,
        child_id: str,
        video_id: str,
    ) -> dict:
        video = await self.repository.find_video_by_id(video_id)

        if video is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vídeo não encontrado.",
            )

        already_completed = await self.repository.was_video_completed(
            child_id=child_id,
            video_id=video_id,
        )

        earned_stickers = []

        if not already_completed:
            await self.repository.mark_video_as_completed(
                child_id=child_id,
                video=video,
            )

            video_sticker = await self.repository.find_sticker_for_video(video_id)

            if video_sticker:
                earned_video_sticker = await self.repository.award_sticker(
                    child_id=child_id,
                    sticker=video_sticker,
                    earned_reason="finish_video",
                    earned_from_video_id=video["_id"],
                )

                if earned_video_sticker:
                    earned_stickers.append(earned_video_sticker)

        last_module_video = await self.repository.find_last_active_video_by_module(
            video["module"]
        )

        module_completed = (
            last_module_video is not None
            and video.get("order", 0) >= last_module_video.get("order", 0)
        )

        if module_completed:
            special_sticker = await self.repository.find_special_sticker_for_module(
                video["module"]
            )

            if special_sticker:
                earned_special_sticker = await self.repository.award_sticker(
                    child_id=child_id,
                    sticker=special_sticker,
                    earned_reason="finish_module",
                    earned_from_video_id=video["_id"],
                )

                if earned_special_sticker:
                    earned_stickers.append(earned_special_sticker)

        return {
            "message": "Progresso registrado com sucesso.",
            "already_completed": already_completed,
            "module_completed": module_completed,
            "earned_stickers": earned_stickers,
        }

    async def get_child_sticker_gallery(self, child_id: str) -> list[dict]:
        return await self.repository.find_child_stickers(child_id)
    
    async def get_child_completed_videos(self, child_id: str) -> list[dict]:
        return await self.repository.find_child_completed_videos(child_id)
