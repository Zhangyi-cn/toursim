<template>
  <div class="main-layout">
    <header-nav />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <keep-alive :include="keepAliveComponents">
            <component :is="Component" />
          </keep-alive>
        </transition>
      </router-view>
    </main>
    <app-footer />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import HeaderNav from './components/HeaderNav.vue'
import AppFooter from './components/AppFooter.vue'

const route = useRoute()

// 确定哪些组件需要被缓存
const keepAliveComponents = computed(() => {
  return ['Home', 'Attractions', 'Activities', 'Notes']
})
</script>

<style lang="scss" scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-top: 64px; // 为固定定位的头部留出空间
}
</style> 