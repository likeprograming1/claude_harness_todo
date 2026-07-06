import styles from './FocusScoreCard.module.css'

interface FocusScoreCardProps {
  score: number
  rate: number
}

export function FocusScoreCard({ score, rate }: FocusScoreCardProps) {
  const trend = rate >= 50 ? 'up' : rate >= 30 ? 'neutral' : 'down'

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.label}>집중도 점수</span>
        <TrendIcon trend={trend} />
      </div>
      <div className={styles.scoreRow}>
        <span className={styles.score}>{score}</span>
        <span className={styles.unit}>점</span>
        <span className={styles.status}>좋음</span>
      </div>
      <p className={styles.sub}>완료율 {Math.round(rate)}%</p>
    </div>
  )
}

function TrendIcon({ trend }: { trend: 'up' | 'neutral' | 'down' }) {
  if (trend === 'up') {
    return (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-label="상승">
        <path d="M4 14l4-4 3 3 5-6" stroke="#34C759" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M13 7h3v3" stroke="#34C759" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  }
  if (trend === 'down') {
    return (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-label="하락">
        <path d="M4 7l4 4 3-3 5 6" stroke="#FF3B30" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M13 14h3v-3" stroke="#FF3B30" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  }
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-label="유지">
      <path d="M4 10h12" stroke="#FF9500" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  )
}
