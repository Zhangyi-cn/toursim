<template>
  <div class="attractions">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>景点管理</span>
          <el-button type="primary" @click="handleAdd">新增景点</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="关键词">
            <el-input v-model="searchForm.keyword" placeholder="请输入景点名称" clearable />
          </el-form-item>
          <el-form-item label="分类">
            <el-select 
              v-model="searchForm.category_id" 
              placeholder="请选择分类" 
              clearable
              style="width: 200px"
            >
              <el-option
                v-for="item in categories"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 景点列表 -->
      <el-table
        v-loading="loading"
        :data="attractions"
        style="width: 100%"
        row-key="id"
        border
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="景点名称" />
        <el-table-column label="封面图片" width="120">
          <template #default="{ row }">
            <el-image
              style="width: 100px; height: 80px"
              :src="formatImageUrl(row.cover_image)"
              fit="cover"
              :preview-src-list="[formatImageUrl(row.cover_image)]"
            />
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="address" label="地址" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增景点' : '编辑景点'"
      width="800px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="景点名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入景点名称" />
        </el-form-item>
        <el-form-item label="所属分类" prop="category_id">
          <el-select 
            v-model="form.category_id" 
            placeholder="请选择分类"
            style="width: 100%"
          >
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="景点描述" prop="description">
          <v-md-editor
            v-model="form.description"
            height="300px"
            placeholder="请输入景点描述"
          />
        </el-form-item>
        <el-form-item label="封面图片" prop="cover_image">
          <el-upload
            class="avatar-uploader"
            action="/api/admin/attractions/upload/image"
            :show-file-list="false"
            :on-success="handleCoverImageSuccess"
            :before-upload="beforeImageUpload"
            :headers="{
              Authorization: `Bearer ${getToken()}`
            }"
          >
            <img 
              v-if="form.cover_image" 
              :src="formatImageUrl(form.cover_image)" 
              class="avatar" 
            />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="详细地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入详细地址" />
        </el-form-item>
        <el-form-item label="开放时间" prop="open_time">
          <el-input v-model="form.open_time" placeholder="请输入开放时间" />
        </el-form-item>
        <el-form-item label="门票信息" prop="ticket_info">
          <el-input
            v-model="form.ticket_info"
            type="textarea"
            :rows="2"
            placeholder="请输入门票信息"
          />
        </el-form-item>
        <el-form-item label="交通信息" prop="traffic_info">
          <el-input
            v-model="form.traffic_info"
            type="textarea"
            :rows="2"
            placeholder="请输入交通信息"
          />
        </el-form-item>
        <el-form-item label="游玩贴士" prop="tips">
          <el-input
            v-model="form.tips"
            type="textarea"
            :rows="2"
            placeholder="请输入游玩贴士"
          />
        </el-form-item>
        <el-form-item label="景点图片">
          <el-upload
            class="image-uploader"
            action="/api/admin/attractions/upload/image"
            :show-file-list="false"
            :on-success="handleImageSuccess"
            :before-upload="beforeImageUpload"
            :headers="{
              Authorization: `Bearer ${getToken()}`
            }"
          >
            <template v-if="form.images && form.images.length > 0">
              <div class="image-list">
                <div v-for="(image, index) in form.images" :key="index" class="image-item">
                  <el-image
                    :src="formatImageUrl(image.url)"
                    style="width: 100px; height: 100px; margin-right: 8px; margin-bottom: 8px"
                    fit="cover"
                  />
                  <div class="image-actions">
                    <el-button type="danger" link @click.stop="handleImageRemove(index)">删除</el-button>
                  </div>
                </div>
              </div>
            </template>
            <el-icon v-else class="image-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import VueMarkdownEditor from '@kangc/v-md-editor'
import '@kangc/v-md-editor/lib/style/base-editor.css'
import vuepressTheme from '@kangc/v-md-editor/lib/theme/vuepress.js'
import '@kangc/v-md-editor/lib/theme/style/vuepress.css'
import { getAttractionList, createAttraction, updateAttraction, deleteAttraction } from '@/api/attraction'
import { getCategoryList } from '@/api/category'
import type { Attraction, AttractionForm } from '@/api/attraction'
import type { Category } from '@/api/category'
import { getToken } from '@/utils/auth'
import { handleApiError, withErrorHandling } from '@/utils/error-handler'

const loading = ref(false)
const attractions = ref<Attraction[]>([])
const categories = ref<Category[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category_id: undefined as number | undefined
})

// 表单数据
const form = reactive<AttractionForm>({
  name: '',
  category_id: undefined as number | undefined,
  description: '',
  address: '',
  cover_image: '',
  images: []
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入景点名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择所属分类', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入景点描述', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入详细地址', trigger: 'blur' }
  ]
}

// 注册编辑器
VueMarkdownEditor.use(vuepressTheme)

// 获取分类列表
const getCategories = async () => {
  try {
    const response = await getCategoryList()
    console.log('分类API响应:', response)
    
    // 检查响应结构
    if (response.data && response.data.data) {
      categories.value = response.data.data
      console.log('分类数据:', categories.value)
    } else if (response.data) {
      // 兼容不同的返回格式
      const responseData = response.data as any
      categories.value = responseData || []
      console.log('分类数据(兼容方式):', categories.value)
    } else {
      categories.value = []
      console.error('分类API返回数据格式不正确:', response)
    }
  } catch (error) {
    console.error('获取分类数据出错:', error)
    handleApiError(error)
    categories.value = []
  }
}

// 获取景点列表
const getAttractions = async () => {
  loading.value = true
  try {
    const response = await getAttractionList({
      page: currentPage.value,
      per_page: pageSize.value,
      keyword: searchForm.keyword,
      category_id: searchForm.category_id
    })
    
    // 调试输出查看响应结构
    console.log('API响应:', response)
    
    // 正确访问数据
    if (response.data && response.data.data) {
      attractions.value = response.data.data.items || []
      total.value = response.data.data.pagination.total || 0
    } else if (response.data) {
      // 兼容不同的返回格式，手动类型转换
      const responseData = response.data as any
      attractions.value = responseData.items || []
      total.value = responseData.pagination?.total || 0
    } else {
      attractions.value = []
      total.value = 0
      console.error('API返回数据格式不正确:', response)
    }
  } catch (error) {
    console.error('获取景点列表出错:', error)
    handleApiError(error)
    attractions.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  getAttractions()
}

// 处理重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.category_id = undefined
  handleSearch()
}

// 处理分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  getAttractions()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getAttractions()
}

// 图片上传前验证
const beforeImageUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('上传图片只能是图片格式!')
  }
  if (!isLt2M) {
    ElMessage.error('上传图片大小不能超过 2MB!')
  }
  return isImage && isLt2M
}

// 图片URL处理函数
const formatImageUrl = (url: string): string => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/static')) return `http://localhost:5000${url}`
  return `http://localhost:5000/static/images/${url.replace(/^\//, '')}`
}

// 封面图片上传成功处理
const handleCoverImageSuccess = (response: any) => {
  form.cover_image = response.data.url
}

// 景点图片上传成功处理
const handleImageSuccess = (response: any) => {
  if (!form.images) {
    form.images = []
  }
  form.images.push({
    url: response.data.url,
    title: '',
    description: '',
    sort_order: form.images.length
  })
}

// 移除景点图片
const handleImageRemove = (index: number) => {
  if (form.images) {
    form.images.splice(index, 1)
  }
}

// 处理新增景点
const handleAdd = () => {
  dialogType.value = 'add'
  form.id = undefined
  form.name = ''
  form.category_id = undefined
  form.description = ''
  form.address = ''
  form.cover_image = ''
  form.images = []
  dialogVisible.value = true
}

// 处理编辑景点
const handleEdit = (row: Attraction) => {
  dialogType.value = 'edit'
  Object.assign(form, {
    ...row,
    images: row.attraction_images || []  // 使用attraction_images
  })
  dialogVisible.value = true
}

// 处理删除景点
const handleDelete = async (row: Attraction) => {
  try {
    await ElMessageBox.confirm('确认删除该景点吗？', '提示', {
      type: 'warning'
    })
    await deleteAttraction(row.id)
    ElMessage.success('删除成功')
    getAttractions()
  } catch (error) {
    if (error !== 'cancel') {
      handleApiError(error)
    }
  }
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (dialogType.value === 'add') {
          await createAttraction(form)
          ElMessage.success('新增成功')
        } else {
          await updateAttraction(form)
          ElMessage.success('编辑成功')
        }
        dialogVisible.value = false
        getAttractions()
      } catch (error) {
        handleApiError(error)
      }
    }
  })
}

// 初始化
onMounted(() => {
  getCategories()
  getAttractions()
})
</script>

<style scoped>
.attractions {
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

.avatar-uploader {
  display: flex;
  justify-content: center;
}

.avatar-uploader .avatar {
  width: 200px;
  height: 150px;
  display: block;
  object-fit: cover;
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

.avatar-uploader .avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 200px;
  height: 150px;
  text-align: center;
  line-height: 150px;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.image-item {
  position: relative;
  width: 200px;
  height: 150px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-actions {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-item:hover .image-actions {
  opacity: 1;
}

.image-uploader {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.image-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
  width: 200px;
  height: 150px;
}

.image-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.image-uploader .image-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 200px;
  height: 150px;
  text-align: center;
  line-height: 150px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 