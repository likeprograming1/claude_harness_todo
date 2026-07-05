# API Specification — Todo List API

Base path: `/api/v1`
Content-Type: `application/json`

---

## Task — `/api/v1/tasks`

### `GET /tasks`
할 일 목록 조회. 쿼리 파라미터로 필터링.

**Query params**
| param | type | description |
|-------|------|-------------|
| `date` | `YYYY-MM-DD` | 해당 날짜의 due_date 필터 |
| `category_id` | string | 카테고리 필터 |
| `done` | bool | 완료 여부 필터 |
| `priority` | `low\|medium\|high` | 우선순위 필터 |

**Response 200**
```json
[{
  "id": "64abc...",
  "task_id": "T001",
  "title": "디자인 시스템 문서 검토",
  "due_date": "2024-10-24",
  "due_time": "09:00",
  "category_id": "업무",
  "priority": "high",
  "is_done": false,
  "notes": null,
  "created_at": "2024-10-23T10:00:00"
}]
```

### `POST /tasks`
새 할 일 생성.

**Request body** — TaskCreate
**Response 201** — TaskResponse
**Response 409** — Duplicate `task_id`
**Response 422** — title 없음, due_time without due_date, 존재하지 않는 category_id

### `GET /tasks/{task_id}`
**Response 200** — TaskResponse
**Response 404** — task_id not found

### `PUT /tasks/{task_id}`
할 일 전체 수정 (제공된 필드만 변경).

**Request body** — TaskUpdate
**Response 200** — TaskResponse
**Response 404** — task_id not found
**Response 422** — due_time without due_date, 존재하지 않는 category_id

### `DELETE /tasks/{task_id}`
**Response 204** — Deleted
**Response 404** — task_id not found

### `PATCH /tasks/{task_id}/done`
완료 상태 토글 (done ↔ not done).

**Response 200** — TaskResponse
**Response 404** — task_id not found

---

## Category — `/api/v1/categories`

### `GET /categories`
**Response 200** — `list[CategoryResponse]`
기본 카테고리(업무·개인·긴급·집중) + 커스텀 카테고리 모두 반환.

### `POST /categories`
커스텀 카테고리 생성.

**Request body** — CategoryCreate
**Response 201** — CategoryResponse
**Response 409** — Duplicate name

### `DELETE /categories/{category_id}`
**Response 204** — Deleted
**Response 404** — category_id not found
**Response 409** — 기본 카테고리는 삭제 불가

---

## Stats — `/api/v1/stats`

### `GET /stats/dashboard`
대시보드 집계 데이터.

**Response 200**
```json
{
  "today": "2024-10-24",
  "total_today": 5,
  "completed_today": 3,
  "completion_rate": 60.0,
  "focus_score": 84,
  "priority_tasks": [ ...TaskResponse x3 ],
  "upcoming": [ ...TaskResponse (오늘 이후 due_date 순) ]
}
```

### `GET /stats/weekly`
최근 7일간 일별 완료/전체 태스크 수.

**Response 200**
```json
{
  "days": [
    { "date": "2024-10-18", "total": 4, "completed": 3 },
    ...
  ]
}
```

### `GET /stats/insights`
스마트 인사이트 — 완료 시각 분포 기반 생산성 피크 시간대.

**Response 200**
```json
{
  "peak_start": "09:00",
  "peak_end": "11:30",
  "message": "오전 9:00~11:30 사이에 가장 생산적입니다."
}
```

---

## Milestone — `/api/v1/milestones`

### `GET /milestones`
달성된 마일스톤 목록 (최신순).

**Response 200**
```json
[{
  "id": "64abc...",
  "milestone_id": "M001",
  "title": "딥 포커스 스트릭",
  "description": "3일 연속으로 5시간 이상의 집중 업무를 완료했습니다.",
  "achieved_at": "2024-10-24"
}]
```

---

## Health

### `GET /health`
**Response 200** — `{ "status": "ok" }`

---

## Common Error Formats

| Status | Meaning | Trigger |
|--------|---------|---------|
| 422 | Unprocessable Entity | Pydantic validation failure, business rule violation |
| 404 | Not Found | Entity does not exist |
| 409 | Conflict | Duplicate creation, default category deletion blocked |
