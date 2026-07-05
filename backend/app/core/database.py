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
    await db["tasks"].create_index("task_id", unique=True)
    await db["tasks"].create_index("due_date")
    await db["tasks"].create_index("category_id")
    await db["tasks"].create_index("is_done")
    await db["categories"].create_index("category_id", unique=True)
    await db["categories"].create_index("name", unique=True)
    await db["milestones"].create_index("milestone_id", unique=True)
    logger.info("MongoDB indexes ensured")
