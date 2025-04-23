<template>
  <div class="login-page">
    <!-- 背景动画 -->
    <div class="background">
      <div class="shape"></div>
      <div class="shape"></div>
    </div>

    <!-- 返回首页链接 -->
    <div class="home-link">
      <el-button link @click="goToHome">
        <el-icon><Back /></el-icon>
        返回首页
      </el-button>
    </div>

    <!-- Logo动画 -->
    <div class="logo-container">
      <svg class="logo" viewBox="0 0 500 500" width="100" height="100">
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#1abc9c;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#16a085;stop-opacity:1" />
          </linearGradient>
        </defs>
        <!-- 飞机图标动画 -->
        <path class="plane" fill="url(#gradient)" d="M482.207,187.088c0-1.862-0.822-3.612-2.231-4.785c-1.409-1.173-3.259-1.718-5.073-1.492L365.412,199.92
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

    <div class="main-content">
      <!-- 左侧介绍信息 -->
      <div class="intro-section">
        <h2 class="intro-title">探索世界的美好</h2>
        <div class="intro-features">
          <div class="feature-item">
            <el-icon class="feature-icon"><Location /></el-icon>
            <div class="feature-text">
              <h3>发现精彩目的地</h3>
              <p>探索世界各地的独特风景和文化</p>
            </div>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Share /></el-icon>
            <div class="feature-text">
              <h3>分享旅行故事</h3>
              <p>记录并分享您的精彩旅行时刻</p>
            </div>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Connection /></el-icon>
            <div class="feature-text">
              <h3>结识志同道合者</h3>
              <p>与其他旅行爱好者交流互动</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="form-container">
        <el-form
          ref="loginForm"
          :model="formData"
          :rules="rules"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <h2>欢迎回来</h2>
          <p class="subtitle">开启您的旅行之旅</p>

          <el-form-item prop="username">
            <el-input
              v-model="formData.username"
              placeholder="用户名"
            >
              <template #prefix>
                <div class="input-icon-container">
                  <el-icon><User /></el-icon>
                </div>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="formData.password"
              type="password"
              placeholder="密码"
              show-password
            >
              <template #prefix>
                <div class="input-icon-container">
                  <el-icon><Lock /></el-icon>
                </div>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="verifyCode" class="verify-code-item">
            <div class="verify-code-container">
              <el-input
                v-model="formData.verifyCode"
                placeholder="验证码"
                maxlength="4"
              >
                <template #prefix>
                  <div class="input-icon-container">
                    <el-icon><Key /></el-icon>
                  </div>
                </template>
              </el-input>
              <VerifyCode
                ref="verifyCodeRef"
                :width="120"
                :height="40"
                @update:code="(code: string) => verifyCode = code"
              />
            </div>
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-button link type="primary" @click="forgotPassword">忘记密码？</el-button>
          </div>

          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>

          <div class="register-link">
            还没有账号？
            <el-button link type="primary" @click="goToRegister">立即注册</el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Back, Location, Share, Connection, Key } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import VerifyCode from '@/components/VerifyCode.vue'

const router = useRouter()
const userStore = useUserStore()

const loginForm = ref(null)
const formData = reactive({
  username: '',
  password: '',
  verifyCode: ''
})

const verifyCodeRef = ref<InstanceType<typeof VerifyCode> | null>(null)
const verifyCode = ref('')

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  verifyCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { 
      validator: (rule: any, value: string, callback: Function) => {
        if (value.toLowerCase() !== verifyCode.value.toLowerCase()) {
          callback(new Error('验证码不正确'))
          // 验证码错误时刷新
          verifyCodeRef.value?.refresh()
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const loading = ref(false)
const rememberMe = ref(false)

// 处理登录
const handleLogin = async () => {
  if (!loginForm.value) return
  
  try {
    // 验证整个表单
    await loginForm.value.validate()
    loading.value = true
    
    const success = await userStore.login({
      username: formData.username,
      password: formData.password
    })

    if (success) {
      // 如果记住我，则保存登录状态
      if (rememberMe.value) {
        localStorage.setItem('rememberMe', 'true')
      }
      router.push('/')
    } else {
      // 登录失败时刷新验证码
      verifyCodeRef.value?.refresh()
    }
  } catch (error: any) {
    // 如果是表单验证错误（包括验证码错误）
    if (error.verifyCode) {
      return // 验证码错误的消息已经由表单验证显示
    }
    
    console.error('Login error:', error)
    // 登录失败时刷新验证码
    verifyCodeRef.value?.refresh()
  } finally {
    loading.value = false
  }
}

// 跳转到注册页
const goToRegister = () => {
  router.push('/auth/register')
}

// 跳转到首页
const goToHome = () => {
  router.push('/')
}

// 忘记密码
const forgotPassword = () => {
  router.push('/auth/forgot-password')
}
</script>

<style lang="scss" scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1abc9c 0%, #16a085 100%);
  position: relative;
  overflow: hidden;

  // 返回首页链接
  .home-link {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 10;

    .el-button {
      color: #ffffff !important;
      font-size: 16px;
      font-weight: 500;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
      
      .el-icon {
        margin-right: 4px;
        transition: transform 0.3s ease;
      }

      &:hover {
        color: #ffffff !important;
        opacity: 0.9;
        transform: translateX(-4px);
        
        .el-icon {
          transform: translateX(-2px);
        }
      }
    }
  }

  // 背景动画
  .background {
    position: absolute;
    width: 100%;
    height: 100%;
    z-index: 1;

    .shape {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(5px);
      animation: float 6s ease-in-out infinite;

      &:first-child {
        width: 600px;
        height: 600px;
        top: -300px;
        left: -200px;
        animation-delay: -3s;
      }

      &:last-child {
        width: 500px;
        height: 500px;
        bottom: -250px;
        right: -150px;
      }
    }
  }

  // Logo容器
  .logo-container {
    position: absolute;
    top: 40px;
    left: 80px;
    text-align: left;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 15px;

    .logo {
      transform: scale(0.8);
      transition: transform 0.3s ease;

      &:hover {
        transform: scale(0.9);
      }
    }

    .logo-text {
      margin: 0;
      font-size: 32px;
      color: #fff;
      font-weight: 700;
      letter-spacing: 1px;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;

      span {
        color: #ffd700;
        display: inline-block;
        transition: transform 0.3s ease;
      }

      &:hover {
        letter-spacing: 2px;
        
        span {
          transform: scale(1.1);
        }
      }
    }
  }

  // 主要内容区
  .main-content {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 60px;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }

  // 左侧介绍区域
  .intro-section {
    flex: 1;
    color: #fff;
    padding-right: 40px;

    .intro-title {
      font-size: 36px;
      font-weight: 700;
      margin-bottom: 40px;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      transform: translateY(0);
      transition: transform 0.3s ease;

      &:hover {
        transform: translateY(-5px);
      }
    }

    .intro-features {
      display: flex;
      flex-direction: column;
      gap: 30px;

      .feature-item {
        display: flex;
        align-items: flex-start;
        gap: 20px;
        padding: 20px;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
        cursor: pointer;

        &:hover {
          transform: translateX(10px);
          background: rgba(255, 255, 255, 0.1);

          .feature-icon {
            transform: scale(1.1) rotate(5deg);
            background: rgba(255, 255, 255, 0.2);
          }

          .feature-text {
            h3 {
              color: #ffd700;
            }

            p {
              opacity: 1;
            }
          }
        }

        .feature-icon {
          font-size: 32px;
          padding: 12px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          backdrop-filter: blur(5px);
          transition: all 0.3s ease;
        }

        .feature-text {
          h3 {
            font-size: 20px;
            margin: 0 0 8px;
            transition: color 0.3s ease;
          }

          p {
            font-size: 16px;
            margin: 0;
            opacity: 0.8;
            transition: opacity 0.3s ease;
          }
        }
      }
    }
  }

  // 表单容器
  .form-container {
    width: 420px;
    padding: 40px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    animation: slideUp 0.6s ease-out;
    position: relative;
    z-index: 10;

    h2 {
      margin: 0 0 10px;
      font-size: 28px;
      color: #333;
      text-align: center;
    }

    .subtitle {
      margin: 0 0 30px;
      font-size: 16px;
      color: #666;
      text-align: center;
    }

    .login-form {
      .el-form-item {
        margin-bottom: 25px;

        .el-input {
          --el-input-height: 45px;
          
          .el-input__wrapper {
            padding: 0 15px;
            border-radius: 25px;
            background: #ffffff;
            box-shadow: 0 0 0 1px #dcdfe6;
            transition: all 0.3s;

            &:hover {
              box-shadow: 0 0 0 1px var(--el-color-primary);
            }

            &:focus-within {
              box-shadow: 0 0 0 1px var(--el-color-primary);
            }
          }

          .input-icon-container {
            display: flex;
            align-items: center;
            padding: 0 5px;
            
            .el-icon {
              font-size: 18px;
              color: #909399;
            }
          }
        }
      }

      .form-options {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;

        .el-checkbox {
          .el-checkbox__label {
            color: #666;
          }
          
          .el-checkbox__input.is-checked {
            .el-checkbox__inner {
              background-color: #1abc9c;
              border-color: #1abc9c;
            }
            
            & + .el-checkbox__label {
              color: #1abc9c;
            }
          }
        }
      }

      .login-button {
        width: 100%;
        height: 45px;
        border-radius: 25px;
        font-size: 16px;
        font-weight: 600;
        background: linear-gradient(to right, #1abc9c, #16a085);
        border: none;
        transition: transform 0.3s, box-shadow 0.3s;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(26, 188, 156, 0.4);
        }

        &:active {
          transform: translateY(0);
          box-shadow: 0 2px 6px rgba(26, 188, 156, 0.4);
        }
      }

      .register-link {
        text-align: center;
        margin-top: 20px;
        font-size: 14px;
        color: #606266;
      }

      .verify-code-item {
        margin-bottom: 24px;
        
        .verify-code-container {
          display: flex;
          gap: 12px;
          align-items: center;

          .el-input {
            flex: 1;
            
            :deep(.el-input__wrapper) {
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
              
              &:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
              }
              
              &.is-focus {
                box-shadow: 0 0 0 1px #1abc9c;
              }
            }
          }
          
          .verify-code {
            transition: all 0.3s ease;
            
            &:hover {
              transform: scale(1.02);
            }
            
            &:active {
              transform: scale(0.98);
            }
          }
        }
      }
    }
  }

  :deep(.el-button--primary.is-link) {
    color: #1abc9c;
    
    &:hover {
      color: #16a085;
    }
  }
}

// 动画
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .login-page {
    .main-content {
      flex-direction: column;
      padding: 20px;
      margin-top: 100px;
      gap: 40px;
    }

    .logo-container {
      left: 50%;
      transform: translateX(-50%);
      text-align: center;
      flex-direction: column;
    }

    .intro-section {
      padding-right: 0;
      text-align: center;

      .intro-features {
        max-width: 600px;
        margin: 0 auto;

        .feature-item {
          justify-content: center;
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .login-page {
    padding: 20px;

    .form-container {
      width: 100%;
      padding: 30px 20px;
    }

    .logo-container {
      .logo {
        transform: scale(0.7);
        
        &:hover {
          transform: scale(0.8);
        }
      }

      .logo-text {
        font-size: 28px;
      }
    }

    .intro-section {
      .intro-title {
        font-size: 28px;
      }

      .intro-features {
        .feature-item {
          &:hover {
            transform: translateY(-5px);
          }
        }
      }
    }
  }
}
</style> 