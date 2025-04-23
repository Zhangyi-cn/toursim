<template>
  <div class="app-wrapper">
    <!-- 侧边栏 -->
    <div class="sidebar-container" :class="{ 'is-collapse': isCollapse }">
      <div class="logo-container">
        <img src="@/assets/logo.svg" alt="Logo" class="logo">
        <h1 class="title" v-show="!isCollapse">旅游管理系统</h1>
      </div>
      
      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :unique-opened="true"
          :collapse-transition="false"
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <!-- <el-menu-item index="/dashboard" @click="handleMenuClick('/dashboard')">
            <el-icon><Odometer /></el-icon>
            <template #title>仪表盘</template>
          </el-menu-item> -->
          
          <el-sub-menu index="1">
            <template #title>
              <el-icon><Location /></el-icon>
              <span>景点管理</span>
            </template>
            <el-menu-item index="/attractions/list" @click="handleMenuClick('/attractions/list')">景点列表</el-menu-item>
            <el-menu-item index="/attractions/categories" @click="handleMenuClick('/attractions/categories')">分类管理</el-menu-item>
          </el-sub-menu>
          
          <!-- <el-sub-menu index="2">
            <template #title>
              <el-icon><Ticket /></el-icon>
              <span>门票管理</span>
            </template>
            <el-menu-item index="/tickets" @click="handleMenuClick('/tickets')">门票列表</el-menu-item>
            <el-menu-item index="/orders" @click="handleMenuClick('/orders')">订单管理</el-menu-item>
          </el-sub-menu> -->
          
          <el-sub-menu index="3">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>内容管理</span>
            </template>
            <el-menu-item index="/content/notes" @click="handleMenuClick('/content/notes')">游记管理</el-menu-item>
            <el-menu-item index="/content/comments" @click="handleMenuClick('/content/comments')">评论管理</el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/users" @click="handleMenuClick('/users')">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          
          <el-menu-item index="/content/banners" @click="handleMenuClick('/content/banners')">
            <el-icon><Picture /></el-icon>
            <template #title>轮播图管理</template>
          </el-menu-item>
          
          <el-sub-menu index="4">
            <template #title>
              <el-icon><Notebook /></el-icon>
              <span>攻略管理</span>
            </template>
            <el-menu-item index="/guides/list" @click="handleMenuClick('/guides/list')">攻略列表</el-menu-item>
            <el-menu-item index="/guides/categories" @click="handleMenuClick('/guides/categories')">分类管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>
    </div>
    
    <!-- 主容器 -->
    <div class="main-container">
      <!-- 头部 -->
      <div class="navbar">
        <div class="left">
          <el-icon class="fold-btn" @click="toggleSidebar">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
          <breadcrumb />
        </div>
        
        <div class="right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="avatar-container">
              <el-avatar :size="32" :src="userInfo.avatar || defaultAvatar" />
              <span class="name">{{ userInfo.nickname || userInfo.username }}</span>
              <el-icon><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 主要内容区 -->
      <div class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import {
  Odometer,
  Location,
  Ticket,
  Document,
  User,
  Picture,
  CaretBottom,
  Expand,
  Fold,
  Notebook
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import Breadcrumb from './components/Breadcrumb.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapse = ref(false)
const defaultAvatar = new URL('@/assets/default-avatar.png', import.meta.url).href

const userInfo = computed(() => userStore.getUserInfo)
const activeMenu = computed(() => route.path)

// 切换侧边栏
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 处理菜单点击
const handleMenuClick = (path: string) => {
  router.push(path)
}

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'password':
      router.push('/password')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await userStore.logout()
      } catch (error) {
        // 用户取消操作
      }
      break
  }
}
</script>

<style lang="scss" scoped>
.app-wrapper {
  display: flex;
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
  
  .sidebar-container {
    width: 210px;
    height: 100%;
    background: #304156;
    transition: width 0.3s;
    overflow: hidden;
    
    &.is-collapse {
      width: 64px;
    }
    
    .logo-container {
      height: 50px;
      padding: 10px;
      display: flex;
      align-items: center;
      background: #2b2f3a;
      
      .logo {
        width: 32px;
        height: 32px;
      }
      
      .title {
        margin-left: 12px;
        color: #fff;
        font-size: 16px;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
      }
    }
    
    .sidebar-menu {
      border: none;
      
      :deep(.el-menu-item), :deep(.el-sub-menu__title) {
        height: 50px;
        line-height: 50px;
      }
      
      :deep(.el-menu-item.is-active) {
        background-color: #263445;
      }
    }
  }
  
  .main-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-width: 0; /* 防止flex子项溢出 */
    width: 100%;  
    
    .navbar {
      height: 50px;
      padding: 0 15px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #fff;
      box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
      
      .left {
        display: flex;
        align-items: center;
        
        .fold-btn {
          padding: 0 15px;
          font-size: 20px;
          cursor: pointer;
          transition: background 0.3s;
          
          &:hover {
            background: rgba(0, 0, 0, 0.025);
          }
        }
      }
      
      .right {
        .avatar-container {
          display: flex;
          align-items: center;
          padding: 0 8px;
          height: 50px;
          cursor: pointer;
          
          .name {
            margin: 0 8px;
            font-size: 14px;
          }
        }
      }
    }
    
    .app-main {
      flex: 1;
      padding: 15px;
      overflow-y: auto;
      background: #f0f2f5;
    }
  }
}

// 路由过渡动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 