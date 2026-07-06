from typing import Any

import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(autouse=True)
async def clean_milestones(test_db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    await test_db["milestones"].delete_many({})
    await test_db["tasks"].delete_many({})
    yield  # type: ignore[misc]
    await test_db["milestones"].delete_many({})
    await test_db["tasks"].delete_many({})


async def test_list_milestones_empty(ac: AsyncClient) -> None:
    resp = await ac.get("/api/v1/milestones")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_milestone_granted_on_total_10(ac: AsyncClient) -> None:
    for i in range(10):
        r = await ac.post("/api/v1/tasks", json={"title": f"Task {i}"})
        await ac.patch(f"/api/v1/tasks/{r.json()['task_id']}/done")

    resp = await ac.get("/api/v1/milestones")
    assert resp.status_code == 200
    ids = [m["milestone_id"] for m in resp.json()]
    assert "total_10" in ids


async def test_milestone_total_10_not_duplicated(ac: AsyncClient) -> None:
    # Complete 12 tasks; total_10 must appear exactly once
    for i in range(12):
        r = await ac.post("/api/v1/tasks", json={"title": f"No-dup {i}"})
        await ac.patch(f"/api/v1/tasks/{r.json()['task_id']}/done")

    resp = await ac.get("/api/v1/milestones")
    ids = [m["milestone_id"] for m in resp.json()]
    assert ids.count("total_10") == 1


async def test_milestone_focus_5(ac: AsyncClient) -> None:
    from datetime import date
    today = date.today().isoformat()
    for i in range(5):
        r = await ac.post(
            "/api/v1/tasks",
            json={"title": f"Focus {i}", "due_date": today, "category_id": "cat_focus"},
        )
        await ac.patch(f"/api/v1/tasks/{r.json()['task_id']}/done")

    resp = await ac.get("/api/v1/milestones")
    ids = [m["milestone_id"] for m in resp.json()]
    assert "focus_5" in ids


async def test_milestone_response_shape(ac: AsyncClient) -> None:
    # Grant one milestone and verify all required fields exist
    for i in range(10):
        r = await ac.post("/api/v1/tasks", json={"title": f"Shape {i}"})
        await ac.patch(f"/api/v1/tasks/{r.json()['task_id']}/done")

    resp = await ac.get("/api/v1/milestones")
    assert resp.status_code == 200
    for m in resp.json():
        assert "id" in m
        assert "milestone_id" in m
        assert "title" in m
        assert "description" in m
        assert "achieved_at" in m
