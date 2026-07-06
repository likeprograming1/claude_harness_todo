# 프로젝트 구조 & 개발 계획

## 디렉터리 구조

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
```

## 페이지 라우팅

| URL | 파일 | Figma 화면 |
|-----|------|-----------|
| `/` | `pages/index.tsx` | 대시보드 (KR) |
| `/tasks` | `pages/tasks/index.tsx` | 할 일 목록 (KR) |
| `/tasks/new` | `pages/tasks/new.tsx` | 할 일 추가 (KR) |
| `/stats` | `pages/stats/index.tsx` | 통계 (KR) |

## 개발 Phase 계획

| Phase | 내용 | 브랜치 |
|-------|------|-------|
| 1 | 디자인 토큰 + 공통 컴포넌트 (Layout, BottomNav, TaskItem) | `feat/phase-1-base` |
| 2 | API client + 타입 정의 + 대시보드 | `feat/phase-2-dashboard` |
| 3 | 할 일 목록 + 완료 토글 + FAB | `feat/phase-3-tasklist` |
| 4 | 할 일 추가 폼 + 유효성 검사 | `feat/phase-4-add-task` |
| 5 | 통계 페이지 (차트 + 마일스톤 + 인사이트) | `feat/phase-5-stats` |
| 6 | 테스트 작성 + 마무리 | `feat/phase-6-tests` |

## 테스트 정책

```
jest.config.ts:
  testEnvironment: jsdom
  moduleNameMapper: @/ → src/
  testMatch: **/__tests__/**/*.{ts,tsx} | **/*.{spec,test}.{ts,tsx}
```

| 레이어 | 범위 |
|-------|------|
| 컴포넌트 | Testing Library — 렌더링, 인터랙션 |
| API 함수 | fetch mock — 요청 파라미터, 에러 처리 |
| 유틸 | 순수 함수 단위 테스트 |
