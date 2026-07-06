import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_health_ok(ac: AsyncClient) -> None:
    resp = await ac.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_docs_accessible(ac: AsyncClient) -> None:
    resp = await ac.get("/docs")
    assert resp.status_code == 200


async def test_openapi_schema(ac: AsyncClient) -> None:
    resp = await ac.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "paths" in schema
    # Verify all major route prefixes are registered
    paths = schema["paths"]
    assert any("/tasks" in p for p in paths)
    assert any("/categories" in p for p in paths)
    assert any("/stats" in p for p in paths)
    assert any("/milestones" in p for p in paths)
