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

## 브랜치 & PR 규칙

- **main 직접 커밋 금지** — feature 브랜치에서 작업
- 네이밍: `feat/`, `fix/`, `docs/`, `test/`, `refactor/`
- Phase 브랜치: `feat/phase-1-base` … `feat/phase-6-tests`

### Phase 완료 시 PR 절차

1. `main` 에서 새 브랜치 생성: `git checkout main && git checkout -b feat/phase-N-xxx`
2. 구현 후 커밋
3. `gh pr create` 로 GitHub PR 생성 → `main` 으로 머지 요청
4. PR 제목 형식: `feat(phase-N): <한 줄 요약>`

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
