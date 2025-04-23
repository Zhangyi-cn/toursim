export interface Order {
  id: number
  order_no: string
  user_id: number
  attraction_id: number
  ticket_id: number
  quantity: number
  total_amount: number
  status: 'pending' | 'paid' | 'cancelled' | 'refunded' | 'completed'
  contact_name: string
  contact_phone: string
  contact_email?: string
  visit_date: string
  payment_method?: string
  payment_time?: string
  refund_time?: string
  refund_reason?: string
  created_at: string
  updated_at: string
  attraction_name?: string
  attraction_image?: string
  ticket_name?: string
  visitor_name?: string
  visitor_phone?: string
}

export interface OrderDetail extends Order {
  attraction: {
    id: number
    name: string
    cover_image: string
  }
  ticket: {
    id: number
    name: string
    price: number
  }
}

export interface CreateOrderParams {
  attraction_id: number
  ticket_id: number
  quantity: number
  contact_name: string
  contact_phone: string
  contact_email?: string
  visit_date: string
}

export interface RefundParams {
  order_id: number
  reason: string
}

export interface OrderStats {
  total_count: number
  pending_count: number
  paid_count: number
  cancelled_count: number
  refunded_count: number
  completed_count: number
  total_amount: number
} 