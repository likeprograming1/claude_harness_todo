import type { Priority } from '@/lib/types'

const CONFIG: Record<Priority, { label: string; color: string }> = {
  high:   { label: '높음', color: '#FF3B30' },
  medium: { label: '중간', color: '#FF9500' },
  low:    { label: '낮음', color: '#34C759' },
}

interface PriorityIconProps {
  priority: Priority
  showLabel?: boolean
}

export function PriorityIcon({ priority, showLabel = false }: PriorityIconProps) {
  const { label, color } = CONFIG[priority]
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
        <circle cx="6" cy="6" r="5" fill={color} />
      </svg>
      {showLabel && (
        <span style={{ fontSize: 12, color, fontWeight: 500 }}>{label}</span>
      )}
    </span>
  )
}
