import type { Insights } from '@/lib/types'
import styles from './InsightsBanner.module.css'

interface InsightsBannerProps {
  insights: Insights
}

export function InsightsBanner({ insights }: InsightsBannerProps) {
  return (
    <div className={styles.banner}>
      <div className={styles.body}>
        <p className={styles.label}>생산성 피크 시간대</p>
        <p className={styles.time}>
          {insights.peak_start} ~ {insights.peak_end}
        </p>
        <p className={styles.message}>{insights.message}</p>
      </div>
      <button type="button" className={styles.btn}>
        일정 조정
      </button>
    </div>
  )
}
