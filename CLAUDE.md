@AGENTS.md

# Frontend — Todo List App

## Stack

| 항목 | 버전 / 선택 |
|------|------------|
| Framework | Next.js **16.2.10** (Pages Router) |
| Language | TypeScript 5 |
| React | 19.2.4 |
| Styling | CSS Modules (`src/styles/`) |
| Testing | Jest 30 + Testing Library + jsdom |
| 모듈 alias | `@/` → `src/` |

---

## ⚠️ Next.js 16 Breaking Changes

> **반드시 `node_modules/next/dist/docs/` 를 먼저 읽고 코드를 작성할 것.**

### `middleware` → `proxy` 이름 변경 (v16.0.0)

```diff
- middleware.ts   →   proxy.ts
- export function middleware()  →  export function proxy()
```

- 런타임 기본값: Edge → **Node.js** 로 변경
- 마이그레이션 codemod: `npx @next/codemod@canary middleware-to-proxy .`
- `<Link>` 에 `transitionTypes` prop 추가 (v16.2.0)

### Pages Router 사용 시 주의사항

- `useRouter` → `next/router` (Pages Router) / `next/navigation` (App Router) 혼용 금지
- `next/compat/router` 로 양쪽 호환 가능
- `getServerSideProps`, `getStaticProps` 는 페이지 파일에서만 사용 가능 (레이아웃 컴포넌트 불가)
- 레이아웃 데이터 패칭은 클라이언트 사이드 (`useEffect` / SWR)

---

## 개발 워크플로우

> **feature 브랜치에서만 작업. `main` 직접 커밋 금지.**

```
git checkout -b feat/phase-X-description
```

| 브랜치 접두사 | 용도 |
|-------------|------|
| `feat/` | 새 기능 구현 |
| `fix/` | 버그 수정 |
| `docs/` | 문서 작업 |
| `test/` | 테스트 추가/수정 |
| `refactor/` | 리팩터링 |

- 각 Phase 완료 후 PR → `main` 머지 → 다음 Phase 시작
- 자동 push hook 활성 (`.claude/settings.json`)

---

## 프로젝트 디렉터리 구조 (계획)

```
src/
  pages/
    index.tsx              # 대시보드
    tasks/
      index.tsx            # 할 일 목록
      new.tsx              # 할 일 추가
    stats/
      index.tsx            # 통계
    _app.tsx               # 전역 레이아웃 래퍼
    _document.tsx          # HTML 문서 커스터마이징
  components/
    layout/
      Layout.tsx           # 공통 레이아웃 (BottomNav 포함)
      BottomNav.tsx        # 하단 네비게이션
      TopAppBar.tsx        # 상단 헤더
    tasks/
      TaskItem.tsx         # 태스크 아이템 (체크박스 + 제목 + 뱃지)
      TaskList.tsx         # 태스크 목록 래퍼
      AddTaskInput.tsx     # 인라인 태스크 추가 입력
    stats/
      FocusScoreCard.tsx   # 집중도 점수 카드
      WeeklyBarChart.tsx   # 주간 막대 차트
      MilestoneItem.tsx    # 마일스톤 아이템
      InsightsBanner.tsx   # 스마트 인사이트 배너
    dashboard/
      ProgressCard.tsx     # 진행 상황 카드 (프로그레스 바)
      FocusSessionCard.tsx # 딥 워크 세션 카드
      UpcomingList.tsx     # 예정된 일정 (가로 스크롤)
    ui/
      CategoryBadge.tsx    # 카테고리 뱃지 칩
      PriorityIcon.tsx     # 우선순위 아이콘
      FAB.tsx              # Floating Action Button
  lib/
    api/
      client.ts            # fetch 래퍼 (base URL, headers)
      tasks.ts             # 태스크 API 함수
      categories.ts        # 카테고리 API 함수
      stats.ts             # 통계 API 함수
      milestones.ts        # 마일스톤 API 함수
    types.ts               # API 응답 타입 정의
  styles/
    globals.css            # 전역 스타일 (디자인 토큰 CSS 변수)
    Home.module.css        # (기존)
```

---

## 페이지 라우팅

| URL | 파일 | Figma 화면 |
|-----|------|-----------|
| `/` | `pages/index.tsx` | 대시보드 (KR) |
| `/tasks` | `pages/tasks/index.tsx` | 할 일 목록 (KR) |
| `/tasks/new` | `pages/tasks/new.tsx` | 할 일 추가 (KR) |
| `/stats` | `pages/stats/index.tsx` | 통계 (KR) |

---

## 백엔드 API 연동

Base URL: `http://localhost:8000/api/v1`  
Content-Type: `application/json`

### 주요 엔드포인트

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

### 핵심 도메인 규칙 (API 제약)

- `is_done` 은 **PATCH /done** 으로만 변경 가능 (PUT 에서 직접 수정 불가)
- `due_time` 은 `due_date` 없이 사용 불가 → 422
- `priority`: `low | medium | high` (기본값 `medium`)
- `category_id` 없으면 null, 있으면 categories 컬렉션에 존재해야 함 → 없으면 422
- 기본 카테고리 4개 (아래) 는 삭제 불가 → 409

### 기본 카테고리

| category_id | name | color |
|-------------|------|-------|
| `cat_work` | 업무 | `#4A6FFF` |
| `cat_personal` | 개인 | `#FF6B6B` |
| `cat_urgent` | 긴급 | `#FF9500` |
| `cat_focus` | 집중 | `#34C759` |

---

## 디자인 시스템 (Figma 추출)

> Figma 파일: `GKxqfxnwUWEhoHbzrlyffq` (page: Page 1)
> Figma URL: https://www.figma.com/design/GKxqfxnwUWEhoHbzrlyffq/Untitled?node-id=0-1

### 색상 토큰

```css
:root {
  /* Primary */
  --color-primary: #1b3fdb;
  --color-primary-dark: #3e5cf4;
  --color-primary-light: #eff4ff;
  --color-primary-bg: #e5eeff;

  /* Background */
  --color-bg: #f8f9ff;
  --color-surface: #ffffff;

  /* Text */
  --color-text-primary: #0b1c30;
  --color-text-secondary: #5c5f61;
  --color-text-tertiary: #757687;
  --color-text-muted: #444655;

  /* Border */
  --color-border: rgba(196, 197, 216, 0.3);
  --color-border-subtle: rgba(196, 197, 216, 0.1);

  /* Category badges */
  --color-badge-work-bg: rgba(27, 63, 219, 0.1);
  --color-badge-work-text: #1b3fdb;
  --color-badge-personal-bg: rgba(255, 219, 205, 0.4);
  --color-badge-personal-text: #7d2d00;
  --color-badge-neutral-bg: #e0e3e5;
  --color-badge-neutral-text: #5c5f61;

  /* UI elements */
  --color-inactive: #e0e3e5;
  --color-inactive-text: #c4c7c9;
}
```

### 타이포그래피

| 역할 | 크기 | 행간 | 자간 | 폰트 |
|-----|------|-----|-----|-----|
| Heading 1 (앱 제목) | 20px | 28px | - | WenQuanYi Zen Hei Medium |
| Heading 2 (페이지 제목) | 32px | 40px | -0.64px | WenQuanYi Zen Hei Medium |
| Heading 3 (섹션 제목) | 20px | 28px | - | WenQuanYi Zen Hei Medium |
| Body | 16px | 24px | - | WenQuanYi Zen Hei Medium |
| Small / Caption | 12px | 16px | - | WenQuanYi Zen Hei Medium |
| Sub-body | 14px | 20px | - | WenQuanYi Zen Hei Medium |
| 숫자 (강조) | 36px | 40px | - | Inter Bold |
| 숫자 (퍼센트) | 32px | 40px | -0.64px | Inter Semi Bold |
| 시간/날짜 | 12px | 16px | - | Inter Bold/Medium |

> 한글 텍스트 → WenQuanYi Zen Hei, 숫자·영문·날짜 → Inter

### 간격 & 크기

```
레이아웃 수평 패딩:  16px
카드 패딩:          24~25px
섹션 간 gap:        32px
아이템 간 gap:      8~12px
카드 border-radius: 12px
인풋 border-radius: 8px
칩 border-radius:   9999px (완전 원형)
```

### 그림자

```css
/* 카드 */
box-shadow: 0px 1px 1px rgba(0, 0, 0, 0.05);

/* FAB / Primary 버튼 */
box-shadow:
  0px 10px 15px -3px rgba(27, 63, 219, 0.2),
  0px 4px 6px -4px rgba(27, 63, 219, 0.2);
```

### 하단 네비게이션 (BottomNav)

| 탭 | 경로 | 아이콘 |
|----|------|-------|
| 할 일 | `/` or `/tasks` | 체크리스트 아이콘 |
| 통계 | `/stats` | 바 차트 아이콘 |
| 캘린더 | (미구현) | 캘린더 아이콘 |
| 설정 | (미구현) | 기어 아이콘 |

> **주의**: Figma 대시보드/할일추가 화면은 3탭(통계 미포함), 통계 화면은 4탭으로 표시됨.  
> **구현 방침**: 4탭으로 통일하여 구현.

---

## Figma 화면별 구현 노트

### 1. 대시보드 (`/`) — node: 1:2

**섹션 구성**
- **Header**: 햄버거 메뉴 + "대시보드" + 프로필 아바타
- **Welcome**: 인사말(`좋은 아침입니다, {name}님.`) + 날짜
- **Progress Bento**:
  - 흰 카드: 집중도 진행 상황 (프로그레스 바, 퍼센트, N개 중 M개 완료)
  - 파란 카드 (#3e5cf4): 다음 세션 (타이머 아이콘, "딥 워크", "15분 후 시작")
- **우선순위 할 일**: 태스크 최대 3개 + "오늘의 할 일 추가" 인풋
- **예정된 일정**: 가로 스크롤 카드 리스트 (시간 + 제목 + 장소)

**API 연동**
- `GET /stats/dashboard` → `total_today`, `completed_today`, `completion_rate`, `focus_score`, `priority_tasks`, `upcoming`
- `PATCH /tasks/{id}/done` → 체크박스 토글

### 2. 할 일 목록 (`/tasks`) — node: 1:122

**섹션 구성**
- **Header**: 햄버거 + "할 일 목록" + 검색 아이콘 + 프로필
- **Welcome**: 인사말 + "오늘 집중해야 할 일이 N개 있습니다."
- **Quick Add**: `+ 할 일 추가...` 인풋 (클릭 시 `/tasks/new` 이동 또는 인라인)
- **오늘 섹션**: 헤딩 + 카운트 뱃지 + 태스크 아이템 목록
  - 태스크 아이템: 드래그 핸들(?) + 체크박스 + 제목 + [카테고리 뱃지] + [시간]
- **예정 섹션**: 헤딩 + 날짜 뱃지 + 태스크 목록
- **FAB**: 우하단 파란 원형 `+` 버튼 → `/tasks/new`

**태스크 완료 상태**
- 미완료: 빈 체크박스 (흰 배경 + #757687 테두리)
- 완료: 파란 체크박스 (#1b3fdb) + 제목 취소선 + 50% 불투명도

**API 연동**
- `GET /tasks?date=YYYY-MM-DD` → 오늘 태스크
- `GET /tasks?done=false` → 미완료 필터
- `PATCH /tasks/{id}/done` → 완료 토글

### 3. 통계 (`/stats`) — node: 1:259

**섹션 구성**
- **Header**: 햄버거 + "데일리 플랜" + 프로필 (파란 테두리)
- **Header Section**: "생산성 트렌드" + "지난주보다 N% 더 완료"
- **Focus Score Card**: "집중도 점수" + 숫자(84) + 트렌드 방향 + "좋음"
- **Weekly Bar Chart**: "주간 진행 상황" + 7개 막대 (요일 아이콘 아래)
  - 오늘 막대: 진한 파랑 (#1b3fdb), 나머지: 연한 파랑 (rgba 40~10%)
- **완료된 마일스톤**: 아이콘 원 + 제목 + 설명 + 날짜
- **Insights Banner**: 파란 배경 (#1b3fdb) + "스마트 인사이트" + 생산성 피크 메시지 + "일정 조정" 버튼

**API 연동**
- `GET /stats/dashboard` → focus_score, completion_rate, 비교값
- `GET /stats/weekly` → 7일 막대 차트 데이터
- `GET /stats/insights` → peak_start, peak_end, message
- `GET /milestones` → 마일스톤 목록

### 4. 할 일 추가 (`/tasks/new`) — node: 1:404

**폼 필드**
| 필드 | 입력 타입 | 필수 | 비고 |
|-----|---------|-----|-----|
| 할 일 이름 | text input (large) | ✅ | 1~200자 |
| 마감일 | date picker | - | mm/dd/yyyy |
| 시간 | time picker | - | due_date 있을 때만 유효 |
| 카테고리 | chip 선택 (단일) | - | 기본 4개 + `+` 버튼 |
| 추가 메모 | textarea | - | 선택 사항 |

**액션 버튼**
- 취소: 이전 페이지로 (`router.back()`)
- 할 일 저장: `POST /tasks` → 성공 시 `/tasks` 로 이동

---

## 테스트 정책

```
jest.config.ts 설정:
  - testEnvironment: jsdom
  - moduleNameMapper: @/ → src/
  - testMatch: **/__tests__/**/*.{ts,tsx} | **/*.{spec,test}.{ts,tsx}
```

| 레이어 | 테스트 범위 |
|-------|-----------|
| 컴포넌트 | Testing Library — 렌더링, 인터랙션, 접근성 |
| API 함수 | fetch mock — 요청 파라미터, 에러 처리 |
| 유틸 | 순수 함수 단위 테스트 |

---

## 개발 Phase 계획

| Phase | 내용 | 브랜치 |
|-------|------|-------|
| 1 | 디자인 토큰 + 공통 컴포넌트 (Layout, BottomNav, TaskItem) | `feat/phase-1-base` |
| 2 | API client + 타입 정의 + 대시보드 | `feat/phase-2-dashboard` |
| 3 | 할 일 목록 + 완료 토글 + FAB | `feat/phase-3-tasklist` |
| 4 | 할 일 추가 폼 + 유효성 검사 | `feat/phase-4-add-task` |
| 5 | 통계 페이지 (차트 + 마일스톤 + 인사이트) | `feat/phase-5-stats` |
| 6 | 테스트 작성 + 마무리 | `feat/phase-6-tests` |

---

## 코드 컨벤션

- **컴포넌트**: PascalCase, Named Export 우선
- **스타일**: CSS Modules (`ComponentName.module.css`)
- **타입**: `interface` > `type` (확장 가능성), `src/lib/types.ts` 에 API 타입 집중
- **API 함수**: `async/await` + `try/catch` 없이 에러를 호출자에게 전파
- **주석**: WHY 가 명확하지 않은 경우만 한 줄

---

## 참고

- API 스펙 → [`../backend/docs/api-spec.md`](../backend/docs/api-spec.md)
- 도메인 규칙 → [`../backend/docs/domain-rules.md`](../backend/docs/domain-rules.md)
- Next.js 16 공식 문서 → `node_modules/next/dist/docs/02-pages/`
