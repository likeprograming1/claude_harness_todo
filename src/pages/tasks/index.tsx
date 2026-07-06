import { useEffect, useState, useCallback } from 'react'
import { getTasks } from '@/lib/api/tasks'
import { toggleDone } from '@/lib/api/tasks'
import type { Task } from '@/lib/types'
import { TaskList } from '@/components/tasks/TaskList'
import { AddTaskInput } from '@/components/tasks/AddTaskInput'
import { FAB } from '@/components/ui/FAB'
import styles from './index.module.css'

function toLocalDateStr(date: Date) {
  return date.toISOString().slice(0, 10)
}

function formatSectionDate(dateStr: string) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', weekday: 'short' })
}

function groupByDate(tasks: Task[]) {
  const map: Record<string, Task[]> = {}
  for (const t of tasks) {
    const key = t.due_date ?? 'none'
    if (!map[key]) map[key] = []
    map[key].push(t)
  }
  return map
}

export default function TasksPage() {
  const [todayTasks, setTodayTasks] = useState<Task[]>([])
  const [upcomingTasks, setUpcomingTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const today = toLocalDateStr(new Date())

  const load = useCallback(async () => {
    try {
      const [todayData, allData] = await Promise.all([
        getTasks({ date: today }),
        getTasks(),
      ])
      setTodayTasks(todayData)
      setUpcomingTasks(
        allData.filter((t) => t.due_date && t.due_date > today)
      )
    } catch {
      setError('할 일을 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }, [today])

  useEffect(() => { load() }, [load])

  const handleToggle = async (taskId: string) => {
    try {
      const updated = await toggleDone(taskId)
      const update = (list: Task[]) =>
        list.map((t) => t.task_id === taskId ? updated : t)
      setTodayTasks(update)
      setUpcomingTasks(update)
    } catch {
      // 토글 실패 무시
    }
  }

  const totalToday = todayTasks.length
  const completedToday = todayTasks.filter((t) => t.is_done).length

  if (loading) return <div className={styles.state}>불러오는 중…</div>
  if (error) return <div className={styles.state}>{error}</div>

  const upcomingByDate = groupByDate(upcomingTasks)
  const upcomingDates = Object.keys(upcomingByDate).sort()

  return (
    <div className={styles.page}>
      {/* Welcome */}
      <section className={styles.welcome}>
        <p className={styles.greeting}>안녕하세요!</p>
        <p className={styles.sub}>
          {completedToday < totalToday
            ? `오늘 집중해야 할 일이 ${totalToday - completedToday}개 있습니다.`
            : totalToday > 0
              ? '오늘 할 일을 모두 완료했습니다! 🎉'
              : '오늘 할 일이 없습니다.'}
        </p>
      </section>

      {/* Quick Add */}
      <AddTaskInput />

      {/* 오늘 섹션 */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>오늘</h2>
          <span className={styles.badge}>{totalToday}</span>
        </div>
        <TaskList tasks={todayTasks} onToggle={handleToggle} />
      </section>

      {/* 예정 섹션 */}
      {upcomingDates.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>예정</h2>
          {upcomingDates.map((date) => (
            <div key={date} className={styles.dateGroup}>
              <div className={styles.dateBadge}>{formatSectionDate(date)}</div>
              <TaskList tasks={upcomingByDate[date]} onToggle={handleToggle} />
            </div>
          ))}
        </section>
      )}

      <FAB href="/tasks/new" label="할 일 추가" />
    </div>
  )
}
