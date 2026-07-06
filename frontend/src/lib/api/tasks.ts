import { get, post, put, patch, del } from './client'
import type { Task, TaskCreate, TaskUpdate } from '@/lib/types'

export function getTasks(params?: {
  date?: string
  category_id?: string
  done?: boolean
  priority?: string
}) {
  const query: Record<string, string> = {}
  if (params?.date) query.date = params.date
  if (params?.category_id) query.category_id = params.category_id
  if (params?.done !== undefined) query.done = String(params.done)
  if (params?.priority) query.priority = params.priority
  return get<Task[]>('/tasks', Object.keys(query).length ? query : undefined)
}

export function getTask(taskId: string) {
  return get<Task>(`/tasks/${taskId}`)
}

export function createTask(data: TaskCreate) {
  return post<Task>('/tasks', data)
}

export function updateTask(taskId: string, data: TaskUpdate) {
  return put<Task>(`/tasks/${taskId}`, data)
}

export function toggleDone(taskId: string) {
  return patch<Task>(`/tasks/${taskId}/done`)
}

export function deleteTask(taskId: string) {
  return del(`/tasks/${taskId}`)
}
