<template>
  <div class="comments-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>评论管理</span>
          <div class="filter-container">
            <el-input
              v-model="queryParams.keyword"
              placeholder="评论内容关键词"
              clearable
              style="width: 200px"
              @keyup.enter="handleQuery"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-select v-model="queryParams.target_type" placeholder="内容类型" clearable style="width: 120px">
              <el-option label="景点" value="attraction" />
              <el-option label="游记" value="note" />
              <el-option label="攻略" value="guide" />
            </el-select>
            
            <el-select v-model="queryParams.status" placeholder="状态" clearable style="width: 120px">
              <el-option label="待审核" :value="0" />
              <el-option label="已发布" :value="1" />
              <el-option label="已拒绝" :value="2" />
            </el-select>
            
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
            
            <el-button type="primary" @click="handleQuery">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="resetQuery">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="commentList"
        style="width: 100%"
        border
      >
        <el-table-column label="用户信息" width="150" align="center">
          <template #default="scope">
            <div class="user-info" v-if="scope.row.user">
              <el-avatar :size="30" :src="formatAvatar(scope.row.user.avatar)">
                {{ formatInitials(scope.row.user) }}
              </el-avatar>
              <div class="user-name">{{ scope.row.user.nickname || scope.row.user.username }}</div>
            </div>
            <span v-else>未知用户</span>
          </template>
        </el-table-column>
        
        <el-table-column label="评论内容" min-width="300">
          <template #default="scope">
            <div class="comment-content">{{ scope.row.content }}</div>
            <div class="image-list" v-if="scope.row.images && scope.row.images.length > 0">
              <el-image 
                v-for="(img, index) in scope.row.images" 
                :key="index"
                :src="formatImageUrl(img)"
                fit="cover"
                :preview-src-list="scope.row.images.map(formatImageUrl)"
                preview-teleported
                class="comment-image"
              />
            </div>
            <div class="target-info">
              <el-tag size="small">{{ getContentTypeText(scope.row.content_type) }}</el-tag>
              <span class="target-name">{{ scope.row.target_name || '未知内容' }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="发布时间" width="170" align="center" />
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="互动数据" width="100" align="center">
          <template #default="scope">
            <div class="interaction-data">
              <div>
                <el-icon><Star /></el-icon>
                <span>{{ scope.row.like_count || 0 }}</span>
              </div>
              <div v-if="scope.row.replies_count !== undefined">
                <el-icon><ChatLineRound /></el-icon>
                <span>{{ scope.row.replies_count }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleDetail(scope.row)">
              查看
            </el-button>
            <el-button 
              v-if="scope.row.status !== 1" 
              type="success" 
              link 
              @click="handleApprove(scope.row)"
            >
              通过
            </el-button>
            <el-button 
              v-if="scope.row.status !== 2" 
              type="warning" 
              link 
              @click="handleReject(scope.row)"
            >
              拒绝
            </el-button>
            <el-button 
              type="danger" 
              link 
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
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
    
    <!-- 评论详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="评论详情"
      width="650px"
      destroy-on-close
    >
      <div class="comment-detail" v-if="currentComment">
        <div class="detail-header">
          <div class="detail-user" v-if="currentComment.user">
            <el-avatar :size="40" :src="formatAvatar(currentComment.user.avatar)">
              {{ formatInitials(currentComment.user) }}
            </el-avatar>
            <div class="detail-user-info">
              <div class="detail-username">{{ currentComment.user.nickname || currentComment.user.username }}</div>
              <div class="detail-time">{{ currentComment.created_at }}</div>
            </div>
          </div>
          <el-tag :type="getStatusType(currentComment.status)">
            {{ getStatusText(currentComment.status) }}
          </el-tag>
        </div>
        
        <div class="detail-target" v-if="currentComment.target_info">
          <div class="target-title">评论对象：{{ getContentTypeText(currentComment.content_type) }}</div>
          <el-card shadow="never" class="target-card">
            <div class="target-content">
              <el-image 
                v-if="currentComment.target_info.cover_image" 
                :src="formatImageUrl(currentComment.target_info.cover_image)"
                class="target-cover"
              />
              <div class="target-name">{{ currentComment.target_info.name }}</div>
            </div>
          </el-card>
        </div>
        
        <div class="detail-content">
          <div class="content-text">{{ currentComment.content }}</div>
          
          <div class="detail-images" v-if="currentComment.images && currentComment.images.length > 0">
            <el-image
              v-for="(img, index) in currentComment.images"
              :key="index"
              :src="formatImageUrl(img)"
              fit="cover"
              :preview-src-list="currentComment.images.map(formatImageUrl)"
              preview-teleported
              class="detail-image"
            />
          </div>
        </div>
        
        <div class="detail-actions">
          <el-button 
            type="success" 
            @click="handleApprove(currentComment)" 
            v-if="currentComment.status !== 1"
          >
            通过审核
          </el-button>
          <el-button 
            type="warning" 
            @click="handleReject(currentComment)" 
            v-if="currentComment.status !== 2"
          >
            拒绝评论
          </el-button>
          <el-button 
            type="danger" 
            @click="handleDelete(currentComment)"
          >
            删除评论
          </el-button>
        </div>
      </div>
    </el-dialog>
    
    <!-- 拒绝原因对话框 -->
    <el-dialog
      v-model="rejectVisible"
      title="拒绝评论"
      width="500px"
      destroy-on-close
    >
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="拒绝原因">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            placeholder="请输入拒绝原因（选填）"
            :rows="4"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rejectVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmReject" :loading="rejectLoading">
            确认拒绝
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
// eslint-disable-next-line no-unused-vars
import { Search, Refresh, Star, ChatLineRound } from '@element-plus/icons-vue'
import { 
  getCommentList, getCommentDetail, approveComment, rejectComment, deleteComment,
  type Comment, type CommentQuery 
} from '@/api/comment'

// 状态与数据
const loading = ref(false)
const commentList = ref<Comment[]>([])
const total = ref(0)
const dateRange = ref<[string, string] | null>(null)
const detailVisible = ref(false)
const currentComment = ref<Comment | null>(null)
const rejectVisible = ref(false)
const rejectLoading = ref(false)
const rejectForm = reactive({
  reason: '',
  commentId: 0
})

// 查询参数
const queryParams = reactive<CommentQuery>({
  keyword: '',
  target_type: '',
  status: undefined,
  start_date: '',
  end_date: '',
  page: 1,
  per_page: 10
})

// 监听日期范围变化
watch(dateRange, (val) => {
  if (val) {
    queryParams.start_date = val[0]
    queryParams.end_date = val[1]
  } else {
    queryParams.start_date = ''
    queryParams.end_date = ''
  }
})

// 获取评论列表
const fetchCommentList = async () => {
  loading.value = true
  try {
    const res = await getCommentList(queryParams)
    // 获取返回数据，适配后端返回格式
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      if (responseData.data && responseData.data.items) {
        commentList.value = responseData.data.items
        total.value = responseData.data.total || 0
      } else if (responseData.items) {
        commentList.value = responseData.items
        total.value = responseData.total || 0
      } else {
        commentList.value = []
        total.value = 0
      }
    } else {
      ElMessage.error(responseData.message || '获取评论列表失败')
      commentList.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取评论列表失败:', error)
    ElMessage.error('获取评论列表失败')
    commentList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 查看详情
const handleDetail = async (row: Comment) => {
  try {
    const res = await getCommentDetail(row.id)
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      currentComment.value = responseData.data
      detailVisible.value = true
    } else {
      ElMessage.error(responseData.message || '获取评论详情失败')
    }
  } catch (error) {
    console.error('获取评论详情失败:', error)
    ElMessage.error('获取评论详情失败')
  }
}

// 审核通过
const handleApprove = async (row: Comment) => {
  try {
    await ElMessageBox.confirm('确认通过该评论吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    const res = await approveComment(row.id)
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      ElMessage.success(responseData.message || '评论审核通过成功')
      fetchCommentList()
      if (detailVisible.value) {
        detailVisible.value = false
      }
    } else {
      ElMessage.error(responseData.message || '评论审核通过失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('审核评论失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 拒绝评论
const handleReject = (row: Comment) => {
  rejectForm.commentId = row.id
  rejectForm.reason = ''
  rejectVisible.value = true
}

// 确认拒绝
const confirmReject = async () => {
  rejectLoading.value = true
  try {
    const res = await rejectComment(rejectForm.commentId, rejectForm.reason || undefined)
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      ElMessage.success(responseData.message || '评论拒绝成功')
      rejectVisible.value = false
      fetchCommentList()
      if (detailVisible.value) {
        detailVisible.value = false
      }
    } else {
      ElMessage.error(responseData.message || '评论拒绝失败')
    }
  } catch (error) {
    console.error('拒绝评论失败:', error)
    ElMessage.error('操作失败')
  } finally {
    rejectLoading.value = false
  }
}

// 删除评论
const handleDelete = async (row: Comment) => {
  try {
    await ElMessageBox.confirm('确认删除该评论吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    
    const res = await deleteComment(row.id)
    const responseData = res as any
    
    if (responseData.code === 0 || responseData.code === 200 || responseData.success) {
      ElMessage.success(responseData.message || '删除成功')
      fetchCommentList()
      if (detailVisible.value) {
        detailVisible.value = false
      }
    } else {
      ElMessage.error(responseData.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除评论失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 处理查询
const handleQuery = () => {
  queryParams.page = 1
  fetchCommentList()
}

// 重置查询
const resetQuery = () => {
  queryParams.keyword = ''
  queryParams.target_type = ''
  queryParams.status = undefined
  dateRange.value = null
  queryParams.start_date = ''
  queryParams.end_date = ''
  queryParams.page = 1
  fetchCommentList()
}

// 每页条数变化
const handleSizeChange = (val: number) => {
  queryParams.per_page = val
  fetchCommentList()
}

// 页码变化
const handleCurrentChange = (val: number) => {
  queryParams.page = val
  fetchCommentList()
}

// 格式化图片URL
const formatImageUrl = (url: string): string => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/static')) return `http://localhost:5000${url}`
  return `http://localhost:5000/static/images/${url.replace(/^\//, '')}`
}

// 格式化头像
const formatAvatar = (avatar?: string): string => {
  if (!avatar) return ''
  return formatImageUrl(avatar)
}

// 格式化用户首字母
const formatInitials = (user: any): string => {
  if (!user) return '?'
  return (user.nickname || user.username || '?').substring(0, 1).toUpperCase()
}

// 获取状态类型
const getStatusType = (status: number): string => {
  switch (status) {
    case 0: return 'info'     // 待审核
    case 1: return 'success'  // 已发布
    case 2: return 'warning'  // 已拒绝
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: number): string => {
  switch (status) {
    case 0: return '待审核'
    case 1: return '已发布'
    case 2: return '已拒绝'
    default: return '未知状态'
  }
}

// 获取内容类型文本
const getContentTypeText = (type: string): string => {
  switch (type) {
    case 'attraction': return '景点'
    case 'note': return '游记'
    case 'guide': return '攻略'
    default: return '未知类型'
  }
}

// 初始化
onMounted(() => {
  fetchCommentList()
})
</script>

<style scoped>
.comments-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.filter-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 用户信息 */
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.user-name {
  font-size: 13px;
  max-width: 100px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 评论内容 */
.comment-content {
  margin-bottom: 8px;
  line-height: 1.5;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 8px;
}

.comment-image {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  object-fit: cover;
}

.target-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.target-name {
  color: #606266;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 互动数据 */
.interaction-data {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 13px;
}

.interaction-data div {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 详情样式 */
.comment-detail {
  padding: 0 10px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-user-info {
  display: flex;
  flex-direction: column;
}

.detail-username {
  font-weight: bold;
  font-size: 16px;
}

.detail-time {
  font-size: 12px;
  color: #909399;
}

.detail-target {
  margin-bottom: 20px;
}

.target-title {
  font-size: 14px;
  margin-bottom: 10px;
  font-weight: bold;
}

.target-card {
  border: 1px solid #ebeef5;
}

.target-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.target-cover {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.detail-content {
  background-color: #f7f7f7;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.content-text {
  line-height: 1.6;
  margin-bottom: 10px;
}

.detail-images {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.detail-image {
  width: 120px;
  height: 120px;
  border-radius: 6px;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style> 