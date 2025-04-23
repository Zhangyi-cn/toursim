export interface TravelGuide {
  id: number
  title: string
  description: string
  content: string
  cover: string
  category_id: number
  category_name: string
  views: number
  likes: number
  author_id: number
  author_name: string
  author_avatar: string
  is_recommended: boolean
  status: 'draft' | 'published' | 'archived'
  created_at: string
  updated_at: string
}

export interface TravelGuideCategory {
  id: number
  name: string
  description: string
  icon: string
  sort_order: number
  guide_count: number
  created_at: string
  updated_at: string
}

export interface CreateTravelGuideParams {
  title: string
  description: string
  content: string
  cover: string
  category_id: number
  is_recommended?: boolean
  status: 'draft' | 'published'
}

export interface UpdateTravelGuideParams extends Partial<CreateTravelGuideParams> {
  id: number
} 