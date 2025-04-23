<template>
  <header class="header">
    <div class="container header-content">
      <div class="logo-container" @click="$router.push('/')">
        <svg class="logo" viewBox="0 0 500 500" width="40" height="40">
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#1abc9c;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#16a085;stop-opacity:1" />
            </linearGradient>
            <filter id="shadow">
              <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#1abc9c" flood-opacity="0.3"/>
            </filter>
          </defs>
          <!-- 飞机图标动画 -->
          <path class="plane" fill="url(#gradient)" filter="url(#shadow)" d="M482.207,187.088c0-1.862-0.822-3.612-2.231-4.785c-1.409-1.173-3.259-1.718-5.073-1.492L365.412,199.92
            l-96.859-132.837c-0.99-1.356-2.534-2.222-4.262-2.358c-1.728-0.136-3.422,0.454-4.629,1.619l-32.358,31.277l-32.358-31.277
            c-1.207-1.165-2.901-1.756-4.629-1.619c-1.728,0.136-3.271,1.002-4.262,2.358L89.197,199.92L-19.294,180.81
            c-1.813-0.227-3.663,0.319-5.073,1.492c-1.409,1.173-2.231,2.923-2.231,4.785v106.928c0,2.255,1.359,4.292,3.44,5.157
            l160.959,66.927c0.979,0.407,2.02,0.611,3.061,0.611c1.041,0,2.082-0.204,3.061-0.611l160.959-66.927
            c2.081-0.865,3.44-2.902,3.44-5.157V187.088z">
            <animateTransform
              attributeName="transform"
              type="translate"
              from="-500,0"
              to="500,0"
              dur="3s"
              repeatCount="indefinite"
            />
          </path>
        </svg>
        <h1 class="logo-text">Travel<span>Joy</span></h1>
      </div>
      
      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <el-menu mode="horizontal" :ellipsis="false" class="main-menu" router :default-active="activeMenu">
          <el-menu-item index="/home">
            <div class="menu-icon home-icon">
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path d="M3 13h1v7c0 1.103.897 2 2 2h12c1.103 0 2-.897 2-2v-7h1a1 1 0 0 0 .707-1.707l-9-9a.999.999 0 0 0-1.414 0l-9 9A1 1 0 0 0 3 13zm9-8.586 6 6V20H6v-9.586l6-6z"/>
                <path d="M12 18c3.703 0 4.901-3.539 4.95-3.689l-1.9-.621c-.008.023-.781 2.31-3.05 2.31-2.238 0-3.02-2.221-3.051-2.316l-1.899.627C7.099 14.461 8.297 18 12 18z"/>
              </svg>
            </div>
            首页
          </el-menu-item>
          <el-menu-item index="/attractions">
            <div class="menu-icon attraction-icon">
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path d="M12 2C7.589 2 4 5.589 4 9.995 3.971 16.44 11.696 21.784 12 22c0 0 8.029-5.56 8-12.005C20 5.589 16.411 2 12 2zm0 14c-3.309 0-6-2.691-6-6s2.691-6 6-6 6 2.691 6 6-2.691 6-6 6z"/>
                <path d="M11 11.586V6h2v5.586l2.707 2.707-1.414 1.414L12 13.414l-2.293 2.293-1.414-1.414z"/>
              </svg>
            </div>
            景区资讯
          </el-menu-item>
          <el-menu-item index="/travel-guides">
            <div class="menu-icon guide-icon">
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path d="M19 3H5c-1.103 0-2 .897-2 2v14c0 1.103.897 2 2 2h14c1.103 0 2-.897 2-2V5c0-1.103-.897-2-2-2zm0 16H5V5h14v14z"/>
                <path d="M7 7h10v2H7zm0 4h10v2H7zm0 4h7v2H7z"/>
                <circle cx="18" cy="18" r="2"/>
              </svg>
            </div>
            攻略
          </el-menu-item>
          <el-menu-item index="/notes">
            <div class="menu-icon note-icon">
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path d="M17.5 2h-12C4.12 2 3 3.12 3 4.5v15C3 20.88 4.12 22 5.5 22h12c1.38 0 2.5-1.12 2.5-2.5v-15C20 3.12 18.88 2 17.5 2z"/>
                <path d="M13 15H7v-2h6v2zm4-4H7V9h10v2zm0-4H7V5h10v2z" fill="#fff"/>
              </svg>
            </div>
            游记
          </el-menu-item>
        </el-menu>
      </nav>
      
      <!-- 用户操作区 -->
      <div class="user-actions">
        <template v-if="!isLoggedIn">
          <el-button type="primary" class="login-btn" @click="$router.push('/auth/login')">
            登录
          </el-button>
          <el-button class="register-btn" @click="$router.push('/auth/register')">
            注册
          </el-button>
        </template>
        <template v-else>
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar 
                :size="32" 
                :src="userInfo?.avatar || '/src/assets/images/default-avatar.svg'"
                @error="() => true"
              >
                <img src="/src/assets/images/default-avatar.svg" alt="默认头像" />
              </el-avatar>
              <span class="username">用户：{{ userInfo?.username || '未知' }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="my-guides">我的攻略</el-dropdown-item>
<!--                <el-dropdown-item command="orders">我的订单</el-dropdown-item>-->
                <el-dropdown-item command="collections">我的收藏</el-dropdown-item>
<!--                <el-dropdown-item command="settings">账号设置</el-dropdown-item>-->
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 用户登录状态
const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInfo = computed(() => userStore.userInfo)

// 处理用户菜单命令
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'my-guides':
      router.push('/user/guides')
      break
    case 'orders':
      router.push('/user/orders')
      break
    case 'collections':
      router.push('/user/collections')
      break
    case 'settings':
      router.push('/user/settings')
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('退出登录成功')
      router.push('/')
      break
  }
}

// 当前激活的菜单项
const activeMenu = computed(() => {
  const path = router.currentRoute.value.path
  if (path === '/') return '/home'
  return path
})

// 确保组件被正确导出
defineOptions({
  name: 'HeaderNav'
})
</script>

<style lang="scss" scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.98);
  }
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 70px;
    padding: 0 30px;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .logo-container {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    padding: 8px;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 2px;
      height: 0;
      background: linear-gradient(to bottom, transparent, #1abc9c, transparent);
      animation: scanVertical 2s ease-in-out infinite;
      box-shadow: 0 0 8px rgba(26, 188, 156, 0.3);
      border-radius: 2px;
    }
    
    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 0;
      height: 2px;
      background: linear-gradient(to right, transparent, #1abc9c, transparent);
      animation: scanHorizontal 2s ease-in-out infinite;
      box-shadow: 0 0 8px rgba(26, 188, 156, 0.3);
      border-radius: 2px;
    }
    
    &:hover {
      transform: translateX(5px);
      
      .logo {
        transform: rotate(15deg) scale(1.1);
        filter: drop-shadow(0 4px 12px rgba(26, 188, 156, 0.4));
      }
      
      .logo-text {
        transform: translateX(5px);
      }
    }
    
    .logo {
      width: 40px;
      height: 40px;
      transition: all 0.3s ease;
      position: relative;
      z-index: 1;
      
      .plane {
        filter: drop-shadow(0 2px 8px rgba(26, 188, 156, 0.3));
      }
    }
    
    .logo-text {
      font-size: 24px;
      font-weight: 800;
      background: linear-gradient(120deg, #1abc9c, #16a085);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: 0.5px;
      transition: all 0.3s ease;
      position: relative;
      z-index: 1;
      
      span {
        font-weight: 400;
        opacity: 0.9;
      }
    }
  }

  .nav-menu {
    flex: 1;
    display: flex;
    justify-content: center;
    
    :deep(.el-menu) {
      border: none;
      background: transparent;
      
      .el-menu-item {
        height: 70px;
        line-height: 70px;
        font-size: 16px;
        padding: 0 35px;
        color: #333;
        font-weight: 500;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        
        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(26, 188, 156, 0.05);
          transform: translateY(100%);
          transition: transform 0.3s ease;
          z-index: -1;
          border-radius: 8px;
        }
        
        &:hover {
          color: #1abc9c;
          transform: translateY(-2px);
          background: transparent;
          
          &::before {
            transform: translateY(0);
          }
          
          .menu-icon {
            transform: translateY(-2px) scale(1.2);
          }
        }
        
        &.is-active {
          color: #1abc9c;
          font-weight: 600;
          background: rgba(26, 188, 156, 0.08);
          border-radius: 8px;
          
          &::after {
            content: '';
            position: absolute;
            bottom: 12px;
            left: 50%;
            transform: translateX(-50%);
            width: 24px;
            height: 3px;
            border-radius: 3px;
            background: linear-gradient(90deg, #1abc9c, #16a085);
            transition: all 0.3s ease;
          }
          
          &:hover::after {
            width: 32px;
            box-shadow: 0 0 10px rgba(26, 188, 156, 0.3);
          }
          
          .menu-icon {
            transform: scale(1.2);
          }
        }
        
        .menu-icon {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          margin-right: 8px;
          border-radius: 8px;
          transition: all 0.3s ease;
          
          svg {
            width: 20px;
            height: 20px;
            fill: #666;
            transition: all 0.3s ease;
          }
          
          &.home-icon {
            background: rgba(26, 188, 156, 0.1);
            svg { fill: #1abc9c; }
          }
          
          &.attraction-icon {
            background: rgba(241, 196, 15, 0.1);
            svg { fill: #f1c40f; }
          }
          
          &.guide-icon {
            background: rgba(52, 152, 219, 0.1);
            svg { fill: #3498db; }
          }
          
          &.note-icon {
            background: rgba(155, 89, 182, 0.1);
            svg { fill: #9b59b6; }
          }
        }
      }
    }
  }
  
  .user-actions {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .login-btn {
      background: linear-gradient(135deg, #1abc9c, #16a085);
      border: none;
      padding: 10px 24px;
      font-size: 15px;
      border-radius: 25px;
      transition: all 0.3s;
      font-weight: 500;
      letter-spacing: 0.5px;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(26, 188, 156, 0.2);
      }
    }
    
    .register-btn {
      border: 2px solid #1abc9c;
      color: #1abc9c;
      padding: 9px 24px;
      font-size: 15px;
      border-radius: 25px;
      transition: all 0.3s;
      font-weight: 500;
      letter-spacing: 0.5px;
      background: transparent;
      
      &:hover {
        color: #fff;
        background: linear-gradient(135deg, #1abc9c, #16a085);
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(26, 188, 156, 0.2);
        border-color: transparent;
      }
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      padding: 6px 16px;
      border-radius: 25px;
      transition: all 0.3s ease;
      background: rgba(26, 188, 156, 0.1);
      
      &:hover {
        background: rgba(26, 188, 156, 0.15);
        transform: translateY(-2px);
        
        .el-avatar {
          transform: scale(1.05);
        }
      }
      
      .el-avatar {
        border: 2px solid #fff;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      
      .username {
        font-size: 15px;
        font-weight: 500;
        color: #1abc9c;
        min-width: 100px;
        display: inline-block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
  }
}

@keyframes scanVertical {
  0% {
    height: 0;
    top: 0;
    opacity: 0;
  }
  50% {
    height: 100%;
    top: 0;
    opacity: 1;
  }
  100% {
    height: 0;
    top: 100%;
    opacity: 0;
  }
}

@keyframes scanHorizontal {
  0% {
    width: 0;
    left: 0;
    opacity: 0;
  }
  50% {
    width: 100%;
    left: 0;
    opacity: 1;
  }
  100% {
    width: 0;
    left: 100%;
    opacity: 0;
  }
}

:deep(.el-dropdown-menu) {
  padding: 8px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  
  .el-dropdown-menu__item {
    padding: 10px 20px;
    font-size: 14px;
    border-radius: 8px;
    margin: 2px 0;
    
    &:hover {
      background: rgba(26, 188, 156, 0.1);
      color: #1abc9c;
    }
    
    &.is-disabled {
      opacity: 0.6;
    }
  }
}
</style> 