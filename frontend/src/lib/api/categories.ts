import { get, post, del } from './client'
import type { Category, CategoryCreate } from '@/lib/types'

export function getCategories() {
  return get<Category[]>('/categories')
}

export function createCategory(data: CategoryCreate) {
  return post<Category>('/categories', data)
}

export function deleteCategory(categoryId: string) {
  return del(`/categories/${categoryId}`)
}
