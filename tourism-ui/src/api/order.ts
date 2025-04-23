import request from '@/utils/request'
import type { ApiResponse, PaginatedData } from '@/types/common'
import type { Order, OrderDetail, CreateOrderParams, RefundParams, OrderStats } from '@/types/order'

// 获取订单列表
export function getOrders(params: {
  page?: number
  page_size?: number
  status?: Order['status']
  start_date?: string
  end_date?: string
}) {
  return request.get<ApiResponse<PaginatedData<Order>>>('/api/orders', { params })
}

// 获取订单详情
export function getOrderDetail(id: number) {
  return request.get<ApiResponse<OrderDetail>>(`/api/orders/${id}`)
}

// 创建订单
export function createOrder(data: CreateOrderParams) {
  return request.post<ApiResponse<Order>>('/api/orders', data)
}

// 取消订单
export function cancelOrder(id: number) {
  return request.post<ApiResponse<void>>(`/api/orders/${id}/cancel`)
}

// 支付订单
export function payOrder(id: number, payment_method: string) {
  return request.post<ApiResponse<{
    order_id: number
    payment_url: string
  }>>(`/api/orders/${id}/pay`, { payment_method })
}

// 申请退款
export function refundOrder(id: number, data: RefundParams) {
  return request.post<ApiResponse<void>>(`/api/orders/${id}/refund`, data)
}

// 获取订单统计信息
export function getOrderStats(params?: {
  start_date?: string
  end_date?: string
}) {
  return request.get<ApiResponse<OrderStats>>('/api/orders/stats', { params })
}

// 获取支付方式列表
export function getPaymentMethods() {
  return request.get<ApiResponse<{
    id: string
    name: string
    icon: string
    description: string
  }[]>>('/api/payment-methods')
}

// 获取订单支付状态
export function getOrderPaymentStatus(id: number) {
  return request.get<ApiResponse<{
    status: 'pending' | 'success' | 'failed'
    message?: string
  }>>(`/api/orders/${id}/payment-status`)
}

// 获取退款状态
export function getOrderRefundStatus(id: number) {
  return request.get<ApiResponse<{
    status: 'pending' | 'approved' | 'rejected' | 'completed'
    message?: string
  }>>(`/api/orders/${id}/refund-status`)
}

// 获取订单凭证
export function getOrderVoucher(id: number) {
  return request.get<ApiResponse<{
    order_no: string
    qr_code: string
    valid_date: string
    instructions: string
  }>>(`/api/orders/${id}/voucher`)
}

// 验证订单凭证
export function verifyOrderVoucher(code: string) {
  return request.post<ApiResponse<{
    order_id: number
    status: 'valid' | 'invalid' | 'used' | 'expired'
    message: string
  }>>('/api/orders/verify-voucher', { code })
}

// 获取可用优惠券
export function getAvailableCoupons(params: {
  attraction_id: number
  amount: number
}) {
  return request.get<ApiResponse<{
    id: number
    name: string
    discount: number
    min_amount: number
    valid_until: string
  }[]>>('/api/orders/available-coupons', { params })
}

// 应用优惠券
export function applyCoupon(order_id: number, coupon_id: number) {
  return request.post<ApiResponse<{
    original_amount: number
    discount_amount: number
    final_amount: number
  }>>(`/api/orders/${order_id}/apply-coupon`, { coupon_id })
}

// 删除订单
export function deleteOrder(id: number) {
  return request.delete<ApiResponse<void>>(`/api/orders/${id}`)
} 