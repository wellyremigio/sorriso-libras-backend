from datetime import date, datetime

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase


class BrushingGoalRepository:
    def __init__(self, database: AsyncDatabase):
        self.collection = database["weekly_brushing_goals"]

    @staticmethod
    def _serialize_date(value: str | date) -> date:
        if isinstance(value, date):
            return value

        return date.fromisoformat(value)

    def _serialize_goal(self, goal: dict | None) -> dict:
        if not goal:
            raise ValueError("Meta semanal não encontrada.")

        return {
            "id": str(goal["_id"]),
            "child_id": goal["child_id"],
            "week_start_date": self._serialize_date(goal["week_start_date"]),
            "week_end_date": self._serialize_date(goal["week_end_date"]),
            "checks": goal.get("checks", {}),
            "total_completed": goal.get("total_completed", 0),
            "total_goal": goal.get("total_goal", 21),
            "is_completed": goal.get("is_completed", False),
            "completed_at": goal.get("completed_at"),
            "created_at": goal["created_at"],
            "updated_at": goal["updated_at"],
        }

    async def find_by_child_and_week(
        self,
        child_id: str,
        week_start_date: date,
    ) -> dict | None:
        goal = await self.collection.find_one(
            {
                "child_id": child_id,
                "week_start_date": week_start_date.isoformat(),
            }
        )

        if not goal:
            return None

        return self._serialize_goal(goal)

    async def create(
        self,
        child_id: str,
        week_start_date: date,
        week_end_date: date,
        checks: dict[str, bool],
        total_completed: int,
        total_goal: int,
        is_completed: bool,
    ) -> dict:
        now = datetime.utcnow()

        goal = {
            "child_id": child_id,
            "week_start_date": week_start_date.isoformat(),
            "week_end_date": week_end_date.isoformat(),
            "checks": checks,
            "total_completed": total_completed,
            "total_goal": total_goal,
            "is_completed": is_completed,
            "completed_at": None,
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(goal)

        created_goal = await self.collection.find_one({"_id": result.inserted_id})

        return self._serialize_goal(created_goal)

    async def update_checks(
        self,
        goal_id: str,
        checks: dict[str, bool],
        total_completed: int,
        is_completed: bool,
    ) -> dict:
        now = datetime.utcnow()

        await self.collection.update_one(
            {"_id": ObjectId(goal_id)},
            {
                "$set": {
                    "checks": checks,
                    "total_completed": total_completed,
                    "is_completed": is_completed,
                    "updated_at": now,
                }
            },
        )

        updated_goal = await self.collection.find_one({"_id": ObjectId(goal_id)})

        return self._serialize_goal(updated_goal)

    async def mark_as_completed(
        self,
        goal_id: str,
        completed_at: datetime,
    ) -> dict:
        now = datetime.utcnow()

        await self.collection.update_one(
            {"_id": ObjectId(goal_id)},
            {
                "$set": {
                    "is_completed": True,
                    "completed_at": completed_at,
                    "updated_at": now,
                }
            },
        )

        updated_goal = await self.collection.find_one({"_id": ObjectId(goal_id)})

        return self._serialize_goal(updated_goal)
