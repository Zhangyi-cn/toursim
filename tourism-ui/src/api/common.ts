import request from '@/utils/request'
import { ApiResponse, PaginatedData } from '@/types/common'
import type { Banner } from '@/types/common'

interface Season {
  id: number
  name: string
  description: string
  start_date: string
  end_date: string
  image: string
  attractions: number[]
  created_at: string
  updated_at: string
}

interface SearchParams {
  q: string
  type?: 'attraction' | 'activity' | 'note'
  page?: number
  page_size?: number
}

// 轮播图接口返回类型
interface Banner {
  id: number
  title: string
  imageUrl: string
  link: string
  sort: number
  status: number
  createTime: string
}

// 获取轮播图列表
export function getBanners() {
  return request.get<{ data: Banner[] }>('/api/banners')
}

// 获取网站统计数据
export function getStatistics() {
  return request.get<{
    data: {
      userCount: number
      noteCount: number
      attractionCount: number
      activityCount: number
    }
  }>('/api/statistics')
}

// 上传文件
export function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<{ data: { url: string } }>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取系统配置
export function getSystemConfig() {
  return request.get<{
    data: {
      siteName: string
      siteDescription: string
      contactEmail: string
      contactPhone: string
    }
  }>('/api/config')
}

// 获取季节信息
export const getSeasons = () => {
  return request.get<ApiResponse<Season[]>>('/api/seasons')
}

// 搜索
export const search = (params: SearchParams) => {
  return request.get<ApiResponse<PaginatedData<any>>>('/api/search', { params })
}

/**
 * 上传图片
 */
export const uploadImage = (data: FormData) => {
  return request.post<ApiResponse<{ url: string }>>('/api/upload/image', data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
} 