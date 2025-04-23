import request from '@/utils/request'
import type { ApiResponse, PaginatedData } from '@/types/common'
import type { Notification, NotificationCount, NotificationPreference } from '@/types/notification'

// 获取通知列表
export function getNotifications(params: {
  page?: number
  page_size?: number
  type?: Notification['type']
  status?: Notification['status']
}) {
  return request.get<ApiResponse<PaginatedData<Notification>>>('/api/notifications', { params })
}

// 获取通知详情
export function getNotificationDetail(id: number) {
  return request.get<ApiResponse<Notification>>(`/api/notifications/${id}`)
}

// 标记通知为已读
export function markNotificationAsRead(id: number) {
  return request.put<ApiResponse<void>>(`/api/notifications/${id}/read`)
}

// 标记所有通知为已读
export function markAllNotificationsAsRead() {
  return request.put<ApiResponse<void>>('/api/notifications/read-all')
}

// 删除通知
export function deleteNotification(id: number) {
  return request.delete<ApiResponse<void>>(`/api/notifications/${id}`)
}

// 清空通知
export function clearNotifications(type?: Notification['type']) {
  return request.delete<ApiResponse<void>>('/api/notifications/clear', { params: { type } })
}

// 获取通知统计
export function getNotificationCount() {
  return request.get<ApiResponse<NotificationCount>>('/api/notifications/count')
}

// 获取通知设置
export function getNotificationPreferences() {
  return request.get<ApiResponse<NotificationPreference[]>>('/api/notifications/preferences')
}

// 更新通知设置
export function updateNotificationPreference(type: NotificationPreference['type'], data: {
  email_enabled: boolean
  push_enabled: boolean
}) {
  return request.put<ApiResponse<NotificationPreference>>(`/api/notifications/preferences/${type}`, data)
}

// 订阅推送
export function subscribePushNotification(subscription: PushSubscription) {
  return request.post<ApiResponse<void>>('/api/notifications/push/subscribe', subscription)
}

// 取消订阅推送
export function unsubscribePushNotification() {
  return request.post<ApiResponse<void>>('/api/notifications/push/unsubscribe')
} 