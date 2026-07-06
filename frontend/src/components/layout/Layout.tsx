import type { ReactNode } from 'react'
import { useRouter } from 'next/router'
import { TopAppBar } from './TopAppBar'
import { BottomNav } from './BottomNav'
import styles from './Layout.module.css'

const PAGE_TITLES: Record<string, string> = {
  '/': '대시보드',
  '/tasks': '할 일 목록',
  '/tasks/new': '할 일 추가',
  '/stats': '데일리 플랜',
}

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { pathname } = useRouter()
  const title = PAGE_TITLES[pathname] ?? ''

  return (
    <div className={styles.container}>
      <TopAppBar title={title} />
      <main className={styles.main}>{children}</main>
      <BottomNav />
    </div>
  )
}
