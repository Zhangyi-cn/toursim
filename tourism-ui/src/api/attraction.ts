import { get, post, del } from '@/utils/request'
import type { Category, Attraction, PaginatedResponse, AttractionQuery } from '@/types/attraction'
import request from '@/utils/request'
import type { CategoryResponse } from '@/types/category'
import type { Collection, CollectionResponse } from '@/types/collection'

// 获取景点分类列表
export const getCategories = () => {
  return get<{ data: Category[] }>('/api/categories')
}

// 获取景点列表
export const getAttractions = (params: AttractionQuery) => {
  // 转换排序参数
  let { order_by, order, ...otherParams } = params
  if (params.order_by === 'views') {
    order_by = 'view_count'
  } else if (params.order_by === 'rating') {
    order_by = 'rating'
  } else {
    order_by = 'created_at'
  }
  
  return request.get<PaginatedResponse<Attraction>>('/api/attractions', {
    ...otherParams,
    order_by,
    order: order || 'desc'
  })
}

// 获取景点详情
export const getAttractionDetail = (id: number) => {
  return request.get<{
    code: number
    msg: string
    data: Attraction
  }>(`/api/attractions/${id}`)
}

// 获取热门景点
export const getHotAttractions = (limit: number = 6) => {
  return get<{ data: Attraction[] }>('/api/attractions/hot', { limit })
}

// 获取推荐景点
export const getRecommendedAttractions = (limit: number = 6) => {
  return get<{ data: Attraction[] }>('/api/attractions/recommended', { limit })
}

// 点赞景点
export const likeAttraction = (attractionId: number) => {
  return post<{
    code: number
    msg: string
    data: {
      like_count: number
    }
  }>(`/api/attractions/${attractionId}/like`)
}

// 取消点赞
export const unlikeAttraction = (attractionId: number) => {
  return post<{
    code: number
    msg: string
    data: {
      like_count: number
    }
  }>(`/api/attractions/${attractionId}/unlike`)
}

// 收藏景点
export const collectAttraction = (attractionId: number) => {
  return post<{
    code: number
    msg: string
    data: null
  }>(`/api/attractions/${attractionId}/collect`)
}

// 取消收藏
export const uncollectAttraction = (attractionId: number) => {
  return post<{
    code: number
    msg: string
    data: null
  }>(`/api/attractions/${attractionId}/uncollect`)
}

// 获取用户收藏列表
export interface CollectionQuery {
  page?: number
  per_page?: number
  type?: 'attraction' | 'guide' | 'note'
}

export const getUserCollections = (params?: CollectionQuery) => {
  return get<CollectionResponse>('/api/collections', params)
}

// 获取相似景点推荐
export const getSimilarAttractions = (id: number, limit: number = 4) => {
  return get<{ data: Attraction[] }>(`/api/attractions/${id}/similar`, { limit })
}

// 增加景点浏览量
export const increaseViewCount = (id: number) => {
  return post<{ message: string }>(`/api/attractions/${id}/view`)
}

// 获取景点分类列表
export const getAttractionCategories = () => {
  return request.get<CategoryResponse>('/api/categories/attractions')
} 