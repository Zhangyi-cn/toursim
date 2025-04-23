import request from '@/utils/request'

// 攻略标签接口
interface GuideTag {
  id: number
  name: string
}

// 攻略分类接口
export interface GuideCategory {
  id: number
  name: string
  icon: string
  sort_order: number
  status: number
  created_at: string
  updated_at: string
}

// 攻略列表项接口
export interface GuideListItem {
  id: number
  title: string
  content: string
  cover_image: string
  category_id: number
  category_name: string
  user_id: number
  user_name?: string
  user_avatar?: string
  status: number
  is_official?: boolean
  is_hot?: boolean
  view_count: number
  like_count: number
  collection_count: number
  comment_count: number
  created_at: string
  updated_at: string
  tags?: GuideTag[]
  has_liked?: boolean
  has_collected?: boolean
}

// 分页信息接口
interface Pagination {
  total: number
  page: number
  per_page: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

// 获取攻略列表的参数接口
interface GetGuidesParams {
  page?: number
  per_page?: number
  category_id?: number
  keyword?: string
  is_hot?: number
  is_official?: number
  order_by?: string
  order?: 'desc' | 'asc'
}

// 创建攻略的参数接口
export interface CreateGuideParams {
  title: string
  content: string
  category_id: number
  cover_image?: string
  status?: number
}

// 更新攻略的参数接口
export interface UpdateGuideParams {
  title?: string
  content?: string
  cover_image?: string
  category_id?: number
  status?: number
}

// 图片上传响应接口
export interface UploadResponse {
  code: number
  success: boolean
  message: string
  data: {
    url: string
    filename: string
    original_name: string
    file_type: string
    size: number
    uploaded_at: string
  }
}

// 获取攻略列表
export function getGuides(params: GetGuidesParams = {}) {
  return request.get<{
    code: number
    success: boolean
    message: string
    data: {
      guides: GuideListItem[]
      pagination: Pagination
    }
  }>('/api/guides', params)
}

// 获取攻略分类
export function getGuideCategories() {
  return request.get<{
    code: number
    success: boolean
    message: string
    data: GuideCategory[]
  }>('/api/categories/guides')
}

// 创建攻略
export function createGuide(data: CreateGuideParams) {
  return request.post<{
    code: number
    success: boolean
    message: string
    data: GuideListItem
  }>('/api/guides', data)
}

// 更新攻略
export function updateGuide(id: number, data: UpdateGuideParams) {
  return request.put<{
    code: number
    success: boolean
    message: string
    data: GuideListItem
  }>(`/api/guides/${id}`, data)
}

// 删除攻略
export function deleteGuide(id: number) {
  return request.delete<{
    code: number
    success: boolean
    message: string
  }>(`/api/guides/${id}`)
}

// 获取我的攻略列表
export function getMyGuides(params: { page: number; limit: number }) {
  return request.get<{
    code: number
    success: boolean
    message: string
    data: {
      guides: GuideListItem[]
      pagination: Pagination
    }
  }>('/api/guides/my', params)
}

// 上传图片
export function uploadImage(file: File, folder: string = 'guides') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('type', 'image')
  formData.append('folder', folder)

  return request.post<UploadResponse>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 评论接口
export interface Comment {
  id: number
  user_id: number
  content_type: string
  content_id: number
  content: string
  images: string[]
  parent_id: number | null
  like_count: number
  status: number
  created_at: string
  updated_at: string
  reply_count?: number
  user?: {
    id: number
    username: string
    avatar: string
  }
}

// 获取攻略评论参数
export interface GetCommentsParams {
  page?: number
  per_page?: number
  parent_id?: number | null
  sort_by?: 'latest' | 'score'
}

// 发表评论参数
export interface AddCommentParams {
  content: string
  score?: number
  parent_id?: number | null
  reply_to?: number | null
}

// 获取攻略评论
export function getGuideComments(guideId: number, params: GetCommentsParams = {}) {
  return request.get<{
    code: number
    success: boolean
    message: string
    data: {
      items: Comment[]
      total: number
      page: number
      per_page: number
      pages: number
    }
  }>(`/api/guides/${guideId}/comments`, params)
}

// 发表评论
export function addComment(guideId: number, data: AddCommentParams) {
  return request.post<{
    code: number
    success: boolean
    message: string
    data: Comment
  }>(`/api/guides/${guideId}/comments`, data)
}

// 点赞攻略
export function likeGuide(guideId: number) {
  return request.post<{
    code: number
    success: boolean
    message: string
    data: { is_liked: boolean }
  }>(`/api/likes/guide/${guideId}`)
}

// 取消点赞
export function unlikeGuide(guideId: number) {
  return request.delete<{
    code: number
    success: boolean
    message: string
    data: { is_liked: boolean }
  }>(`/api/likes/guide/${guideId}`)
}

// 收藏攻略
export function collectGuide(guideId: number) {
  return request.post<{
    code: number
    success: boolean
    message: string
    data: { is_collected: boolean }
  }>(`/api/collections/guide/${guideId}`)
}

// 取消收藏
export function uncollectGuide(guideId: number) {
  return request.delete<{
    code: number
    success: boolean
    message: string
    data: { is_collected: boolean }
  }>(`/api/collections/guide/${guideId}`)
}

// 检查是否已点赞和收藏
export function checkGuideStatus(guideId: number) {
  return request.get<{
    code: number
    success: boolean
    message: string
    data: {
      is_liked: boolean
      is_collected: boolean
    }
  }>(`/api/guides/${guideId}/status`)
}

// 获取推荐攻略
export function getRecommendedGuides(limit: number = 6) {
  return request.get<{
    code: number
    success: boolean
    message: string
    data: GuideListItem[]
  }>('/api/guides/recommended', { limit })
}

// 获取热门攻略
export function getHotGuides(limit: number = 6) {
  return request.get<{
    code: number
    success: boolean
    message: string
    data: GuideListItem[]
  }>('/api/guides/hot', { limit })
}

// 旅游攻略接口返回类型
interface TravelGuide {
  id: number
  title: string
  description: string
  content: string
  coverImage: string
  destination: string
  duration: number
  budget: number
  difficulty: string
  bestTime: string
  tips: string[]
  viewCount: number
  likeCount: number
  userId: number
  username: string
  userAvatar: string
  createTime: string
  updateTime: string
}

// 获取旅游攻略列表
export function getTravelGuides(params: {
  page: number
  pageSize: number
  destination?: string
  keyword?: string
  difficulty?: string
}) {
  return request.get<{
    data: {
      list: TravelGuide[]
      total: number
    }
  }>('/travel-guides', params)
}

// 获取旅游攻略详情
export function getTravelGuideDetail(id: number) {
  return request.get<{ data: TravelGuide }>(`/travel-guides/${id}`)
}

// 创建旅游攻略
export function createTravelGuide(data: {
  title: string
  description: string
  content: string
  coverImage: string
  destination: string
  duration: number
  budget: number
  difficulty: string
  bestTime: string
  tips: string[]
}) {
  return request.post<{ data: TravelGuide }>('/travel-guides', data)
}

// 更新旅游攻略
export function updateTravelGuide(id: number, data: {
  title?: string
  description?: string
  content?: string
  coverImage?: string
  destination?: string
  duration?: number
  budget?: number
  difficulty?: string
  bestTime?: string
  tips?: string[]
}) {
  return request.put<{ data: TravelGuide }>(`/travel-guides/${id}`, data)
}

// 删除旅游攻略
export function deleteTravelGuide(id: number) {
  return request.delete<{ message: string }>(`/travel-guides/${id}`)
}

// 获取目的地列表
export function getDestinations() {
  return request.get<{ data: string[] }>('/travel-guides/destinations')
}

// 获取攻略分类列表
export interface TravelGuideCategory {
  id: number
  name: string
  description?: string
}

export function getTravelGuideCategories() {
  return request.get<{ data: TravelGuideCategory[] }>('/travel-guides/categories')
}

// 获取攻略详情
export function getGuideDetail(id: number) {
  return request.get<{
    code: number
    success: boolean
    message: string
    data: GuideListItem
  }>(`/api/guides/${id}`)
} 