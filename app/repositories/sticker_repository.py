from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.sticker_schema import StickerCreate, StickerUpdate


class StickerRepository:
    def __init__(self, database: AsyncDatabase):
        self.collection = database["stickers"]

    @staticmethod
    def _serialize_sticker(sticker: dict) -> dict:
        return {
            "id": str(sticker["_id"]),
            "name": sticker["name"],
            "description": sticker.get("description"),
            "module": sticker["module"],
            "image_url": sticker["image_url"],
            "unlock_condition": sticker["unlock_condition"],
            "video_id": sticker.get("video_id"),
            "is_special": sticker.get("is_special", False),
            "order": sticker.get("order", 0),
            "is_active": sticker.get("is_active", True),
        }

    async def create(self, sticker_data: StickerCreate) -> dict:
        sticker_dict = sticker_data.model_dump()

        result = await self.collection.insert_one(sticker_dict)

        created_sticker = await self.collection.find_one({"_id": result.inserted_id})

        assert created_sticker is not None, "Failed to retrieve inserted video"

        return self._serialize_sticker(created_sticker)

    async def find_all(self) -> list[dict]:
        cursor = self.collection.find({"is_active": True}).sort("order", 1)
        stickers = await cursor.to_list(length=100)

        return [self._serialize_sticker(sticker) for sticker in stickers]

    async def find_by_id(self, sticker_id: str) -> dict | None:
        if not ObjectId.is_valid(sticker_id):
            return None

        sticker = await self.collection.find_one(
            {
                "_id": ObjectId(sticker_id),
                "is_active": True,
            }
        )

        if sticker is None:
            return None

        return self._serialize_sticker(sticker)

    async def find_by_module(self, module: str) -> list[dict]:
        cursor = self.collection.find(
            {
                "module": module,
                "is_active": True,
            }
        ).sort("order", 1)

        stickers = await cursor.to_list(length=100)

        return [self._serialize_sticker(sticker) for sticker in stickers]

    async def update(
        self,
        sticker_id: str,
        sticker_data: StickerUpdate,
    ) -> dict | None:
        if not ObjectId.is_valid(sticker_id):
            return None

        update_data = sticker_data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if not update_data:
            return await self.find_by_id(sticker_id)

        await self.collection.update_one(
            {"_id": ObjectId(sticker_id)},
            {"$set": update_data},
        )

        updated_sticker = await self.collection.find_one({"_id": ObjectId(sticker_id)})

        if updated_sticker is None:
            return None

        return self._serialize_sticker(updated_sticker)

    async def deactivate(self, sticker_id: str) -> bool:
        if not ObjectId.is_valid(sticker_id):
            return False

        result = await self.collection.update_one(
            {"_id": ObjectId(sticker_id)},
            {"$set": {"is_active": False}},
        )

        return result.modified_count > 0
