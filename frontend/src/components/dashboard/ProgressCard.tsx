import styles from './ProgressCard.module.css'

interface ProgressCardProps {
  total: number
  completed: number
  rate: number
  focusScore: number
}

export function ProgressCard({ total, completed, rate, focusScore }: ProgressCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.label}>집중도 진행 상황</span>
        <span className={styles.score}>
          <span className={styles.scoreNum}>{focusScore}</span>
          <span className={styles.scoreUnit}>점</span>
        </span>
      </div>
      <div className={styles.progressWrap}>
        <div className={styles.progressBg}>
          <div
            className={styles.progressFill}
            style={{ width: `${Math.min(rate, 100)}%` }}
            role="progressbar"
            aria-valuenow={rate}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
        <span className={styles.rate}>{Math.round(rate)}%</span>
      </div>
      <p className={styles.count}>{total}개 중 {completed}개 완료</p>
    </div>
  )
}
