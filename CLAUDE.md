# claude_harness_todo

Full-stack Harness Engineering application.

## Structure

| Directory | Stack | Status |
|-----------|-------|--------|
| `backend/` | FastAPI · Motor · Pydantic v2 · Python 3.12+ | Active |
| `frontend/` | TBD | Planned |

## Development Workflow

> All work happens in feature branches — never commit directly to `main`.

- Per-module details and phase progress: see each subdirectory's `CLAUDE.md`
- Branch naming: `feat/`, `fix/`, `docs/`, `test/`, `refactor/`
- Auto-push hook active for feature branches (`.claude/settings.json`)

## References

- Backend spec → [`backend/CLAUDE.md`](backend/CLAUDE.md)
- API endpoints → [`backend/docs/api-spec.md`](backend/docs/api-spec.md)
- Domain rules → [`backend/docs/domain-rules.md`](backend/docs/domain-rules.md)
