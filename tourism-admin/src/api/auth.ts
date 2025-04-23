import request from '@/utils/request'

export interface LoginData {
  username: string
  password: string
}

export interface UserInfo {
  id: number
  username: string
  nickname: string
  avatar?: string
  email?: string
  role: number
}

export interface LoginResponse {
  code: number
  message: string
  success: boolean
  token: string
  user: UserInfo
}

// 登录
export function login(data: LoginData) {
  return request({
    url: '/admin/login',
    method: 'post',
    data
  })
}

export function getProfile() {
  return request({
    url: '/admin/profile',
    method: 'get'
  })
}

export function updateProfile(data: any) {
  return request({
    url: '/admin/profile',
    method: 'put',
    data
  })
}

export function updatePassword(data: {
  oldPassword: string
  newPassword: string
}) {
  return request({
    url: '/admin/password',
    method: 'put',
    data
  })
}

export function logout() {
  return request({
    url: '/admin/logout',
    method: 'post'
  })
} 