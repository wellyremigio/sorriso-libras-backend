from datetime import date, datetime, timedelta, timezone

from app.repositories.brushing_goal_repository import BrushingGoalRepository
from app.repositories.sticker_repository import StickerRepository
from app.repositories.sticker_gallery_repository import StickerGalleryRepository
from fastapi import HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

DAYS_OF_WEEK = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
VALID_SHIFTS = ["morning", "afternoon", "night"]
TOTAL_WEEKLY_GOAL = 21


class BrushingGoalService:
    def __init__(self, database: AsyncDatabase):
        self.brushing_goal_repository = BrushingGoalRepository(database)
        self.sticker_repository = StickerRepository(database)
        self.sticker_gallery_repository  = StickerGalleryRepository(database)

    def _get_current_week_range(self) -> tuple[date, date]:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        return week_start, week_end

    def _get_current_day_index(self) -> int:
        return date.today().weekday()

    def _validate_day_and_shift(self, day: str, shift: str) -> None:
        if day not in DAYS_OF_WEEK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dia da semana inválido.",
            )

        if shift not in VALID_SHIFTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Turno de escovação inválido.",
            )

    def _validate_not_future_day(self, day: str) -> None:
        requested_day_index = DAYS_OF_WEEK.index(day)
        current_day_index = self._get_current_day_index()

        if requested_day_index > current_day_index:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível marcar escovações em dias futuros.",
            )

    def _count_completed_checks(self, checks: dict[str, bool]) -> int:
        return sum(1 for checked in checks.values() if checked)

    async def get_or_create_current_goal(self, child_id: str) -> dict:
        week_start, week_end = self._get_current_week_range()

        goal = await self.brushing_goal_repository.find_by_child_and_week(
            child_id=child_id,
            week_start_date=week_start,
        )

        if goal:
            return goal

        return await self.brushing_goal_repository.create(
            child_id=child_id,
            week_start_date=week_start,
            week_end_date=week_end,
            checks={},
            total_completed=0,
            total_goal=TOTAL_WEEKLY_GOAL,
            is_completed=False,
        )

    async def update_check(
        self,
        child_id: str,
        day: str,
        shift: str,
        checked: bool,
    ) -> dict:
        self._validate_day_and_shift(day, shift)
        self._validate_not_future_day(day)

        goal = await self.get_or_create_current_goal(child_id)

        check_key = f"{day}-{shift}"
        checks = goal.get("checks", {})
        checks[check_key] = checked

        total_completed = self._count_completed_checks(checks)
        is_completed = total_completed >= TOTAL_WEEKLY_GOAL

        return await self.brushing_goal_repository.update_checks(
            goal_id=goal["id"],
            checks=checks,
            total_completed=total_completed,
            is_completed=is_completed,
        )

    async def complete_current_goal(self, child_id: str) -> dict:
        goal = await self.get_or_create_current_goal(child_id)

        total_completed = goal.get("total_completed", 0)

        if total_completed < TOTAL_WEEKLY_GOAL:
            return {
                "completed": False,
                "message": "Você ainda não completou a meta semanal. Continue tentando!",
                "earned_stickers": [],
                "goal": goal,
            }

        if goal.get("is_completed") and goal.get("completed_at"):
            return {
                "completed": True,
                "message": "Meta semanal já foi concluída.",
                "earned_stickers": [],
                "goal": goal,
            }

        completed_goal = await self.brushing_goal_repository.mark_as_completed(
            goal_id=goal["id"],
            completed_at=datetime.now(timezone.utc),
        )

        sticker = await self.sticker_gallery_repository.find_weekly_brushing_goal_sticker()

        earned_stickers = []

        if sticker:
            earned_sticker = await self.sticker_gallery_repository.award_sticker(
                child_id=child_id,
                sticker=sticker,
                earned_reason="weekly_brushing_goal",
                earned_from_video_id=None,
            )

            if earned_sticker:
                earned_stickers.append(earned_sticker)

        return {
            "completed": True,
            "message": "Parabéns! Você completou sua meta semanal.",
            "earned_stickers": earned_stickers,
            "goal": completed_goal,
        }