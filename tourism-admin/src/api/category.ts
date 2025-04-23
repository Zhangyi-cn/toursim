import request from '@/utils/request'

export interface Category {
  id: number
  name: string
  icon: string
  sort_order: number
  status: number
  created_at: string
  updated_at: string
}

export interface CategoryForm {
  id?: number
  name: string
  icon: string
  sort_order: number
}

export interface ApiResponse<T> {
  code: number
  data: T
  message: string
  success: boolean
}

// 获取分类列表
export function getCategoryList() {
  return request.get<ApiResponse<Category[]>>('/admin/attractions/categories')
}

// 创建分类
export function createCategory(data: CategoryForm) {
  return request.post<ApiResponse<Category>>('/admin/attractions/categories', data)
}

// 更新分类
export function updateCategory(data: CategoryForm) {
  return request.put<ApiResponse<Category>>(`/admin/attractions/categories/${data.id}`, data)
}

// 删除分类
export function deleteCategory(id: number) {
  return request.delete<ApiResponse<null>>(`/admin/attractions/categories/${id}`)
} 