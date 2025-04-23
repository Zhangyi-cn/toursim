import request from '@/utils/request'

export interface Profile {
  username: string
  nickname: string
  avatar: string
  phone: string
  email: string
  gender: number
}

export interface UpdatePasswordParams {
  oldPassword: string
  newPassword: string
  confirmPassword: string
}

// 获取个人资料
export function getProfile() {
  return request({
    url: '/admin/profile',
    method: 'get'
  })
}

// 更新个人资料
export function updateProfile(data: Profile) {
  return request({
    url: '/admin/profile',
    method: 'put',
    data
  })
}

// 修改密码
export function updatePassword(data: UpdatePasswordParams) {
  return request({
    url: '/admin/profile/password',
    method: 'put',
    data
  })
} 