from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

from app.models.task import TaskModel
from app.repositories.task_repository import TaskRepository

_PRIORITY_ORDER: dict[str, int] = {"high": 3, "medium": 2, "low": 1}


@dataclass
class DayStats:
    date: str
    total: int
    completed: int


@dataclass
class WeeklyStats:
    days: list[DayStats] = field(default_factory=list)


@dataclass
class InsightsStats:
    peak_start: str | None
    peak_end: str | None
    message: str


@dataclass
class DashboardStats:
    today: str
    total_today: int
    completed_today: int
    completion_rate: float
    focus_score: int
    priority_tasks: list[TaskModel] = field(default_factory=list)
    upcoming: list[TaskModel] = field(default_factory=list)


class StatsService:
    def __init__(self, task_repo: TaskRepository | None = None) -> None:
        self._task_repo = task_repo or TaskRepository()

    async def get_dashboard(self) -> DashboardStats:
        today_str = date.today().isoformat()
        today_tasks = await self._task_repo.list_all(date=today_str)

        total_today = len(today_tasks)
        completed_today = sum(1 for t in today_tasks if t.is_done)
        completion_rate = (
            round(completed_today / total_today * 100, 1) if total_today > 0 else 0.0
        )

        undone = sorted(
            [t for t in today_tasks if not t.is_done],
            key=lambda t: _PRIORITY_ORDER.get(str(t.priority), 0),
            reverse=True,
        )

        all_upcoming = await self._task_repo.list_all(is_done=False)
        upcoming = sorted(
            [t for t in all_upcoming if t.due_date and t.due_date > today_str],
            key=lambda t: t.due_date or "",
        )[:5]

        return DashboardStats(
            today=today_str,
            total_today=total_today,
            completed_today=completed_today,
            completion_rate=completion_rate,
            focus_score=int(completion_rate),
            priority_tasks=undone[:3],
            upcoming=upcoming,
        )

    async def get_weekly(self) -> WeeklyStats:
        today = date.today()
        start = today - timedelta(days=6)
        tasks = await self._task_repo.get_by_due_date_range(
            start.isoformat(), today.isoformat()
        )

        per_day: dict[str, list[TaskModel]] = {
            (start + timedelta(days=i)).isoformat(): [] for i in range(7)
        }
        for t in tasks:
            if t.due_date and t.due_date in per_day:
                per_day[t.due_date].append(t)

        days = [
            DayStats(
                date=d,
                total=len(ts),
                completed=sum(1 for t in ts if t.is_done),
            )
            for d, ts in sorted(per_day.items())
        ]
        return WeeklyStats(days=days)

    async def get_insights(self) -> InsightsStats:
        completed = await self._task_repo.get_completed_with_time()
        if len(completed) < 5:
            return InsightsStats(
                peak_start=None,
                peak_end=None,
                message="데이터가 부족합니다. 더 많은 할 일을 완료하면 인사이트를 확인할 수 있습니다.",
            )

        hour_counts: dict[int, int] = defaultdict(int)
        for task in completed:
            if task.completed_at:
                hour_counts[task.completed_at.hour] += 1

        best_hour = max(
            range(24),
            key=lambda h: hour_counts.get(h, 0) + hour_counts.get((h + 1) % 24, 0),
        )
        peak_start = f"{best_hour:02d}:00"
        peak_end = f"{(best_hour + 2) % 24:02d}:00"
        return InsightsStats(
            peak_start=peak_start,
            peak_end=peak_end,
            message=f"{peak_start}~{peak_end} 사이에 가장 생산적입니다.",
        )
