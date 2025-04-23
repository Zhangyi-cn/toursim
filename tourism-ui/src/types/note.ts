export interface Note {
  id: number
  title: string
  content: string
  cover_image: string
  category_id: number
  category_name: string
  tags: string[]
  views: number
  likes: number
  collections: number
  comments: number
  is_liked: boolean
  is_collected: boolean
  status: 'draft' | 'published'
  author: {
    id: number
    nickname: string
    avatar: string
    bio?: string
    notes_count?: number
    followers_count?: number
    likes_count?: number
    is_followed?: boolean
  }
  created_at: string
  updated_at: string
}

export interface Comment {
  id: number
  content: string
  user: {
    id: number
    nickname: string
    avatar: string
  }
  created_at: string
  updated_at: string
} 