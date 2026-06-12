from fastapi import HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase
from app.schemas.sticker_schema import StickerCreate, StickerUpdate
from app.repositories.sticker_repository import StickerRepository

class StickerService:
    def __init__(self, database: AsyncDatabase):
        self.repository = StickerRepository(database)

    async def create_sticker(self, sticker_data: StickerCreate) -> dict:
        return await self.repository.create(sticker_data)

    async def get_all_stickers(self) -> list[dict]:
        return await self.repository.find_all()

    async def get_sticker_by_id(self, sticker_id: str) -> dict:
        sticker = await self.repository.find_by_id(sticker_id)

        if sticker is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Adesivo não encontrado.",
            )

        return sticker

    async def get_stickers_by_module(self, module: str) -> list[dict]:
        if module not in ["children", "dentist"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Módulo inválido. Use 'children' ou 'dentist'.",
            )

        return await self.repository.find_by_module(module)

    async def update_sticker(
        self,
        sticker_id: str,
        sticker_data: StickerUpdate,
    ) -> dict:
        sticker = await self.repository.update(sticker_id, sticker_data)

        if sticker is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Adesivo não encontrado.",
            )

        return sticker

    async def delete_sticker(self, sticker_id: str) -> dict:
        was_deleted = await self.repository.deactivate(sticker_id)

        if not was_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Adesivo não encontrado.",
            )

        return {
            "message": "Adesivo removido com sucesso."
        }