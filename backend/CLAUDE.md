# Todo List API — Backend

## Stack
FastAPI · Motor (async MongoDB) · Pydantic v2 · Python 3.12+
Dev tools: ruff · mypy · pytest-asyncio

---

## Directory Structure

```
app/
  api/v1/endpoints/   # FastAPI routers (tasks.py, categories.py, stats.py, milestones.py)
  core/               # config, database, exceptions, types
  models/             # Python dataclasses (domain models)
  repositories/       # Motor async CRUD (base.py + per-entity)
  schemas/            # Pydantic v2 I/O schemas
  services/           # Business logic & validation
docs/
  api-spec.md         # Endpoint specification (routes, requests, responses, status codes)
  domain-rules.md     # Todo domain rules (priority, category, milestone logic)
tests/
  unit/               # Pure business logic unit tests (no DB)
  integration/        # Integration tests against a real Motor client with isolated test DB
```

---

## Development Workflow

> **Always work in a feature branch. Never push directly to `main`.**

### Per-task steps
1. **Create a branch** before starting any task:
   ```
   git checkout -b feat/phase-X-short-description
   ```
2. **Propose changes first** — show diffs or describe the edit, then apply only after review.
3. **Commit** when a logical unit is complete with a descriptive message.
4. **Push** to the feature branch — the auto-push hook handles this (`.claude/settings.json`).
5. **Open a PR** to merge into `main` once the branch is ready.
6. **PR must be merged before starting the next phase** — never begin a new phase on an unmerged branch.

### Branch naming convention
| Prefix | Use |
|--------|-----|
| `feat/` | New feature or phase implementation |
| `fix/` | Bug fix |
| `docs/` | Documentation only |
| `test/` | Test additions or fixes |
| `refactor/` | Refactoring without behaviour change |

---

## Code Conventions

- **Async**: all DB operations use `async/await` (Motor)
- **Types**: `mypy --strict` must pass. Minimise `Any`; annotate every `# type: ignore` with the reason
- **Lint**: `ruff check` must pass before every commit
- **Schema separation**: never mix Pydantic schemas (`schemas/`) with dataclass models (`models/`)
- **Exceptions**: use only `EntityNotFoundError`, `DuplicateEntityError`, `EntityInUseError`, `AppValidationError` from `app/core/exceptions.py`
- **MongoDB `_id`**: fully converted to `mongo_id: str` inside the repository layer — never expose `ObjectId` above repositories
- **Indexes**: managed exclusively in `ensure_indexes()` — register every new collection there

---

## Testing Policy

Tests are written **alongside** each feature. A phase is not complete until its tests pass.

| Layer | Location | Scope |
|-------|----------|-------|
| Validators, service logic | `tests/unit/` | No DB, pure Python |
| Repository CRUD, integrity | `tests/integration/` | Real Motor client, isolated test DB |

### Required coverage per feature
- Happy path (201 / 200)
- Validation errors → 422
- Not-found → 404
- Conflict → 409 (duplicate, delete default category, etc.)
- Domain-specific edge cases (see `docs/domain-rules.md`)

### Commands
```bash
make test        # pytest --asyncio-mode=auto
make lint        # ruff check app/
make typecheck   # mypy app/
```

---

## Phase Progress

| Phase | Content | Status |
|-------|---------|--------|
| 1 | Project init (requirements, .env, pyproject.toml) | ✅ |
| 2 | Core (config, database, exceptions, lifespan) | ✅ |
| 3 | Domain models & schemas (Task, Category, Milestone) | 🔲 |
| 4 | Repositories (base + task / category / milestone) | 🔲 |
| 5 | Services (business logic, validation) + unit tests | 🔲 |
| 6 | API Endpoints + router registration + integration tests | 🔲 |
| 7 | Full test suite (conftest, task / category / stats) | 🔲 |
| 8 | Docker & local dev (docker-compose, Makefile) | ✅ |

---

## References

- Endpoint specification → [`docs/api-spec.md`](docs/api-spec.md)
- Domain business rules → [`docs/domain-rules.md`](docs/domain-rules.md)
- Phase changelog → [`docs/CHANGELOG.md`](docs/CHANGELOG.md)
