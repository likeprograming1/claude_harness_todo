import type { ReactElement } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import styles from './BottomNav.module.css'

interface NavItem {
  label: string
  href: string | null
  icon: () => ReactElement
  activeOn: string[]
}

const NAV_ITEMS: NavItem[] = [
  { label: '할 일', href: '/', icon: TaskIcon, activeOn: ['/', '/tasks', '/tasks/new'] },
  { label: '통계', href: '/stats', icon: StatsIcon, activeOn: ['/stats'] },
  { label: '캘린더', href: null, icon: CalendarIcon, activeOn: [] },
  { label: '설정', href: null, icon: SettingsIcon, activeOn: [] },
]

export function BottomNav() {
  const { pathname } = useRouter()

  return (
    <nav className={styles.nav} aria-label="하단 네비게이션">
      {NAV_ITEMS.map(({ label, href, icon: Icon, activeOn }) => {
        const isActive = activeOn.includes(pathname)
        const isDisabled = href === null

        if (isDisabled) {
          return (
            <span key={label} className={`${styles.item} ${styles.disabled}`} aria-disabled="true">
              <Icon />
              <span className={styles.label}>{label}</span>
            </span>
          )
        }

        return (
          <Link
            key={label}
            href={href}
            className={`${styles.item} ${isActive ? styles.active : ''}`}
            aria-current={isActive ? 'page' : undefined}
          >
            <Icon />
            <span className={styles.label}>{label}</span>
          </Link>
        )
      })}
    </nav>
  )
}

function TaskIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="5" width="3" height="3" rx="0.5" stroke="currentColor" strokeWidth="1.5" />
      <rect x="3" y="10.5" width="3" height="3" rx="0.5" stroke="currentColor" strokeWidth="1.5" />
      <rect x="3" y="16" width="3" height="3" rx="0.5" stroke="currentColor" strokeWidth="1.5" />
      <line x1="9" y1="6.5" x2="21" y2="6.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="9" y1="12" x2="21" y2="12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="9" y1="17.5" x2="21" y2="17.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

function StatsIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="12" width="4" height="9" rx="1" fill="currentColor" opacity="0.7" />
      <rect x="10" y="7" width="4" height="14" rx="1" fill="currentColor" />
      <rect x="17" y="3" width="4" height="18" rx="1" fill="currentColor" opacity="0.5" />
    </svg>
  )
}

function CalendarIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="1.5" />
      <line x1="8" y1="3" x2="8" y2="7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="16" y1="3" x2="16" y2="7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

function SettingsIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  )
}
