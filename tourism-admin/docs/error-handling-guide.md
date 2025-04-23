# 错误处理最佳实践指南

## 概述

本文档介绍了项目中统一的错误处理机制，旨在避免重复的错误处理代码，提高代码的可维护性和用户体验。

## 问题

在之前的代码中，存在以下问题：

1. 在 axios 拦截器中已经处理了错误（显示 ElMessage），但在组件中又再次捕获同样的错误并显示另一条消息
2. 不同组件对同类错误的处理方式不一致
3. 用户可能会看到多个错误提示（一个来自拦截器，一个来自组件）

## 解决方案

我们采用了以下策略来统一错误处理：

1. **拦截器中不显示错误消息**：拦截器仅负责标准化错误对象，不直接显示错误提示
2. **统一的错误处理工具**：创建了 `error-handler.ts` 工具，提供统一的错误处理函数
3. **组件中使用统一工具**：所有组件统一使用错误处理工具来显示错误消息
4. **充分利用后端返回的错误信息**：优先使用后端返回的错误信息，而不是自定义的通用错误消息

## 主要修改

1. **src/utils/request.ts**
   - 移除了拦截器中的 ElMessage 错误提示
   - 标准化错误响应对象格式，包含 code 和 message 属性

2. **src/utils/error-handler.ts**（新增）
   - 提供了 `handleApiError` 函数用于统一处理 API 错误
   - 提供了 `withErrorHandling` 工具函数，简化错误处理代码

3. **各个组件和服务**
   - 修改了错误处理逻辑，使用统一的错误处理工具

## 使用示例

### 基本错误处理（使用后端返回的错误信息）

```typescript
import { handleApiError } from '@/utils/error-handler'

try {
  await someApiCall()
  // 成功处理...
} catch (error) {
  handleApiError(error) // 直接使用后端返回的错误信息
}
```

### 使用自定义错误消息

```typescript
import { handleApiError } from '@/utils/error-handler'

try {
  await someApiCall()
  // 成功处理...
} catch (error) {
  handleApiError(error, '自定义错误消息') // 提供自定义错误消息
}
```

### 使用包装函数简化代码

```typescript
import { withErrorHandling } from '@/utils/error-handler'

// 使用后端返回的错误信息
await withErrorHandling(async () => {
  const result = await someApiCall()
  // 处理成功结果...
})

// 或者使用自定义错误消息
await withErrorHandling(async () => {
  const result = await someApiCall()
  // 处理成功结果...
}, '操作失败')
```

## 优势

1. **代码精简**：减少重复的错误处理代码
2. **统一体验**：用户只会看到一条错误消息
3. **可维护性**：集中管理错误处理逻辑，便于调整和修改
4. **可扩展性**：可以轻松添加新的错误处理策略，如日志记录、错误上报等
5. **错误信息准确**：优先使用后端返回的具体错误信息，提高用户体验

## 最佳实践

1. 始终使用统一的错误处理工具处理 API 错误
2. 避免在不同层级重复处理同一个错误
3. 默认使用后端返回的错误信息，只在必要时才使用自定义错误信息
4. 适当区分用户操作错误和系统错误，给予不同的提示 