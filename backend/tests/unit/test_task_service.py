from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import AppValidationError, EntityNotFoundError
from app.core.types import Priority
from app.models.task import TaskModel
from app.services.task_service import TaskService


def _make_task(
    task_id: str = "task1",
    is_done: bool = False,
    category_id: str | None = None,
    due_date: str | None = None,
    due_time: str | None = None,
    priority: Priority = Priority.MEDIUM,
) -> TaskModel:
    return TaskModel(
        task_id=task_id,
        title="Test Task",
        priority=priority,
        is_done=is_done,
        due_date=due_date,
        due_time=due_time,
        category_id=category_id,
        mongo_id="abc123",
    )


def _make_svc(
    *,
    existing_task: TaskModel | None = None,
    toggled_task: TaskModel | None = None,
    delete_ok: bool = True,
    category_exists: bool = True,
) -> TaskService:
    t_repo = MagicMock()
    t_repo.get_by_id = AsyncMock(return_value=existing_task)
    t_repo.list_all = AsyncMock(return_value=[existing_task] if existing_task else [])
    t_repo.create = AsyncMock(return_value=existing_task or _make_task())
    t_repo.update = AsyncMock(return_value=existing_task)
    t_repo.delete = AsyncMock(return_value=delete_ok)
    t_repo.toggle_done = AsyncMock(return_value=toggled_task)

    c_repo = MagicMock()
    c_repo.exists = AsyncMock(return_value=category_exists)

    m_svc = MagicMock()
    m_svc.check_and_grant = AsyncMock(return_value=[])

    return TaskService(task_repo=t_repo, category_repo=c_repo, milestone_svc=m_svc)


# ── list_tasks ────────────────────────────────────────────────────────────────

async def test_list_tasks_returns_all() -> None:
    task = _make_task()
    svc = _make_svc(existing_task=task)
    result = await svc.list_tasks()
    assert len(result) == 1


# ── get_task ──────────────────────────────────────────────────────────────────

async def test_get_task_found() -> None:
    task = _make_task()
    svc = _make_svc(existing_task=task)
    result = await svc.get_task("task1")
    assert result.task_id == "task1"


async def test_get_task_not_found() -> None:
    svc = _make_svc(existing_task=None)
    with pytest.raises(EntityNotFoundError):
        await svc.get_task("missing")


# ── create_task ───────────────────────────────────────────────────────────────

async def test_create_task_no_category() -> None:
    task = _make_task()
    svc = _make_svc(existing_task=task)
    result = await svc.create_task({"title": "Test"})
    assert result.task_id == "task1"


async def test_create_task_valid_category() -> None:
    task = _make_task(category_id="cat_work")
    svc = _make_svc(existing_task=task, category_exists=True)
    result = await svc.create_task({"title": "Test", "category_id": "cat_work"})
    assert result.category_id == "cat_work"


async def test_create_task_invalid_category() -> None:
    svc = _make_svc(category_exists=False)
    with pytest.raises(AppValidationError):
        await svc.create_task({"title": "Test", "category_id": "bad_cat"})


# ── update_task ───────────────────────────────────────────────────────────────

async def test_update_task_not_found() -> None:
    svc = _make_svc(existing_task=None)
    with pytest.raises(EntityNotFoundError):
        await svc.update_task("missing", {"title": "New"})


async def test_update_task_invalid_category() -> None:
    svc = _make_svc(existing_task=_make_task(), category_exists=False)
    with pytest.raises(AppValidationError):
        await svc.update_task("task1", {"category_id": "bad_cat"})


async def test_update_task_due_time_without_due_date() -> None:
    task = _make_task(due_date=None, due_time=None)
    svc = _make_svc(existing_task=task)
    with pytest.raises(AppValidationError):
        await svc.update_task("task1", {"due_time": "09:00"})


async def test_update_task_due_time_with_existing_due_date() -> None:
    task = _make_task(due_date="2025-01-01", due_time=None)
    svc = _make_svc(existing_task=task)
    result = await svc.update_task("task1", {"due_time": "09:00"})
    assert result is not None


async def test_update_task_success() -> None:
    task = _make_task()
    svc = _make_svc(existing_task=task)
    result = await svc.update_task("task1", {"title": "Updated"})
    assert result is not None


# ── delete_task ───────────────────────────────────────────────────────────────

async def test_delete_task_success() -> None:
    svc = _make_svc(delete_ok=True)
    await svc.delete_task("task1")  # should not raise


async def test_delete_task_not_found() -> None:
    svc = _make_svc(delete_ok=False)
    with pytest.raises(EntityNotFoundError):
        await svc.delete_task("missing")


# ── toggle_done ───────────────────────────────────────────────────────────────

async def test_toggle_done_marks_done() -> None:
    done_task = _make_task(is_done=True)
    svc = _make_svc(existing_task=_make_task(), toggled_task=done_task)
    result = await svc.toggle_done("task1")
    assert result.is_done is True


async def test_toggle_done_marks_undone() -> None:
    undone_task = _make_task(is_done=False)
    svc = _make_svc(existing_task=_make_task(is_done=True), toggled_task=undone_task)
    result = await svc.toggle_done("task1")
    assert result.is_done is False


async def test_toggle_done_not_found() -> None:
    svc = _make_svc(existing_task=None, toggled_task=None)
    with pytest.raises(EntityNotFoundError):
        await svc.toggle_done("missing")


async def test_toggle_done_triggers_milestone_check() -> None:
    done_task = _make_task(is_done=True)
    svc = _make_svc(existing_task=_make_task(), toggled_task=done_task)
    await svc.toggle_done("task1")
    svc._milestone_svc.check_and_grant.assert_called_once()  # type: ignore[union-attr]


async def test_toggle_undone_does_not_trigger_milestone() -> None:
    undone_task = _make_task(is_done=False)
    svc = _make_svc(existing_task=_make_task(is_done=True), toggled_task=undone_task)
    await svc.toggle_done("task1")
    svc._milestone_svc.check_and_grant.assert_not_called()  # type: ignore[union-attr]
