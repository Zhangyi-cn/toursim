<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'

const userStore = useUserStore()
const themeStore = useThemeStore()

onMounted(async () => {
  // 如果有token，获取用户信息
  if (userStore.token) {
    await userStore.getUserInfo()
  }
  themeStore.initTheme()
})
</script>

<template>
  <router-view />
</template>

<style>
/* 全局样式将由styles/index.scss提供 */
</style>
