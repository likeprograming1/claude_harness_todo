import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient[dict[str, Any]] | None = None


async def connect_db() -> None:
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    logger.info("MongoDB connected: %s", settings.MONGODB_URL)


async def close_db() -> None:
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase[dict[str, Any]]:
    if client is None:
        raise RuntimeError("Database client is not initialized")
    return client[settings.DATABASE_NAME]


async def ensure_indexes() -> None:
    db = get_db()
    await db["wires"].create_index("wire_id", unique=True)
    await db["connectors"].create_index("connector_id", unique=True)
    await db["harness_drawings"].create_index("drawing_id", unique=True)
    await db["harness_drawings"].create_index("wire_ids")
    await db["harness_drawings"].create_index("connector_ids")
    logger.info("MongoDB indexes ensured")
