# Changelog

Phase별 완료 기록과 주요 변경 사항을 여기에 추가합니다.  
형식: `## [Phase N] YYYY-MM-DD` → 완료 항목 나열

---

## [Phase 5] 2026-07-05

**Services + Unit Tests** — `feat/phase-5-services`

- `app/services/wire_service.py` — WireService (CRUD + delete 시 참조 도면 충돌 검사)
- `app/services/connector_service.py` — ConnectorService (CRUD + delete 시 참조 도면 충돌 검사)
- `app/services/harness_drawing_service.py` — HarnessDrawingService (CRUD + 개정 자동 증가 + validate_drawing)
- `tests/unit/test_wire_service.py`
- `tests/unit/test_connector_service.py`
- `tests/unit/test_harness_drawing_service.py`
- 단위 테스트 **24/24 pass**

---

## [Infra] 2026-07-05

**MongoDB 로컬 Docker 연결 설정**

- `.env`, `.env.example`, `app/core/config.py` 기본값을 `mongodb://127.0.0.1:27017`으로 통일
- 배포 전까지 Atlas URI 제외, 로컬 Docker 컨테이너 기준으로 개발

---

## [Phase 1–4] (초기 구축)

- Phase 1: 프로젝트 초기화 (requirements, .env, pyproject.toml)
- Phase 2: Core 레이어 (config, database, exceptions, lifespan)
- Phase 3: Domain models & Pydantic v2 schemas
- Phase 4: Repositories (BaseRepository + wire / connector / harness_drawing)
- Phase 8: Docker & local dev (docker-compose, Makefile)
