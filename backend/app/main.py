from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_db, connect_db, ensure_indexes
from app.core.exceptions import (
    DuplicateEntityError,
    EntityInUseError,
    EntityNotFoundError,
    HarnessValidationError,
    duplicate_entity_handler,
    entity_in_use_handler,
    entity_not_found_handler,
    harness_validation_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await connect_db()
    await ensure_indexes()
    yield
    await close_db()


app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)  # type: ignore[arg-type]
app.add_exception_handler(DuplicateEntityError, duplicate_entity_handler)  # type: ignore[arg-type]
app.add_exception_handler(EntityInUseError, entity_in_use_handler)  # type: ignore[arg-type]
app.add_exception_handler(HarnessValidationError, harness_validation_handler)  # type: ignore[arg-type]

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
