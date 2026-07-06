from app.database.mongodb import get_database
from app.schemas.brushing_goal_schema import (
    BrushingGoalCheckUpdate,
    BrushingGoalCompleteResponse,
    WeeklyBrushingGoalResponse,
)
from app.services.brushing_goal_services import BrushingGoalService
from fastapi import APIRouter, Depends, status
from pymongo.asynchronous.database import AsyncDatabase

router = APIRouter(
    prefix="/children",
    tags=["Weekly Brushing Goals"],
)

def get_brushing_goal_service(
    database: AsyncDatabase = Depends(get_database),
) -> BrushingGoalService:
    return BrushingGoalService(database)

@router.get(
    "/{child_id}/brushing-goals/current",
    response_model=WeeklyBrushingGoalResponse,
)
async def get_current_weekly_goal(
    child_id: str,
    service: BrushingGoalService = Depends(get_brushing_goal_service),
):
    return await service.get_or_create_current_goal(child_id)

@router.patch(
    "/{child_id}/brushing-goals/current/check",
    response_model=WeeklyBrushingGoalResponse,
)
async def update_current_weekly_goal_check(
    child_id: str,
    payload: BrushingGoalCheckUpdate,
    service: BrushingGoalService = Depends(get_brushing_goal_service),
):
    return await service.update_check(
        child_id=child_id,
        day=payload.day,
        shift=payload.shift,
        checked=payload.checked,
    )

@router.post(
    "/{child_id}/brushing-goals/current/complete",
    response_model=BrushingGoalCompleteResponse,
    status_code=status.HTTP_200_OK,
)
async def complete_current_weekly_goal(
    child_id: str,
    service: BrushingGoalService = Depends(get_brushing_goal_service),
):
    return await service.complete_current_goal(child_id)