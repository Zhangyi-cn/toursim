import request from '@/utils/request'

export interface DashboardData {
  userCount: number
  orderCount: number
  totalRevenue: number
  attractionCount: number
  userTrend: number
  orderTrend: number
  revenueTrend: number
  attractionTrend: number
}

export function getDashboardData() {
  return request({
    url: '/admin/dashboard',
    method: 'get'
  })
}

export function getDashboardChartData(params: {
  type: 'order' | 'revenue'
  timeRange: 'week' | 'month' | 'year'
}) {
  return request({
    url: '/admin/dashboard/chart',
    method: 'get',
    params
  })
}

export function getHotAttractions() {
  return request({
    url: '/admin/dashboard/hot-attractions',
    method: 'get'
  })
}

export function getLatestOrders() {
  return request({
    url: '/admin/dashboard/latest-orders',
    method: 'get'
  })
} 