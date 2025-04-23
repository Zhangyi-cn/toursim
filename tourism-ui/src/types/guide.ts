export interface Guide {
  id: number
  user_id: number
  name: string
  avatar: string
  gender: 'male' | 'female' | 'other'
  phone: string
  email: string
  languages: string[]
  introduction: string
  certification: string
  years_of_experience: number
  specialties: string[]
  rating_avg: number
  review_count: number
  status: 'active' | 'inactive' | 'pending'
  created_at: string
  updated_at: string
}

export interface GuideReview {
  id: number
  guide_id: number
  user_id: number
  rating: number
  content: string
  images?: string[]
  created_at: string
  updated_at: string
}

export interface GuideSchedule {
  id: number
  guide_id: number
  date: string
  time_slots: {
    start_time: string
    end_time: string
    is_available: boolean
    order_id?: number
  }[]
}

export interface CreateGuideParams {
  name: string
  gender: 'male' | 'female' | 'other'
  phone: string
  email: string
  languages: string[]
  introduction: string
  certification: string
  years_of_experience: number
  specialties: string[]
} 