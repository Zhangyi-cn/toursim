export type ActivityStatus = 'not_started' | 'in_progress' | 'ended'

export interface Activity {
  id: number
  title: string
  description: string
  content: string
  cover_image: string
  images: string[]
  location: string
  start_time: string
  end_time: string
  max_participants: number
  current_participants: number
  price: number
  original_price: number
  view_count: number
  like_count: number
  collection_count: number
  status: ActivityStatus
  notice?: string
  is_joined: boolean
  created_at: string
  updated_at: string
  latitude?: number
  longitude?: number
}

export interface ActivityEnrollment {
  id: number
  activity_id: number
  user_id: number
  name: string
  phone: string
  remark?: string
  status: 'pending' | 'confirmed' | 'cancelled'
  created_at: string
  updated_at: string
}

export const ACTIVITY_STATUS_MAP = {
  not_started: '未开始',
  in_progress: '进行中',
  ended: '已结束'
}

export const ACTIVITY_STATUS_CLASS = {
  not_started: 'upcoming',
  in_progress: 'ongoing',
  ended: 'ended'
} 