import { useRouter } from 'next/router'
import styles from './AddTaskInput.module.css'

export function AddTaskInput() {
  const router = useRouter()

  return (
    <button
      className={styles.input}
      onClick={() => router.push('/tasks/new')}
      aria-label="할 일 추가"
    >
      <span className={styles.icon}>+</span>
      <span className={styles.placeholder}>할 일 추가...</span>
    </button>
  )
}
