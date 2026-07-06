import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { getCategories } from '@/lib/api/categories'
import { createTask } from '@/lib/api/tasks'
import type { Category, Priority, TaskCreate } from '@/lib/types'
import { CategoryBadge } from '@/components/ui/CategoryBadge'
import { ApiError } from '@/lib/api/client'
import styles from './new.module.css'

const PRIORITIES: { value: Priority; label: string; color: string }[] = [
  { value: 'high',   label: '높음', color: '#FF3B30' },
  { value: 'medium', label: '중간', color: '#FF9500' },
  { value: 'low',    label: '낮음', color: '#34C759' },
]

interface FormState {
  title: string
  due_date: string
  due_time: string
  category_id: string
  priority: Priority
  notes: string
}

interface FormErrors {
  title?: string
  due_time?: string
}

function validate(form: FormState): FormErrors {
  const errors: FormErrors = {}
  if (!form.title.trim()) {
    errors.title = '할 일 이름을 입력해주세요.'
  } else if (form.title.trim().length > 200) {
    errors.title = '200자 이하로 입력해주세요.'
  }
  if (form.due_time && !form.due_date) {
    errors.due_time = '시간을 설정하려면 마감일을 먼저 선택해주세요.'
  }
  return errors
}

export default function NewTaskPage() {
  const router = useRouter()
  const [categories, setCategories] = useState<Category[]>([])
  const [form, setForm] = useState<FormState>({
    title: '',
    due_date: '',
    due_time: '',
    category_id: '',
    priority: 'medium',
    notes: '',
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [submitting, setSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  useEffect(() => {
    getCategories().then(setCategories).catch(() => {})
  }, [])

  const set = (field: keyof FormState) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
    setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setForm((prev) => ({
      ...prev,
      due_date: val,
      due_time: val ? prev.due_time : '',
    }))
  }

  const handleCategoryToggle = (categoryId: string) => {
    setForm((prev) => ({
      ...prev,
      category_id: prev.category_id === categoryId ? '' : categoryId,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const errs = validate(form)
    if (Object.keys(errs).length) {
      setErrors(errs)
      return
    }

    const payload: TaskCreate = {
      title: form.title.trim(),
      due_date: form.due_date || null,
      due_time: form.due_time || null,
      category_id: form.category_id || null,
      priority: form.priority,
      notes: form.notes.trim() || null,
    }

    setSubmitting(true)
    setServerError(null)
    try {
      await createTask(payload)
      router.push('/tasks')
    } catch (err) {
      if (err instanceof ApiError) {
        setServerError(`저장 실패 (${err.status}): ${err.message}`)
      } else {
        setServerError('저장 중 오류가 발생했습니다.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      {/* 할 일 이름 */}
      <div className={styles.field}>
        <input
          className={`${styles.titleInput} ${errors.title ? styles.inputError : ''}`}
          type="text"
          placeholder="할 일 이름을 입력하세요"
          value={form.title}
          onChange={set('title')}
          maxLength={200}
          autoFocus
        />
        {errors.title && <p className={styles.errorMsg}>{errors.title}</p>}
      </div>

      <div className={styles.divider} />

      {/* 마감일 */}
      <div className={styles.row}>
        <label className={styles.rowLabel}>
          <CalendarIcon />
          <span>마감일</span>
        </label>
        <input
          className={styles.dateInput}
          type="date"
          value={form.due_date}
          onChange={handleDateChange}
        />
      </div>

      {/* 시간 */}
      <div className={styles.row}>
        <label className={styles.rowLabel}>
          <ClockIcon />
          <span>시간</span>
        </label>
        <input
          className={styles.dateInput}
          type="time"
          value={form.due_time}
          onChange={set('due_time')}
          disabled={!form.due_date}
        />
        {errors.due_time && <p className={styles.errorMsg}>{errors.due_time}</p>}
      </div>

      {/* 카테고리 */}
      {categories.length > 0 && (
        <div className={styles.field}>
          <p className={styles.fieldLabel}>카테고리</p>
          <div className={styles.chips}>
            {categories.map((cat) => (
              <CategoryBadge
                key={cat.category_id}
                name={cat.name}
                color={cat.color}
                selected={form.category_id === cat.category_id}
                onClick={() => handleCategoryToggle(cat.category_id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* 우선순위 */}
      <div className={styles.field}>
        <p className={styles.fieldLabel}>우선순위</p>
        <div className={styles.chips}>
          {PRIORITIES.map(({ value, label, color }) => (
            <button
              key={value}
              type="button"
              className={`${styles.priorityChip} ${form.priority === value ? styles.prioritySelected : ''}`}
              style={{ '--chip-color': color } as React.CSSProperties}
              onClick={() => setForm((prev) => ({ ...prev, priority: value }))}
              aria-pressed={form.priority === value}
            >
              <span className={styles.priorityDot} />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* 추가 메모 */}
      <div className={styles.field}>
        <p className={styles.fieldLabel}>추가 메모</p>
        <textarea
          className={styles.textarea}
          placeholder="선택 사항"
          value={form.notes}
          onChange={set('notes')}
          rows={3}
        />
      </div>

      {serverError && <p className={styles.serverError}>{serverError}</p>}

      {/* 액션 버튼 */}
      <div className={styles.actions}>
        <button
          type="button"
          className={styles.cancelBtn}
          onClick={() => router.back()}
        >
          취소
        </button>
        <button
          type="submit"
          className={styles.submitBtn}
          disabled={submitting}
        >
          {submitting ? '저장 중…' : '할 일 저장'}
        </button>
      </div>
    </form>
  )
}

function CalendarIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <rect x="2" y="3" width="14" height="13" rx="2" stroke="currentColor" strokeWidth="1.4" />
      <line x1="2" y1="7.5" x2="16" y2="7.5" stroke="currentColor" strokeWidth="1.4" />
      <line x1="6" y1="2" x2="6" y2="5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <line x1="12" y1="2" x2="12" y2="5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  )
}

function ClockIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.4" />
      <path d="M9 5.5V9l2.5 2" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  )
}
