# 디자인 시스템 (Figma 추출)

Figma 파일 키: `GKxqfxnwUWEhoHbzrlyffq` (Page 1)
Figma URL: https://www.figma.com/design/GKxqfxnwUWEhoHbzrlyffq/Untitled?node-id=0-1

## 색상 토큰

```css
:root {
  /* Primary */
  --color-primary:       #1b3fdb;
  --color-primary-dark:  #3e5cf4;
  --color-primary-light: #eff4ff;
  --color-primary-bg:    #e5eeff;

  /* Background */
  --color-bg:      #f8f9ff;
  --color-surface: #ffffff;

  /* Text */
  --color-text-primary:   #0b1c30;
  --color-text-secondary: #5c5f61;
  --color-text-tertiary:  #757687;
  --color-text-muted:     #444655;

  /* Border */
  --color-border:        rgba(196, 197, 216, 0.3);
  --color-border-subtle: rgba(196, 197, 216, 0.1);

  /* Category badges */
  --color-badge-work-bg:       rgba(27, 63, 219, 0.1);
  --color-badge-work-text:     #1b3fdb;
  --color-badge-personal-bg:   rgba(255, 219, 205, 0.4);
  --color-badge-personal-text: #7d2d00;
  --color-badge-neutral-bg:    #e0e3e5;
  --color-badge-neutral-text:  #5c5f61;

  /* UI elements */
  --color-inactive:      #e0e3e5;
  --color-inactive-text: #c4c7c9;
}
```

## 타이포그래피

| 역할 | 크기 | 행간 | 자간 | 폰트 |
|-----|------|-----|-----|-----|
| Heading 1 (앱 제목) | 20px | 28px | - | WenQuanYi Zen Hei Medium |
| Heading 2 (페이지 제목) | 32px | 40px | -0.64px | WenQuanYi Zen Hei Medium |
| Heading 3 (섹션 제목) | 20px | 28px | - | WenQuanYi Zen Hei Medium |
| Body | 16px | 24px | - | WenQuanYi Zen Hei Medium |
| Sub-body | 14px | 20px | - | WenQuanYi Zen Hei Medium |
| Small / Caption | 12px | 16px | - | WenQuanYi Zen Hei Medium |
| 숫자 강조 | 36px | 40px | - | Inter Bold |
| 숫자 퍼센트 | 32px | 40px | -0.64px | Inter Semi Bold |
| 시간 / 날짜 | 12px | 16px | - | Inter Bold/Medium |

> 한글 → WenQuanYi Zen Hei | 숫자·영문·날짜 → Inter

## 간격 & 크기

```
레이아웃 수평 패딩:  16px
카드 패딩:          24~25px
섹션 간 gap:        32px
아이템 간 gap:      8~12px
카드 border-radius: 12px
인풋 border-radius: 8px
칩 border-radius:   9999px
```

## 그림자

```css
/* 카드 */
box-shadow: 0px 1px 1px rgba(0, 0, 0, 0.05);

/* FAB / Primary 버튼 */
box-shadow:
  0px 10px 15px -3px rgba(27, 63, 219, 0.2),
  0px 4px 6px -4px rgba(27, 63, 219, 0.2);
```

## 하단 네비게이션

| 탭 | 경로 | 비고 |
|----|------|-----|
| 할 일 | `/` or `/tasks` | |
| 통계 | `/stats` | |
| 캘린더 | - | 미구현 |
| 설정 | - | 미구현 |

> Figma 대시보드/할일추가는 3탭, 통계는 4탭으로 표시됨 → **4탭으로 통일 구현**
