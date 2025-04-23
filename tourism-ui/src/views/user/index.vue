<template>
  <div class="user-center-page">
    <div class="page-container container">
      <el-row :gutter="20">
        <!-- 左侧导航 -->
        <el-col :span="6">
          <el-card class="menu-card">
            <el-menu
              :default-active="activeMenu"
              class="user-menu"
              @select="handleMenuSelect"
            >
              <el-menu-item index="profile">
                <el-icon><User /></el-icon>
                <span>个人资料</span>
              </el-menu-item>
              <el-menu-item index="security">
                <el-icon><Lock /></el-icon>
                <span>账号安全</span>
              </el-menu-item>
              <el-menu-item index="notification">
                <el-icon><Bell /></el-icon>
                <span>消息通知</span>
              </el-menu-item>
            </el-menu>
          </el-card>
        </el-col>

        <!-- 右侧内容 -->
        <el-col :span="18">
          <el-card class="content-card">
            <!-- 个人资料 -->
            <div v-if="activeMenu === 'profile'" class="profile-section">
              <h2 class="section-title">个人资料</h2>
              <el-form
                ref="profileForm"
                :model="profileData"
                :rules="profileRules"
                label-width="100px"
              >
                <el-form-item label="个人头像">
                  <div class="avatar-upload">
                    <el-avatar 
                      :size="100" 
                      :src="profileData.avatar || '/default-avatar.png'" 
                      class="avatar-preview"
                    />
                    <div class="upload-trigger">
                      <el-upload
                        class="avatar-uploader"
                        :show-file-list="false"
                        :before-upload="beforeAvatarUpload"
                        :http-request="handleAvatarUpload"
                        accept="image/jpeg,image/png,image/gif"
                      >
                        <div class="upload-hover-area">
                          <el-button 
                            type="primary" 
                            :loading="uploadingAvatar"
                            size="small"
                            class="upload-button"
                          >
                            <el-icon><Upload /></el-icon>
                            <span>更换头像</span>
                          </el-button>
                        </div>
                        <template #tip>
                          <div class="el-upload__tip">
                            支持JPG、PNG、GIF格式，文件大小不超过2MB
                          </div>
                        </template>
                      </el-upload>
                    </div>
                  </div>
                </el-form-item>

                <el-form-item label="昵称" prop="nickname">
                  <el-input v-model="profileData.nickname" maxlength="20" show-word-limit />
                </el-form-item>

                <el-form-item label="个人简介" prop="bio">
                  <el-input
                    v-model="profileData.bio"
                    type="textarea"
                    maxlength="200"
                    show-word-limit
                    :rows="4"
                  />
                </el-form-item>

                <el-form-item label="电子邮箱" prop="email">
                  <el-input v-model="profileData.email" disabled>
                    <template #append>
                      <el-button @click="handleVerifyEmail">验证邮箱</el-button>
                    </template>
                  </el-input>
                </el-form-item>

                <el-form-item label="手机号码" prop="phone">
                  <el-input v-model="profileData.phone" />
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" @click="handleUpdateProfile" :loading="updating">
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 账号安全 -->
            <div v-if="activeMenu === 'security'" class="security-section">
              <h2 class="section-title">账号安全</h2>
              <el-form
                ref="passwordForm"
                :model="passwordData"
                :rules="passwordRules"
                label-width="100px"
              >
                <el-form-item label="当前密码" prop="oldPassword">
                  <el-input
                    v-model="passwordData.oldPassword"
                    type="password"
                    show-password
                  />
                </el-form-item>

                <el-form-item label="新密码" prop="newPassword">
                  <el-input
                    v-model="passwordData.newPassword"
                    type="password"
                    show-password
                  />
                </el-form-item>

                <el-form-item label="确认新密码" prop="confirmPassword">
                  <el-input
                    v-model="passwordData.confirmPassword"
                    type="password"
                    show-password
                  />
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">
                    修改密码
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 消息通知 -->
            <div v-if="activeMenu === 'notification'" class="notification-section">
              <h2 class="section-title">消息通知</h2>
              <el-form label-width="120px">
                <el-form-item label="系统通知">
                  <el-switch v-model="notificationSettings.system" />
                </el-form-item>
                <el-form-item label="评论通知">
                  <el-switch v-model="notificationSettings.comment" />
                </el-form-item>
                <el-form-item label="点赞通知">
                  <el-switch v-model="notificationSettings.like" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSaveNotificationSettings">
                    保存设置
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock, Bell, Upload } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import {
  getCurrentUser,
  updateProfile,
  changePassword,
  uploadAvatar,
  verifyEmail,
  sendVerificationCode
} from '@/api/user'

// 静态资源基础URL - 修正为正确的环境变量名
const staticBaseUrl = import.meta.env.VITE_STATIC_ASSETS_URL_AVATARS || ''

const userStore = useUserStore()

// 菜单激活状态
const activeMenu = ref('profile')

// 个人资料表单数据
const profileData = reactive({
  avatar: userStore.userInfo?.avatar || '',
  nickname: userStore.userInfo?.nickname || '',
  bio: userStore.userInfo?.bio || '',
  email: userStore.userInfo?.email || '',
  phone: userStore.userInfo?.phone || ''
})

// 个人资料验证规则
const profileRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  bio: [
    { max: 200, message: '不能超过 200 个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 密码表单数据
const passwordData = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码验证规则
const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordData.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 通知设置
const notificationSettings = reactive({
  system: true,
  comment: true,
  like: true
})

// 加载状态
const updating = ref(false)
const changingPassword = ref(false)
const uploadingAvatar = ref(false)

// 表单引用
const profileForm = ref(null)
const passwordForm = ref(null)

// 处理头像URL，确保路径正确
const getFullAvatarUrl = (avatarPath) => {
  if (!avatarPath) return '';
  if (avatarPath.startsWith('http')) return avatarPath;
  
  // 确保有路径分隔符
  const baseUrl = staticBaseUrl.endsWith('/') ? staticBaseUrl : `${staticBaseUrl}/`;
  return `${baseUrl}${avatarPath}`;
}

// 在组件挂载后初始化数据
onMounted(() => {
  // 加载用户信息
  loadUserProfile()
})

// 加载用户个人资料
const loadUserProfile = async () => {
  try {
    const res = await getCurrentUser()
    if (res && res.data) {
      // 为头像添加静态资源基础URL前缀
      const avatar = res.data.avatar ? getFullAvatarUrl(res.data.avatar) : profileData.avatar

      // 更新表单数据
      Object.assign(profileData, {
        avatar,
        nickname: res.data.nickname || profileData.nickname,
        bio: res.data.bio || profileData.bio,
        email: res.data.email || profileData.email,
        phone: res.data.phone || profileData.phone
      })
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 处理菜单选择
const handleMenuSelect = (index) => {
  activeMenu.value = index
}

// 头像上传前的验证
const beforeAvatarUpload = (file) => {
  // 检查文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  const isAllowedType = allowedTypes.includes(file.type)
  
  // 检查文件大小，限制为2MB
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isAllowedType) {
    ElMessage.error('只能上传JPG、PNG、GIF格式的图片！')
    return false
  }
  
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB！')
    return false
  }
  
  // 创建本地预览（可选）
  /*
  if (window.FileReader) {
    const reader = new FileReader()
    reader.onload = (e) => {
      profileData.avatar = e.target.result
    }
    reader.readAsDataURL(file)
  }
  */
  
  return true
}

// 处理头像上传
const handleAvatarUpload = async ({ file }) => {
  uploadingAvatar.value = true
  try {
    const res = await uploadAvatar(file)
    console.log('上传头像响应(成功):', res)
    
    // 直接处理成功情况
    const avatarUrl = res?.data?.avatar
    if (avatarUrl) {
      // 添加静态资源基础URL前缀
      const fullAvatarUrl = getFullAvatarUrl(avatarUrl)
      profileData.avatar = fullAvatarUrl
      // 更新用户仓库的头像
      if (userStore.updateUserInfo) {
        userStore.updateUserInfo({ avatar: fullAvatarUrl })
      } else {
        console.warn('userStore.updateUserInfo 方法不存在')
      }
      ElMessage.success(res.message || '头像上传成功')
    } else {
      ElMessage.error('上传失败：未获取到头像地址')
    }
  } catch (error) {
    console.error('上传头像失败(异常):', error)
    
    // 检查是否为成功响应但被拦截器视为错误
    if (error && typeof error === 'object') {
      let avatarUrl = null
      let successMessage = null
      
      // 检查各种可能的错误响应结构
      if (error.data && error.data.avatar) {
        avatarUrl = error.data.avatar
        successMessage = error.message
      } else if (error.data && error.data.data && error.data.data.avatar) {
        avatarUrl = error.data.data.avatar
        successMessage = error.data.message
      } else if (error.avatar) {
        avatarUrl = error.avatar
        successMessage = error.message
      }
      
      // 如果找到了头像URL，则更新
      if (avatarUrl) {
        console.log('从错误对象中提取的头像URL:', avatarUrl)
        // 添加静态资源基础URL前缀
        const fullAvatarUrl = getFullAvatarUrl(avatarUrl)
        profileData.avatar = fullAvatarUrl
        
        // 使用可选链和条件检查，确保方法存在
        if (userStore.updateUserInfo) {
          userStore.updateUserInfo({ avatar: fullAvatarUrl })
        } else {
          console.warn('userStore.updateUserInfo 方法不存在')
        }
        
        ElMessage.success(successMessage || '头像上传成功')
        return
      }
    }
    
    ElMessage.error('上传头像失败，请稍后重试：' + (error.message || '未知错误'))
  } finally {
    uploadingAvatar.value = false
  }
}

// 处理个人资料更新
const handleUpdateProfile = async () => {
  if (!profileForm.value) return
  
  await profileForm.value.validate(async (valid, fields) => {
    if (!valid) {
      console.error('表单验证失败:', fields)
      return
    }
    
    updating.value = true
    try {
      const res = await updateProfile({
        nickname: profileData.nickname,
        bio: profileData.bio,
        phone: profileData.phone,
        email: profileData.email
      })
      
      // 更新用户信息并提示成功
      const userData = {
        nickname: profileData.nickname,
        bio: profileData.bio,
        phone: profileData.phone,
        email: profileData.email
      }
      
      // 安全地更新用户仓库
      if (userStore.updateUserInfo) {
        userStore.updateUserInfo(userData)
      } else {
        console.warn('userStore.updateUserInfo 方法不存在')
      }
      
      ElMessage.success('个人资料更新成功')
    } catch (error) {
      console.error('更新个人资料失败:', error)
      // 检查错误对象是否包含成功信息
      if (error && error.code === 200) {
        const userData = {
          nickname: profileData.nickname,
          bio: profileData.bio,
          phone: profileData.phone,
          email: profileData.email
        }
        
        // 安全地更新用户仓库
        if (userStore.updateUserInfo) {
          userStore.updateUserInfo(userData)
        } else {
          console.warn('userStore.updateUserInfo 方法不存在')
        }
        
        ElMessage.success(error.message || '个人资料更新成功')
        return
      }
      ElMessage.error(error.message || '更新个人资料失败')
    } finally {
      updating.value = false
    }
  })
}

// 处理修改密码
const handleChangePassword = async () => {
  if (!passwordForm.value) return
  
  await passwordForm.value.validate(async (valid, fields) => {
    if (!valid) {
      console.error('表单验证失败:', fields)
      return
    }
    
    changingPassword.value = true
    try {
      await changePassword({
        old_password: passwordData.oldPassword,
        new_password: passwordData.newPassword
      })
      
      // 清空表单并提示成功
      ElMessage.success('密码修改成功')
      passwordData.oldPassword = ''
      passwordData.newPassword = ''
      passwordData.confirmPassword = ''
    } catch (error) {
      console.error('修改密码失败:', error)
      // 检查错误对象是否包含成功信息
      if (error && error.code === 200) {
        ElMessage.success(error.message || '密码修改成功')
        passwordData.oldPassword = ''
        passwordData.newPassword = ''
        passwordData.confirmPassword = ''
        return
      }
      ElMessage.error(error.message || '密码修改失败')
    } finally {
      changingPassword.value = false
    }
  })
}

// 处理邮箱验证
const handleVerifyEmail = async () => {
  if (!profileData.email) {
    ElMessage.warning('请先设置邮箱地址')
    return
  }
  
  try {
    // 发送验证码到邮箱
    await sendVerificationCode(profileData.email)
    ElMessage.success('验证邮件已发送，请查收')
  } catch (error) {
    console.error('发送验证邮件失败:', error)
    // 检查错误对象是否包含成功信息
    if (error && error.code === 200) {
      ElMessage.success(error.message || '验证邮件已发送，请查收')
      return
    }
    ElMessage.error(error.message || '发送验证邮件失败')
  }
}

// 保存通知设置
const handleSaveNotificationSettings = () => {
  ElMessage.success('通知设置保存成功')
}
</script>

<style lang="scss" scoped>
@use "@/styles/variables" as *;
@use "@/styles/mixins" as *;

.user-center-page {
  padding: $spacing-lg 0;

  .menu-card {
    .user-menu {
      border-right: none;
    }
  }

  .content-card {
    .section-title {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: $spacing-lg;
      padding-bottom: $spacing-sm;
      border-bottom: 1px solid $border-color;
    }

    .avatar-upload {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 10px;
    }

    .avatar-preview {
      border: 2px solid #eee;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      position: relative;
      overflow: hidden;
    }

    .upload-trigger {
      position: relative;
    }

    .upload-hover-area {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    .upload-button {
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .el-upload__tip {
      font-size: 12px;
      color: #909399;
      margin-top: 5px;
    }
  }
}

@include mobile {
  .user-center-page {
    .el-row {
      margin: 0 !important;
    }

    .el-col {
      padding: 0 !important;
    }

    .menu-card {
      margin-bottom: $spacing-md;
    }
  }
}
</style> 