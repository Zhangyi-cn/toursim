<template>
  <div class="users-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="left">
        <el-button type="primary" @click="handleAddUser">添加用户</el-button>
        <el-button @click="exportUserData">导出数据</el-button>
      </div>
      <div class="right">
        <el-input
          v-model="queryParams.keyword"
          placeholder="用户名/昵称/邮箱"
          class="search-input"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="queryParams">
          <el-form-item label="关键词">
            <el-input
              v-model="queryParams.keyword"
              placeholder="用户名/昵称/邮箱/手机"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="queryParams.status" placeholder="全部状态" clearable>
              <el-option label="正常" :value="1" />
              <el-option label="禁用" :value="0" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>
          </div>

      <!-- 用户列表 -->
      <el-table
        v-loading="loading"
        :data="userList"
        border
        style="width: 100%"
        row-key="id"
        stripe
        highlight-current-row
      >
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :size="40" :src="row.avatar">
              {{ row.nickname ? row.nickname.substring(0, 1) : row.username.substring(0, 1) }}
            </el-avatar>
      </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" show-overflow-tooltip />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="created_at" label="注册时间" width="160" />
        <el-table-column prop="last_login" label="最后登录" width="160" />
        <el-table-column label="兴趣标签" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag
              v-for="tag in row.interest_tags"
              :key="tag"
              size="small"
              style="margin-right: 5px; margin-bottom: 5px"
            >
              {{ tag }}
            </el-tag>
            <span v-if="!row.interest_tags || row.interest_tags.length === 0">暂无</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="() => handleStatusChange(row)"
              active-text="正常"
              inactive-text="禁用"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="handleViewUser(row)">查看</el-button>
              <el-button type="primary" size="small" @click="handleEditUser(row)">编辑</el-button>
              <el-dropdown @command="(command) => handleMoreOperations(command, row)">
                <el-button size="small">
                  更多<el-icon><ArrowDown /></el-icon>
              </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="reset">重置密码</el-dropdown-item>
                    <el-dropdown-item 
                      :disabled="row.status === 0" 
                      command="disable"
                    >禁用账户</el-dropdown-item>
                    <el-dropdown-item 
                      :disabled="row.status === 1" 
                      command="enable"
                    >启用账户</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.per_page"
          :page-sizes="[10, 20, 50, 100]"
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 用户表单对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      :title="dialogType === 'add' ? '创建用户' : dialogType === 'edit' ? '编辑用户' : '用户详情'"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="80px"
        :disabled="dialogType === 'view'"
      >
        <el-form-item label="用户名" prop="username" v-if="dialogType === 'add'">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogType === 'add'">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="userForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="头像" prop="avatar">
          <div class="avatar-uploader-container">
            <div class="avatar-preview">
              <el-avatar v-if="userForm.avatar" :src="userForm.avatar" :size="80"></el-avatar>
              <div v-else class="avatar-placeholder">
                <el-icon><User /></el-icon>
              </div>
            </div>
            <el-input v-model="userForm.avatar" placeholder="请输入头像URL">
              <template #append>
                <el-button @click="previewAvatar">预览</el-button>
              </template>
            </el-input>
          </div>
        </el-form-item>
        <el-form-item label="个人简介" prop="bio">
          <el-input
            v-model="userForm.bio"
            type="textarea"
            :rows="3"
            placeholder="请输入个人简介"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="userForm.status">
            <el-radio :label="1">正常</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUserForm" v-if="dialogType !== 'view'">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetPasswordVisible"
      title="重置密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <div v-if="resetPasswordLoading" class="reset-password-loading">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>正在重置密码，请稍候...</p>
      </div>
      <div v-else-if="newPassword" class="reset-password-result">
        <p>密码重置成功！请妥善保存新密码：</p>
        <el-alert
          type="success"
          :closable="false"
          show-icon
        >
          <strong>{{ newPassword }}</strong>
        </el-alert>
        <p class="password-tip">提示：请将此密码安全地传达给用户</p>
      </div>
      <div v-else>
        <p>您确定要重置用户 <strong>{{ currentUser?.nickname || currentUser?.username }}</strong> 的密码吗？</p>
        <p class="warning-text">此操作将生成一个新的随机密码，原密码将立即失效。</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resetPasswordVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmResetPassword" 
            :disabled="resetPasswordLoading || newPassword"
          >
            {{ newPassword ? '关闭' : '确认重置' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, User, Loading } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import {
  getUserList,
  getUserDetail,
  createUser,
  updateUser,
  updateUserStatus,
  resetUserPassword,
  type User as UserType,
  type UserQueryParams,
  type UserCreateForm,
  type UserUpdateForm
} from '@/api/user'
import { handleApiError } from '@/utils/error-handler'

// 自定义类型
type DialogType = 'add' | 'edit' | 'view'
type OperationCommand = 'reset' | 'disable' | 'enable'

// 数据定义
const loading = ref(false)
const userList = ref<UserType[]>([])
const total = ref(0)
const queryParams = reactive<UserQueryParams>({
  page: 1,
  per_page: 10,
  keyword: '',
  status: undefined
})

// 对话框控制
const userDialogVisible = ref(false)
const resetPasswordVisible = ref(false)
const resetPasswordLoading = ref(false)
const dialogType = ref<DialogType>('add')
const userFormRef = ref<FormInstance>()
const newPassword = ref('')
const currentUser = ref<UserType | null>(null)

// 用户表单
const userForm = reactive<UserCreateForm & UserUpdateForm & { id?: number }>({
  id: undefined,
  username: '',
  password: '',
  nickname: '',
  email: '',
  phone: '',
  avatar: '',
  bio: '',
  status: 1
})

// 表单验证规则
const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
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
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

// 获取用户列表
const fetchUserList = async () => {
  loading.value = true
  try {
    const response = await getUserList(queryParams)
    userList.value = response.data.items
    total.value = response.data.pagination.total
  } catch (error) {
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

// 搜索用户
const handleSearch = () => {
  queryParams.page = 1
  fetchUserList()
}

// 重置搜索条件
const resetQuery = () => {
  queryParams.keyword = ''
  queryParams.status = undefined
  handleSearch()
}

// 处理分页变化
const handleSizeChange = (val: number) => {
  queryParams.per_page = val
  fetchUserList()
}

const handleCurrentChange = (val: number) => {
  queryParams.page = val
  fetchUserList()
}

// 处理创建用户
const handleAddUser = () => {
  dialogType.value = 'add'
  userForm.username = ''
  userForm.password = ''
  userForm.nickname = ''
  userForm.email = ''
  userForm.phone = ''
  userForm.avatar = ''
  userForm.bio = ''
  userForm.status = 1
  userDialogVisible.value = true
}

// 处理查看用户
const handleViewUser = async (row: UserType) => {
  dialogType.value = 'view'
  try {
    const response = await getUserDetail(row.id)
    // 将用户信息填充到表单，包括ID
    userForm.id = row.id
    Object.assign(userForm, response.data)
    userDialogVisible.value = true
  } catch (error) {
    handleApiError(error)
  }
}

// 处理编辑用户
const handleEditUser = async (row: UserType) => {
  dialogType.value = 'edit'
  try {
    const response = await getUserDetail(row.id)
    // 将用户信息填充到表单，包括ID
    userForm.id = row.id
    Object.assign(userForm, response.data)
    userDialogVisible.value = true
  } catch (error) {
    handleApiError(error)
  }
}

// 提交用户表单
const submitUserForm = async () => {
  if (!userFormRef.value) return

  await userFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (dialogType.value === 'add') {
          // 创建用户
          await createUser(userForm as UserCreateForm)
          ElMessage.success('创建用户成功')
        } else {
          // 确保用户ID存在
          if (!userForm.id) {
            ElMessage.error('用户ID不存在')
            return
          }

          // 编辑用户，移除不需要的字段
          const updateData: UserUpdateForm = {
            nickname: userForm.nickname,
            email: userForm.email,
            phone: userForm.phone,
            avatar: userForm.avatar,
            bio: userForm.bio,
            status: userForm.status
          }
          
          await updateUser(userForm.id, updateData)
          ElMessage.success('更新用户成功')
        }
        
        userDialogVisible.value = false
        fetchUserList()
      } catch (error) {
        handleApiError(error)
      }
    }
  })
}

// 预览头像
const previewAvatar = () => {
  if (!userForm.avatar) {
    ElMessage.warning('请先输入头像URL')
    return
  }
  
  // 检查URL是否有效
  const img = new Image()
  img.onload = () => {
    ElMessage.success('头像URL有效')
  }
  img.onerror = () => {
    ElMessage.error('头像URL无效，无法加载图片')
  }
  img.src = userForm.avatar
}

// 修改状态变更处理函数
const handleStatusChange = async (row: UserType) => {
  const statusText = row.status === 1 ? '启用' : '禁用'
  const originalStatus = row.status === 1 ? 0 : 1
  
  try {
    // 先弹出确认对话框
    await ElMessageBox.confirm(
      `确定要${statusText}用户 "${row.nickname || row.username}" 吗？`, 
      '确认操作', 
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: row.status === 1 ? 'success' : 'warning'
      }
    )
    
    // 用户确认后，发送请求
    await updateUserStatus(row.id, row.status)
    ElMessage.success(`${statusText}用户成功`)
  } catch (error: any) {
    // 如果是用户取消，恢复状态但不显示错误
    if (error === 'cancel') {
      row.status = originalStatus
      return
    }
    
    // 其他错误，恢复状态并显示错误
    row.status = originalStatus
    handleApiError(error)
  }
}

// 处理更多操作
const handleMoreOperations = (command: OperationCommand, row: UserType) => {
  switch (command) {
    case 'reset':
      handleResetPassword(row)
      break
    case 'disable':
      row.status = 0
      handleStatusChange(row)
      break
    case 'enable':
      row.status = 1
      handleStatusChange(row)
      break
  }
}

// 处理密码重置
const handleResetPassword = (row: UserType) => {
  resetPasswordVisible.value = true
  resetPasswordLoading.value = false
  newPassword.value = ''
  currentUser.value = row
}

// 确认重置密码
const confirmResetPassword = async () => {
  if (!currentUser.value) return
  
  try {
    resetPasswordLoading.value = true
    const response = await resetUserPassword(currentUser.value.id)
    newPassword.value = response.data.new_password
    resetPasswordLoading.value = false
  } catch (error) {
    resetPasswordLoading.value = false
    handleApiError(error)
  }
}

// 导出用户数据
const exportUserData = () => {
  if (!userList.value.length) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  // 准备CSV数据
  const headers = ['ID', '用户名', '昵称', '邮箱', '电话', '角色', '状态', '创建时间', '最后登录']
  const data = userList.value.map(user => [
    user.id,
    user.username,
    user.nickname || '',
    user.email || '',
    user.phone || '',
    user.role === 1 ? '管理员' : '普通用户',
    user.status === 1 ? '正常' : '禁用',
    user.created_at || '',
    user.last_login || ''
  ])
  
  // 合并数据
  const csvContent = [
    headers.join(','),
    ...data.map(row => row.join(','))
  ].join('\n')
  
  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `用户数据_${new Date().toISOString().substring(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('用户数据已导出')
}

// 页面初始化
onMounted(() => {
  fetchUserList()
})
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.reset-password-loading {
  text-align: center;
  padding: 20px 0;
}

.loading-icon {
  font-size: 24px;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.reset-password-result {
  text-align: center;
}

.password-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
}

.warning-text {
  color: #e6a23c;
  font-size: 14px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.search-input {
  width: 300px;
}

.avatar-uploader-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.avatar-preview {
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 40px;
  background-color: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 30px;
  color: #909399;
}
</style> 