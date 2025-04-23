<template>
  <el-breadcrumb separator="/">
    <transition-group name="breadcrumb">
      <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
        <span 
          :class="{ 'no-redirect': item.redirect === 'noredirect' || index === breadcrumbs.length - 1 }"
          @click="handleLink(item)"
        >
          {{ item.meta?.title }}
        </span>
      </el-breadcrumb-item>
    </transition-group>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { RouteLocationMatched } from 'vue-router'

const route = useRoute()
const router = useRouter()

const breadcrumbs = ref<RouteLocationMatched[]>([])

const getBreadcrumb = () => {
  let matched = route.matched.filter(item => item.meta && item.meta.title)
  const first = matched[0]
  
  if (!isDashboard(first)) {
    matched = [{ path: '/dashboard', meta: { title: '首页' } } as RouteLocationMatched].concat(matched)
  }
  
  breadcrumbs.value = matched
}

const isDashboard = (route: RouteLocationMatched) => {
  const name = route?.name
  if (!name) {
    return false
  }
  return name.toString().trim().toLocaleLowerCase() === 'Dashboard'.toLocaleLowerCase()
}

const handleLink = (item: RouteLocationMatched) => {
  const { redirect, path } = item
  if (redirect) {
    router.push(redirect.toString())
    return
  }
  router.push(path)
}

watch(
  () => route.path,
  () => getBreadcrumb(),
  {
    immediate: true
  }
)
</script>

<style lang="scss" scoped>
.el-breadcrumb {
  display: inline-block;
  font-size: 14px;
  line-height: 50px;
  margin-left: 8px;
  
  :deep(.el-breadcrumb__inner) {
    color: #666;
    cursor: text;
    
    &.no-redirect {
      color: #97a8be;
      cursor: text;
    }
  }
  
  :deep(.el-breadcrumb__separator) {
    margin: 0 9px;
    font-weight: 400;
  }
}

.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all 0.5s;
}

.breadcrumb-enter-from,
.breadcrumb-leave-active {
  opacity: 0;
  transform: translateX(20px);
}

.breadcrumb-leave-active {
  position: absolute;
}
</style> 