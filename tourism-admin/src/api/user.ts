import request from '@/utils/request'

export interface User {
  id: number
  username: string
  email: string
  phone: string
  avatar: string
  bio: string
  nickname: string
  role: number
  status: number
  created_at: string
  last_login: string
  interest_tags: string[]
}

export interface UserCreateForm {
  username: string
  password: string
  nickname: string
  email: string
  phone: string
  avatar: string
  bio: string
  status: number
}

export interface UserUpdateForm {
  nickname?: string
  email?: string
  phone?: string
  avatar?: string
  bio?: string
  status?: number
}

export interface UserQueryParams {
  page?: number
  per_page?: number
  keyword?: string
  status?: number
}

export interface Pagination {
  total: number
  page: number
  per_page: number
  pages: number
}

export interface UserListResponse {
  items: User[]
  pagination: Pagination
}

// 获取用户列表
export function getUserList(params: UserQueryParams) {
  return request.get<UserListResponse>('/admin/users', { params })
}

// 获取用户详情
export function getUserDetail(id: number) {
  return request.get<User>(`/admin/users/${id}`)
}

// 创建用户
export function createUser(data: UserCreateForm) {
  return request.post<User>('/admin/users', data)
}

// 更新用户信息
export function updateUser(id: number, data: UserUpdateForm) {
  return request.put<User>(`/admin/users/${id}`, data)
}

// 更新用户状态
export function updateUserStatus(id: number, status: number) {
  return request.put(`/admin/users/${id}/status`, { status })
}

// 重置用户密码
export function resetUserPassword(id: number) {
  return request.post<{ new_password: string }>(`/admin/users/${id}/reset_password`)
} 