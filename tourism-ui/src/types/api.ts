// API 响应的基础接口
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  success: boolean
}

// 分页数据的接口
export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 用户相关接口
export interface User {
  id: number
  username: string
  email: string
  nickname: string
  avatar: string
  phone?: string
  bio?: string
  created_at: string
  updated_at: string
}

// 登录参数接口
export interface LoginParams {
  username: string
  password: string
  remember?: boolean
}

// 登录响应接口
export interface LoginResponse {
  token: string
  user: User
}

// 注册参数接口
export interface RegisterParams {
  username: string
  password: string
  email: string
  nickname?: string
  phone?: string
}

// 注册响应接口
export interface RegisterResponse {
  token: string
  user: User
}

// 更新用户资料参数接口
export interface UpdateProfileParams {
  nickname?: string
  bio?: string
  phone?: string
  avatar?: string
}

// 修改密码参数接口
export interface ChangePasswordParams {
  old_password: string
  new_password: string
  confirm_password: string
}

// 重置密码参数接口
export interface ResetPasswordParams {
  email: string
  code: string
  new_password: string
  confirm_password: string
} 