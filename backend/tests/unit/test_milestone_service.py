from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.types import Priority
from app.models.milestone import MilestoneModel
from app.models.task import TaskModel
from app.services.milestone_service import MilestoneService


def _make_task(
    task_id: str = "t1",
    is_done: bool = True,
    due_date: str | None = None,
    category_id: str | None = None,
) -> TaskModel:
    return TaskModel(
        task_id=task_id,
        title="Test",
        priority=Priority.MEDIUM,
        is_done=is_done,
        due_date=due_date,
        category_id=category_id,
        mongo_id="abc",
    )


def _make_milestone(mid: str = "total_10") -> MilestoneModel:
    return MilestoneModel(
        milestone_id=mid,
        title="10개 완료!",
        description="할 일을 10개 완료했습니다",
        achieved_at=date.today(),
        mongo_id="abc",
    )


def _make_svc(
    *,
    total_completed: int = 0,
    range_tasks: list[TaskModel] | None = None,
    list_tasks: list[TaskModel] | None = None,
    milestone_exists: bool = False,
    milestone_list: list[MilestoneModel] | None = None,
) -> MilestoneService:
    m_repo = MagicMock()
    m_repo.list_all = AsyncMock(return_value=milestone_list or [])
    m_repo.exists = AsyncMock(return_value=milestone_exists)
    m_repo.create = AsyncMock(side_effect=lambda data: _make_milestone(str(data["milestone_id"])))

    t_repo = MagicMock()
    t_repo.count_total_completed = AsyncMock(return_value=total_completed)
    t_repo.get_by_due_date_range = AsyncMock(return_value=range_tasks or [])
    t_repo.list_all = AsyncMock(return_value=list_tasks or [])

    return MilestoneService(milestone_repo=m_repo, task_repo=t_repo)


async def test_list_milestones() -> None:
    svc = _make_svc(milestone_list=[_make_milestone()])
    result = await svc.list_milestones()
    assert len(result) == 1


async def test_check_and_grant_total_10() -> None:
    svc = _make_svc(total_completed=10)
    result = await svc.check_and_grant()
    assert any(m.milestone_id == "total_10" for m in result)


async def test_check_and_grant_total_50_grants_both() -> None:
    svc = _make_svc(total_completed=50)
    result = await svc.check_and_grant()
    ids = [m.milestone_id for m in result]
    assert "total_10" in ids
    assert "total_50" in ids


async def test_check_and_grant_already_granted_skipped() -> None:
    svc = _make_svc(total_completed=50, milestone_exists=True)
    result = await svc.check_and_grant()
    assert result == []


async def test_check_and_grant_streak_3() -> None:
    today = date.today()
    streak_tasks = [
        _make_task(f"t{i}", is_done=True, due_date=(today.__class__.fromordinal(today.toordinal() - i)).isoformat())
        for i in range(3)
    ]
    svc = _make_svc(range_tasks=streak_tasks)
    result = await svc.check_and_grant()
    assert any(m.milestone_id == "streak_3" for m in result)


async def test_check_and_grant_focus_5() -> None:
    today_str = date.today().isoformat()
    focus_tasks = [
        _make_task(f"t{i}", is_done=True, due_date=today_str, category_id="cat_focus")
        for i in range(5)
    ]
    svc = _make_svc(list_tasks=focus_tasks)
    result = await svc.check_and_grant()
    assert any(m.milestone_id == "focus_5" for m in result)


async def test_check_and_grant_focus_4_not_enough() -> None:
    today_str = date.today().isoformat()
    focus_tasks = [
        _make_task(f"t{i}", is_done=True, due_date=today_str, category_id="cat_focus")
        for i in range(4)
    ]
    svc = _make_svc(list_tasks=focus_tasks)
    result = await svc.check_and_grant()
    assert not any(m.milestone_id == "focus_5" for m in result)
