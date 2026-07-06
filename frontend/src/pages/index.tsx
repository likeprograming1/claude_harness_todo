import { useEffect, useState, useCallback } from 'react'
import { getDashboard } from '@/lib/api/stats'
import { toggleDone } from '@/lib/api/tasks'
import type { DashboardStats } from '@/lib/types'
import { ProgressCard } from '@/components/dashboard/ProgressCard'
import { FocusSessionCard } from '@/components/dashboard/FocusSessionCard'
import { UpcomingList } from '@/components/dashboard/UpcomingList'
import { TaskItem } from '@/components/tasks/TaskItem'
import styles from './index.module.css'

const GREETINGS = [
  { range: [5, 11], text: '좋은 아침입니다' },
  { range: [11, 17], text: '좋은 오후입니다' },
  { range: [17, 21], text: '좋은 저녁입니다' },
  { range: [21, 24], text: '좋은 밤입니다' },
  { range: [0, 5], text: '좋은 밤입니다' },
]

function getGreeting() {
  const h = new Date().getHours()
  return GREETINGS.find(({ range }) => h >= range[0] && h < range[1])?.text ?? '안녕하세요'
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', weekday: 'short' })
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const data = await getDashboard()
      setStats(data)
    } catch {
      setError('데이터를 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleToggle = async (taskId: string) => {
    if (!stats) return
    try {
      const updated = await toggleDone(taskId)
      setStats((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          priority_tasks: prev.priority_tasks.map((t) => t.task_id === taskId ? updated : t),
        }
      })
    } catch {
      // 토글 실패 시 무시
    }
  }

  if (loading) return <div className={styles.state}>불러오는 중…</div>
  if (error) return <div className={styles.state}>{error}</div>
  if (!stats) return null

  return (
    <div className={styles.page}>
      <section className={styles.welcome}>
        <p className={styles.greeting}>{getGreeting()}, 사용자님.</p>
        <p className={styles.date}>{formatDate(stats.today)}</p>
      </section>

      <section className={styles.bento}>
        <ProgressCard
          total={stats.total_today}
          completed={stats.completed_today}
          rate={stats.completion_rate}
          focusScore={stats.focus_score}
        />
        <FocusSessionCard />
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>우선순위 할 일</h2>
        {stats.priority_tasks.length === 0 ? (
          <p className={styles.empty}>오늘 할 일이 없습니다.</p>
        ) : (
          <div className={styles.taskList}>
            {stats.priority_tasks.slice(0, 3).map((task) => (
              <TaskItem
                key={task.id}
                id={task.task_id}
                title={task.title}
                is_done={task.is_done}
                priority={task.priority}
                onToggle={handleToggle}
              />
            ))}
          </div>
        )}
      </section>

      {stats.upcoming.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>예정된 일정</h2>
          <UpcomingList tasks={stats.upcoming} />
        </section>
      )}
    </div>
  )
}
