import request from '@/utils/request'

export interface Comment {
  id: number
  user_id: number
  content_type: 'attraction' | 'note' | 'guide'
  content_id: number
  content: string
  images: string[]
  parent_id: number | null
  like_count: number
  status: number
  status_text?: string
  created_at: string
  updated_at: string
  user?: {
    id: number
    username: string
    nickname?: string
    avatar?: string
  }
  target_name?: string
  replies_count?: number
  target_info?: {
    id: number
    name: string
    cover_image?: string
  }
}

export interface CommentQuery {
  keyword?: string
  user_id?: number
  target_type?: string
  target_id?: number
  status?: number
  start_date?: string
  end_date?: string
  page?: number
  per_page?: number
}

// 获取评论列表
export function getCommentList(params: CommentQuery) {
  return request({
    url: '/admin/comments',
    method: 'get',
    params
  })
}

// 获取评论详情
export function getCommentDetail(id: number) {
  return request({
    url: `/admin/comments/${id}`,
    method: 'get'
  })
}

// 审核通过评论
export function approveComment(id: number) {
  return request({
    url: `/admin/comments/${id}/approve`,
    method: 'post'
  })
}

// 拒绝评论
export function rejectComment(id: number, reason?: string) {
  return request({
    url: `/admin/comments/${id}/reject`,
    method: 'post',
    data: reason ? { reason } : {}
  })
}

// 删除评论
export function deleteComment(id: number) {
  return request({
    url: `/admin/comments/${id}`,
    method: 'delete'
  })
} 