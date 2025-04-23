import { ElMessage } from 'element-plus'

// 定义错误接口
export interface ApiError {
  code: number;
  message: string;
}

/**
 * 处理API请求错误
 * @param error 错误对象
 * @param customMessage 自定义错误消息（可选）
 */
export function handleApiError(error: unknown, customMessage?: string): void {
  console.error('API Error:', error)
  
  // 如果是API标准错误
  if (error && typeof error === 'object' && 'code' in error && 'message' in error) {
    const apiError = error as ApiError
    ElMessage.error(customMessage || apiError.message)
    return
  }
  
  // 其他类型错误
  if (error instanceof Error) {
    ElMessage.error(customMessage || error.message)
    return
  }
  
  // 未知错误
  ElMessage.error(customMessage || '发生未知错误')
}

/**
 * 捕获API错误的包装函数
 * @param apiCall API调用函数
 * @param errorMessage 自定义错误消息（可选）
 * @returns 包装后的异步函数
 */
export function withErrorHandling<T>(
  apiCall: () => Promise<T>,
  errorMessage?: string
): Promise<T | undefined> {
  return apiCall().catch(error => {
    handleApiError(error, errorMessage)
    return undefined
  })
} 