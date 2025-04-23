<template>
  <div class="notes">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>游记管理</span>
          <div class="header-operations">
            <el-input
              v-model="searchForm.keyword"
              placeholder="请输入标题/作者"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-select v-model="searchForm.status" placeholder="状态" clearable @change="handleSearch">
              <el-option label="已发布" :value="1" />
              <el-option label="草稿" :value="0" />
              <el-option label="已下架" :value="2" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="notes" v-loading="loading" border stripe>
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column label="封面" width="100">
          <template #default="{ row }">
            <el-image
              v-if="row.cover_image"
              :src="formatImageUrl(row.cover_image)"
              style="width: 80px; height: 60px"
              fit="cover"
              :preview-src-list="[formatImageUrl(row.cover_image)]"
            />
            <span v-else>无封面</span>
          </template>
        </el-table-column>
        <el-table-column label="作者" width="120">
          <template #default="{ row }">
            <div class="user-info" v-if="row.user">
              <el-avatar :size="30" :src="row.user.avatar">
                {{ row.user.nickname?.substring(0, 1) || row.user.username.substring(0, 1) }}
              </el-avatar>
              <span>{{ row.user.nickname || row.user.username }}</span>
            </div>
            <span v-else>未知用户</span>
          </template>
        </el-table-column>
        <el-table-column label="位置" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.location || '无位置信息' }}
          </template>
        </el-table-column>
        <el-table-column label="数据统计" width="200">
          <template #default="{ row }">
            <div class="stats">
              <el-tooltip content="浏览量">
                <span><el-icon><View /></el-icon> {{ row.views }}</span>
              </el-tooltip>
              <el-tooltip content="点赞数">
                <span><el-icon><Star /></el-icon> {{ row.likes }}</span>
              </el-tooltip>
              <el-tooltip content="收藏数">
                <span><el-icon><Collection /></el-icon> {{ row.collections }}</span>
              </el-tooltip>
              <el-tooltip content="评论数">
                <span><el-icon><ChatDotRound /></el-icon> {{ row.comments }}</span>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleView(row)">查看</el-button>
              <el-button type="success" link @click="handleSetStatus(row, 1)" v-if="row.status !== 1">发布</el-button>
              <el-button type="warning" link @click="handleSetStatus(row, 2)" v-if="row.status !== 2">下架</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </el-button-group>
            <el-button-group style="margin-top: 5px">
              <el-button 
                :type="row.featured ? 'info' : 'default'" 
                link 
                @click="handleFeature(row)"
              >
                {{ row.featured ? '取消精选' : '设为精选' }}
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 查看游记对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="游记详情"
      width="800px"
    >
      <div class="note-detail" v-if="currentNote">
        <div class="note-header">
          <h2>{{ currentNote.title }}</h2>
          <el-tag :type="getStatusType(currentNote.status)">{{ currentNote.status_text }}</el-tag>
        </div>
        
        <div class="note-meta">
          <div v-if="currentNote.user" class="author">
            <el-avatar :size="40" :src="currentNote.user.avatar">
              {{ currentNote.user.nickname?.substring(0, 1) || currentNote.user.username.substring(0, 1) }}
            </el-avatar>
            <span>{{ currentNote.user.nickname || currentNote.user.username }}</span>
          </div>
          <div class="meta-info">
            <span v-if="currentNote.location"><el-icon><Location /></el-icon> {{ currentNote.location }}</span>
            <span><el-icon><Calendar /></el-icon> {{ currentNote.created_at }}</span>
          </div>
        </div>
        
        <div class="cover" v-if="currentNote.cover_image">
          <img :src="formatImageUrl(currentNote.cover_image)" alt="封面图">
        </div>
        
        <div class="description" v-if="currentNote.description">
          <p>{{ currentNote.description }}</p>
        </div>
        
        <div class="content" v-if="currentNote.content" v-html="currentNote.content"></div>
        
        <div class="tags" v-if="currentNote.tags && currentNote.tags.length > 0">
          <span>标签：</span>
          <el-tag 
            v-for="tag in currentNote.tags" 
            :key="tag.id" 
            class="tag"
            size="small"
          >
            {{ tag.name }}
          </el-tag>
        </div>
        
        <div class="images" v-if="currentNote.images && currentNote.images.length > 0">
          <h3>游记图片</h3>
          <el-row :gutter="10">
            <el-col :span="8" v-for="image in currentNote.images" :key="image.id">
              <el-card class="image-card">
                <img :src="formatImageUrl(image.url)" :alt="image.title || '游记图片'" class="note-image">
                <div class="image-title" v-if="image.title">{{ image.title }}</div>
                <div class="image-description" v-if="image.description">{{ image.description }}</div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div class="stats-detail">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <el-icon><View /></el-icon>
                <span>浏览量：{{ currentNote.views }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <el-icon><Star /></el-icon>
                <span>点赞数：{{ currentNote.likes }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <el-icon><Collection /></el-icon>
                <span>收藏数：{{ currentNote.collections }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <el-icon><ChatDotRound /></el-icon>
                <span>评论数：{{ currentNote.comments }}</span>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, View, Star, Collection, ChatDotRound, 
  Calendar, Location 
} from '@element-plus/icons-vue'
import { 
  getNoteList, getNoteDetail, deleteNote, updateNoteStatus,
  featureNote, unfeatureNote,
  type Note, type NoteQuery 
} from '@/api/note'

const loading = ref(false)
const notes = ref<Note[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const currentNote = ref<Note | null>(null)

const searchForm = reactive<NoteQuery>({
  keyword: '',
  status: undefined,
  page: 1,
  per_page: 10
})

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
    case 0: return 'info'    // 草稿
    case 1: return 'success' // 已发布
    case 2: return 'warning' // 已下架
    default: return 'info'
  }
}

// 获取游记列表
const getNotes = async () => {
  loading.value = true
  try {
    const response = await getNoteList({
      ...searchForm,
      page: currentPage.value,
      per_page: pageSize.value
    })
    
    console.log('游记列表响应:', response)
    
    // 检查返回的数据结构并处理
    const responseData = response as any
    
    if (responseData) {
      // 检查是否存在分页属性
      if ('has_next' in responseData || 'total_pages' in responseData) {
        // 直接是分页数据
        notes.value = responseData.items || []
        total.value = responseData.total || 0
      } else if (responseData.data) {
        // API返回了嵌套的数据结构
        notes.value = responseData.data.items || []
        total.value = responseData.data.total || 0
      } else {
        // 兜底处理
        notes.value = []
        total.value = 0
        ElMessage.warning('返回数据格式异常')
      }
    } else {
      ElMessage.error('获取游记列表失败')
      notes.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取游记列表失败:', error)
    ElMessage.error('获取游记列表失败')
    notes.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 查看游记详情
const handleView = async (row: Note) => {
  try {
    const response = await getNoteDetail(row.id)
    
    // 从响应中提取游记详情数据
    const responseData = response as any
    
    if (responseData?.data) {
      currentNote.value = responseData.data
      dialogVisible.value = true
    } else {
      ElMessage.error('获取游记详情失败')
    }
  } catch (error) {
    console.error('获取游记详情失败:', error)
    ElMessage.error('获取游记详情失败')
  }
}

// 修改游记状态
const handleSetStatus = async (row: Note, status: number) => {
  try {
    const statusText = status === 1 ? '发布' : status === 2 ? '下架' : '修改状态'
    
    await ElMessageBox.confirm(`确认要${statusText}该游记吗？`, '提示', {
      type: 'warning'
    })
    
    const response = await updateNoteStatus(row.id, status)
    
    // 从响应中提取结果数据
    const responseData = response as any
    
    if (responseData?.success || responseData?.code === 200 || responseData?.code === 0) {
      ElMessage.success(responseData.message || `${statusText}成功`)
      getNotes()
    } else {
      ElMessage.error(responseData?.message || `${statusText}失败`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('修改游记状态失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 设置/取消精选
const handleFeature = async (row: Note) => {
  try {
    const action = row.featured ? '取消精选' : '设为精选'
    
    await ElMessageBox.confirm(`确认要${action}该游记吗？`, '提示', {
      type: 'warning'
    })
    
    const response = row.featured
      ? await unfeatureNote(row.id)
      : await featureNote(row.id)
    
    // 从响应中提取结果数据
    const responseData = response as any
    
    if (responseData?.success || responseData?.code === 200 || responseData?.code === 0) {
      ElMessage.success(responseData.message || `${action}成功`)
      getNotes()
    } else {
      ElMessage.error(responseData?.message || `${action}失败`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('设置/取消精选失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 处理删除
const handleDelete = async (row: Note) => {
  try {
    await ElMessageBox.confirm('确认删除该游记吗？此操作不可恢复！', '警告', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger'
    })
    
    const response = await deleteNote(row.id)
    
    // 从响应中提取结果数据
    const responseData = response as any
    
    if (responseData?.success || responseData?.code === 200 || responseData?.code === 0) {
      ElMessage.success(responseData.message || '删除成功')
      getNotes()
    } else {
      ElMessage.error(responseData?.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除游记失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  getNotes()
}

// 处理每页数量变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  getNotes()
}

// 处理页码变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getNotes()
}

// 初始化
onMounted(() => {
  getNotes()
})
</script>

<style scoped>
.notes {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-operations {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stats {
  display: flex;
  gap: 10px;
}

.note-detail {
  padding: 20px;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.meta-info {
  display: flex;
  gap: 15px;
}

.cover {
  margin-bottom: 20px;
}

.cover img {
  max-width: 100%;
  border-radius: 8px;
}

.description {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.content {
  line-height: 1.6;
  margin-bottom: 20px;
}

.content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 10px 0;
}

.content :deep(p) {
  margin-bottom: 15px;
}

.tags {
  margin-bottom: 20px;
}

.tag {
  margin-right: 5px;
}

.images {
  margin-bottom: 20px;
}

.image-card {
  margin-bottom: 15px;
}

.note-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}

.image-title {
  font-weight: bold;
  margin-top: 8px;
}

.image-description {
  color: #666;
  font-size: 0.9em;
  margin-top: 5px;
}

.stats-detail {
  margin-top: 30px;
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style> 