from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

import app.core.database as db_module
import app.repositories.base as base_module
from app.main import app

TEST_DB = "todo_test"

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
async def motor_client() -> AsyncGenerator[AsyncIOMotorClient[dict[str, Any]], None]:
    client: AsyncIOMotorClient[dict[str, Any]] = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

    def _get_test_db() -> AsyncIOMotorDatabase[dict[str, Any]]:
        return client[TEST_DB]  # type: ignore[return-value]

    # Patch both the database module AND base.py's imported reference
    db_module.client = client
    db_module.get_db = _get_test_db  # type: ignore[assignment]
    base_module.get_db = _get_test_db  # type: ignore[assignment]

    yield client
    await client.drop_database(TEST_DB)
    client.close()


@pytest.fixture(scope="session")
async def test_db(
    motor_client: AsyncIOMotorClient[dict[str, Any]],
) -> AsyncIOMotorDatabase[dict[str, Any]]:
    db = motor_client[TEST_DB]
    await db_module.ensure_indexes()
    await db_module.seed_categories()
    return db  # type: ignore[return-value]


@pytest.fixture(scope="session")
async def ac(
    test_db: AsyncIOMotorDatabase[dict[str, Any]],
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
