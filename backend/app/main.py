from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_db, connect_db, ensure_indexes, seed_categories
from app.core.exceptions import (
    AppValidationError,
    DuplicateEntityError,
    EntityInUseError,
    EntityNotFoundError,
    app_validation_handler,
    duplicate_entity_handler,
    entity_in_use_handler,
    entity_not_found_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await connect_db()
    await ensure_indexes()
    await seed_categories()
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
app.add_exception_handler(AppValidationError, app_validation_handler)  # type: ignore[arg-type]

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
