import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getUserInfo as getUserInfoApi } from '@/api/auth'
import type { LoginParams, ApiResponse, AuthResponse } from '@/types/auth'
import type { User } from '@/types/user'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 静态资源基础URL
const staticBaseUrl = import.meta.env.VITE_STATIC_ASSETS_URL_AVATARS || ''

// 处理头像URL，添加静态资源基础路径
const processAvatarUrl = (avatar: string | undefined | null): string | undefined | null => {
  if (!avatar) return avatar;
  
  // 如果已经是完整URL，直接返回
  if (avatar.startsWith('http')) return avatar;
  
  // 否则添加静态资源基础路径
  // 确保静态资源基础URL和头像路径之间有斜杠
  const baseUrl = staticBaseUrl.endsWith('/') ? staticBaseUrl : `${staticBaseUrl}/`;
  return `${baseUrl}${avatar}`;
}

export const useUserStore = defineStore('user', () => {
  // 用户信息
  const userInfo = ref<User | null>(null)

  // token
  const token = ref<string | null>(localStorage.getItem('token'))

  // 登录状态
  const isLoggedIn = ref(!!token.value)

  // 登录
  const login = async (params: LoginParams) => {
    try {
      const response = await loginApi(params)
      const authData = response.data
      // 保存token
      token.value = authData.token
      localStorage.setItem('token', authData.token)
      
      // 处理头像URL
      if (authData.user && authData.user.avatar) {
        authData.user.avatar = processAvatarUrl(authData.user.avatar)
      }
      
      // 保存用户信息
      userInfo.value = authData.user
      isLoggedIn.value = true
      ElMessage.success('登录成功')
      return true
    } catch (error: any) {
      console.error('Login failed:', error)
      ElMessage.error(error.message || '登录失败，请检查用户名和密码')
      return false
    }
  }

  // 登出
  const logout = () => {
    // 清除token
    token.value = null
    localStorage.removeItem('token')
    // 清除用户信息
    userInfo.value = null
    isLoggedIn.value = false
  }

  // 获取用户信息
  const getUserInfo = async () => {
    try {
      if (token.value) {
        const response = await getUserInfoApi()
        // 直接使用 response.data.data，因为这就是用户信息对象
        if (response.code === 200 && response.success) {
          // 处理头像URL
          if (response.data && response.data.avatar) {
            response.data.avatar = processAvatarUrl(response.data.avatar)
          }
          
          userInfo.value = response.data
          isLoggedIn.value = true
          console.log('User info updated:', userInfo.value)
        } else {
          throw new Error(response.data.message || '获取用户信息失败')
        }
      } else {
        userInfo.value = null
        isLoggedIn.value = false
      }
    } catch (error: any) {
      console.error('Failed to get user info:', error)
      ElMessage.error(error.message || '获取用户信息失败')
      // 如果获取用户信息失败，可能是token过期，清除登录状态
      logout()
    }
  }

  // 更新用户信息
  const updateUserInfo = (userData: Partial<User>) => {
    if (userInfo.value) {
      // 处理头像URL
      if (userData.avatar) {
        userData.avatar = processAvatarUrl(userData.avatar)
      }
      
      userInfo.value = { ...userInfo.value, ...userData }
      console.log('User info updated:', userInfo.value)
    }
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    login,
    logout,
    getUserInfo,
    updateUserInfo
  }
}) 