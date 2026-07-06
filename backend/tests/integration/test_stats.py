from datetime import date
from typing import Any

import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase

pytestmark = pytest.mark.asyncio(loop_scope="session")

TODAY = date.today().isoformat()


@pytest.fixture(autouse=True)
async def clean_tasks(test_db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    await test_db["tasks"].delete_many({})
    yield  # type: ignore[misc]
    await test_db["tasks"].delete_many({})


# ── dashboard ─────────────────────────────────────────────────────────────────

async def test_dashboard_shape(ac: AsyncClient) -> None:
    resp = await ac.get("/api/v1/stats/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "today" in data
    assert "total_today" in data
    assert "completed_today" in data
    assert "completion_rate" in data
    assert "focus_score" in data
    assert isinstance(data["priority_tasks"], list)
    assert isinstance(data["upcoming"], list)


async def test_dashboard_counts(ac: AsyncClient) -> None:
    await ac.post("/api/v1/tasks", json={"title": "T1", "due_date": TODAY})
    r2 = await ac.post("/api/v1/tasks", json={"title": "T2", "due_date": TODAY})
    task_id = r2.json()["task_id"]
    await ac.patch(f"/api/v1/tasks/{task_id}/done")

    resp = await ac.get("/api/v1/stats/dashboard")
    data = resp.json()
    assert data["total_today"] >= 2
    assert data["completed_today"] >= 1
    assert data["completion_rate"] > 0


# ── weekly ────────────────────────────────────────────────────────────────────

async def test_weekly_returns_7_days(ac: AsyncClient) -> None:
    resp = await ac.get("/api/v1/stats/weekly")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["days"]) == 7
    for day in data["days"]:
        assert "date" in day
        assert "total" in day
        assert "completed" in day


async def test_weekly_days_sorted(ac: AsyncClient) -> None:
    resp = await ac.get("/api/v1/stats/weekly")
    dates = [d["date"] for d in resp.json()["days"]]
    assert dates == sorted(dates)


async def test_weekly_counts_today_task(ac: AsyncClient) -> None:
    await ac.post("/api/v1/tasks", json={"title": "Today task", "due_date": TODAY})
    resp = await ac.get("/api/v1/stats/weekly")
    today_day = next((d for d in resp.json()["days"] if d["date"] == TODAY), None)
    assert today_day is not None
    assert today_day["total"] >= 1


# ── insights ──────────────────────────────────────────────────────────────────

async def test_insights_insufficient_data(ac: AsyncClient) -> None:
    resp = await ac.get("/api/v1/stats/insights")
    assert resp.status_code == 200
    data = resp.json()
    assert data["peak_start"] is None
    assert data["peak_end"] is None
    assert "부족" in data["message"]


async def test_insights_with_enough_data(ac: AsyncClient) -> None:
    # Complete 5 tasks so completed_at is populated
    for i in range(5):
        r = await ac.post("/api/v1/tasks", json={"title": f"Insight task {i}"})
        await ac.patch(f"/api/v1/tasks/{r.json()['task_id']}/done")

    resp = await ac.get("/api/v1/stats/insights")
    assert resp.status_code == 200
    data = resp.json()
    assert data["peak_start"] is not None
    assert data["peak_end"] is not None
    assert "~" in data["message"]


# ── dashboard edge cases ──────────────────────────────────────────────────────

async def test_dashboard_priority_tasks_max_3(ac: AsyncClient) -> None:
    # Create 5 undone tasks today — priority_tasks must return at most 3
    for i in range(5):
        await ac.post("/api/v1/tasks", json={"title": f"PT {i}", "due_date": TODAY, "priority": "high"})

    resp = await ac.get("/api/v1/stats/dashboard")
    assert resp.status_code == 200
    assert len(resp.json()["priority_tasks"]) <= 3


async def test_dashboard_done_tasks_excluded_from_priority(ac: AsyncClient) -> None:
    r1 = await ac.post("/api/v1/tasks", json={"title": "Done today", "due_date": TODAY})
    await ac.patch(f"/api/v1/tasks/{r1.json()['task_id']}/done")
    r2 = await ac.post("/api/v1/tasks", json={"title": "Undone today", "due_date": TODAY})

    resp = await ac.get("/api/v1/stats/dashboard")
    data = resp.json()
    priority_ids = [t["task_id"] for t in data["priority_tasks"]]
    assert r1.json()["task_id"] not in priority_ids
    assert r2.json()["task_id"] in priority_ids


async def test_dashboard_upcoming_excludes_past(ac: AsyncClient) -> None:
    from datetime import date, timedelta
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    await ac.post("/api/v1/tasks", json={"title": "Past task", "due_date": yesterday})
    r_future = await ac.post("/api/v1/tasks", json={"title": "Future task", "due_date": tomorrow})

    resp = await ac.get("/api/v1/stats/dashboard")
    upcoming_ids = [t["task_id"] for t in resp.json()["upcoming"]]
    assert r_future.json()["task_id"] in upcoming_ids
