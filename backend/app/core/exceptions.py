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


class EntityInUseError(Exception):
    def __init__(self, entity: str, entity_id: str, reason: str):
        self.entity = entity
        self.entity_id = entity_id
        self.reason = reason
        super().__init__(f"{entity} '{entity_id}' cannot be deleted: {reason}")


class AppValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {errors}")


async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def duplicate_entity_handler(request: Request, exc: DuplicateEntityError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def entity_in_use_handler(request: Request, exc: EntityInUseError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def app_validation_handler(request: Request, exc: AppValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors})
