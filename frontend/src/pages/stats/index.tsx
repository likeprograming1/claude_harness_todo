import { useEffect, useState } from 'react'
import { getDashboard, getWeekly, getInsights } from '@/lib/api/stats'
import { getMilestones } from '@/lib/api/milestones'
import type { DashboardStats, WeeklyStats, Insights, Milestone } from '@/lib/types'
import { FocusScoreCard } from '@/components/stats/FocusScoreCard'
import { WeeklyBarChart } from '@/components/stats/WeeklyBarChart'
import { MilestoneItem } from '@/components/stats/MilestoneItem'
import { InsightsBanner } from '@/components/stats/InsightsBanner'
import styles from './index.module.css'

interface StatsData {
  dashboard: DashboardStats
  weekly: WeeklyStats
  insights: Insights
  milestones: Milestone[]
}

function calcWeekChange(days: WeeklyStats['days']): number {
  if (days.length < 7) return 0
  const thisWeek = days.slice(3).reduce((s, d) => s + d.completed, 0)
  const lastWeek = days.slice(0, 3).reduce((s, d) => s + d.completed, 0)
  if (lastWeek === 0) return thisWeek > 0 ? 100 : 0
  return Math.round(((thisWeek - lastWeek) / lastWeek) * 100)
}

export default function StatsPage() {
  const [data, setData] = useState<StatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      getDashboard(),
      getWeekly(),
      getInsights(),
      getMilestones(),
    ])
      .then(([dashboard, weekly, insights, milestones]) => {
        setData({ dashboard, weekly, insights, milestones })
      })
      .catch(() => setError('데이터를 불러오지 못했습니다.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className={styles.state}>불러오는 중…</div>
  if (error)   return <div className={styles.state}>{error}</div>
  if (!data)   return null

  const weekChange = calcWeekChange(data.weekly.days)

  return (
    <div className={styles.page}>
      {/* 타이틀 */}
      <section>
        <h1 className={styles.heading}>생산성 트렌드</h1>
        {weekChange !== 0 && (
          <p className={`${styles.weekChange} ${weekChange > 0 ? styles.positive : styles.negative}`}>
            지난주보다 {Math.abs(weekChange)}% {weekChange > 0 ? '더' : '덜'} 완료
          </p>
        )}
      </section>

      {/* 집중도 점수 */}
      <FocusScoreCard
        score={data.dashboard.focus_score}
        rate={data.dashboard.completion_rate}
      />

      {/* 주간 막대 차트 */}
      <WeeklyBarChart days={data.weekly.days} />

      {/* 완료된 마일스톤 */}
      {data.milestones.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>완료된 마일스톤</h2>
          <div className={styles.milestoneList}>
            {data.milestones.map((m) => (
              <MilestoneItem key={m.id} milestone={m} />
            ))}
          </div>
        </section>
      )}

      {/* 인사이트 배너 */}
      <InsightsBanner insights={data.insights} />
    </div>
  )
}
