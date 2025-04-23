<template>
  <div class="guide-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>攻略管理</span>
          <div class="header-operations">
            <el-input
              v-model="queryParams.keyword"
              placeholder="请输入攻略标题"
              clearable
              style="width: 250px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-select
              v-model="queryParams.category_id"
              placeholder="选择分类"
              clearable
              style="width: 180px"
              @change="handleSearch"
            >
              <el-option
                v-for="item in categoryOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
            
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="resetQuery">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
            <el-button type="success" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增攻略
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="guideList"
        border
        style="width: 100%"
      >
        <el-table-column label="封面" width="100" align="center">
          <template #default="{ row }">
            <el-image
              :src="formatImageUrl(row.cover_image)"
              style="width: 70px; height: 50px"
              fit="cover"
              :preview-src-list="[formatImageUrl(row.cover_image)]"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        
        <el-table-column label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category_name }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="数据统计" width="200" align="center">
          <template #default="{ row }">
            <div class="stats-info">
              <div>
                <el-icon><View /></el-icon>
                <span>{{ row.view_count }}</span>
              </div>
              <div>
                <el-icon><Star /></el-icon>
                <span>{{ row.like_count }}</span>
              </div>
              <div>
                <el-icon><Collection /></el-icon>
                <span>{{ row.collection_count }}</span>
              </div>
              <div>
                <el-icon><ChatDotRound /></el-icon>
                <span>{{ row.comment_count }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="属性" width="110" align="center">
          <template #default="{ row }">
            <div class="property-tags">
              <el-tag v-if="row.is_official" type="success" size="small">官方</el-tag>
              <el-tag v-if="row.is_hot" type="danger" size="small">热门</el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="170" />
        
        <el-table-column label="操作" fixed="right" width="160" align="center">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleView(row)">查看</el-button>
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.per_page"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 攻略详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="攻略详情"
      width="800px"
      top="50px"
    >
      <div class="guide-detail" v-if="currentGuide">
        <div class="detail-header">
          <h2>{{ currentGuide.title }}</h2>
          <div class="detail-meta">
            <el-tag size="small">{{ currentGuide.category_name }}</el-tag>
            <span>作者: {{ currentGuide.author || '未知' }}</span>
            <span>创建时间: {{ currentGuide.created_at }}</span>
          </div>
        </div>
        
        <div class="detail-cover">
          <el-image
            :src="formatImageUrl(currentGuide.cover_image)"
            fit="cover"
            style="width: 100%; max-height: 300px"
          />
        </div>
        
        <div class="detail-content">
          <div v-html="currentGuide.content"></div>
        </div>
        
        <div class="detail-footer">
          <div class="detail-stats">
            <div>
              <el-icon><View /></el-icon>
              <span>浏览: {{ currentGuide.view_count }}</span>
            </div>
            <div>
              <el-icon><Star /></el-icon>
              <span>点赞: {{ currentGuide.like_count }}</span>
            </div>
            <div>
              <el-icon><Collection /></el-icon>
              <span>收藏: {{ currentGuide.collection_count }}</span>
            </div>
            <div>
              <el-icon><ChatDotRound /></el-icon>
              <span>评论: {{ currentGuide.comment_count }}</span>
            </div>
          </div>
          
          <div class="detail-tags" v-if="currentGuide.tags && currentGuide.tags.length > 0">
            <span>标签:</span>
            <el-tag
              v-for="(tag, index) in currentGuide.tags"
              :key="index"
              type="info"
              size="small"
              style="margin-right: 5px"
            >
              {{ typeof tag === 'string' ? tag : tag.name }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- 攻略表单对话框 -->
    <el-dialog
      v-model="formVisible"
      :title="dialogType === 'add' ? '新增攻略' : '编辑攻略'"
      width="900px"
      top="30px"
      destroy-on-close
    >
      <el-form
        ref="guideFormRef"
        :model="guideForm"
        :rules="guideRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="guideForm.title" placeholder="请输入攻略标题" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="guideForm.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="item in categoryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="封面图" prop="cover_image">
          <el-upload
            class="cover-uploader"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleCoverSuccess"
            :before-upload="beforeCoverUpload"
          >
            <el-image
              v-if="guideForm.cover_image"
              :src="formatImageUrl(guideForm.cover_image)"
              class="cover-image"
            />
            <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="el-upload__tip">建议尺寸: 1200px * 675px, 支持 jpg/png 文件，不超过 5MB</div>
        </el-form-item>
        
        <el-form-item label="摘要" prop="summary">
          <el-input
            v-model="guideForm.summary"
            type="textarea"
            :rows="2"
            placeholder="请输入攻略摘要"
          />
        </el-form-item>
        
        <el-form-item label="内容" prop="content">
          <div style="width: 100%;">
            <VueMarkdownEditor
              v-model="guideForm.content"
              height="400px"
              placeholder="请输入攻略内容，支持Markdown格式"
              style="width: 100%"
            />
          </div>
          <div class="el-form-item__tip">支持Markdown格式，可以插入图片、链接等富文本内容</div>
        </el-form-item>
        
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="guideForm.tags"
            multiple
            allow-create
            filterable
            default-first-option
            placeholder="请输入标签，可自定义添加"
            style="width: 100%"
          >
            <el-option
              v-for="item in tagOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="作者" prop="author">
              <el-input v-model="guideForm.author" placeholder="请输入作者" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="浏览量" prop="view_count">
              <el-input-number v-model="guideForm.view_count" :min="0" :max="99999" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="点赞量" prop="like_count">
              <el-input-number v-model="guideForm.like_count" :min="0" :max="99999" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="guideForm.status">
            <el-radio :label="1">已发布</el-radio>
            <el-radio :label="0">草稿</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="formVisible = false">取消</el-button>
          <el-button type="primary" @click="submitGuideForm" :loading="formLoading">
            {{ dialogType === 'add' ? '发布' : '更新' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Refresh, Plus, View, Star, 
  Collection, ChatDotRound 
} from '@element-plus/icons-vue'
import { 
  getGuideList, getGuideDetail, createGuide, updateGuide, deleteGuide,
  getGuideCategoryList,
  type Guide, type GuideQuery, type GuideForm, type GuideCategory 
} from '@/api/guide'
import VueMarkdownEditor from '@kangc/v-md-editor'
import '@kangc/v-md-editor/lib/style/base-editor.css'
import vuepressTheme from '@kangc/v-md-editor/lib/theme/vuepress.js'
import '@kangc/v-md-editor/lib/theme/style/vuepress.css'

// 注册编辑器
VueMarkdownEditor.use(vuepressTheme)

// 状态变量
const loading = ref(false)
const guideList = ref<Guide[]>([])
const total = ref(0)
const categoryOptions = ref<GuideCategory[]>([])
const tagOptions = ref<string[]>([
  '美食', '文化', '自然', '历史', '购物', '交通', '住宿', '景点', '摄影'
])

// 查询参数
const queryParams = reactive<GuideQuery>({
  keyword: '',
  category_id: undefined,
  page: 1,
  per_page: 10
})

// 详情对话框
const detailVisible = ref(false)
const currentGuide = ref<Guide | null>(null)

// 表单对话框
const formVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formLoading = ref(false)
const guideFormRef = ref()
const guideForm = reactive<GuideForm>({
  title: '',
  content: '',
  cover_image: '',
  category_id: 0,
  tags: [],
  summary: '',
  author: '',
  view_count: 0,
  like_count: 0,
  status: 1
})

// 表单验证规则
const guideRules = {
  title: [
    { required: true, message: '请输入攻略标题', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  cover_image: [
    { required: true, message: '请上传封面图片', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入攻略内容', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 上传相关
const uploadUrl = '/api/upload'
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

// 获取攻略列表
const fetchGuideList = async () => {
  loading.value = true
  try {
    const res = await getGuideList(queryParams)
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      if (responseData.data && responseData.data.items) {
        guideList.value = responseData.data.items
        total.value = responseData.data.total || 0
      } else {
        guideList.value = []
        total.value = 0
      }
    } else {
      ElMessage.error(responseData.message || '获取攻略列表失败')
      guideList.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取攻略列表失败:', error)
    ElMessage.error('获取攻略列表失败')
    guideList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 获取分类列表
const fetchCategoryList = async () => {
  try {
    const res = await getGuideCategoryList()
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      categoryOptions.value = responseData.data || []
    } else {
      ElMessage.error(responseData.message || '获取分类列表失败')
    }
  } catch (error) {
    console.error('获取分类列表失败:', error)
    ElMessage.error('获取分类列表失败')
  }
}

// 查看攻略
const handleView = async (row: Guide) => {
  try {
    const res = await getGuideDetail(row.id)
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      currentGuide.value = responseData.data
      detailVisible.value = true
    } else {
      ElMessage.error(responseData.message || '获取攻略详情失败')
    }
  } catch (error) {
    console.error('获取攻略详情失败:', error)
    ElMessage.error('获取攻略详情失败')
  }
}

// 初始化表单
const initGuideForm = () => {
  guideForm.title = ''
  guideForm.content = ''
  guideForm.cover_image = ''
  guideForm.category_id = 0
  guideForm.tags = []
  guideForm.summary = ''
  guideForm.author = ''
  guideForm.view_count = 0
  guideForm.like_count = 0
  guideForm.status = 1
}

// 打开新增对话框
const handleAdd = () => {
  dialogType.value = 'add'
  initGuideForm()
  formVisible.value = true
}

// 打开编辑对话框
const handleEdit = async (row: Guide) => {
  try {
    const res = await getGuideDetail(row.id)
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      dialogType.value = 'edit'
      const guideData = responseData.data
      
      // 填充表单
      guideForm.title = guideData.title
      guideForm.content = guideData.content || ''
      guideForm.cover_image = guideData.cover_image
      guideForm.category_id = guideData.category_id
      guideForm.summary = guideData.summary || ''
      guideForm.author = guideData.author || ''
      guideForm.view_count = guideData.view_count || 0
      guideForm.like_count = guideData.like_count || 0
      guideForm.status = guideData.status
      
      // 处理标签
      if (guideData.tags) {
        if (Array.isArray(guideData.tags)) {
          guideForm.tags = guideData.tags.map((tag: string | {name: string}) => 
            typeof tag === 'string' ? tag : tag.name
          )
        }
      } else {
        guideForm.tags = []
      }
      
      currentGuide.value = guideData
      formVisible.value = true
    } else {
      ElMessage.error(responseData.message || '获取攻略详情失败')
    }
  } catch (error) {
    console.error('获取攻略详情失败:', error)
    ElMessage.error('获取攻略详情失败')
  }
}

// 删除攻略
const handleDelete = async (row: Guide) => {
  try {
    await ElMessageBox.confirm(`确认删除攻略 "${row.title}" 吗？此操作不可恢复！`, '警告', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger'
    })
    
    const res = await deleteGuide(row.id)
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      ElMessage.success(responseData.message || '删除成功')
      fetchGuideList()
    } else {
      ElMessage.error(responseData.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除攻略失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 提交攻略表单
const submitGuideForm = async () => {
  if (!guideFormRef.value) return
  
  try {
    await guideFormRef.value.validate()
    
    formLoading.value = true
    let res
    
    if (dialogType.value === 'add') {
      res = await createGuide(guideForm)
    } else {
      if (!currentGuide.value) return
      res = await updateGuide(currentGuide.value.id, guideForm)
    }
    
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      ElMessage.success(responseData.message || `${dialogType.value === 'add' ? '添加' : '更新'}成功`)
      formVisible.value = false
      fetchGuideList()
    } else {
      ElMessage.error(responseData.message || `${dialogType.value === 'add' ? '添加' : '更新'}失败`)
    }
  } catch (error) {
    console.error(`${dialogType.value === 'add' ? '添加' : '更新'}攻略失败:`, error)
    ElMessage.error(`${dialogType.value === 'add' ? '添加' : '更新'}失败`)
  } finally {
    formLoading.value = false
  }
}

// 封面上传成功处理
const handleCoverSuccess = (response: any) => {
  if (response.code === 0 || response.code === 200 || response.success) {
    guideForm.cover_image = response.data.url
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 封面上传前验证
const beforeCoverUpload = (file: File) => {
  const isImage = ['image/jpeg', 'image/png'].includes(file.type)
  const isLt5M = file.size / 1024 / 1024 < 5
  
  if (!isImage) {
    ElMessage.error('上传封面图片只能是 JPG 或 PNG 格式!')
  }
  
  if (!isLt5M) {
    ElMessage.error('上传封面图片大小不能超过 5MB!')
  }
  
  return isImage && isLt5M
}

// 处理搜索
const handleSearch = () => {
  queryParams.page = 1
  fetchGuideList()
}

// 重置搜索
const resetQuery = () => {
  queryParams.keyword = ''
  queryParams.category_id = undefined
  queryParams.page = 1
  fetchGuideList()
}

// 每页条数变化
const handleSizeChange = (val: number) => {
  queryParams.per_page = val
  fetchGuideList()
}

// 页码变化
const handleCurrentChange = (val: number) => {
  queryParams.page = val
  fetchGuideList()
}

// 格式化图片URL
const formatImageUrl = (url: string): string => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/static')) return `http://localhost:5000${url}`
  return `http://localhost:5000/static/images/${url.replace(/^\//, '')}`
}

// 获取状态类型
const getStatusType = (status: number): string => {
  switch (status) {
    case 0: return 'info'     // 草稿
    case 1: return 'success'  // 已发布
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: number): string => {
  switch (status) {
    case 0: return '草稿'
    case 1: return '已发布'
    default: return '未知'
  }
}

// 初始化
onMounted(() => {
  fetchGuideList()
  fetchCategoryList()
})
</script>

<style scoped>
.guide-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.header-operations {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 5px;
}

.stats-info {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.stats-info div {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
  font-size: 13px;
}

.property-tags {
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 详情样式 */
.guide-detail {
  padding: 20px 0;
}

.detail-header {
  margin-bottom: 20px;
}

.detail-header h2 {
  margin-top: 0;
  margin-bottom: 10px;
}

.detail-meta {
  display: flex;
  gap: 15px;
  color: #909399;
  font-size: 14px;
  align-items: center;
}

.detail-cover {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.detail-content {
  margin-bottom: 20px;
  line-height: 1.6;
}

/* 设置内容区域的图片样式 */
.detail-content :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 10px auto;
  border-radius: 4px;
}

.detail-content :deep(p) {
  margin: 1em 0;
}

.detail-footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.detail-stats {
  display: flex;
  gap: 20px;
}

.detail-stats div {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #606266;
}

.detail-tags {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 表单样式 */
.cover-uploader {
  display: flex;
  justify-content: center;
}

.cover-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.cover-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.cover-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 360px;
  height: 200px;
  text-align: center;
  line-height: 200px;
}

.cover-image {
  width: 360px;
  height: 200px;
  display: block;
  object-fit: cover;
}

.el-upload__tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.el-form-item__tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
</style> 