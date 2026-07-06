# 화면별 구현 노트

## 1. 대시보드 (`/`) — Figma node: 1:2

**섹션 구성**
- **Header**: 햄버거 메뉴 + "대시보드" + 프로필 아바타
- **Welcome**: 인사말(`좋은 아침입니다, {name}님.`) + 오늘 날짜
- **Progress Bento**:
  - 흰 카드: 집중도 진행 상황 (프로그레스 바, 퍼센트, N개 중 M개 완료)
  - 파란 카드 (`#3e5cf4`): 다음 세션 (타이머 아이콘, "딥 워크", "15분 후 시작")
- **우선순위 할 일**: 태스크 최대 3개 + "오늘의 할 일 추가" 인풋
- **예정된 일정**: 가로 스크롤 카드 리스트 (시간 + 제목 + 장소)

**API 연동**
- `GET /stats/dashboard` → `total_today`, `completed_today`, `completion_rate`, `focus_score`, `priority_tasks`, `upcoming`
- `PATCH /tasks/{id}/done` → 체크박스 토글

---

## 2. 할 일 목록 (`/tasks`) — Figma node: 1:122

**섹션 구성**
- **Header**: 햄버거 + "할 일 목록" + 검색 아이콘 + 프로필
- **Welcome**: 인사말 + "오늘 집중해야 할 일이 N개 있습니다."
- **Quick Add**: `+ 할 일 추가...` 인풋 → 클릭 시 `/tasks/new` 이동
- **오늘 섹션**: 헤딩 + 카운트 뱃지 + 태스크 아이템 목록
- **예정 섹션**: 헤딩 + 날짜 뱃지 + 태스크 목록
- **FAB**: 우하단 파란 원형 `+` 버튼 → `/tasks/new`

**태스크 아이템 상태**
- 미완료: 빈 체크박스 (흰 배경 + `#757687` 테두리)
- 완료: 파란 체크박스 (`#1b3fdb`) + 제목 취소선 + 50% 불투명도

**API 연동**
- `GET /tasks?date=YYYY-MM-DD` → 오늘 태스크
- `PATCH /tasks/{id}/done` → 완료 토글

---

## 3. 통계 (`/stats`) — Figma node: 1:259

**섹션 구성**
- **Header**: 햄버거 + "데일리 플랜" + 프로필 (파란 테두리 `#3e5cf4`)
- **타이틀**: "생산성 트렌드" + "지난주보다 N% 더 완료"
- **Focus Score Card**: "집중도 점수" + 숫자 + 트렌드 아이콘 + "좋음"
- **Weekly Bar Chart**: "주간 진행 상황" + 7개 막대 + 요일 라벨
  - 오늘 막대: `#1b3fdb`, 나머지: `rgba(27,63,219, 0.1~0.4)`
- **완료된 마일스톤**: 아이콘 원 + 제목 + 설명 + 날짜
- **Insights Banner**: 파란 배경 `#1b3fdb` + 생산성 피크 메시지 + "일정 조정" 버튼

**API 연동**
- `GET /stats/dashboard` → `focus_score`, `completion_rate`
- `GET /stats/weekly` → 7일 막대 차트 데이터
- `GET /stats/insights` → `peak_start`, `peak_end`, `message`
- `GET /milestones` → 마일스톤 목록

---

## 4. 할 일 추가 (`/tasks/new`) — Figma node: 1:404

**폼 필드**

| 필드 | 입력 타입 | 필수 | 비고 |
|-----|---------|-----|-----|
| 할 일 이름 | text (large) | ✅ | 1~200자 |
| 마감일 | date picker | - | mm/dd/yyyy |
| 시간 | time picker | - | `due_date` 있을 때만 유효 |
| 카테고리 | chip 단일 선택 | - | 기본 4개 + `+` 버튼 |
| 추가 메모 | textarea | - | 선택 사항 |

**액션**
- 취소 → `router.back()`
- 할 일 저장 → `POST /tasks` → 성공 시 `/tasks` 이동
