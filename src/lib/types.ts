export type Priority = 'low' | 'medium' | 'high'

export interface Task {
  id: string
  task_id: string
  title: string
  due_date: string | null
  due_time: string | null
  category_id: string | null
  priority: Priority
  is_done: boolean
  notes: string | null
  created_at: string
}

export interface TaskCreate {
  title: string
  due_date?: string | null
  due_time?: string | null
  category_id?: string | null
  priority?: Priority
  notes?: string | null
}

export interface TaskUpdate {
  title?: string
  due_date?: string | null
  due_time?: string | null
  category_id?: string | null
  priority?: Priority
  notes?: string | null
}

export interface Category {
  id: string
  category_id: string
  name: string
  color: string
  is_default: boolean
}

export interface CategoryCreate {
  name: string
  color: string
}

export interface DashboardStats {
  today: string
  total_today: number
  completed_today: number
  completion_rate: number
  focus_score: number
  priority_tasks: Task[]
  upcoming: Task[]
}

export interface WeeklyDay {
  date: string
  total: number
  completed: number
}

export interface WeeklyStats {
  days: WeeklyDay[]
}

export interface Insights {
  peak_start: string
  peak_end: string
  message: string
}

export interface Milestone {
  id: string
  milestone_id: string
  title: string
  description: string
  achieved_at: string
}

export interface ApiError {
  status: number
  message: string
}
