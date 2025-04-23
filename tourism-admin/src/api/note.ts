import request from '@/utils/request'

export interface User {
  id: number
  username: string
  nickname?: string
  avatar?: string
}

export interface NoteTag {
  id: number
  name: string
}

export interface NoteImage {
  id: number
  url: string
  title?: string
  description?: string
}

export interface Note {
  id: number
  title: string
  content?: string
  description?: string
  cover_image?: string
  location?: string
  status: number
  status_text?: string
  featured: boolean
  views: number
  likes: number
  collections: number
  comments: number
  created_at: string
  updated_at?: string
  user?: User
  tags?: NoteTag[]
  images?: NoteImage[]
}

export interface NoteQuery {
  keyword?: string
  status?: number
  page?: number
  per_page?: number
}

export interface ListResponse<T> {
  items: T[]
  total: number
}

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/**
 * 获取游记列表
 */
export function getNoteList(params: NoteQuery) {
  return request({
    url: '/notes',
    method: 'get',
    params
  })
}

/**
 * 获取游记详情
 */
export function getNoteDetail(id: number) {
  return request({
    url: `/notes/${id}`,
    method: 'get'
  })
}

/**
 * 删除游记
 */
export function deleteNote(id: number) {
  return request({
    url: `/notes/${id}`,
    method: 'delete'
  })
}

/**
 * 更新游记状态
 */
export function updateNoteStatus(id: number, status: number) {
  return request({
    url: `/notes/${id}/status`,
    method: 'put',
    data: { status }
  })
}

/**
 * 将游记设为精选
 */
export function featureNote(id: number) {
  return request({
    url: `/notes/${id}/feature`,
    method: 'put'
  })
}

/**
 * 取消游记精选
 */
export function unfeatureNote(id: number) {
  return request({
    url: `/notes/${id}/feature`,
    method: 'delete'
  })
} 