import type { Task } from '@/lib/types'
import styles from './UpcomingList.module.css'

interface UpcomingListProps {
  tasks: Task[]
}

export function UpcomingList({ tasks }: UpcomingListProps) {
  if (tasks.length === 0) {
    return <p className={styles.empty}>예정된 일정이 없습니다.</p>
  }

  return (
    <div className={styles.scroll}>
      {tasks.map((task) => (
        <div key={task.id} className={styles.card}>
          <p className={styles.time}>{task.due_time ?? '시간 미정'}</p>
          <p className={styles.title}>{task.title}</p>
          {task.category_id && (
            <p className={styles.category}>{task.category_id}</p>
          )}
        </div>
      ))}
    </div>
  )
}
