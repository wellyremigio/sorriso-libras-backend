from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.video_schema import VideoCreate, VideoUpdate

class VideoRepository:
    def __init__(self, database: AsyncDatabase):
        self.collection = database["videos"]

    @staticmethod
    def _serialize_video(video: dict) -> dict:
        return {
            "id": str(video["_id"]),
            "title": video["title"],
            "description": video.get("description"),
            "module": video["module"],
            "category": video["category"],
            "video_url": video["video_url"],
            "thumbnail_url": video.get("thumbnail_url"),
            "order": video.get("order", 0),
            "is_active": video.get("is_active", True),
        }

    async def create(self, video_data: VideoCreate) -> dict:
        video_dict = video_data.model_dump()

        result = await self.collection.insert_one(video_dict)

        created_video = await self.collection.find_one(
            {"_id": result.inserted_id}
        )
        assert created_video is not None, "Failed to retrieve inserted video"

        return self._serialize_video(created_video)

    async def find_all(self) -> list[dict]:
        cursor = self.collection.find({"is_active": True}).sort("order", 1)
        videos = await cursor.to_list(length=100)

        return [self._serialize_video(video) for video in videos]

    async def find_by_id(self, video_id: str) -> dict | None:
        if not ObjectId.is_valid(video_id):
            return None

        video = await self.collection.find_one(
            {
                "_id": ObjectId(video_id),
                "is_active": True,
            }
        )

        if video is None:
            return None

        return self._serialize_video(video)

    async def find_by_module(self, module: str) -> list[dict]:
        cursor = self.collection.find(
            {
                "module": module,
                "is_active": True,
            }
        ).sort("order", 1)

        videos = await cursor.to_list(length=100)

        return [self._serialize_video(video) for video in videos]

    async def update(self, video_id: str, video_data: VideoUpdate) -> dict | None:
        if not ObjectId.is_valid(video_id):
            return None

        update_data = video_data.model_dump(
            exclude_unset=True,
            exclude_none=True
            )

        if not update_data:
            return await self.find_by_id(video_id)

        await self.collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": update_data},
        )

        updated_video = await self.collection.find_one(
            {"_id": ObjectId(video_id)}
        )

        if updated_video is None:
            return None

        return self._serialize_video(updated_video)

    async def deactivate(self, video_id: str) -> bool:
        if not ObjectId.is_valid(video_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {"is_active": False}},
        )

        return result.modified_count > 0