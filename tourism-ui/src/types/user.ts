export interface User {
  id: number
  username: string
  email: string
  phone?: string
  nickname?: string
  avatar?: string
  bio?: string
  created_at: string
  last_login?: string
  is_admin: boolean
}

export interface UserProfile extends User {
  like_count: number
  collection_count: number
  note_count: number
  following_count: number
  follower_count: number
}

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
  email: string
  confirmPassword: string
}

export interface UpdateProfileParams {
  nickname?: string
  bio?: string
  email?: string
  phone?: string
  avatar?: string
}

export interface ChangePasswordParams {
  old_password: string
  new_password: string
}

export interface ResetPasswordParams {
  email: string
  code: string
  new_password: string
} 