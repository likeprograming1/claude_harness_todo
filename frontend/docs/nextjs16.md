# Next.js 16 Breaking Changes

> **반드시 `node_modules/next/dist/docs/` 를 먼저 읽고 코드를 작성할 것.**

## `middleware` → `proxy` 이름 변경 (v16.0.0)

```diff
- middleware.ts   →   proxy.ts
- export function middleware()  →  export function proxy()
```

- 런타임 기본값: Edge → **Node.js** 로 변경
- 마이그레이션 codemod: `npx @next/codemod@canary middleware-to-proxy .`
- `<Link>` 에 `transitionTypes` prop 추가 (v16.2.0)

## Pages Router 사용 시 주의사항

- `useRouter` → `next/router` (Pages Router) / `next/navigation` (App Router) 혼용 금지
- `next/compat/router` 로 양쪽 호환 가능
- `getServerSideProps`, `getStaticProps` 는 페이지 파일에서만 사용 가능 (레이아웃 컴포넌트 불가)
- 레이아웃 데이터 패칭은 클라이언트 사이드 (`useEffect` / SWR)
