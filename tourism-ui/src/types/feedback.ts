export interface Feedback {
  id: number
  user_id: number
  type: 'bug' | 'feature' | 'suggestion' | 'other'
  title: string
  content: string
  images?: string[]
  status: 'pending' | 'processing' | 'resolved' | 'rejected'
  reply?: string
  created_at: string
  updated_at: string
}

export interface CreateFeedbackParams {
  type: 'bug' | 'feature' | 'suggestion' | 'other'
  title: string
  content: string
  images?: string[]
}

export interface ReplyFeedbackParams {
  feedback_id: number
  reply: string
  status: 'resolved' | 'rejected'
} 