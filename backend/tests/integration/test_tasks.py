from typing import Any

import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(autouse=True)
async def clean_tasks(test_db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    await test_db["tasks"].delete_many({})
    yield  # type: ignore[misc]
    await test_db["tasks"].delete_many({})


# ── create ────────────────────────────────────────────────────────────────────

async def test_create_task(ac: AsyncClient) -> None:
    resp = await ac.post("/api/v1/tasks", json={"title": "Test task"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test task"
    assert data["priority"] == "medium"
    assert data["is_done"] is False
    assert data["id"] != ""
    assert data["task_id"] != ""


async def test_create_task_with_all_fields(ac: AsyncClient) -> None:
    resp = await ac.post(
        "/api/v1/tasks",
        json={
            "title": "Full task",
            "priority": "high",
            "due_date": "2025-12-31",
            "due_time": "09:00",
            "category_id": "cat_work",
            "notes": "Some notes",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["priority"] == "high"
    assert data["due_date"] == "2025-12-31"
    assert data["due_time"] == "09:00"
    assert data["category_id"] == "cat_work"


async def test_create_task_missing_title(ac: AsyncClient) -> None:
    resp = await ac.post("/api/v1/tasks", json={})
    assert resp.status_code == 422


async def test_create_task_due_time_without_due_date(ac: AsyncClient) -> None:
    resp = await ac.post("/api/v1/tasks", json={"title": "T", "due_time": "09:00"})
    assert resp.status_code == 422


async def test_create_task_invalid_category(ac: AsyncClient) -> None:
    resp = await ac.post("/api/v1/tasks", json={"title": "T", "category_id": "nonexistent"})
    assert resp.status_code == 422


# ── get ───────────────────────────────────────────────────────────────────────

async def test_get_task(ac: AsyncClient) -> None:
    create_resp = await ac.post("/api/v1/tasks", json={"title": "Get me"})
    task_id = create_resp.json()["task_id"]
    resp = await ac.get(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get me"


async def test_get_task_not_found(ac: AsyncClient) -> None:
    resp = await ac.get("/api/v1/tasks/nonexistent_id")
    assert resp.status_code == 404


# ── list ──────────────────────────────────────────────────────────────────────

async def test_list_tasks(ac: AsyncClient) -> None:
    await ac.post("/api/v1/tasks", json={"title": "Task A"})
    await ac.post("/api/v1/tasks", json={"title": "Task B"})
    resp = await ac.get("/api/v1/tasks")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


async def test_list_tasks_filter_done(ac: AsyncClient) -> None:
    create = await ac.post("/api/v1/tasks", json={"title": "Done task"})
    task_id = create.json()["task_id"]
    await ac.patch(f"/api/v1/tasks/{task_id}/done")

    resp = await ac.get("/api/v1/tasks?done=true")
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) >= 1
    assert all(t["is_done"] for t in tasks)


async def test_list_tasks_filter_priority(ac: AsyncClient) -> None:
    await ac.post("/api/v1/tasks", json={"title": "High task", "priority": "high"})
    await ac.post("/api/v1/tasks", json={"title": "Low task", "priority": "low"})
    resp = await ac.get("/api/v1/tasks?priority=high")
    assert resp.status_code == 200
    tasks = resp.json()
    assert all(t["priority"] == "high" for t in tasks)


# ── update ────────────────────────────────────────────────────────────────────

async def test_update_task(ac: AsyncClient) -> None:
    create_resp = await ac.post("/api/v1/tasks", json={"title": "Original"})
    task_id = create_resp.json()["task_id"]
    resp = await ac.put(f"/api/v1/tasks/{task_id}", json={"title": "Updated", "priority": "high"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated"
    assert data["priority"] == "high"


async def test_update_task_not_found(ac: AsyncClient) -> None:
    resp = await ac.put("/api/v1/tasks/missing", json={"title": "X"})
    assert resp.status_code == 404


async def test_update_task_due_time_without_due_date(ac: AsyncClient) -> None:
    create_resp = await ac.post("/api/v1/tasks", json={"title": "No date"})
    task_id = create_resp.json()["task_id"]
    resp = await ac.put(f"/api/v1/tasks/{task_id}", json={"due_time": "10:00"})
    assert resp.status_code == 422


# ── delete ────────────────────────────────────────────────────────────────────

async def test_delete_task(ac: AsyncClient) -> None:
    create_resp = await ac.post("/api/v1/tasks", json={"title": "Delete me"})
    task_id = create_resp.json()["task_id"]
    resp = await ac.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204
    assert (await ac.get(f"/api/v1/tasks/{task_id}")).status_code == 404


async def test_delete_task_not_found(ac: AsyncClient) -> None:
    resp = await ac.delete("/api/v1/tasks/missing_id")
    assert resp.status_code == 404


# ── toggle_done ───────────────────────────────────────────────────────────────

async def test_toggle_done_to_done(ac: AsyncClient) -> None:
    create_resp = await ac.post("/api/v1/tasks", json={"title": "Toggle me"})
    task_id = create_resp.json()["task_id"]
    resp = await ac.patch(f"/api/v1/tasks/{task_id}/done")
    assert resp.status_code == 200
    assert resp.json()["is_done"] is True


async def test_toggle_done_back_to_undone(ac: AsyncClient) -> None:
    create_resp = await ac.post("/api/v1/tasks", json={"title": "Double toggle"})
    task_id = create_resp.json()["task_id"]
    await ac.patch(f"/api/v1/tasks/{task_id}/done")
    resp = await ac.patch(f"/api/v1/tasks/{task_id}/done")
    assert resp.status_code == 200
    assert resp.json()["is_done"] is False


async def test_toggle_done_not_found(ac: AsyncClient) -> None:
    resp = await ac.patch("/api/v1/tasks/missing_id/done")
    assert resp.status_code == 404
