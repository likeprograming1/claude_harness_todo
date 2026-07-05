from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
import app.core.database as db_module

TEST_DB_NAME = "harness_test_db"

# Redirect all DB operations to the isolated test database
settings.DATABASE_NAME = TEST_DB_NAME  # type: ignore[misc]

from app.main import app  # noqa: E402


@pytest_asyncio.fixture(scope="session")
async def motor_client() -> AsyncGenerator[AsyncIOMotorClient, None]:  # type: ignore[type-arg]
    """
    Create a dedicated Motor client for the test session and inject it into
    the database module. ASGITransport does not run the ASGI lifespan, so
    connect_db() never fires — we wire the client manually here.
    """
    client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://127.0.0.1:27017")  # type: ignore[type-arg]
    db_module.client = client  # type: ignore[assignment]
    yield client
    await client.drop_database(TEST_DB_NAME)
    db_module.client = None
    client.close()


@pytest_asyncio.fixture(scope="session")
async def http_client(motor_client: AsyncIOMotorClient) -> AsyncGenerator[AsyncClient, None]:  # type: ignore[type-arg]
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def clean_db(motor_client: AsyncIOMotorClient) -> None:  # type: ignore[type-arg]
    """Drop and re-index all collections before every test."""
    db = motor_client[TEST_DB_NAME]
    for name in await db.list_collection_names():
        await db.drop_collection(name)
    await db["wires"].create_index("wire_id", unique=True)
    await db["connectors"].create_index("connector_id", unique=True)
    await db["harness_drawings"].create_index("drawing_id", unique=True)
    await db["harness_drawings"].create_index("wire_ids")
    await db["harness_drawings"].create_index("connector_ids")
