# Changelog

Phase별 완료 기록과 주요 변경 사항.
형식: `## [Phase N] YYYY-MM-DD` → 완료 항목 나열

---

## [Redesign] 2026-07-05

**도메인 전환: Harness Engineering → Todo List API**

- 기존 하네스 엔지니어링 도메인 코드 전체 제거
- UI 목업(대시보드, 할 일 목록, 데일리 플랜, 새 할 일) 기반으로 재설계
- `docs/api-spec.md` 전면 재작성 (Task / Category / Stats / Milestone)
- `docs/domain-rules.md` 전면 재작성
- `CLAUDE.md` 업데이트 (Phase 3~7 리셋)
- Core 인프라 유지 (Phase 1, 2, 8)

---

## [Phase 1–2, 8] (기존 인프라 — 재사용)

- Phase 1: 프로젝트 초기화 (requirements, .env, pyproject.toml)
- Phase 2: Core 레이어 (config, database, exceptions, lifespan)
- Phase 8: Docker & local dev (docker-compose, Makefile)
