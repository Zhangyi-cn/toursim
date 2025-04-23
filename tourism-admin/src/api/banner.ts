import request from '@/utils/request'

export interface Banner {
  id: number
  title: string
  image_url: string
  link_url: string
  description: string
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface BannerForm {
  id?: number
  title: string
  image_url: string
  link_url: string
  description: string
  sort_order: number
  is_active: boolean
}

export interface BannerQuery {
  page: number
  pageSize: number
}

export interface Pagination {
  total: number
  page: number
  per_page: number
  pages: number
}

export interface BannerListResponse {
  items: Banner[]
  pagination: Pagination
}

// 获取轮播图列表
export function getBannerList(params: BannerQuery) {
  return request.get<BannerListResponse>('/admin/banners', { params })
}

// 创建轮播图
export function createBanner(data: BannerForm) {
  return request.post('/admin/banners', data)
}

// 更新轮播图
export function updateBanner(data: BannerForm) {
  return request.put(`/admin/banners/${data.id}`, data)
}

// 删除轮播图
export function deleteBanner(id: number) {
  return request.delete(`/admin/banners/${id}`)
} 