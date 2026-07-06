from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.types import Priority
from app.models.task import TaskModel
from app.services.stats_service import StatsService

TODAY = date.today().isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()


def _make_task(
    task_id: str = "t1",
    is_done: bool = False,
    due_date: str | None = None,
    priority: Priority = Priority.MEDIUM,
    completed_at: datetime | None = None,
) -> TaskModel:
    return TaskModel(
        task_id=task_id,
        title="Test",
        priority=priority,
        is_done=is_done,
        due_date=due_date,
        completed_at=completed_at,
        mongo_id="abc",
    )


# ── get_dashboard ─────────────────────────────────────────────────────────────

async def test_get_dashboard_empty() -> None:
    repo = MagicMock()
    repo.list_all = AsyncMock(return_value=[])
    svc = StatsService(task_repo=repo)
    result = await svc.get_dashboard()
    assert result.total_today == 0
    assert result.completed_today == 0
    assert result.completion_rate == 0.0
    assert result.focus_score == 0


async def test_get_dashboard_completion_rate() -> None:
    today_tasks = [
        _make_task("t1", is_done=True, due_date=TODAY),
        _make_task("t2", is_done=False, due_date=TODAY),
    ]

    async def mock_list_all(**kwargs: object) -> list[TaskModel]:
        if kwargs.get("date") == TODAY:
            return today_tasks
        return []

    repo = MagicMock()
    repo.list_all = mock_list_all
    svc = StatsService(task_repo=repo)
    result = await svc.get_dashboard()
    assert result.total_today == 2
    assert result.completed_today == 1
    assert result.completion_rate == 50.0


async def test_get_dashboard_priority_tasks_ordered() -> None:
    today_tasks = [
        _make_task("t1", is_done=False, due_date=TODAY, priority=Priority.LOW),
        _make_task("t2", is_done=False, due_date=TODAY, priority=Priority.HIGH),
        _make_task("t3", is_done=False, due_date=TODAY, priority=Priority.MEDIUM),
    ]

    async def mock_list_all(**kwargs: object) -> list[TaskModel]:
        if kwargs.get("date") == TODAY:
            return today_tasks
        return []

    repo = MagicMock()
    repo.list_all = mock_list_all
    svc = StatsService(task_repo=repo)
    result = await svc.get_dashboard()
    assert result.priority_tasks[0].priority == Priority.HIGH
    assert result.priority_tasks[1].priority == Priority.MEDIUM
    assert result.priority_tasks[2].priority == Priority.LOW


async def test_get_dashboard_upcoming_future_only() -> None:
    async def mock_list_all(**kwargs: object) -> list[TaskModel]:
        if kwargs.get("date") == TODAY:
            return []
        # is_done=False query returns past + future tasks
        return [
            _make_task("past", is_done=False, due_date=YESTERDAY),
            _make_task("future", is_done=False, due_date=TOMORROW),
        ]

    repo = MagicMock()
    repo.list_all = mock_list_all
    svc = StatsService(task_repo=repo)
    result = await svc.get_dashboard()
    assert len(result.upcoming) == 1
    assert result.upcoming[0].task_id == "future"


# ── get_weekly ────────────────────────────────────────────────────────────────

async def test_get_weekly_returns_7_days() -> None:
    repo = MagicMock()
    repo.get_by_due_date_range = AsyncMock(return_value=[])
    svc = StatsService(task_repo=repo)
    result = await svc.get_weekly()
    assert len(result.days) == 7


async def test_get_weekly_counts_correctly() -> None:
    task_done = _make_task("t1", is_done=True, due_date=TODAY)
    task_undone = _make_task("t2", is_done=False, due_date=TODAY)

    repo = MagicMock()
    repo.get_by_due_date_range = AsyncMock(return_value=[task_done, task_undone])
    svc = StatsService(task_repo=repo)
    result = await svc.get_weekly()

    today_stat = next(d for d in result.days if d.date == TODAY)
    assert today_stat.total == 2
    assert today_stat.completed == 1


async def test_get_weekly_days_are_sorted() -> None:
    repo = MagicMock()
    repo.get_by_due_date_range = AsyncMock(return_value=[])
    svc = StatsService(task_repo=repo)
    result = await svc.get_weekly()
    dates = [d.date for d in result.days]
    assert dates == sorted(dates)


# ── get_insights ──────────────────────────────────────────────────────────────

async def test_get_insights_insufficient_data() -> None:
    repo = MagicMock()
    repo.get_completed_with_time = AsyncMock(return_value=[])
    svc = StatsService(task_repo=repo)
    result = await svc.get_insights()
    assert result.peak_start is None
    assert result.peak_end is None
    assert "부족" in result.message


async def test_get_insights_peak_hour() -> None:
    # 14:00 x3 + 15:00 x3 → 14:00-16:00 window wins with 6 (vs 13:00-15:00 with 3)
    tasks = [
        _make_task(f"t{i}", is_done=True, completed_at=datetime(2024, 1, 1, 14, 0))
        for i in range(3)
    ] + [
        _make_task(f"u{i}", is_done=True, completed_at=datetime(2024, 1, 1, 15, 0))
        for i in range(3)
    ]
    repo = MagicMock()
    repo.get_completed_with_time = AsyncMock(return_value=tasks)
    svc = StatsService(task_repo=repo)
    result = await svc.get_insights()
    assert result.peak_start == "14:00"
    assert result.peak_end == "16:00"


async def test_get_insights_exactly_5_tasks() -> None:
    tasks = [
        _make_task(f"t{i}", is_done=True, completed_at=datetime(2024, 1, 1, 9, 0))
        for i in range(5)
    ]
    repo = MagicMock()
    repo.get_completed_with_time = AsyncMock(return_value=tasks)
    svc = StatsService(task_repo=repo)
    result = await svc.get_insights()
    assert result.peak_start is not None
