import type { User } from './user'

// API响应接口
export interface ApiResponse<T> {
  code: number
  message: string
  success: boolean
  data: T
}

// 登录参数接口
export interface LoginParams {
  username: string
  password: string
}

// 认证响应接口
export interface AuthResponse {
  token: string
  user: User
}

// 注册参数接口
export interface RegisterParams {
  username: string
  password: string
  email: string
  nickname?: string
}

// 更新用户信息参数接口
export interface UpdateProfileParams {
  nickname?: string
  avatar?: string
  email?: string
} 