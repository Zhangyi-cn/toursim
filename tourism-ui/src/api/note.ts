import request from '@/utils/request'
import type { ApiResponse, PaginatedData } from '@/types/common'

// 游记接口返回类型
export interface Note {
  id: number
  user_id: number
  title: string
  content?: string
  description: string
  cover_image: string
  views: number
  likes: number
  collections: number
  comments: number
  status: number
  status_text: string
  location: string
  latitude?: number
  longitude?: number
  trip_start_date?: string
  trip_end_date?: string
  trip_days?: number
  trip_cost?: number
  attraction_ids?: number[]
  created_at: string
  updated_at: string
  is_liked?: boolean
  is_collected?: boolean
  // 前端额外字段
  user_name?: string
  user_avatar?: string
}

// 创建/更新游记参数
export interface NoteParams {
  title: string
  content: string
  cover_image: string
  summary?: string
  destination?: string
  trip_date?: string
  days?: number
  companions?: string
  cost?: string
  status?: number
}

// 获取游记列表参数
export interface GetNotesParams {
  keyword?: string
  destination?: string
  user_id?: number
  sort?: 'newest' | 'hottest' | 'most_viewed' | 'most_liked' | 'most_collected'
  page?: number
  per_page?: number
}

/**
 * 获取用户的游记列表
 */
export const getUserNotes = (params?: {
  page?: number
  pageSize?: number
  userId?: number
}) => {
  return request.get<ApiResponse<PaginatedData<Note>>>('/api/notes/user', { 
    params: {
      ...params,
      userId: params?.userId || localStorage.getItem('userId')
    }
  })
}

/**
 * 获取游记列表
 */
export const getNotes = async (params?: GetNotesParams) => {
  try {
    const response = await request.get<any>('/api/notes', { params })
    // 判断响应是否为被拦截器拒绝的错误
    if (response && response.code === 0) {
      // code为0表示成功，构造与拦截器期望格式一致的响应
      return {
        code: 200,
        message: response.message,
        data: response.data
      }
    }
    return response
  } catch (error: any) {
    // 处理API返回code为0但被拦截器拒绝的情况
    if (error && typeof error === 'object' && 'code' in error && error.code === 0) {
      return {
        code: 200,
        message: error.message,
        data: error.data
      }
    }
    throw error
  }
}

/**
 * 获取游记详情
 */
export const getNoteDetail = async (id: number) => {
  try {
    const response = await request.get<any>(`/api/notes/${id}`)
    // 判断响应是否为被拦截器拒绝的错误
    if (response && response.code === 0) {
      // code为0表示成功，构造与拦截器期望格式一致的响应
      return {
        code: 200,
        message: response.message,
        data: response.data
      }
    }
    return response
  } catch (error: any) {
    // 处理API返回code为0但被拦截器拒绝的情况
    if (error && typeof error === 'object' && 'code' in error && error.code === 0) {
      return {
        code: 200,
        message: error.message,
        data: error.data
      }
    }
    throw error
  }
}

/**
 * 获取游记分类
 */
export const getNoteCategories = () => {
  return request.get<ApiResponse<{ id: number; name: string }[]>>('/api/notes/categories')
}

/**
 * 创建游记
 */
export const createNote = async (data: NoteParams) => {
  try {
    const response = await request.post<any>('/api/notes', data)
    if (response && response.code === 0) {
      return {
        code: 200,
        message: response.message,
        data: response.data
      }
    }
    return response
  } catch (error: any) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 0) {
      return {
        code: 200,
        message: error.message,
        data: error.data
      }
    }
    throw error
  }
}

/**
 * 更新游记
 */
export const updateNote = async (id: number, data: Partial<NoteParams>) => {
  try {
    const response = await request.put<any>(`/api/notes/${id}`, data)
    if (response && response.code === 0) {
      return {
        code: 200,
        message: response.message,
        data: response.data
      }
    }
    return response
  } catch (error: any) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 0) {
      return {
        code: 200,
        message: error.message,
        data: error.data
      }
    }
    throw error
  }
}

/**
 * 保存草稿
 */
export const saveDraft = (data: {
  title: string
  content: string
  coverImage?: string
  categoryId?: number
  tags?: string[]
}) => {
  return request.post<ApiResponse<Note>>('/api/notes/draft', data)
}

/**
 * 获取游记评论
 */
export const getNoteComments = (id: number, params?: {
  page?: number
  per_page?: number
}) => {
  return request.get<ApiResponse<{
    items: {
      id: number
      user_id: number
      user_name: string
      user_avatar: string
      content: string
      created_at: string
    }[]
    pagination: {
      total: number
      page: number
      per_page: number
      total_pages: number
      has_next: boolean
      has_prev: boolean
    }
  }>>(`/api/notes/${id}/comments`, { params })
}

/**
 * 添加游记评论
 */
export const createNoteComment = (id: number, data: { content: string }) => {
  return request.post<ApiResponse<any>>(`/api/notes/${id}/comments`, data)
}

/**
 * 点赞游记
 */
export const likeNote = (id: number) => {
  return request.post<ApiResponse<null>>(`/api/notes/${id}/like`)
}

/**
 * 取消点赞游记
 */
export const unlikeNote = (id: number) => {
  return request.delete<ApiResponse<null>>(`/api/notes/${id}/like`)
}

/**
 * 收藏游记
 */
export const collectNote = (id: number) => {
  return request.post<ApiResponse<null>>(`/api/notes/${id}/collect`)
}

/**
 * 取消收藏游记
 */
export const uncollectNote = (id: number) => {
  return request.delete<ApiResponse<null>>(`/api/notes/${id}/collect`)
}

/**
 * 获取相关游记
 */
export const getRelatedNotes = (id: number) => {
  return request.get<ApiResponse<Note[]>>(`/api/notes/${id}/related`)
}

/**
 * 删除游记
 */
export const deleteNote = async (id: number) => {
  try {
    const response = await request.delete<any>(`/api/notes/${id}`)
    if (response && response.code === 0) {
      return {
        code: 200,
        message: response.message,
        data: response.data
      }
    }
    return response
  } catch (error: any) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 0) {
      return {
        code: 200,
        message: error.message,
        data: error.data
      }
    }
    throw error
  }
}

/**
 * 获取热门游记
 */
export const getHotNotes = (limit: number = 6) => {
  return request.get<ApiResponse<Note[]>>('/api/notes/hot', { params: { limit } })
}

/**
 * 获取推荐游记
 */
export const getRecommendedNotes = (limit: number = 6) => {
  return request.get<ApiResponse<Note[]>>('/api/notes/recommended', { params: { limit } })
}

/**
 * 获取我的游记列表
 */
export const getMyNotes = async (params?: {
  status?: number
  page?: number
  per_page?: number
}) => {
  try {
    const response = await request.get<any>('/api/notes/my', { params })
    if (response && response.code === 0) {
      return {
        code: 200,
        message: response.message,
        data: response.data
      }
    }
    return response
  } catch (error: any) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 0) {
      return {
        code: 200,
        message: error.message,
        data: error.data
      }
    }
    throw error
  }
}

/**
 * 上传游记图片
 */
export const uploadNoteImage = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await request.post<any>('/api/notes/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    if (response && response.code === 0) {
      return {
        code: 200,
        message: response.message,
        data: response.data
      }
    }
    return response
  } catch (error: any) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 0) {
      return {
        code: 200,
        message: error.message,
        data: error.data
      }
    }
    throw error
  }
} 