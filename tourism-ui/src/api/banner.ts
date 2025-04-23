import request from '@/utils/request'
import type { BannerResponse } from '@/types/banner'

// 获取轮播图列表
export const getBanners = () => {
  return request.get<BannerResponse>('/api/system/banners')
} 