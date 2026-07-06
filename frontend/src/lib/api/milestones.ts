import { get } from './client'
import type { Milestone } from '@/lib/types'

export function getMilestones() {
  return get<Milestone[]>('/milestones')
}
