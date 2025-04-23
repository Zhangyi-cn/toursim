// 轮播图数据接口
export interface Banner {
  id: number
  title: string
  description: string
  image_url: string
  link_url?: string
  sort_order: number
  is_active: boolean
  created_at: string | null
  updated_at: string | null
}

// API响应的通用格式
export interface ApiResponse<T> {
  code: number
  data: T
  message: string
  success: boolean
}

// 轮播图列表数据
export interface BannerList {
  items: Banner[]
}

// 轮播图列表响应接口
export type BannerResponse = ApiResponse<BannerList> 