import type { WeeklyDay } from '@/lib/types'
import styles from './WeeklyBarChart.module.css'

const DAY_LABELS = ['일', '월', '화', '수', '목', '금', '토']

interface WeeklyBarChartProps {
  days: WeeklyDay[]
}

export function WeeklyBarChart({ days }: WeeklyBarChartProps) {
  const today = new Date().toISOString().slice(0, 10)
  const maxTotal = Math.max(...days.map((d) => d.total), 1)

  return (
    <div className={styles.card}>
      <p className={styles.title}>주간 진행 상황</p>
      <div className={styles.chart}>
        {days.map((day) => {
          const isToday = day.date === today
          const heightPct = day.total > 0 ? (day.total / maxTotal) * 100 : 4
          const completedPct = day.total > 0 ? (day.completed / day.total) * 100 : 0
          const label = DAY_LABELS[new Date(day.date + 'T00:00:00').getDay()]

          return (
            <div key={day.date} className={styles.col}>
              <div className={styles.barWrap}>
                <div
                  className={`${styles.bar} ${isToday ? styles.today : ''}`}
                  style={{ height: `${heightPct}%` }}
                  title={`${day.completed}/${day.total}개 완료`}
                >
                  {day.total > 0 && (
                    <div
                      className={styles.completedFill}
                      style={{ height: `${completedPct}%` }}
                    />
                  )}
                </div>
              </div>
              <span className={`${styles.dayLabel} ${isToday ? styles.todayLabel : ''}`}>
                {label}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
