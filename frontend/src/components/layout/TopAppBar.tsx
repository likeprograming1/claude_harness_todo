import type { ReactNode } from 'react'
import Link from 'next/link'
import styles from './TopAppBar.module.css'

interface TopAppBarProps {
  title: string
  right?: ReactNode
}

export function TopAppBar({ title, right }: TopAppBarProps) {
  return (
    <header className={styles.header}>
      <button className={styles.hamburger} aria-label="메뉴">
        <HamburgerIcon />
      </button>
      <Link href="/" className={styles.title}>{title}</Link>
      <div className={styles.right}>{right ?? <Avatar />}</div>
    </header>
  )
}

function HamburgerIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="6" width="18" height="2" rx="1" fill="currentColor" />
      <rect x="3" y="11" width="18" height="2" rx="1" fill="currentColor" />
      <rect x="3" y="16" width="18" height="2" rx="1" fill="currentColor" />
    </svg>
  )
}

function Avatar() {
  return (
    <div className={styles.avatar} aria-label="프로필">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <circle cx="10" cy="7" r="4" fill="currentColor" />
        <path d="M2 17c0-4 3.6-6 8-6s8 2 8 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    </div>
  )
}
