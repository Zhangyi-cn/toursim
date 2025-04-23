import request from '@/utils/request'

export interface AttractionImage {
  url: string
  title: string
  description: string
  sort_order: number
}

export interface Attraction {
  id: number
  name: string
  description: string
  cover_image: string
  attraction_images: AttractionImage[]
  address: string
  longitude: number
  latitude: number
  category_id: number
  category_name: string
  region_id: number
  open_time: string
  ticket_info: string
  traffic_info: string
  tips: string
  status: number
  like_count: number
  collection_count: number
  comment_count: number
  view_count: number
  is_hot: boolean
  is_recommended: boolean
  created_at: string
  updated_at: string
}

export interface AttractionForm {
  id?: number
  name: string
  category_id?: number
  description: string
  address: string
  latitude?: number
  longitude?: number
  open_time?: string
  ticket_info?: string
  traffic_info?: string
  cover_image?: string
  tips?: string
  status?: number
  images?: AttractionImage[]
  tags?: number[]
}

export interface Pagination {
  total: number
  page: number
  per_page: number
  pages: number
}

export interface AttractionListResponse {
  items: Attraction[]
  pagination: {
    page: number
    pages: number
    per_page: number
    total: number
  }
}

export interface ApiResponse<T> {
  code: number
  data: T
  message: string
  success: boolean
}

// 获取景点列表
export function getAttractionList(params: {
  page?: number
  per_page?: number
  keyword?: string
  category_id?: number
}) {
  return request.get<ApiResponse<AttractionListResponse>>('/admin/attractions', { params })
}

// 创建景点
export function createAttraction(data: AttractionForm) {
  return request.post<ApiResponse<Attraction>>('/admin/attractions', data)
}

// 获取景点详情
export function getAttractionDetail(id: number) {
  return request.get<ApiResponse<Attraction>>(`/admin/attractions/${id}`)
}

// 更新景点
export function updateAttraction(data: AttractionForm) {
  return request.put<ApiResponse<Attraction>>(`/admin/attractions/${data.id}`, data)
}

// 删除景点
export function deleteAttraction(id: number) {
  return request.delete<ApiResponse<null>>(`/admin/attractions/${id}`)
}

// 上传景点图片
export function uploadAttractionImage(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<ApiResponse<{ url: string }>>('/admin/attractions/upload/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
} 