from fastapi import APIRouter

from app.models.task import TaskModel
from app.schemas.stats import DashboardResponse, DayStatsResponse, InsightsResponse, WeeklyResponse
from app.schemas.task import TaskResponse
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])


def _task_to_response(task: TaskModel) -> TaskResponse:
    return TaskResponse(
        id=task.mongo_id or "",
        task_id=task.task_id,
        title=task.title,
        priority=task.priority,
        is_done=task.is_done,
        due_date=task.due_date,
        due_time=task.due_time,
        category_id=task.category_id,
        notes=task.notes,
        completed_at=task.completed_at,
        created_at=task.created_at,
    )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard() -> DashboardResponse:
    stats = await StatsService().get_dashboard()
    return DashboardResponse(
        today=stats.today,
        total_today=stats.total_today,
        completed_today=stats.completed_today,
        completion_rate=stats.completion_rate,
        focus_score=stats.focus_score,
        priority_tasks=[_task_to_response(t) for t in stats.priority_tasks],
        upcoming=[_task_to_response(t) for t in stats.upcoming],
    )


@router.get("/weekly", response_model=WeeklyResponse)
async def get_weekly() -> WeeklyResponse:
    stats = await StatsService().get_weekly()
    return WeeklyResponse(
        days=[
            DayStatsResponse(date=d.date, total=d.total, completed=d.completed)
            for d in stats.days
        ]
    )


@router.get("/insights", response_model=InsightsResponse)
async def get_insights() -> InsightsResponse:
    stats = await StatsService().get_insights()
    return InsightsResponse(
        peak_start=stats.peak_start,
        peak_end=stats.peak_end,
        message=stats.message,
    )
