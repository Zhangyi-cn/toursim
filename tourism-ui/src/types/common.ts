export interface Banner {
  id: number
  title: string
  image: string
  url?: string
  position: string
  sort_order: number
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedData<T = any> {
  items: T[]
  total: number
}

export interface ApiError {
  code: number
  message: string
  details?: any
} 