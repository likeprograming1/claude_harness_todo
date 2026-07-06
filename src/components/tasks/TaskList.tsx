import type { Task } from '@/lib/types'
import { TaskItem } from './TaskItem'
import styles from './TaskList.module.css'

interface TaskListProps {
  tasks: Task[]
  onToggle: (taskId: string) => void
}

export function TaskList({ tasks, onToggle }: TaskListProps) {
  if (tasks.length === 0) {
    return <p className={styles.empty}>할 일이 없습니다.</p>
  }

  return (
    <div className={styles.list}>
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          id={task.task_id}
          title={task.title}
          is_done={task.is_done}
          priority={task.priority}
          onToggle={onToggle}
        />
      ))}
    </div>
  )
}
