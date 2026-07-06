@AGENTS.md

# Frontend — Todo List App

## Stack

| | 버전 |
|--|------|
| Next.js | 16.2.10 (Pages Router) |
| React | 19.2.4 |
| TypeScript | 5 |
| 스타일링 | CSS Modules |
| 테스트 | Jest 30 + Testing Library |

## 브랜치 규칙

- **main 직접 커밋 금지** — feature 브랜치에서 작업
- 네이밍: `feat/`, `fix/`, `docs/`, `test/`, `refactor/`
- Phase 브랜치: `feat/phase-1-base` … `feat/phase-6-tests`

## 코딩 컨벤션

- 컴포넌트: PascalCase 파일명, named export
- 훅: `use` prefix
- API 함수: `lib/api/*.ts` — `fetch` 기반 래퍼
- CSS: CSS Modules (`Component.module.css`)

## 참고 문서

@docs/nextjs16.md
@docs/api.md
@docs/design.md
@docs/screens.md
@docs/structure.md
