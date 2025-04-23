import request from '@/utils/request'
import { Activity } from '@/types/activity'
import { ApiResponse, PaginatedData } from '@/types/common'

interface ActivityEnrollment {
  activity_id: number
  user_id: number
  status: 'pending' | 'confirmed' | 'cancelled'
  created_at: string
  updated_at: string
}

interface GetActivitiesParams {
  page?: number
  page_size?: number
  q?: string
  status?: Activity['status']
  sort?: string
}

/**
 * 获取活动列表
 */
export const getActivities = (params: {
  page: number
  pageSize: number
  category?: string
  keyword?: string
  status?: number
}) => {
  return request.get<{
    data: {
      list: Activity[]
      total: number
    }
  }>('/api/activities', params)
}

/**
 * 获取活动详情
 */
export const getActivityDetail = (id: number) => {
  return request.get<{ data: Activity }>(`/activities/${id}`)
}

/**
 * 报名参加活动
 */
export const joinActivity = (id: number) => {
  return request.post<ApiResponse<null>>(`/api/activities/${id}/join`)
}

/**
 * 取消报名活动
 */
export const cancelActivity = (id: number) => {
  return request.delete<ApiResponse<null>>(`/api/activities/${id}/join`)
}

export const getJoinedActivities = (params: Omit<GetActivitiesParams, 'sort'>) => {
  return request.get<ApiResponse<PaginatedData<Activity>>>('/api/activities/joined', { params })
}

export function likeActivity(id: number) {
  return request({
    url: `/api/likes/activity/${id}`,
    method: 'post'
  })
}

export function unlikeActivity(id: number) {
  return request({
    url: `/api/likes/activity/${id}`,
    method: 'delete'
  })
}

export function collectActivity(id: number) {
  return request({
    url: `/api/collections/activity/${id}`,
    method: 'post'
  })
}

export function uncollectActivity(id: number) {
  return request({
    url: `/api/collections/activity/${id}`,
    method: 'delete'
  })
}

/**
 * 获取最新活动
 */
export function getLatestActivities(limit: number = 6) {
  return request.get<{ data: Activity[] }>('/activities/latest', { limit })
}

/**
 * 获取热门活动
 */
export function getHotActivities(limit: number = 6) {
  return request.get<{ data: Activity[] }>('/api/activities/hot', { limit })
}

/**
 * 获取活动分类
 */
export function getActivityCategories() {
  return request.get<{ data: string[] }>('/api/activities/categories')
}

/**
 * 报名活动
 */
export function enrollActivity(id: number, data: {
  name: string
  phone: string
  email: string
  participants: number
}) {
  return request.post<{ message: string }>(`/activities/${id}/enroll`, data)
}

/**
 * 取消报名
 */
export function cancelEnrollment(id: number) {
  return request.delete<{ message: string }>(`/activities/${id}/enroll`)
}

/**
 * 获取活动评论
 */
export function getActivityReviews(id: number, params: {
  page: number
  pageSize: number
}) {
  return request.get<{
    data: {
      list: {
        id: number
        userId: number
        username: string
        avatar: string
        content: string
        rating: number
        createTime: string
      }[]
      total: number
    }
  }>(`/activities/${id}/reviews`, params)
}

/**
 * 发表活动评论
 */
export function createActivityReview(id: number, data: {
  content: string
  rating: number
}) {
  return request.post<{ message: string }>(`/activities/${id}/reviews`, data)
} 