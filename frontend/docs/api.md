# 백엔드 API 연동

Base URL: `http://localhost:8000/api/v1`
Content-Type: `application/json`

## 엔드포인트

```
GET    /tasks                    # 목록 조회 (date, category_id, done, priority 필터)
POST   /tasks                    # 생성
GET    /tasks/{task_id}          # 단건 조회
PUT    /tasks/{task_id}          # 수정
DELETE /tasks/{task_id}          # 삭제
PATCH  /tasks/{task_id}/done     # 완료 토글 (is_done 변경은 이것만 사용)

GET    /categories               # 목록
POST   /categories               # 커스텀 카테고리 생성
DELETE /categories/{category_id} # 삭제 (기본 카테고리 삭제 시 409)

GET    /stats/dashboard          # 대시보드 집계
GET    /stats/weekly             # 주간 완료/전체 수
GET    /stats/insights           # 생산성 피크 시간대

GET    /milestones               # 달성된 마일스톤 (읽기 전용)
GET    /health                   # 서버 상태
```

## 핵심 도메인 규칙

- `is_done` 은 **PATCH /done** 으로만 변경 가능 (PUT 에서 직접 수정 불가)
- `due_time` 은 `due_date` 없이 사용 불가 → 422
- `priority`: `low | medium | high` (기본값 `medium`)
- `category_id` 없으면 null, 있으면 categories 컬렉션에 존재해야 함 → 없으면 422
- 기본 카테고리 4개는 삭제 불가 → 409

## 기본 카테고리

| category_id | name | color |
|-------------|------|-------|
| `cat_work` | 업무 | `#4A6FFF` |
| `cat_personal` | 개인 | `#FF6B6B` |
| `cat_urgent` | 긴급 | `#FF9500` |
| `cat_focus` | 집중 | `#34C759` |

## 에러 코드

| Status | 의미 | 발생 조건 |
|--------|------|---------|
| 422 | Unprocessable Entity | 유효성 검사 실패, 비즈니스 규칙 위반 |
| 404 | Not Found | 엔티티 없음 |
| 409 | Conflict | 중복 생성, 기본 카테고리 삭제 시도 |

## 참고

- 전체 스펙 → [`../../backend/docs/api-spec.md`](../../backend/docs/api-spec.md)
- 도메인 규칙 → [`../../backend/docs/domain-rules.md`](../../backend/docs/domain-rules.md)
