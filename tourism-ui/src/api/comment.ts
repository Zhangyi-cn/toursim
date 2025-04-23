import request from '@/utils/request'
import { ApiResponse, PaginatedData } from '@/types/api'

// 评论接口类型定义
export interface Comment {
  id: number
  content: string
  parent_id: number | null
  reply_count: number
  images: string[]
  user: {
    id: number
    nickname: string
    avatar: string
  }
  created_at: string
}

// 获取景点评论列表
export const getAttractionComments = (
  attractionId: number | string,
  params?: {
    page?: number
    per_page?: number
    parent_id?: number
  }
) => {
  return request.get<ApiResponse<PaginatedData<Comment>>>(
    `/api/attractions/${attractionId}/comments`,
    { params }
  )
}

// 添加景点评论
export const addAttractionComment = (
  attractionId: number | string,
  data: {
    content: string
    parent_id?: number
    images?: string[]
  }
) => {
  return request.post<ApiResponse<Comment>>(
    `/api/attractions/${attractionId}/comments`, 
    data
  )
}

// 删除评论
export const deleteComment = (commentId: number) => {
  return request.delete<ApiResponse<null>>(`/api/comments/${commentId}`)
} 