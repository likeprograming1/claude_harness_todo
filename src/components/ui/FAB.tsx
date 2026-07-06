import Link from 'next/link'
import styles from './FAB.module.css'

interface FABProps {
  href: string
  label?: string
}

export function FAB({ href, label = '추가' }: FABProps) {
  return (
    <Link href={href} className={styles.fab} aria-label={label}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 5v14M5 12h14" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
      </svg>
    </Link>
  )
}
