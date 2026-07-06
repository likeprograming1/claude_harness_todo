from pydantic import BaseModel

from app.schemas.task import TaskResponse


class DayStatsResponse(BaseModel):
    date: str
    total: int
    completed: int


class WeeklyResponse(BaseModel):
    days: list[DayStatsResponse]


class InsightsResponse(BaseModel):
    peak_start: str | None
    peak_end: str | None
    message: str


class DashboardResponse(BaseModel):
    today: str
    total_today: int
    completed_today: int
    completion_rate: float
    focus_score: int
    priority_tasks: list[TaskResponse]
    upcoming: list[TaskResponse]
