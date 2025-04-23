import request from '@/utils/request'
import type { RecommendationResponse, RecommendationParams } from '@/types/recommendation'

// 获取推荐列表
export const getRecommendations = (params?: RecommendationParams) => {
  return request.get<{
    code: number
    message: string
    data: RecommendationResponse
  }>('/api/recommendations', { params })
}

// 获取今日推荐列表
export const getTodayRecommendations = () => {
  return request.get<{
    code: number
    message: string
    data: RecommendationResponse
  }>('/api/recommendations/today')
}

// 获取特定推荐项目详情
export const getRecommendationDetail = (id: number) => {
  return request.get<RecommendationItem>(`/api/recommendations/${id}`)
}

// 获取个性化推荐列表
export const getPersonalizedRecommendations = (params?: RecommendationParams) => {
  return request.get<{
    code: number
    message: string
    data: RecommendationResponse
  }>('/api/recommendations/personalized', { params })
} 