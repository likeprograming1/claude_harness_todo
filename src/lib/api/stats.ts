import { get } from './client'
import type { DashboardStats, WeeklyStats, Insights } from '@/lib/types'

export function getDashboard() {
  return get<DashboardStats>('/stats/dashboard')
}

export function getWeekly() {
  return get<WeeklyStats>('/stats/weekly')
}

export function getInsights() {
  return get<Insights>('/stats/insights')
}
