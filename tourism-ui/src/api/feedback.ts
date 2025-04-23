import request from '@/utils/request'
import type { ApiResponse, PaginatedData } from '@/types/common'
import type { Feedback, CreateFeedbackParams, ReplyFeedbackParams } from '@/types/feedback'

// 获取反馈列表
export function getFeedbacks(params: {
  page?: number
  page_size?: number
  type?: Feedback['type']
  status?: Feedback['status']
}) {
  return request.get<ApiResponse<PaginatedData<Feedback>>>('/api/user/feedbacks', { params })
}

// 获取反馈详情
export function getFeedbackDetail(id: number) {
  return request.get<ApiResponse<Feedback>>(`/api/user/feedbacks/${id}`)
}

// 创建反馈
export function createFeedback(data: CreateFeedbackParams) {
  return request.post<ApiResponse<Feedback>>('/api/user/feedback', data)
}

// 回复反馈
export function replyFeedback(id: number, data: ReplyFeedbackParams) {
  return request.post<ApiResponse<Feedback>>(`/api/user/feedbacks/${id}/reply`, data)
}

// 删除反馈
export function deleteFeedback(id: number) {
  return request.delete<ApiResponse<void>>(`/api/user/feedbacks/${id}`)
}

// 获取我的反馈列表
export function getMyFeedbacks(params: {
  page?: number
  page_size?: number
  type?: Feedback['type']
  status?: Feedback['status']
}) {
  return request.get<ApiResponse<PaginatedData<Feedback>>>('/api/user/feedbacks', { params })
} 