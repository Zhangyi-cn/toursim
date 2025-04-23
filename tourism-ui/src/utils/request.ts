import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // 从环境变量获取 API 基础 URL
  timeout: 15000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    // 如果返回的状态码不是200，说明有错误
    if (res.code !== 200 && res.code !== undefined) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(res)
    }
    return res
  },
  (error) => {
    console.error('Response error:', error)
    // 处理后端返回的错误信息
    if (error.response) {
      // 处理 401 未授权的情况
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('userId')
        router.push('/auth/login')
        return Promise.reject(error.response.data || { message: '登录已过期，请重新登录' })
      }
      
      // 处理其他错误状态
      if (error.response.data) {
        return Promise.reject(error.response.data)
      }
    }
    // 如果没有具体错误信息，显示通用错误
    return Promise.reject({ message: '网络请求失败，请稍后重试' })
  }
)

// 封装 GET 请求
export const get = <T>(url: string, params?: any): Promise<T> => {
  return service.get(url, { params })
}

// 封装 POST 请求
export const post = <T>(url: string, data?: any, config?: any): Promise<T> => {
  return service.post(url, data, config)
}

// 封装 PUT 请求
export const put = <T>(url: string, data?: any): Promise<T> => {
  return service.put(url, data)
}

// 封装 DELETE 请求
export const del = <T>(url: string): Promise<T> => {
  return service.delete(url)
}

// 导出请求方法
export default {
  get,
  post,
  put,
  delete: del
}