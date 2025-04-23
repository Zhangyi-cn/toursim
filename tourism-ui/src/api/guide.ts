import request from '@/utils/request'
import type { ApiResponse, PaginatedData } from '@/types/common'
import type { Guide, GuideReview, GuideSchedule, CreateGuideParams } from '@/types/guide'

// 获取导游列表
export function getGuides(params: {
  page?: number
  page_size?: number
  keyword?: string
  languages?: string[]
  specialties?: string[]
  min_rating?: number
  status?: Guide['status']
}) {
  return request.get<ApiResponse<PaginatedData<Guide>>>('/api/guides', { params })
}

// 获取导游详情
export function getGuideDetail(id: number) {
  return request.get<ApiResponse<Guide>>(`/api/guides/${id}`)
}

// 创建导游信息
export function createGuide(data: CreateGuideParams) {
  return request.post<ApiResponse<Guide>>('/api/guides', data)
}

// 更新导游信息
export function updateGuide(id: number, data: Partial<CreateGuideParams>) {
  return request.put<ApiResponse<Guide>>(`/api/guides/${id}`, data)
}

// 删除导游信息
export function deleteGuide(id: number) {
  return request.delete<ApiResponse<void>>(`/api/guides/${id}`)
}

// 获取导游评价列表
export function getGuideReviews(guideId: number, params: {
  page?: number
  page_size?: number
  rating?: number
}) {
  return request.get<ApiResponse<PaginatedData<GuideReview>>>(`/api/guides/${guideId}/reviews`, { params })
}

// 发表导游评价
export function createGuideReview(guideId: number, data: {
  rating: number
  content: string
  images?: string[]
}) {
  return request.post<ApiResponse<GuideReview>>(`/api/guides/${guideId}/reviews`, data)
}

// 删除导游评价
export function deleteGuideReview(guideId: number, reviewId: number) {
  return request.delete<ApiResponse<void>>(`/api/guides/${guideId}/reviews/${reviewId}`)
}

// 获取导游排班表
export function getGuideSchedule(guideId: number, params: {
  start_date: string
  end_date: string
}) {
  return request.get<ApiResponse<GuideSchedule[]>>(`/api/guides/${guideId}/schedule`, { params })
}

// 更新导游排班
export function updateGuideSchedule(guideId: number, data: {
  date: string
  time_slots: {
    start_time: string
    end_time: string
    is_available: boolean
  }[]
}) {
  return request.put<ApiResponse<GuideSchedule>>(`/api/guides/${guideId}/schedule`, data)
}

// 获取导游统计信息
export function getGuideStats(guideId: number) {
  return request.get<ApiResponse<{
    total_orders: number
    completed_orders: number
    total_revenue: number
    rating_avg: number
    review_count: number
  }>>(`/api/guides/${guideId}/stats`)
}

// 检查导游是否可预约
export function checkGuideAvailability(guideId: number, params: {
  date: string
  start_time: string
  end_time: string
}) {
  return request.get<ApiResponse<{
    available: boolean
    reason?: string
  }>>(`/api/guides/${guideId}/availability`, { params })
} 