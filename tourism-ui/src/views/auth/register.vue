<template>
  <div class="register-page">
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
        <h2 class="intro-title">加入我们的旅行社区</h2>
        <div class="intro-features">
          <div class="feature-item">
            <el-icon class="feature-icon"><PictureFilled /></el-icon>
            <div class="feature-text">
              <h3>记录精彩瞬间</h3>
              <p>创建个性化的旅行日记和照片集</p>
            </div>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><StarFilled /></el-icon>
            <div class="feature-text">
              <h3>获取专属推荐</h3>
              <p>基于兴趣为您推荐最佳旅行目的地</p>
            </div>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><UserFilled /></el-icon>
            <div class="feature-text">
              <h3>建立旅行圈子</h3>
              <p>找到志同道合的旅行伙伴</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧注册表单 -->
      <div class="form-container">
        <el-form
          ref="registerForm"
          :model="formData"
          :rules="rules"
          class="register-form"
          @keyup.enter="handleRegister"
        >
          <h2>创建账号</h2>
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

          <el-form-item prop="email">
            <el-input
              v-model="formData.email"
              placeholder="电子邮箱"
            >
              <template #prefix>
                <div class="input-icon-container">
                  <el-icon><Message /></el-icon>
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

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="formData.confirmPassword"
              type="password"
              placeholder="确认密码"
              show-password
              @keyup.enter="handleRegister"
            >
              <template #prefix>
                <div class="input-icon-container">
                  <el-icon><Key /></el-icon>
                </div>
              </template>
            </el-input>
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="agreeTerms">
              我已阅读并同意
              <el-button link type="primary" @click="showTerms">服务条款</el-button>
            </el-checkbox>
          </div>

          <el-button
            type="primary"
            class="register-button"
            :loading="loading"
            :disabled="!agreeTerms"
            @click="handleRegister"
          >
            立即注册
          </el-button>

          <div class="login-link">
            已有账号？
            <el-button link type="primary" @click="goToLogin">立即登录</el-button>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 服务条款对话框 -->
    <el-dialog
      v-model="termsVisible"
      title="服务条款"
      width="50%"
      class="terms-dialog"
    >
      <div class="terms-content">
        <h3>欢迎使用 TravelJoy</h3>
        <p>请仔细阅读以下条款，这些条款将影响您的权利和义务。</p>
        <!-- 这里添加具体的服务条款内容 -->
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="termsVisible = false">关闭</el-button>
          <el-button type="primary" @click="acceptTerms">
            同意并继续
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, 
  Lock, 
  Back, 
  Message, 
  Key,
  PictureFilled,
  StarFilled,
  UserFilled
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { register } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const registerForm = ref(null)
const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const validatePass = (rule: any, value: string, callback: Function) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    if (formData.confirmPassword !== '') {
      if (formData.password !== formData.confirmPassword) {
        callback(new Error('两次输入密码不一致'))
      }
    }
    callback()
  }
}

const validatePass2 = (rule: any, value: string, callback: Function) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== formData.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePass, trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validatePass2, trigger: 'blur' }
  ]
}

const loading = ref(false)
const agreeTerms = ref(false)
const termsVisible = ref(false)

// 处理注册
const handleRegister = async () => {
  if (!registerForm.value) return
  
  if (!agreeTerms.value) {
    ElMessage.warning('请先同意服务条款')
    return
  }

  try {
    await registerForm.value.validate()
    loading.value = true
    
    const res = await register({
      username: formData.username,
      email: formData.email,
      password: formData.password,
      confirmPassword: formData.confirmPassword
    })
    
    ElMessage.success('注册成功，请登录')
    router.push('/auth/login')
  } catch (error: any) {
    // 只记录错误，不再显示消息（已经在请求拦截器中显示过了）
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}

// 显示服务条款
const showTerms = () => {
  termsVisible.value = true
}

// 同意服务条款
const acceptTerms = () => {
  agreeTerms.value = true
  termsVisible.value = false
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/auth/login')
}

// 跳转到首页
const goToHome = () => {
  router.push('/')
}
</script>

<style lang="scss" scoped>
.register-page {
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

    .register-form {
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
        margin-bottom: 25px;
        
        .el-checkbox {
          display: flex;
          align-items: center;
          
          .el-checkbox__input {
            .el-checkbox__inner {
              width: 18px;
              height: 18px;
              border: 2px solid #dcdfe6;
              transition: all 0.3s;
              
              &:hover {
                border-color: #1abc9c;
              }
            }
            
            &.is-checked {
              .el-checkbox__inner {
                background-color: #1abc9c;
                border-color: #1abc9c;
              }
            }
          }
          
          .el-checkbox__label {
            color: #666;
            font-size: 14px;
            padding-left: 8px;
            
            .el-button--primary.is-link {
              font-weight: 600;
              text-decoration: none;
              padding: 0 4px;
              
              &:hover {
                text-decoration: underline;
              }
            }
          }
        }
      }

      .register-button {
        width: 100%;
        height: 45px;
        border-radius: 25px;
        font-size: 16px;
        font-weight: 600;
        background: linear-gradient(to right, #1abc9c, #16a085);
        border: none;
        transition: transform 0.3s, box-shadow 0.3s, opacity 0.3s;

        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          background: linear-gradient(to right, #a8a8a8, #888888);
          
          &:hover {
            transform: none;
            box-shadow: none;
          }
        }

        &:not(:disabled) {
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(26, 188, 156, 0.4);
          }

          &:active {
            transform: translateY(0);
            box-shadow: 0 2px 6px rgba(26, 188, 156, 0.4);
          }
        }
      }

      .login-link {
        text-align: center;
        margin-top: 20px;
        font-size: 14px;
        color: #606266;
      }
    }
  }

  :deep(.el-button--primary.is-link) {
    color: #1abc9c;
    
    &:hover {
      color: #16a085;
    }
  }

  .form-container {
    .register-form {
      .form-options {
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
    }
  }
}

// 服务条款对话框
.terms-dialog {
  .terms-content {
    max-height: 400px;
    overflow-y: auto;
    padding: 20px;

    h3 {
      margin-top: 0;
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
  .register-page {
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
  .register-page {
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

  .terms-dialog {
    width: 90% !important;
  }
}
</style> 