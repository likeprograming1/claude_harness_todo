from typing import Any

import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(autouse=True)
async def clean_custom_categories(test_db: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
    await test_db["categories"].delete_many({"is_default": {"$ne": True}})
    yield  # type: ignore[misc]
    await test_db["categories"].delete_many({"is_default": {"$ne": True}})


# ── list ──────────────────────────────────────────────────────────────────────

async def test_list_categories_includes_defaults(ac: AsyncClient) -> None:
    resp = await ac.get("/api/v1/categories")
    assert resp.status_code == 200
    ids = {c["category_id"] for c in resp.json()}
    assert {"cat_work", "cat_personal", "cat_urgent", "cat_focus"} <= ids


async def test_list_categories_defaults_marked(ac: AsyncClient) -> None:
    resp = await ac.get("/api/v1/categories")
    for cat in resp.json():
        if cat["category_id"] in ("cat_work", "cat_personal", "cat_urgent", "cat_focus"):
            assert cat["is_default"] is True


# ── create ────────────────────────────────────────────────────────────────────

async def test_create_category(ac: AsyncClient) -> None:
    resp = await ac.post("/api/v1/categories", json={"name": "Study", "color": "#FF0000"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Study"
    assert data["color"] == "#FF0000"
    assert data["is_default"] is False
    assert data["id"] != ""


async def test_create_category_default_color(ac: AsyncClient) -> None:
    resp = await ac.post("/api/v1/categories", json={"name": "Default color"})
    assert resp.status_code == 201
    assert resp.json()["color"] == "#888888"


async def test_create_category_duplicate_name(ac: AsyncClient) -> None:
    await ac.post("/api/v1/categories", json={"name": "Unique Cat", "color": "#FF0000"})
    resp = await ac.post("/api/v1/categories", json={"name": "Unique Cat", "color": "#00FF00"})
    assert resp.status_code == 409


async def test_create_category_invalid_color(ac: AsyncClient) -> None:
    resp = await ac.post("/api/v1/categories", json={"name": "Bad color", "color": "red"})
    assert resp.status_code == 422


async def test_create_category_empty_name(ac: AsyncClient) -> None:
    resp = await ac.post("/api/v1/categories", json={"name": "", "color": "#FF0000"})
    assert resp.status_code == 422


# ── delete ────────────────────────────────────────────────────────────────────

async def test_delete_category(ac: AsyncClient) -> None:
    create_resp = await ac.post("/api/v1/categories", json={"name": "Temporary", "color": "#123456"})
    category_id = create_resp.json()["category_id"]
    resp = await ac.delete(f"/api/v1/categories/{category_id}")
    assert resp.status_code == 204


async def test_delete_category_not_found(ac: AsyncClient) -> None:
    resp = await ac.delete("/api/v1/categories/nonexistent_cat")
    assert resp.status_code == 404


@pytest.mark.parametrize("default_id", ["cat_work", "cat_personal", "cat_urgent", "cat_focus"])
async def test_delete_default_category_blocked(ac: AsyncClient, default_id: str) -> None:
    resp = await ac.delete(f"/api/v1/categories/{default_id}")
    assert resp.status_code == 409
