# Domain Rules — Todo List API

---

## Task

### task_id
- 클라이언트가 직접 제공하거나 서버가 자동 생성 (UUID4 단축형)
- 컬렉션 내 유일해야 함 → 중복 시 409

### title
- 필수, 1~200자

### due_date / due_time
- `due_date`: 선택, `YYYY-MM-DD` 형식
- `due_time`: 선택, `HH:MM` 형식 (24시간)
- **due_time은 due_date 없이 단독 사용 불가 → 422**

### priority
- 허용 값: `low`, `medium`, `high`
- 기본값: `medium`

### category_id
- 선택 필드
- 제공 시 `categories` 컬렉션에 존재해야 함 → 없으면 422

### is_done
- 기본값: `false`
- `PATCH /tasks/{task_id}/done` 으로만 토글

### created_at
- 서버가 자동 부여 (UTC), 클라이언트 제공 불가

---

## Category

### 기본 카테고리 (앱 시작 시 seed)
| category_id | name | color |
|-------------|------|-------|
| `cat_work` | 업무 | `#4A6FFF` |
| `cat_personal` | 개인 | `#FF6B6B` |
| `cat_urgent` | 긴급 | `#FF9500` |
| `cat_focus` | 집중 | `#34C759` |

- 기본 카테고리는 **삭제 불가** → 409

### 커스텀 카테고리
- name: 1~50자, 컬렉션 내 유일 → 중복 시 409
- color: 유효한 hex 코드 (`#RRGGBB` 형식), 기본값 `#888888`

---

## Stats

### focus_score (집중도 점수, 0~100)
- 오늘 완료한 태스크 수 / 오늘 전체 태스크 수 × 100 (정수)
- 태스크가 없으면 0

### completion_rate (완료율, %)
- 오늘 completed / 오늘 total × 100 (소수점 1자리)

### priority_tasks (우선순위 할 일)
- 오늘 미완료 태스크 중 priority=high → medium → low 순, 최대 3개

### weekly stats
- 오늘 기준 -6일 ~ 오늘 총 7일
- 날짜별 total / completed 집계

### insights (스마트 인사이트)
- 과거 30일 완료 태스크의 `completed_at` 시각 분포 분석
- 완료가 가장 많이 몰린 2시간 구간 → `peak_start` / `peak_end`
- 데이터 부족(완료 태스크 < 5개) 시 기본 메시지 반환

---

## Milestone

- 자동 생성 — API로 직접 생성/수정/삭제 불가 (GET 전용)
- 서비스 계층이 태스크 완료 이벤트 후 조건 평가하여 자동 발급

### 달성 조건
| milestone_id | 조건 |
|--------------|------|
| `streak_3` | 3일 연속 1개 이상 태스크 완료 |
| `streak_7` | 7일 연속 1개 이상 태스크 완료 |
| `total_10` | 누적 완료 태스크 10개 이상 |
| `total_50` | 누적 완료 태스크 50개 이상 |
| `focus_5` | 하루 집중(category=집중) 태스크 5개 이상 완료 |

- 같은 마일스톤은 **최초 달성 시 1회만** 발급
