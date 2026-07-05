# Backend Agent Rules — FastAPI + MongoDB + Harness Engineering

## Stack & Runtime
- Python 3.12+, FastAPI, Motor (async MongoDB driver), Pydantic v2
- All I/O (DB, HTTP) must be `async`/`await` — never use synchronous Motor or `requests`
- Entry point: `app/main.py`; API versioned under `/api/v1/`

## Project Layer Architecture

```
app/
  api/v1/endpoints/   ← thin HTTP layer: validate input, call service, return schema
  services/           ← business logic, harness validation rules
  repositories/       ← all MongoDB queries (Motor), no business logic here
  models/             ← internal domain dataclasses / ODM-adjacent
  schemas/            ← Pydantic request/response models (never expose ODM models)
  core/               ← config (pydantic-settings), DB lifespan, shared utils
```

Rules:
- Endpoints call services; services call repositories. Never skip layers.
- Repositories return plain dicts or domain models — never return Motor cursors to callers.
- Schemas used for API I/O are defined in `schemas/`; internal domain objects go in `models/`.

## FastAPI Conventions
- Use `APIRouter` per resource; register in `app/api/v1/router.py`.
- Inject the DB via `Depends(get_db)` — never import `client` directly in endpoints/services.
- Use FastAPI lifespan (`@asynccontextmanager`) for `connect_db` / `close_db`; do not use deprecated `startup`/`shutdown` events.
- HTTP status codes: 201 for creation, 404 with detail message for not-found, 422 auto from Pydantic, 409 for duplicate key conflicts.
- Always type-annotate route return types with `response_model=`.

## MongoDB / Motor Rules
- Collection names: lowercase plural snake_case (`wires`, `connectors`, `harness_drawings`).
- All `_id` fields stored as MongoDB `ObjectId`; serialize to `str` in response schemas using `PyObjectId` alias pattern.
- Use `motor.motor_asyncio.AsyncIOMotorCollection` type annotations in repositories.
- Index creation goes in a dedicated `ensure_indexes()` called at startup, not inline in queries.
- Never do N+1 queries; use `$lookup` aggregation or batch `$in` queries.
- Connection string from `settings.MONGODB_URL`; database name from `settings.DATABASE_NAME` — no hardcoding.

## Harness Engineering Domain Rules

### Entities
| Entity | Collection | Key fields |
|---|---|---|
| Wire | `wires` | `wire_id`, `gauge_awg`, `material`, `color`, `length_mm`, `insulation_rating_v` |
| Connector | `connectors` | `connector_id`, `manufacturer`, `pin_count`, `housing_type`, `gender`, `mating_connector_id` |
| HarnessDrawing | `harness_drawings` | `drawing_id`, `revision`, `title`, `wire_ids[]`, `connector_ids[]`, `circuits[]` |
| Circuit | embedded in drawing | `circuit_id`, `from_connector_pin`, `to_connector_pin`, `wire_id`, `signal_name` |

### Validation Rules (enforced in service layer, not just schema)
- `gauge_awg` must be one of valid AWG sizes: `[30, 28, 26, 24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]`
- `insulation_rating_v` must be positive; warn (log) if < 12 V for automotive context
- `pin_count` must match the actual number of `circuits` referencing that connector
- `from_connector_pin` and `to_connector_pin` must be within bounds of their connector's `pin_count`
- No circuit may reference a `wire_id` or `connector_id` that does not exist in the DB (referential integrity check in service)
- `mating_connector_id` pairing must be symmetric: if A mates B, B must mate A
- `revision` on `HarnessDrawing` follows `[A-Z]` single-letter format; bump on every update
- Duplicate `circuit_id` within the same drawing is a 409 conflict

### Drawing Validation Endpoint
`POST /api/v1/harness/drawings/{drawing_id}/validate` — runs full integrity check and returns a structured report:
```json
{ "valid": false, "errors": [...], "warnings": [...] }
```
Never raise HTTP 422 from business validation — return the report object with `valid: false`.

## Pydantic v2 Rules
- Use `model_config = ConfigDict(...)` instead of inner `class Config`.
- Use `Field(alias="...")` for MongoDB `_id` ↔ `id` mapping.
- Use `model_validator(mode="after")` for cross-field harness validation in schemas.
- Avoid `Optional[X]` — prefer `X | None` with explicit `= None` default.

## Error Handling
- Define custom exceptions in `app/core/exceptions.py`: `HarnessValidationError`, `EntityNotFoundError`, `DuplicateEntityError`.
- Register exception handlers in `main.py` — do not use `try/except` in endpoints for these.
- Log at `ERROR` level with full context dict (never bare `print()`).

## Testing
- Tests in `tests/`; use `pytest-asyncio` with `asyncio_mode = "auto"` in `pyproject.toml`.
- Use a real test MongoDB (local or Docker); no mocking of the DB layer.
- Fixture for DB client in `tests/conftest.py`; drop test collections in teardown.
- Each endpoint test covers: happy path, not-found, invalid input, and harness-specific validation failure.

## Code Style
- `ruff` for linting + formatting; `mypy` for type checking (strict on domain models).
- No `print()` — use `logging.getLogger(__name__)`.
- No inline comments explaining *what* code does — only *why* if non-obvious.
- Function names: `async def get_wire_by_id(...)` not `async def getWire(...)`.
