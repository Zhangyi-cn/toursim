export interface History {
  id: number
  user_id: number
  target_id: number
  target_type: 'attraction' | 'activity' | 'note'
  created_at: string
  updated_at: string
}

export interface HistoryDetail extends History {
  target: {
    id: number
    title?: string
    name?: string
    cover_image: string
  }
}

export interface HistoryStats {
  total_count: number
  attraction_count: number
  activity_count: number
  note_count: number
} 