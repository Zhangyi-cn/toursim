// 分类数据接口
export interface Category {
  id: number
  name: string
  description: string
  type: number
  sort_order: number
  created_at: string
  updated_at: string
}

// API响应的通用格式
export interface ApiResponse<T> {
  code: number
  data: T
  message: string
  success: boolean
}

// 分类列表响应接口
export type CategoryResponse = ApiResponse<Category[]> 