<template>
  <div class="not-found">
    <div class="content">
      <h1>404</h1>
      <h2>页面不存在</h2>
      <p>抱歉，您访问的页面不存在或已被删除</p>
      <el-button type="primary" @click="router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped>
.not-found {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.content {
  text-align: center;
  padding: 2rem;
}

h1 {
  font-size: 6rem;
  color: #409eff;
  margin: 0;
  line-height: 1.2;
}

h2 {
  font-size: 2rem;
  color: #303133;
  margin: 1rem 0;
}

p {
  color: #606266;
  margin-bottom: 2rem;
}
</style> 