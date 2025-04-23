import request from '@/utils/request'

// 攻略接口类型定义
export interface Guide {
  id: number
  title: string
  content?: string
  cover_image: string
  category_id: number
  category_name?: string
  user_id?: number
  status: number
  is_official: boolean
  is_hot: boolean
  view_count: number
  like_count: number
  collection_count: number
  comment_count: number
  created_at: string
  updated_at: string
  summary?: string
  author?: string
  tags?: Array<{id: number, name: string}> | string[]
}

// 攻略分类接口类型定义
export interface GuideCategory {
  id: number
  name: string
  icon: string
  sort_order: number
  status: number
  created_at?: string
  updated_at?: string
}

// 攻略查询参数
export interface GuideQuery {
  page?: number
  per_page?: number
  keyword?: string
  category_id?: number
  status?: number
}

// 攻略表单数据
export interface GuideForm {
  title: string
  content: string
  cover_image: string
  category_id: number
  tags: string[]
  summary?: string
  author?: string
  view_count?: number
  like_count?: number
  status: number
}

// 攻略分类表单数据
export interface GuideCategoryForm {
  name: string
  icon?: string
  sort_order: number
  status: number
}

// 获取攻略列表
export function getGuideList(params: GuideQuery) {
  return request({
    url: '/admin/guides',
    method: 'get',
    params
  })
}

// 获取攻略详情
export function getGuideDetail(id: number) {
  return request({
    url: `/admin/guides/${id}`,
    method: 'get'
  })
}

// 创建攻略
export function createGuide(data: GuideForm) {
  return request({
    url: '/admin/guides',
    method: 'post',
    data
  })
}

// 更新攻略
export function updateGuide(id: number, data: GuideForm) {
  return request({
    url: `/admin/guides/${id}`,
    method: 'put',
    data
  })
}

// 删除攻略
export function deleteGuide(id: number) {
  return request({
    url: `/admin/guides/${id}`,
    method: 'delete'
  })
}

// 获取攻略分类列表
export function getGuideCategoryList() {
  return request({
    url: '/admin/guides/categories',
    method: 'get'
  })
}

// 创建攻略分类
export function createGuideCategory(data: GuideCategoryForm) {
  return request({
    url: '/admin/guides/categories',
    method: 'post',
    data
  })
}

// 更新攻略分类
export function updateGuideCategory(id: number, data: GuideCategoryForm) {
  return request({
    url: `/admin/guides/categories/${id}`,
    method: 'put',
    data
  })
}

// 删除攻略分类
export function deleteGuideCategory(id: number) {
  return request({
    url: `/admin/guides/categories/${id}`,
    method: 'delete'
  })
} 