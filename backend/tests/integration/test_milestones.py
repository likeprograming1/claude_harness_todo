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


async def test_milestone_granted_on_total_10(ac: AsyncClient, test_db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    await test_db["tasks"].delete_many({})

    # Create and complete 10 tasks
    for i in range(10):
        r = await ac.post("/api/v1/tasks", json={"title": f"Task {i}"})
        task_id = r.json()["task_id"]
        await ac.patch(f"/api/v1/tasks/{task_id}/done")

    resp = await ac.get("/api/v1/milestones")
    assert resp.status_code == 200
    ids = [m["milestone_id"] for m in resp.json()]
    assert "total_10" in ids

    # cleanup tasks used for this test
    await test_db["tasks"].delete_many({})
