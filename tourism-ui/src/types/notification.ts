export interface Notification {
  id: number
  user_id: number
  title: string
  content: string
  type: 'system' | 'order' | 'activity' | 'note' | 'follow'
  status: 'unread' | 'read'
  target_id?: number
  target_type?: string
  created_at: string
  updated_at: string
}

export interface NotificationCount {
  total: number
  unread: number
  system: number
  order: number
  activity: number
  note: number
  follow: number
}

export interface NotificationPreference {
  id: number
  user_id: number
  type: 'system' | 'order' | 'activity' | 'note' | 'follow'
  email_enabled: boolean
  push_enabled: boolean
  created_at: string
  updated_at: string
} 