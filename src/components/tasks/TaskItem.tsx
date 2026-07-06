import styles from './TaskItem.module.css'

interface Category {
  id: string
  name: string
  color: string
}

interface TaskItemProps {
  id: string
  title: string
  is_done: boolean
  priority?: 'low' | 'medium' | 'high'
  category?: Category | null
  onToggle: (id: string) => void
}

export function TaskItem({ id, title, is_done, category, onToggle }: TaskItemProps) {
  return (
    <div className={`${styles.item} ${is_done ? styles.done : ''}`}>
      <button
        className={`${styles.checkbox} ${is_done ? styles.checked : ''}`}
        onClick={() => onToggle(id)}
        aria-label={is_done ? '완료 취소' : '완료'}
        aria-pressed={is_done}
      >
        {is_done && <CheckIcon />}
      </button>
      <span className={styles.title}>{title}</span>
      {category && (
        <span
          className={styles.badge}
          style={{ '--badge-color': category.color } as React.CSSProperties}
        >
          {category.name}
        </span>
      )}
    </div>
  )
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path
        d="M2 7l3.5 3.5L12 3"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
