# Claude Harness Todo — AI 주도 개발 Todo 앱

Claude Code의 **Harness Engineering** 방식으로 제작한 풀스택 Todo List 애플리케이션입니다.
백엔드부터 프론트엔드까지 6개 Phase로 나눠 AI가 설계·구현·테스트까지 일관되게 수행했습니다.

---

## Harness Engineering이란?

Harness Engineering은 AI 에이전트가 단순히 코드 조각을 생성하는 것을 넘어,
**프로젝트 전체 구조를 이해하고 스스로 판단하며 개발 사이클을 완주**하는 방식입니다.

핵심 원칙:

- **CLAUDE.md로 컨텍스트 주입** — 스택, 컨벤션, Phase 계획을 문서화해 에이전트가 매 대화에서 일관된 판단을 내리게 함
- **Phase 단위 브랜치 관리** — 각 Phase를 독립 feature 브랜치에서 구현하고 GitHub PR로 리뷰 후 머지
- **자동화된 검증** — 커밋마다 테스트·린트가 통과해야 다음 단계로 진행
- **설계→구현→테스트 일관성** — 에이전트가 스펙 문서를 직접 참조하며 구현하므로 드리프트 없음

---

## 프로젝트 구조

```
claude_harness_todo/
├── backend/          # FastAPI + Motor + MongoDB
│   ├── app/
│   │   ├── api/v1/endpoints/   # tasks, categories, stats, milestones
│   │   ├── core/               # config, db 연결, 예외 처리
│   │   ├── models/             # 도메인 모델 (dataclass)
│   │   ├── repositories/       # Motor 비동기 CRUD
│   │   ├── schemas/            # Pydantic v2 I/O 스키마
│   │   └── services/           # 비즈니스 로직 & 유효성 검사
│   ├── tests/
│   │   ├── unit/               # 순수 함수 단위 테스트
│   │   └── integration/        # 실 DB 연동 통합 테스트
│   └── docs/
│       ├── api-spec.md         # 전체 엔드포인트 스펙
│       └── domain-rules.md     # 도메인 규칙 정의
└── frontend/         # Next.js 16 + React 19 + TypeScript
    ├── src/
    │   ├── pages/              # 대시보드, 할 일 목록, 추가 폼, 통계
    │   ├── components/         # layout, tasks, stats, dashboard, ui
    │   ├── lib/api/            # fetch 기반 API 클라이언트
    │   └── styles/             # CSS Modules + 디자인 토큰
    └── docs/
        ├── api.md              # 백엔드 API 연동 가이드
        ├── design.md           # Figma 디자인 시스템
        ├── screens.md          # 화면별 구현 노트
        └── structure.md        # 개발 Phase 계획
```

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 백엔드 프레임워크 | FastAPI |
| 비동기 DB 드라이버 | Motor (MongoDB) |
| 스키마 유효성 검사 | Pydantic v2 |
| 백엔드 테스트 | pytest-asyncio |
| 프론트엔드 프레임워크 | Next.js 16.2 (Pages Router) |
| UI 라이브러리 | React 19 |
| 언어 | TypeScript 5 |
| 스타일링 | CSS Modules |
| 프론트 테스트 | Jest 30 + Testing Library |
| 인프라 | Docker Compose |

---

## 개발 Phase 기록

### Backend

| Phase | 내용 | 브랜치 |
|-------|------|--------|
| 1 | 프로젝트 구조 + 도메인 모델 + 스키마 설계 | `feat/phase-1-base` |
| 2 | MongoDB 연동 + Repository 레이어 | `feat/phase-2-dashboard` |
| 3 | Service 레이어 + 비즈니스 로직 | `feat/phase-3-models-schemas` |
| 4 | API 엔드포인트 (tasks, categories, stats, milestones) | `feat/phase-4-repositories` |
| 5 | 통계 API + 마일스톤 로직 | `feat/phase-5-services` |
| 6 | pytest 단위 + 통합 테스트 | `feat/phase-6-api-endpoints` |

### Frontend

| Phase | 내용 | 브랜치 |
|-------|------|--------|
| 1 | 디자인 토큰 + 공통 컴포넌트 (Layout, BottomNav, TaskItem) | `feat/phase-1-base` |
| 2 | API 클라이언트 + 타입 정의 + 대시보드 페이지 | `feat/phase-2-dashboard` |
| 3 | 할 일 목록 + 완료 토글 + FAB | `feat/phase-3-tasklist` |
| 4 | 할 일 추가 폼 + 유효성 검사 | `feat/phase-4-add-task` |
| 5 | 통계 페이지 (주간 차트 + 마일스톤 + 인사이트 배너) | `feat/phase-5-stats` |
| 6 | Jest 테스트 26개 (컴포넌트 + API 함수) | `feat/phase-6-tests` |

---

## API 엔드포인트 요약

```
Base URL: http://localhost:8000/api/v1

GET    /tasks                    # 목록 조회 (date, category_id, done, priority 필터)
POST   /tasks                    # 태스크 생성
GET    /tasks/{task_id}          # 단건 조회
PUT    /tasks/{task_id}          # 수정
DELETE /tasks/{task_id}          # 삭제
PATCH  /tasks/{task_id}/done     # 완료 토글

GET    /categories               # 카테고리 목록
POST   /categories               # 커스텀 카테고리 생성
DELETE /categories/{category_id} # 삭제 (기본 카테고리 삭제 시 409)

GET    /stats/dashboard          # 오늘 집계 + 우선순위 태스크
GET    /stats/weekly             # 주간 완료/전체 수
GET    /stats/insights           # 생산성 피크 시간대

GET    /milestones               # 달성된 마일스톤 목록
GET    /health                   # 서버 상태
```

---

## 주요 도메인 규칙

- `is_done` 변경은 `PATCH /done` 으로만 가능 (PUT에서 직접 수정 불가)
- `due_time`은 `due_date` 없이 사용 불가 → 422 오류
- 우선순위: `low | medium | high` (기본값 `medium`)
- 기본 카테고리 4개 (업무, 개인, 긴급, 집중)는 삭제 불가 → 409 오류

---

## 화면 구성

| 경로 | 화면 |
|------|------|
| `/` | 대시보드 — 오늘 진행률, 우선순위 할 일 3개, 예정된 일정 |
| `/tasks` | 할 일 목록 — 오늘/예정 섹션, 완료 토글 |
| `/tasks/new` | 할 일 추가 폼 — 제목, 마감일/시간, 카테고리, 우선순위, 메모 |
| `/stats` | 통계 — 집중도 점수, 주간 바 차트, 마일스톤, 인사이트 배너 |

---

## 로컬 실행

```bash
# 백엔드 (MongoDB 필요)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 또는 Docker Compose
docker-compose up

# 프론트엔드
cd frontend
npm install
npm run dev       # http://localhost:3000
```

---

## 테스트 실행

```bash
# 백엔드
cd backend && pytest

# 프론트엔드
cd frontend && npm test
```
