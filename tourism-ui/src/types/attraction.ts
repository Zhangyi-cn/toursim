// 景点分类
export interface Category {
  id: number
  name: string
  description?: string
  icon?: string
  created_at?: string
  updated_at?: string
}

// 景点数据接口
export interface Attraction {
  id: number
  name: string
  description: string
  cover_image: string
  address: string
  longitude: string
  latitude: string
  category_id: number
  open_time: string
  ticket_info: string
  contact: string
  tips: string
  view_count: number
  like_count: number
  collection_count: number
  comment_count: number
  is_hot: boolean
  is_recommended: boolean
  is_liked: boolean
  is_collected: boolean
  created_at: string
  updated_at: string
  price_start?: number
  rating?: number
}

// 分页信息接口
export interface Pagination {
  total: number
  page: number
  per_page: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

// 分页响应接口
export interface PaginatedResponse<T> {
  code: number
  message: string
  data: {
    items: T[]
    pagination: Pagination
  }
}

// 景点查询参数接口
export interface AttractionQuery {
  page?: number
  per_page?: number
  category_id?: number
  keyword?: string
  is_hot?: boolean
  is_recommended?: boolean
  order_by?: string
  order?: 'asc' | 'desc'
}

export interface Ticket {
  id: number
  attraction_id: number
  name: string
  description: string
  price: number
  original_price?: number
  stock: number
  sold_count: number
  start_time?: string
  end_time?: string
  notice?: string
  created_at: string
  updated_at: string
} 