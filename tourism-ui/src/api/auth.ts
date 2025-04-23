import request from '@/utils/request'
import type { User, LoginParams, RegisterParams, UpdateProfileParams } from '@/types/user'

// API响应接口
export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

// 认证响应接口
export interface AuthResponse {
  token: string
  user: User
}

// 登录
export const login = (data: LoginParams): Promise<{ data: ApiResponse<AuthResponse> }> => {
  return request.post('/api/auth/login', data)
}

// 获取用户信息
export const getUserInfo = (): Promise<{ data: ApiResponse<User> }> => {
  return request.get('/api/user/profile')
}

// 登出
export const logout = (): Promise<{ data: ApiResponse<null> }> => {
  return request.post('/api/auth/logout')
}

// 获取当前用户信息
export const getCurrentUser = (): Promise<{ data: ApiResponse<User> }> => {
  return request.get('/api/auth/current-user')
}

// 注册
export const register = (data: RegisterParams): Promise<{ data: ApiResponse<AuthResponse> }> => {
  return request.post('/api/auth/register', data)
}

// 更新用户信息
export const updateProfile = (data: UpdateProfileParams): Promise<{ data: ApiResponse<User> }> => {
  return request.put('/api/user/profile', data)
}

// 重置密码
export const resetPassword = (data: {
  email: string
  code: string
  newPassword: string
  confirmPassword: string
}): Promise<{ data: ApiResponse<null> }> => {
  return request.post('/api/auth/reset-password', data)
}

// 发送重置密码邮件
export const sendResetPasswordEmail = (email: string): Promise<{ data: ApiResponse<null> }> => {
  return request.post('/api/auth/send-reset-email', { email })
} 