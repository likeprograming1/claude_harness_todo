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
