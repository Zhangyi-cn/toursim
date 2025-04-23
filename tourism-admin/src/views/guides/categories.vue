<template>
  <div class="guide-categories">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>攻略分类管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加分类
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="categoryList"
        style="width: 100%"
        border
      >
        <el-table-column type="index" width="50" align="center" label="#" />
        
        <el-table-column prop="name" label="分类名称" width="180" />
        
        <el-table-column label="图标" width="100" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.icon"
              :src="formatIconUrl(row.icon)"
              style="width: 30px; height: 30px"
              fit="cover"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="170" />
        
        <el-table-column label="操作" fixed="right" width="150" align="center">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(row)">
                编辑
              </el-button>
              <el-button type="danger" link @click="handleDelete(row)">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加分类' : '编辑分类'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        
        <el-form-item label="图标" prop="icon">
          <el-upload
            class="avatar-uploader"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleIconSuccess"
            :before-upload="beforeIconUpload"
          >
            <img v-if="form.icon" :src="formatIconUrl(form.icon)" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="el-upload__tip">支持 jpg/png 文件，不超过 2MB</div>
        </el-form-item>
        
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="1" :max="999" />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getGuideCategoryList, 
  createGuideCategory, 
  updateGuideCategory, 
  deleteGuideCategory,
  type GuideCategory,
  type GuideCategoryForm
} from '@/api/guide'

// 状态
const loading = ref(false)
const categoryList = ref<GuideCategory[]>([])
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const submitLoading = ref(false)
const currentId = ref<number | null>(null)

// 表单
const formRef = ref()
const form = reactive<GuideCategoryForm>({
  name: '',
  icon: '',
  sort_order: 1,
  status: 1
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  sort_order: [
    { required: true, message: '请输入排序号', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 上传相关
const uploadUrl = 'http://localhost:5000/api/upload'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

// 获取分类列表
const fetchCategoryList = async () => {
  loading.value = true
  try {
    const res = await getGuideCategoryList()
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      categoryList.value = responseData.data || []
    } else {
      ElMessage.error(responseData.message || '获取分类列表失败')
    }
  } catch (error) {
    console.error('获取分类列表失败:', error)
    ElMessage.error('获取分类列表失败')
  } finally {
    loading.value = false
  }
}

// 初始化表单
const initForm = () => {
  form.name = ''
  form.icon = ''
  form.sort_order = 1
  form.status = 1
}

// 打开添加对话框
const handleAdd = () => {
  dialogType.value = 'add'
  initForm()
  dialogVisible.value = true
}

// 打开编辑对话框
const handleEdit = (row: GuideCategory) => {
  dialogType.value = 'edit'
  currentId.value = row.id
  
  // 填充表单
  form.name = row.name
  form.icon = row.icon
  form.sort_order = row.sort_order
  form.status = row.status
  
  dialogVisible.value = true
}

// 处理删除
const handleDelete = async (row: GuideCategory) => {
  try {
    await ElMessageBox.confirm(`确认删除 "${row.name}" 分类吗？此操作将无法恢复！`, '警告', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger'
    })
    
    const res = await deleteGuideCategory(row.id)
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      ElMessage.success(responseData.message || '删除成功')
      fetchCategoryList()
    } else {
      ElMessage.error(responseData.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除分类失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitLoading.value = true
    let res
    
    if (dialogType.value === 'add') {
      res = await createGuideCategory(form)
    } else {
      if (!currentId.value) return
      res = await updateGuideCategory(currentId.value, form)
    }
    
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      ElMessage.success(responseData.message || `${dialogType.value === 'add' ? '添加' : '更新'}成功`)
      dialogVisible.value = false
      fetchCategoryList()
    } else {
      ElMessage.error(responseData.message || `${dialogType.value === 'add' ? '添加' : '更新'}失败`)
    }
  } catch (error) {
    console.error(`${dialogType.value === 'add' ? '添加' : '更新'}分类失败:`, error)
    ElMessage.error(`${dialogType.value === 'add' ? '添加' : '更新'}失败`)
  } finally {
    submitLoading.value = false
  }
}

// 图标上传成功处理
const handleIconSuccess = (response: any) => {
  if (response.code === 0 || response.code === 200 || response.success) {
    form.icon = response.data.url
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 图标上传前验证
const beforeIconUpload = (file: File) => {
  const isImage = ['image/jpeg', 'image/png'].includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('上传头像图片只能是 JPG 或 PNG 格式!')
  }
  
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
  }
  
  return isImage && isLt2M
}

// 格式化图标URL
const formatIconUrl = (url: string): string => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/static')) return `http://localhost:5000${url}`
  return `http://localhost:5000/static/images/${url.replace(/^\//, '')}`
}

// 初始化
onMounted(() => {
  fetchCategoryList()
})
</script>

<style scoped>
.guide-categories {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-uploader {
  display: flex;
  justify-content: center;
}

.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
  line-height: 100px;
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
  object-fit: cover;
}

.el-upload__tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style> 