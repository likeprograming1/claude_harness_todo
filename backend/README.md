# claude_harness_todo

Todo List REST API — FastAPI · Motor · Pydantic v2 · MongoDB

---

## 목차

- [스택](#스택)
- [프로젝트 구조](#프로젝트-구조)
- [사전 요구사항](#사전-요구사항)
- [로컬 개발 환경 실행](#로컬-개발-환경-실행)
- [Docker로 실행](#docker로-실행)
- [환경 변수](#환경-변수)
- [Makefile 명령어](#makefile-명령어)
- [API 명세](#api-명세)
  - [Task](#task---apiv1tasks)
  - [Category](#category---apiv1categories)
  - [Stats](#stats---apiv1stats)
  - [Milestone](#milestone---apiv1milestones)
  - [Health](#health)
  - [공통 에러 형식](#공통-에러-형식)
- [도메인 규칙](#도메인-규칙)
- [기본 카테고리](#기본-카테고리)
- [마일스톤 달성 조건](#마일스톤-달성-조건)
- [테스트](#테스트)

---

## 스택

| 구분 | 기술 |
|------|------|
| Runtime | Python 3.12+ |
| Framework | FastAPI 0.115 |
| DB Driver | Motor 3.6 (async MongoDB) |
| Validation | Pydantic v2 |
| DB | MongoDB 7 |
| Lint | Ruff |
| Type check | mypy (strict) |
| Test | pytest-asyncio 0.24 |

---

## 프로젝트 구조

```
claude_harness_todo/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # FastAPI 라우터 (tasks, categories, stats, milestones)
│   │   ├── core/               # config, database, exceptions, types
│   │   ├── models/             # Python 도메인 모델 (dataclass)
│   │   ├── repositories/       # Motor 비동기 CRUD
│   │   ├── schemas/            # Pydantic v2 I/O 스키마
│   │   └── services/           # 비즈니스 로직
│   ├── tests/
│   │   ├── unit/               # 순수 로직 단위 테스트 (DB 없음)
│   │   └── integration/        # 실제 Motor 클라이언트 통합 테스트
│   ├── docs/
│   │   ├── api-spec.md
│   │   └── domain-rules.md
│   ├── Dockerfile
│   ├── Makefile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
├── docker-compose.yml
└── README.md
```

---

## 사전 요구사항

- Python 3.12+
- Docker & Docker Compose (MongoDB 로컬 실행용)
- pip

---

## 로컬 개발 환경 실행

### 1. 의존성 설치

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate    # Git Bash / Windows
# PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

### 2. 환경 변수 설정

```bash
cp backend/.env.example backend/.env
# .env 내용은 기본값으로 로컬 MongoDB를 가리킴 (수정 불필요)
```

### 3. MongoDB 실행 (Docker)

```bash
# 프로젝트 루트에서 MongoDB만 기동
docker compose up -d mongo
```

### 4. API 서버 실행

```bash
cd backend
make dev
# 또는: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면 다음 URL에서 확인:

- API: `http://localhost:8000/api/v1/`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

---

## Docker로 실행

백엔드 + MongoDB를 모두 컨테이너로 실행합니다.

```bash
# 루트 디렉토리에서
docker compose up -d --build

# 로그 확인
docker compose logs -f backend

# 종료
docker compose down
```

> MongoDB 컨테이너가 healthy 상태가 된 후 백엔드가 자동으로 기동됩니다 (health check 연결).

---

## 환경 변수

`backend/.env` 파일에서 관리합니다. `.env.example`을 참조하세요.

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `PROJECT_NAME` | `claude-harness-todo` | FastAPI 앱 이름 |
| `MONGODB_URL` | `mongodb://127.0.0.1:27017` | MongoDB 연결 URI |
| `DATABASE_NAME` | `harness_db` | 사용할 데이터베이스 이름 |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | 허용할 CORS 오리진 목록 |

Docker 실행 시 `MONGODB_URL`은 `mongodb://mongo:27017`으로 자동 설정됩니다 (docker-compose.yml).

---

## Makefile 명령어

`backend/` 디렉토리에서 실행합니다.

| 명령어 | 설명 |
|--------|------|
| `make install` | 프로덕션 의존성 설치 (`requirements.txt`) |
| `make install-dev` | 개발 의존성 설치 (`requirements-dev.txt`) |
| `make dev` | uvicorn 개발 서버 실행 (hot reload) |
| `make test` | 전체 테스트 실행 (단위 + 통합) |
| `make lint` | Ruff 린트 검사 |
| `make typecheck` | mypy 타입 검사 |
| `make clean` | 캐시 디렉토리 정리 (`__pycache__`, `.pytest_cache` 등) |
| `make docker-up` | Docker Compose로 전체 스택 기동 |
| `make docker-down` | Docker Compose 종료 |
| `make docker-logs` | 백엔드 컨테이너 로그 스트리밍 |

---

## API 명세

**Base URL:** `http://localhost:8000/api/v1`  
**Content-Type:** `application/json`

---

### Task — `/api/v1/tasks`

#### `GET /tasks` — 할 일 목록 조회

쿼리 파라미터로 필터링합니다.

**Query Parameters**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `date` | `YYYY-MM-DD` | 해당 날짜의 due_date 필터 |
| `category_id` | string | 카테고리 ID 필터 |
| `done` | boolean | 완료 여부 필터 (`true` / `false`) |
| `priority` | `low` \| `medium` \| `high` | 우선순위 필터 |

**Response 200**

```json
[
  {
    "id": "64abc123def456",
    "task_id": "T001",
    "title": "디자인 시스템 문서 검토",
    "priority": "high",
    "is_done": false,
    "due_date": "2024-10-24",
    "due_time": "09:00",
    "category_id": "cat_work",
    "notes": null,
    "completed_at": null,
    "created_at": "2024-10-23T10:00:00"
  }
]
```

---

#### `POST /tasks` — 할 일 생성

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `title` | string | ✅ | 1~200자 |
| `task_id` | string | | 직접 지정 (생략 시 서버 자동 생성, 최대 50자) |
| `priority` | `low` \| `medium` \| `high` | | 기본값 `medium` |
| `due_date` | `YYYY-MM-DD` | | 마감일 |
| `due_time` | `HH:MM` | | 마감 시각 (due_date 없이 단독 사용 불가) |
| `category_id` | string | | 카테고리 ID (존재하는 카테고리여야 함) |
| `notes` | string | | 메모 (최대 1000자) |

**Request Body 예시**

```json
{
  "title": "주간 보고서 작성",
  "priority": "high",
  "due_date": "2024-10-25",
  "due_time": "17:00",
  "category_id": "cat_work",
  "notes": "3분기 실적 포함"
}
```

**Response 201** — TaskResponse  
**Response 409** — `task_id` 중복  
**Response 422** — title 누락, due_time without due_date, 존재하지 않는 category_id, 형식 오류

---

#### `GET /tasks/{task_id}` — 할 일 단건 조회

**Response 200** — TaskResponse  
**Response 404** — task_id 없음

---

#### `PUT /tasks/{task_id}` — 할 일 수정

제공된 필드만 업데이트합니다. 필드를 `null`로 보내면 값을 초기화합니다.

**Request Body** — TaskUpdate (모든 필드 선택)

| 필드 | 타입 | 설명 |
|------|------|------|
| `title` | string \| null | 1~200자 |
| `priority` | `low` \| `medium` \| `high` \| null | |
| `due_date` | `YYYY-MM-DD` \| null | |
| `due_time` | `HH:MM` \| null | |
| `category_id` | string \| null | |
| `notes` | string \| null | |

**Response 200** — TaskResponse  
**Response 404** — task_id 없음  
**Response 422** — due_time without due_date, 존재하지 않는 category_id

---

#### `DELETE /tasks/{task_id}` — 할 일 삭제

**Response 204** — 삭제 성공 (body 없음)  
**Response 404** — task_id 없음

---

#### `PATCH /tasks/{task_id}/done` — 완료 상태 토글

완료(done) ↔ 미완료(not done)를 토글합니다.  
완료로 전환 시 `completed_at`이 현재 UTC 시각으로 설정됩니다.  
미완료로 전환 시 `completed_at`이 `null`로 초기화됩니다.  
완료 토글 후 마일스톤 달성 조건을 자동으로 평가합니다.

**Response 200** — TaskResponse  
**Response 404** — task_id 없음

---

### TaskResponse 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | MongoDB document id |
| `task_id` | string | 비즈니스 식별자 |
| `title` | string | 제목 |
| `priority` | `low` \| `medium` \| `high` | 우선순위 |
| `is_done` | boolean | 완료 여부 |
| `due_date` | `YYYY-MM-DD` \| null | 마감일 |
| `due_time` | `HH:MM` \| null | 마감 시각 |
| `category_id` | string \| null | 카테고리 ID |
| `notes` | string \| null | 메모 |
| `completed_at` | ISO8601 \| null | 완료 시각 (UTC) |
| `created_at` | ISO8601 | 생성 시각 (UTC) |

---

### Category — `/api/v1/categories`

#### `GET /categories` — 카테고리 목록 조회

기본 카테고리(업무·개인·긴급·집중) + 커스텀 카테고리를 모두 반환합니다.

**Response 200**

```json
[
  {
    "id": "64abc...",
    "category_id": "cat_work",
    "name": "업무",
    "color": "#4A6FFF",
    "is_default": true
  },
  {
    "id": "64def...",
    "category_id": "a1b2c3d4",
    "name": "스터디",
    "color": "#9B59B6",
    "is_default": false
  }
]
```

---

#### `POST /categories` — 커스텀 카테고리 생성

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | ✅ | 1~50자, 중복 불가 |
| `color` | string | | Hex 컬러 코드 (`#RRGGBB`), 기본값 `#888888` |

**Request Body 예시**

```json
{
  "name": "스터디",
  "color": "#9B59B6"
}
```

**Response 201** — CategoryResponse  
**Response 409** — 동일 name 중복

---

#### `DELETE /categories/{category_id}` — 카테고리 삭제

**Response 204** — 삭제 성공  
**Response 404** — category_id 없음  
**Response 409** — 기본 카테고리는 삭제 불가

---

### CategoryResponse 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | MongoDB document id |
| `category_id` | string | 비즈니스 식별자 |
| `name` | string | 카테고리 이름 |
| `color` | string | Hex 컬러 코드 |
| `is_default` | boolean | 기본 카테고리 여부 |

---

### Stats — `/api/v1/stats`

#### `GET /stats/dashboard` — 대시보드

오늘 날짜 기준 집계 데이터를 반환합니다.

**Response 200**

```json
{
  "today": "2024-10-24",
  "total_today": 5,
  "completed_today": 3,
  "completion_rate": 60.0,
  "focus_score": 60,
  "priority_tasks": [
    { "task_id": "T001", "title": "기획 회의", "priority": "high", ... }
  ],
  "upcoming": [
    { "task_id": "T002", "title": "주간 보고", "due_date": "2024-10-25", ... }
  ]
}
```

| 필드 | 설명 |
|------|------|
| `completion_rate` | 오늘 완료율 (%, 소수점 1자리) |
| `focus_score` | 오늘 집중도 점수 0~100 (완료/전체 × 100, 정수) |
| `priority_tasks` | 오늘 미완료 태스크 중 우선순위 높은 순 최대 3개 |
| `upcoming` | 오늘 이후 due_date를 가진 미완료 태스크 (날짜 오름차순) |

---

#### `GET /stats/weekly` — 주간 통계

오늘 기준 최근 7일간 일별 집계를 반환합니다.

**Response 200**

```json
{
  "days": [
    { "date": "2024-10-18", "total": 4, "completed": 3 },
    { "date": "2024-10-19", "total": 2, "completed": 2 },
    { "date": "2024-10-20", "total": 0, "completed": 0 },
    { "date": "2024-10-21", "total": 5, "completed": 1 },
    { "date": "2024-10-22", "total": 3, "completed": 3 },
    { "date": "2024-10-23", "total": 6, "completed": 4 },
    { "date": "2024-10-24", "total": 5, "completed": 3 }
  ]
}
```

---

#### `GET /stats/insights` — 스마트 인사이트

완료 태스크의 `completed_at` 시각 분포를 분석해 생산성이 가장 높은 2시간 구간을 반환합니다.

**Response 200 — 데이터 충분 시 (완료 태스크 ≥ 5개)**

```json
{
  "peak_start": "09:00",
  "peak_end": "11:00",
  "message": "09:00~11:00 사이에 가장 생산적입니다."
}
```

**Response 200 — 데이터 부족 시**

```json
{
  "peak_start": null,
  "peak_end": null,
  "message": "데이터가 부족합니다. 더 많은 태스크를 완료하면 인사이트를 제공할 수 있습니다."
}
```

---

### Milestone — `/api/v1/milestones`

마일스톤은 API로 직접 생성/수정/삭제할 수 없습니다. 태스크 완료 이벤트 후 서비스 계층이 자동으로 조건을 평가하여 발급합니다.

#### `GET /milestones` — 달성 마일스톤 목록

달성된 마일스톤을 최신순으로 반환합니다.

**Response 200**

```json
[
  {
    "id": "64abc...",
    "milestone_id": "total_10",
    "title": "첫 번째 10개 달성",
    "description": "할 일 10개를 완료했습니다.",
    "achieved_at": "2024-10-24"
  }
]
```

---

### Health

#### `GET /health` — 헬스 체크

**Response 200**

```json
{ "status": "ok" }
```

---

### 공통 에러 형식

| HTTP 상태 | 의미 | 발생 조건 |
|-----------|------|---------|
| `422 Unprocessable Entity` | 유효성 검사 실패 | Pydantic 검증 오류, 비즈니스 규칙 위반 |
| `404 Not Found` | 엔티티 없음 | 존재하지 않는 ID 조회/수정/삭제 |
| `409 Conflict` | 충돌 | task_id/category name 중복, 기본 카테고리 삭제 시도 |

**422 에러 응답 예시**

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "due_time"],
      "msg": "Value error, due_time requires due_date to be set",
      "input": "09:00"
    }
  ]
}
```

**404 / 409 에러 응답 예시**

```json
{
  "detail": "Task 'T001' not found"
}
```

---

## 도메인 규칙

### Task

- `task_id`: 클라이언트 직접 제공 또는 서버 자동 생성 (UUID4 단축형). 컬렉션 내 유일 → 중복 시 409
- `title`: 필수, 1~200자
- `due_time`: `due_date` 없이 단독 사용 불가 → 422
- `priority` 기본값: `medium`
- `category_id`: 제공 시 반드시 존재하는 카테고리여야 함 → 없으면 422
- `is_done`: `PATCH /tasks/{id}/done`으로만 토글 가능
- `created_at`: 서버 자동 부여 (UTC), 클라이언트 제공 불가

### Category

- 기본 카테고리 4개는 앱 시작 시 자동 seed, 삭제 불가 → 409
- 커스텀 카테고리 name: 1~50자, 컬렉션 내 유일 → 중복 시 409
- color: 유효한 Hex 코드 (`#RRGGBB`), 기본값 `#888888`

---

## 기본 카테고리

앱 최초 기동 시 자동으로 생성됩니다.

| category_id | name | color |
|-------------|------|-------|
| `cat_work` | 업무 | `#4A6FFF` |
| `cat_personal` | 개인 | `#FF6B6B` |
| `cat_urgent` | 긴급 | `#FF9500` |
| `cat_focus` | 집중 | `#34C759` |

---

## 마일스톤 달성 조건

태스크를 완료(done)할 때마다 서버가 자동으로 조건을 평가합니다. 같은 마일스톤은 **최초 달성 시 1회만** 발급됩니다.

| milestone_id | 달성 조건 |
|--------------|----------|
| `total_10` | 누적 완료 태스크 10개 이상 |
| `total_50` | 누적 완료 태스크 50개 이상 |
| `streak_3` | 3일 연속 1개 이상 태스크 완료 |
| `streak_7` | 7일 연속 1개 이상 태스크 완료 |
| `focus_5` | 하루에 category=집중(`cat_focus`) 태스크 5개 이상 완료 |

> 연속 스트릭은 `due_date`가 있는 태스크를 기준으로 최근 7일을 역산하여 계산합니다.

---

## 테스트

테스트는 단위 테스트(43개)와 통합 테스트(58개)로 구성됩니다.

### 전체 실행

```bash
cd backend
make test
# 또는: pytest tests/ --asyncio-mode=auto -v
```

### 단위 테스트만

```bash
pytest tests/unit/ -v
```

### 통합 테스트만

통합 테스트는 실제 MongoDB가 필요합니다 (`mongodb://127.0.0.1:27017`).  
테스트용 DB(`todo_test`)를 별도로 사용하며, 테스트 종료 후 자동으로 삭제됩니다.

```bash
docker compose up -d mongo   # MongoDB 기동
pytest tests/integration/ -v
```

### 테스트 커버리지

| 계층 | 파일 | 테스트 수 |
|------|------|----------|
| 단위 | `tests/unit/test_task_service.py` | 12 |
| 단위 | `tests/unit/test_category_service.py` | 5 |
| 단위 | `tests/unit/test_milestone_service.py` | 14 |
| 단위 | `tests/unit/test_stats_service.py` | 12 |
| 통합 | `tests/integration/test_tasks.py` | 28 |
| 통합 | `tests/integration/test_categories.py` | 13 |
| 통합 | `tests/integration/test_stats.py` | 11 |
| 통합 | `tests/integration/test_milestones.py` | 5 |
| 통합 | `tests/integration/test_health.py` | 3 |
| **합계** | | **103** |
