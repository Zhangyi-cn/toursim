import { defineStore } from 'pinia'
import { login, getProfile, logout } from '@/api/auth'
import type { LoginData, UserInfo, LoginResponse } from '@/api/auth'
import router from '@/router'

// 扩展用户信息类型，使id可为null
interface StoreUserInfo extends Omit<UserInfo, 'id'> {
  id: number | null;
}

interface UserState {
  token: string | null
  userInfo: StoreUserInfo
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('token'),
    userInfo: {
      id: null,
      username: '',
      nickname: '',
      avatar: '',
      role: 0
    }
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    getUserInfo: (state) => state.userInfo
  },
  
  actions: {
    // 设置 token
    setToken(token: string) {
      this.token = token
      localStorage.setItem('token', token)
    },
    
    // 清除 token
    clearToken() {
      this.token = null
      localStorage.removeItem('token')
    },
    
    // 设置用户信息
    setUserInfo(userInfo: UserInfo) {
      this.userInfo = userInfo as StoreUserInfo
    },
    
    // 登录
    async login(loginData: LoginData) {
      const response = await login(loginData)
      console.log('登录响应:', response)
      
      // 正确处理响应格式：token和user在message对象中
      const { message } = response as any
      if (!message || !message.token || !message.user) {
        throw new Error('登录响应格式错误')
      }
      
      this.setToken(message.token)
      this.setUserInfo(message.user)
      return response
    },
    
    // 获取用户资料
    async getProfile() {
      const res = await getProfile()
      this.setUserInfo(res.data)
      return res
    },
    
    // 登出
    async logout() {
      try {
        await logout()
      } catch (error) {
        console.error('Logout failed:', error)
      } finally {
        this.clearToken()
        this.setUserInfo({
          id: null,
          username: '',
          nickname: '',
          avatar: '',
          role: 0
        } as unknown as UserInfo)
        router.push('/login')
      }
    }
  }
}) 