import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import router from '@/router'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api', // API 的 base_url
  timeout: 15000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    // 对请求错误做些什么
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    console.log('API响应数据:', res) // 调试日志
    
    // 如果响应不是标准格式，直接返回
    if (!res.code) {
      return res
    }
    
    // 如果响应码不是 200，说明有错误
    if (res.code !== 200) {
      // 401: 未登录或 token 过期
      if (res.code === 401) {
        // 清除本地存储的 token
        localStorage.removeItem('token')
        // 重定向到登录页
        router.push('/login')
      }
      
      return Promise.reject({
        code: res.code,
        message: res.message || 'Error'
      })
    }
    
    return res // 直接返回响应数据
  },
  (error) => {
    console.error('Response error:', error)
    return Promise.reject({
      code: error.response?.status || 500,
      message: error.message || '请求失败'
    })
  }
)

// 封装 GET 请求
export function get(url: string, params?: any) {
  return service.get(url, { params })
}

// 封装 POST 请求
export function post(url: string, data?: any) {
  return service.post(url, data)
}

// 封装 PUT 请求
export function put(url: string, data?: any) {
  return service.put(url, data)
}

// 封装 DELETE 请求
export function del(url: string) {
  return service.delete(url)
}

export default service 