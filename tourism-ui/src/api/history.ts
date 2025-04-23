import request from '@/utils/request'
import type { ApiResponse, PaginatedData } from '@/types/common'
import type { History, HistoryDetail, HistoryStats } from '@/types/history'

// 获取浏览历史列表
export function getHistories(params: {
  page?: number
  page_size?: number
  target_type?: History['target_type']
  start_date?: string
  end_date?: string
}) {
  return request.get<ApiResponse<PaginatedData<HistoryDetail>>>('/api/history/browse', { params })
}

// 获取历史记录详情
export function getHistoryDetail(id: number) {
  return request.get<ApiResponse<HistoryDetail>>(`/api/histories/${id}`)
}

// 删除历史记录
export function deleteHistory(id: number) {
  return request.delete<ApiResponse<void>>(`/api/histories/${id}`)
}

// 清空历史记录
export function clearHistories(target_type?: History['target_type']) {
  return request.delete<ApiResponse<void>>('/api/history/browse/clear', { params: { target_type } })
}

// 获取历史记录统计
export function getHistoryStats(params?: {
  start_date?: string
  end_date?: string
}) {
  return request.get<ApiResponse<HistoryStats>>('/api/history/stats', { params })
}

// 添加历史记录
export function addHistory(data: {
  target_id: number
  target_type: History['target_type']
}) {
  return request.post<ApiResponse<History>>('/api/histories', data)
} 