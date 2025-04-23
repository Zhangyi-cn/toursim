import request from '@/utils/request'
import type { ApiResponse } from '@/types/common'
import type {
  User,
  UserProfile,
  LoginParams,
  RegisterParams,
  UpdateProfileParams,
  ChangePasswordParams,
  ResetPasswordParams
} from '@/types/user'

// 用户登录
export function login(data: LoginParams) {
  return request.post<ApiResponse<{ token: string; user: User }>>('/api/login', data)
}

// 用户注册
export function register(data: RegisterParams) {
  return request.post<ApiResponse<{ token: string; user: User }>>('/api/register', data)
}

// 获取当前用户信息
export function getCurrentUser() {
  return request.get<{
    code: number;
    data: User;
    message: string;
    success: boolean;
  }>('/api/user/profile')
}

// 更新用户信息
export function updateProfile(data: {
  nickname?: string
  avatar?: string
  bio?: string
  phone?: string
  email?: string
}) {
  return request.put<ApiResponse<void>>('/api/user/profile', data)
}

// 修改密码
export function changePassword(data: {
  old_password: string
  new_password: string
}) {
  return request.post<ApiResponse<void>>('/api/user/change_password', data)
}

// 发送重置密码邮件
export function sendResetPasswordEmail(email: string) {
  return request.post<ApiResponse<void>>('/api/password/reset/email', { email })
}

// 重置密码
export function resetPassword(data: ResetPasswordParams) {
  return request.post<ApiResponse<void>>('/api/password/reset', data)
}

// 发送验证码
export function sendVerificationCode(email: string) {
  return request.post<ApiResponse<void>>('/api/verification-code', { email })
}

// 验证邮箱
export function verifyEmail(code: string) {
  return request.post<ApiResponse<void>>('/api/verify-email', { code })
}

// 上传头像
export function uploadAvatar(file: File) {
  const formData = new FormData()
  formData.append('avatar', file)
  formData.append('type', 'image')
  return request.post<{
    code: number;
    data: { avatar: string };
    message: string;
    success: boolean;
  }>('/api/user/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取用户信息
export function getUserProfile(userId: number) {
  return request.get<ApiResponse<UserProfile>>(`/api/user/profile`)
}

// 关注用户
export function followUser(userId: number) {
  return request.post<ApiResponse<void>>(`/api/users/${userId}/follow`)
}

// 取消关注用户
export function unfollowUser(userId: number) {
  return request.delete<ApiResponse<void>>(`/api/users/${userId}/follow`)
}

// 获取关注列表
export function getFollowings(params: { page?: number; page_size?: number }) {
  return request.get<ApiResponse<{ items: UserProfile[]; total: number }>>('/api/user/followings', { params })
}

// 获取粉丝列表
export function getFollowers(params: { page?: number; page_size?: number }) {
  return request.get<ApiResponse<{ items: UserProfile[]; total: number }>>('/api/user/followers', { params })
}

// 获取用户统计信息
export function getUserStats() {
  return request.get<ApiResponse<{
    note_count: number
    following_count: number
    follower_count: number
    like_count: number
    collection_count: number
  }>>('/api/user/stats')
}

// 检查用户名是否可用
export function checkUsername(username: string) {
  return request.get<ApiResponse<{ available: boolean }>>('/api/check-username', { params: { username } })
}

// 检查邮箱是否可用
export function checkEmail(email: string) {
  return request.get<ApiResponse<{ available: boolean }>>('/api/check-email', { params: { email } })
}

// 绑定手机号
export function bindPhone(data: { phone: string; code: string }) {
  return request.post<ApiResponse<void>>('/api/user/phone/bind', data)
}

// 解绑手机号
export function unbindPhone() {
  return request.post<ApiResponse<void>>('/api/user/phone/unbind')
}

// 发送手机验证码
export function sendPhoneCode(phone: string) {
  return request.post<ApiResponse<void>>('/api/phone-code', { phone })
}

// 验证手机号
export function verifyPhone(data: { phone: string; code: string }) {
  return request.post<ApiResponse<void>>('/api/verify-phone', data)
}

// 第三方登录
export function thirdPartyLogin(provider: string, code: string) {
  return request.post<ApiResponse<{ token: string; user: User }>>('/api/third-party/login', { provider, code })
}

// 绑定第三方账号
export function bindThirdParty(provider: string, code: string) {
  return request.post<ApiResponse<void>>('/api/user/third-party/bind', { provider, code })
}

// 解绑第三方账号
export function unbindThirdParty(provider: string) {
  return request.post<ApiResponse<void>>('/api/user/third-party/unbind', { provider })
}

// 获取第三方账号绑定状态
export function getThirdPartyBindings() {
  return request.get<ApiResponse<{
    wechat: boolean
    weibo: boolean
    qq: boolean
  }>>('/api/user/third-party/bindings')
}

// 注销账号
export function deleteAccount(password: string) {
  return request.post<ApiResponse<void>>('/api/user/delete', { password })
}

// 获取用户收藏列表
export function getCollections(params: { page?: number; page_size?: number; type?: string }) {
  return request.get<ApiResponse<{ items: any[]; total: number }>>('/api/user/collections', { params })
}

// 取消收藏
export function cancelCollection(type: string, id: number) {
  return request.delete<ApiResponse<void>>(`/api/user/collections/${type}/${id}`)
}

// 获取用户信息
export function getUserInfo(userId: number) {
  return request.get<ApiResponse<UserProfile>>(`/api/users/${userId}/profile`)
}

// 获取用户游记列表
export function getUserNotes(params: { page?: number; per_page?: number }) {
  return request.get<ApiResponse<{ items: any[]; total: number }>>('/api/user/notes', { params })
}

// 获取用户收藏列表
export function getUserCollections(params: { page?: number; per_page?: number }) {
  return request.get<ApiResponse<{ items: any[]; total: number }>>('/api/user/collections', { params })
}

// 获取用户点赞列表
export function getUserLikes(params: { page?: number; per_page?: number }) {
  return request.get<ApiResponse<{ items: any[]; total: number }>>('/api/user/likes', { params })
}

// 获取用户关注列表
export function getUserFollowing(userId: number, params: { page?: number; per_page?: number }) {
  return request.get<ApiResponse<{ items: UserProfile[]; total: number }>>(`/api/users/${userId}/following`, { params })
}

// 获取用户粉丝列表
export function getUserFollowers(userId: number, params: { page?: number; per_page?: number }) {
  return request.get<ApiResponse<{ items: UserProfile[]; total: number }>>(`/api/users/${userId}/followers`, { params })
} 