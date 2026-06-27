from datetime import datetime, timezone

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase


class StickerGalleryRepository:
    def __init__(self, database: AsyncDatabase):
        self.videos_collection = database["videos"]
        self.stickers_collection = database["stickers"]
        self.completed_videos_collection = database["completed_videos"]
        self.child_stickers_collection = database["child_stickers"]

    @staticmethod
    def _serialize_earned_sticker(sticker: dict, earned_sticker: dict) -> dict:
        earned_at = earned_sticker.get("earned_at")

        return {
            "id": str(sticker["_id"]),
            "name": sticker["name"],
            "description": sticker.get("description"),
            "module": sticker["module"],
            "image_url": sticker["image_url"],
            "unlock_condition": sticker["unlock_condition"],
            "video_id": sticker.get("video_id"),
            "is_special": sticker.get("is_special", False),
            "earned_at": earned_at.isoformat() if earned_at else "",
            "earned_reason": earned_sticker.get("earned_reason", ""),
            "earned_from_video_id": (
                str(earned_sticker["earned_from_video_id"])
                if earned_sticker.get("earned_from_video_id")
                else None
            ),
        }

    async def find_video_by_id(self, video_id: str) -> dict | None:
        if not ObjectId.is_valid(video_id):
            return None

        return await self.videos_collection.find_one(
            {
                "_id": ObjectId(video_id),
                "is_active": True,
            }
        )

    async def was_video_completed(self, child_id: str, video_id: str) -> bool:
        if not ObjectId.is_valid(video_id):
            return False

        completed_video = await self.completed_videos_collection.find_one(
            {
                "child_id": child_id,
                "video_id": ObjectId(video_id),
            }
        )

        return completed_video is not None

    async def mark_video_as_completed(self, child_id: str, video: dict) -> None:
        await self.completed_videos_collection.insert_one(
            {
                "child_id": child_id,
                "video_id": video["_id"],
                "module": video["module"],
                "completed_at": datetime.now(timezone.utc),
            }
        )

    @staticmethod
    def serialize_completed_video(video: dict, completed_video: dict) -> dict:
        completed_at = completed_video.get("completed_at")

        return {
            "id": str(video["_id"]),
            "title": video["title"],
            "description": video.get("description"),
            "module": video["module"],
            "video_url": video["video_url"],
            "thumbnail_url": video.get("thumbnail_url"),
            "order": video.get("order", 0),
            "is_active": video.get("is_active", True),
            "completed_at": completed_at.isoformat() if completed_at else "",
        }

    async def find_child_completed_videos(self, child_id: str) -> list[dict]:
        cursor = self.completed_videos_collection.find(
            {
                "child_id": child_id,
            }
        ).sort("completed_at", -1)

        completed_videos = await cursor.to_list(length=200)
        result = []

        for completed_video in completed_videos:
            video_id = completed_video.get("video_id")

            if isinstance(video_id, str):
                if not ObjectId.is_valid(video_id):
                    continue
                video_object_id = ObjectId(video_id)
            else:
                video_object_id = video_id

            video = await self.videos_collection.find_one(
                {
                    "_id": video_object_id,
                }
            )

            if video:
                result.append(
                    self.serialize_completed_video(
                        video=video,
                        completed_video=completed_video,
                    )
                )

        return result

    async def find_sticker_for_video(self, video_id: str) -> dict | None:
        return await self.stickers_collection.find_one(
            {
                "video_id": video_id,
                "unlock_condition": "finish_video",
                "is_active": True,
            }
        )

    async def count_active_videos_by_module(self, module: str) -> int:
        return await self.videos_collection.count_documents(
            {
                "module": module,
                "is_active": True,
            }
        )

    async def count_completed_videos_by_module(
        self,
        child_id: str,
        module: str,
    ) -> int:
        return await self.completed_videos_collection.count_documents(
            {
                "child_id": child_id,
                "module": module,
            }
        )

    async def find_special_sticker_for_module(self, module: str) -> dict | None:
        return await self.stickers_collection.find_one(
            {
                "module": module,
                "unlock_condition": "finish_module",
                "is_special": True,
                "is_active": True,
            }
        )

    async def child_already_has_sticker(
        self,
        child_id: str,
        sticker_id: ObjectId,
    ) -> bool:
        earned_sticker = await self.child_stickers_collection.find_one(
            {
                "child_id": child_id,
                "sticker_id": sticker_id,
            }
        )

        return earned_sticker is not None

    async def award_sticker(
        self,
        child_id: str,
        sticker: dict,
        earned_reason: str,
        earned_from_video_id: ObjectId | None = None,
    ) -> dict | None:
        already_has_sticker = await self.child_already_has_sticker(
            child_id=child_id,
            sticker_id=sticker["_id"],
        )

        if already_has_sticker:
            return None

        earned_sticker = {
            "child_id": child_id,
            "sticker_id": sticker["_id"],
            "earned_reason": earned_reason,
            "earned_from_video_id": earned_from_video_id,
            "earned_at": datetime.now(timezone.utc),
        }

        await self.child_stickers_collection.insert_one(earned_sticker)

        return self._serialize_earned_sticker(sticker, earned_sticker)

    async def find_child_stickers(self, child_id: str) -> list[dict]:
        cursor = self.child_stickers_collection.find(
            {
                "child_id": child_id,
            }
        ).sort("earned_at", 1)

        earned_stickers = await cursor.to_list(length=200)

        result = []

        for earned_sticker in earned_stickers:
            sticker = await self.stickers_collection.find_one(
                {
                    "_id": earned_sticker["sticker_id"],
                    "is_active": True,
                }
            )

            if sticker:
                result.append(
                    self._serialize_earned_sticker(
                        sticker=sticker,
                        earned_sticker=earned_sticker,
                    )
                )

        return result
