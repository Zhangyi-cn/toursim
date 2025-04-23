<template>
  <div class="settings-page">
    <div class="page-container container">
      <el-card>
        <template #header>
          <div class="card-header">
            <h2>个人设置</h2>
          </div>
        </template>

        <el-tabs v-model="activeTab">
          <!-- 基本资料 -->
          <el-tab-pane label="基本资料" name="profile">
            <el-form
              ref="profileForm"
              :model="profileData"
              :rules="profileRules"
              label-width="100px"
              class="settings-form"
            >
              <el-form-item label="用户名">
                <el-input v-model="profileData.username" disabled></el-input>
              </el-form-item>

              <el-form-item label="昵称" prop="nickname">
                <el-input
                  v-model="profileData.nickname"
                  placeholder="请输入昵称"
                  maxlength="20"
                  show-word-limit
                ></el-input>
              </el-form-item>

              <el-form-item label="邮箱" prop="email">
                <el-input
                  v-model="profileData.email"
                  placeholder="请输入邮箱"
                  type="email"
                ></el-input>
              </el-form-item>

              <el-form-item label="手机号" prop="phone">
                <el-input
                  v-model="profileData.phone"
                  placeholder="请输入手机号"
                ></el-input>
              </el-form-item>

              <el-form-item label="个人简介" prop="bio">
                <el-input
                  v-model="profileData.bio"
                  type="textarea"
                  :rows="4"
                  placeholder="介绍一下自己吧"
                  maxlength="200"
                  show-word-limit
                ></el-input>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="handleUpdateProfile"
                  :loading="updateProfileLoading"
                >
                  保存修改
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 修改密码 -->
          <el-tab-pane label="修改密码" name="password">
            <el-form
              ref="passwordForm"
              :model="passwordData"
              :rules="passwordRules"
              label-width="100px"
              class="settings-form"
            >
              <el-form-item label="当前密码" prop="old_password">
                <el-input
                  v-model="passwordData.old_password"
                  type="password"
                  placeholder="请输入当前密码"
                  show-password
                ></el-input>
              </el-form-item>

              <el-form-item label="新密码" prop="new_password">
                <el-input
                  v-model="passwordData.new_password"
                  type="password"
                  placeholder="请输入新密码"
                  show-password
                ></el-input>
              </el-form-item>

              <el-form-item label="确认新密码" prop="confirm_password">
                <el-input
                  v-model="passwordData.confirm_password"
                  type="password"
                  placeholder="请再次输入新密码"
                  show-password
                ></el-input>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="handleChangePassword"
                  :loading="changePasswordLoading"
                >
                  修改密码
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 隐私设置 -->
          <el-tab-pane label="隐私设置" name="privacy">
            <el-form
              ref="privacyForm"
              :model="privacyData"
              label-width="200px"
              class="settings-form"
            >
              <el-form-item label="允许陌生人发送私信">
                <el-switch v-model="privacyData.allow_message" />
              </el-form-item>

              <el-form-item label="公开我的收藏">
                <el-switch v-model="privacyData.public_collections" />
              </el-form-item>

              <el-form-item label="公开我的关注列表">
                <el-switch v-model="privacyData.public_following" />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="handleUpdatePrivacy"
                  :loading="updatePrivacyLoading"
                >
                  保存设置
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getUserProfile, updateUserProfile, changePassword } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

// 当前激活的标签页
const activeTab = ref('profile')

// 表单ref
const profileForm = ref(null)
const passwordForm = ref(null)
const privacyForm = ref(null)

// 加载状态
const updateProfileLoading = ref(false)
const changePasswordLoading = ref(false)
const updatePrivacyLoading = ref(false)

// 表单数据
const profileData = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  bio: ''
})

const passwordData = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const privacyData = reactive({
  allow_message: true,
  public_collections: true,
  public_following: true
})

// 表单验证规则
const profileRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  bio: [
    { max: 200, message: '个人简介不能超过200个字符', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
    { min: 6, message: '密码不能少于6个字符', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码不能少于6个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordData.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载用户资料
const loadUserProfile = async () => {
  try {
    const res = await getUserProfile()
    const { username, nickname, email, phone, bio } = res.data
    Object.assign(profileData, { username, nickname, email, phone, bio })
  } catch (error) {
    console.error('获取用户资料失败:', error)
    ElMessage.error('获取用户资料失败')
  }
}

// 更新个人资料
const handleUpdateProfile = async () => {
  if (!profileForm.value) return
  
  try {
    await profileForm.value.validate()
    
    updateProfileLoading.value = true
    await updateUserProfile({
      nickname: profileData.nickname,
      email: profileData.email,
      phone: profileData.phone,
      bio: profileData.bio
    })
    
    // 更新store中的用户信息
    userStore.updateUserInfo({
      nickname: profileData.nickname,
      email: profileData.email,
      phone: profileData.phone,
      bio: profileData.bio
    })
    
    ElMessage.success('个人资料更新成功')
  } catch (error) {
    console.error('更新个人资料失败:', error)
    ElMessage.error(error.response?.data?.message || '更新个人资料失败')
  } finally {
    updateProfileLoading.value = false
  }
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordForm.value) return
  
  try {
    await passwordForm.value.validate()
    
    changePasswordLoading.value = true
    await changePassword({
      old_password: passwordData.old_password,
      new_password: passwordData.new_password
    })
    
    ElMessage.success('密码修改成功，请重新登录')
    // 清空表单
    passwordForm.value.resetFields()
    // 退出登录
    userStore.logout()
    // 跳转到登录页
    router.push('/auth/login')
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error(error.response?.data?.message || '修改密码失败')
  } finally {
    changePasswordLoading.value = false
  }
}

// 更新隐私设置
const handleUpdatePrivacy = async () => {
  try {
    updatePrivacyLoading.value = true
    // TODO: 实现隐私设置的保存
    ElMessage.success('隐私设置更新成功')
  } catch (error) {
    console.error('更新隐私设置失败:', error)
    ElMessage.error('更新隐私设置失败')
  } finally {
    updatePrivacyLoading.value = false
  }
}

// 页面加载时获取用户资料
onMounted(() => {
  loadUserProfile()
})
</script>

<style lang="scss" scoped>
.settings-page {
  padding: 20px 0;
  
  .card-header {
    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: bold;
    }
  }
  
  .settings-form {
    max-width: 600px;
    margin: 20px auto;
    
    .el-form-item:last-child {
      margin-bottom: 0;
    }
  }
}

@media (max-width: 768px) {
  .settings-page {
    .settings-form {
      max-width: 100%;
    }
  }
}
</style> 