import type { Milestone } from '@/lib/types'
import styles from './MilestoneItem.module.css'

interface MilestoneItemProps {
  milestone: Milestone
}

export function MilestoneItem({ milestone }: MilestoneItemProps) {
  const date = new Date(milestone.achieved_at).toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
  })

  return (
    <div className={styles.item}>
      <div className={styles.icon}>
        <TrophyIcon />
      </div>
      <div className={styles.body}>
        <p className={styles.title}>{milestone.title}</p>
        <p className={styles.desc}>{milestone.description}</p>
      </div>
      <span className={styles.date}>{date}</span>
    </div>
  )
}

function TrophyIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M10 13c-3.3 0-6-2.7-6-6V3h12v4c0 3.3-2.7 6-6 6z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M10 13v4M7 17h6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <path d="M4 5H2v2a3 3 0 003 3M16 5h2v2a3 3 0 01-3 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
