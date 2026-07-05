from fastapi import Request
from fastapi.responses import JSONResponse


class EntityNotFoundError(Exception):
    def __init__(self, entity: str, entity_id: str):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} '{entity_id}' not found")


class DuplicateEntityError(Exception):
    def __init__(self, entity: str, field: str, value: str):
        self.entity = entity
        self.field = field
        self.value = value
        super().__init__(f"{entity} with {field}='{value}' already exists")


class HarnessValidationError(Exception):
    def __init__(self, errors: list[str], warnings: list[str] | None = None):
        self.errors = errors
        self.warnings = warnings or []
        super().__init__(f"Harness validation failed: {errors}")


async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def duplicate_entity_handler(request: Request, exc: DuplicateEntityError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
