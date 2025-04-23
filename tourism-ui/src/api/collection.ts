import request from '@/utils/request'
import type { ApiResponse, PaginatedData } from '@/types/common'

// 定义收藏项类型
export interface CollectionItem {
  id: number
  target_type: string // 'attraction' | 'guide'
  target_id: number
  created_at: string
  target_info: any // 收藏对象的详细信息
}

// 获取用户收藏列表
export const getUserCollections = (params?: {
  type?: string // 收藏类型,可选
  page?: number
  per_page?: number
}) => {
  return request.get<ApiResponse<PaginatedData<CollectionItem>>>('/api/user/collections', { params })
}

// 收藏景区
export const collectAttraction = (attractionId: number) => {
  return request.post<ApiResponse<{ collection_count: number }>>(`/api/attractions/${attractionId}/collect`)
}

// 取消收藏景区
export const uncollectAttraction = (attractionId: number) => {
  return request.post<ApiResponse<{ collection_count: number }>>(`/api/attractions/${attractionId}/uncollect`)
}

// 收藏攻略
export const collectGuide = (guideId: number) => {
  return request.post<ApiResponse<null>>(`/api/collections/guide/${guideId}`)
}

// 取消收藏攻略
export const uncollectGuide = (guideId: number) => {
  return request.delete<ApiResponse<null>>(`/api/collections/guide/${guideId}`)
}

// 处理取消收藏的通用方法
export const uncollectItem = (targetType: 'guide', targetId: number) => {
  if (targetType === 'guide') {
    return uncollectGuide(targetId)
  }
  // 只支持攻略类型
  throw new Error('不支持的收藏类型')
} 