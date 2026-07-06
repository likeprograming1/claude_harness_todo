import styles from './CategoryBadge.module.css'

interface CategoryBadgeProps {
  name: string
  color: string
  selected?: boolean
  onClick?: () => void
}

export function CategoryBadge({ name, color, selected = false, onClick }: CategoryBadgeProps) {
  return (
    <button
      type="button"
      className={`${styles.badge} ${selected ? styles.selected : ''}`}
      style={{ '--badge-color': color } as React.CSSProperties}
      onClick={onClick}
      aria-pressed={selected}
    >
      {name}
    </button>
  )
}
