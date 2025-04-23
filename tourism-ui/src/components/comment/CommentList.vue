<template>
  <div class="comment-list-component">
    <div class="comment-list-header">
      <h3 v-if="title">{{ title }}</h3>
      <span class="comment-count">{{ totalComments || 0 }}条评论</span>
    </div>

    <!-- 评论输入框 -->
    <div class="comment-input-container" v-if="!replyTo">
      <el-avatar :src="userInfo?.avatar || '/default-avatar.png'" :size="40"></el-avatar>
      <div class="comment-input-wrapper">
        <template v-if="isLoggedIn">
          <el-input
            v-model="commentContent"
            type="textarea"
            :rows="2"
            placeholder="说点什么吧..."
            @focus="handleFocus"
          />
          <div class="comment-actions" v-if="inputActive || commentContent">
            <div class="upload-container" v-if="supportImages">
              <el-upload
                action="#"
                :auto-upload="false"
                :on-change="handleImageChange"
                :on-remove="handleImageRemove"
                :limit="3"
                list-type="picture-card"
                :file-list="fileList"
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
            </div>
            <div class="button-container">
              <el-button @click="cancelComment">取消</el-button>
              <el-button type="primary" @click="submitComment" :loading="submitting">发布评论</el-button>
            </div>
          </div>
        </template>
        <div v-else class="login-tip">
          <span>请先<el-button type="primary" size="small" @click="goToLogin">登录</el-button>后参与评论</span>
        </div>
      </div>
    </div>

    <!-- 评论加载提示 -->
    <div v-if="loading" class="comment-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 评论为空提示 -->
    <el-empty v-if="!loading && comments.length === 0" description="暂无评论，快来发表第一条评论吧！"></el-empty>

    <!-- 评论列表 -->
    <div class="comments-container" v-if="!loading && comments.length > 0">
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-author">
          <el-avatar :src="comment.user?.avatar || '/default-avatar.png'" :size="40"></el-avatar>
        </div>
        <div class="comment-content">
          <div class="comment-header">
            <span class="author-name">{{ comment.user?.nickname || '匿名用户' }}</span>
            <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
          </div>
          <div class="comment-text">{{ comment.content }}</div>
          
          <!-- 评论图片 -->
          <div class="comment-images" v-if="comment.images && comment.images.length > 0">
            <el-image
              v-for="(image, index) in comment.images"
              :key="index"
              :src="getImageUrl(image)"
              :preview-src-list="comment.images.map(getImageUrl)"
              fit="cover"
              class="comment-image"
            />
          </div>
          
          <div class="comment-actions">
            <!-- 暂时屏蔽回复功能 -->
            <!-- <el-button type="text" @click="showReply(comment)" v-if="isLoggedIn">回复</el-button> -->
            <el-button 
              type="text" 
              class="delete-btn" 
              @click="handleDelete(comment)" 
              v-if="isLoggedIn && canDelete(comment)"
            >删除</el-button>
            <!-- 暂时屏蔽回复列表显示 -->
            <!-- <el-button 
              type="text" 
              @click="loadReplies(comment)" 
              v-if="comment.reply_count > 0 && !comment.repliesLoaded"
            >
              查看回复({{ comment.reply_count }})
            </el-button> -->
          </div>
          
          <!-- 回复区域 - 暂时屏蔽 -->
          <!-- <div class="reply-container" v-if="replyTo && replyTo.id === comment.id">
            <div class="reply-input-wrapper">
              <template v-if="isLoggedIn">
                <el-input
                  v-model="replyContent"
                  type="textarea"
                  :rows="2"
                  :placeholder="`回复 ${comment.user.nickname}:`"
                />
                <div class="reply-actions">
                  <el-button @click="cancelReply">取消</el-button>
                  <el-button type="primary" @click="submitReply(comment)" :loading="submitting">回复</el-button>
                </div>
              </template>
              <div v-else class="login-tip">
                <span>请先<el-button type="primary" size="small" @click="goToLogin">登录</el-button>后参与评论</span>
              </div>
            </div>
          </div> -->
          
          <!-- 回复列表 - 暂时屏蔽 -->
          <!-- <div class="replies-container" v-if="comment.replies && comment.replies.length > 0">
            <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
              <div class="reply-author">
                <el-avatar :src="reply.user?.avatar || '/default-avatar.png'" :size="30"></el-avatar>
              </div>
              <div class="reply-content">
                <div class="reply-header">
                  <span class="author-name">{{ reply.user?.nickname || '用户' }}</span>
                  <span class="reply-time">{{ formatDate(reply.created_at) }}</span>
                </div>
                <div class="reply-text">{{ reply.content }}</div>
                <div class="reply-actions">
                  <el-button type="text" @click="showReply(comment, reply)" v-if="isLoggedIn">回复</el-button>
                  <el-button 
                    type="text" 
                    class="delete-btn" 
                    @click="handleDelete(reply)" 
                    v-if="isLoggedIn && canDelete(reply)"
                  >删除</el-button>
                </div>
              </div>
            </div>
          </div> -->
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="totalPages > 1">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="totalComments"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineProps, defineEmits } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { getAttractionComments, addAttractionComment, deleteComment, type Comment } from '@/api/comment'

const props = defineProps({
  targetId: {
    type: [Number, String],
    required: true
  },
  title: {
    type: String,
    default: '评论'
  },
  supportImages: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:count'])

// 状态
const loading = ref(false)
const submitting = ref(false)
const inputActive = ref(false)
const comments = ref([])
const commentContent = ref('')
const replyContent = ref('')
const replyTo = ref(null)
const fileList = ref([])
const totalComments = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 用户信息
const userStore = useUserStore()
const router = useRouter()
const userInfo = computed(() => userStore.userInfo)
const isLoggedIn = computed(() => userStore.isLoggedIn)

// 计算属性
const totalPages = computed(() => Math.ceil(totalComments.value / pageSize.value))

// 获取评论列表
const fetchComments = async () => {
  loading.value = true
  try {
    const response = await getAttractionComments(props.targetId, {
      page: currentPage.value,
      per_page: pageSize.value,
      parent_id: 0 // 只获取顶级评论
    })
    
    if (response.data?.items) {
      comments.value = response.data.items
      totalComments.value = response.data.pagination.total
      emit('update:count', totalComments.value)
    }
  } catch (error) {
    console.error('获取评论失败:', error)
    ElMessage.error('获取评论失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 加载回复
const loadReplies = async (comment) => {
  if (comment.repliesLoaded) return
  
  try {
    const response = await getAttractionComments(props.targetId, {
      parent_id: comment.id,
      page: 1,
      per_page: 50 // 获取所有回复，一般回复不会太多
    })
    
    if (response.data?.items) {
      // 将回复添加到父评论中
      comment.replies = response.data.items || []
      comment.repliesLoaded = true
      
      // 如果没有回复但API返回成功，设置空数组
      if (!comment.replies.length) {
        console.log('回复列表为空，设置空数组')
        comment.replies = []
      }
    } else {
      console.error('加载回复失败：响应数据格式不正确', response)
      comment.replies = []
      comment.repliesLoaded = true
    }
  } catch (error) {
    console.error('获取回复失败:', error)
    ElMessage.error('获取回复失败，请稍后重试')
    // 防止反复请求出错
    comment.repliesLoaded = true
    comment.replies = []
  }
}

// 发布评论
const submitComment = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录后再发表评论')
    return
  }
  
  if (!commentContent.value.trim()) {
    ElMessage.warning('评论内容不能为空')
    return
  }
  
  submitting.value = true
  
  try {
    // 处理图片上传
    let images = []
    if (fileList.value.length > 0) {
      // 这里假设您有一个上传图片的API，这里省略具体实现
      // 上传完成后获取图片URL列表
      // images = await uploadImages(fileList.value)
      images = fileList.value.map(file => file.url || file.response?.url)
    }
    
    const response = await addAttractionComment(props.targetId, {
      content: commentContent.value,
      images: images.length > 0 ? images : undefined
    })
    
    if (response.code === 200) {
      ElMessage.success('评论发布成功')
      commentContent.value = ''
      fileList.value = []
      inputActive.value = false
      // 重新加载评论列表
      fetchComments()
    }
  } catch (error) {
    console.error('发布评论失败:', error)
    ElMessage.error('发布评论失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// 发布回复
const submitReply = async (comment) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录后再回复评论')
    return
  }
  
  if (!replyContent.value.trim()) {
    ElMessage.warning('回复内容不能为空')
    return
  }
  
  submitting.value = true
  
  try {
    const response = await addAttractionComment(props.targetId, {
      content: replyContent.value,
      parent_id: replyTo.value.id
    })
    
    if (response.code === 200) {
      ElMessage.success('回复发布成功')
      
      // 如果已经加载了回复，则添加新回复到列表中
      if (comment.repliesLoaded && comment.replies) {
        // 构建新回复对象，确保包含所有必要字段
        const newReply = {
          ...response.data,
          user: userInfo.value || {
            id: 0,
            nickname: '当前用户',
            avatar: ''
          }
        }
        // 添加到回复列表顶部
        comment.replies.unshift(newReply)
      } else {
        // 如果还没加载回复，初始化回复列表并添加
        comment.replies = [
          {
            ...response.data,
            user: userInfo.value || {
              id: 0,
              nickname: '当前用户',
              avatar: ''
            }
          }
        ]
        comment.repliesLoaded = true
      }
      
      // 更新回复数
      comment.reply_count += 1
      
      // 清空回复框
      replyContent.value = ''
      replyTo.value = null
    }
  } catch (error) {
    console.error('发布回复失败:', error)
    ElMessage.error('发布回复失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// 删除评论
const handleDelete = (comment) => {
  ElMessageBox.confirm('确定要删除此评论吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const response = await deleteComment(comment.id)
      
      if (response.code === 200) {
        ElMessage.success('评论删除成功')
        
        // 如果是回复，从回复列表中移除
        if (comment.parent_id) {
          const parentComment = comments.value.find(c => c.id === comment.parent_id)
          if (parentComment && parentComment.replies) {
            parentComment.replies = parentComment.replies.filter(r => r.id !== comment.id)
            parentComment.reply_count -= 1
          }
        } else {
          // 如果是主评论，从评论列表中移除
          comments.value = comments.value.filter(c => c.id !== comment.id)
          totalComments.value -= 1
          emit('update:count', totalComments.value)
        }
      }
    } catch (error) {
      console.error('删除评论失败:', error)
      ElMessage.error('删除评论失败，请稍后重试')
    }
  }).catch(() => {})
}

// 判断是否可以删除评论
const canDelete = (comment) => {
  if (!isLoggedIn.value || !userInfo.value) return false
  // 用户可以删除自己的评论
  return comment.user && userInfo.value && comment.user.id === userInfo.value.id
}

// 显示回复框
const showReply = (comment, reply = null) => {
  replyTo.value = comment
  replyContent.value = reply && reply.user && reply.user.nickname 
    ? `@${reply.user.nickname} ` 
    : ''
}

// 取消回复
const cancelReply = () => {
  replyTo.value = null
  replyContent.value = ''
}

// 取消评论
const cancelComment = () => {
  commentContent.value = ''
  fileList.value = []
  inputActive.value = false
}

// 处理输入框获取焦点
const handleFocus = () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录后再发表评论')
    return
  }
  inputActive.value = true
}

// 处理图片变更
const handleImageChange = (file) => {
  // 这里可以添加图片大小、类型等验证
  return file
}

// 处理图片删除
const handleImageRemove = (file) => {
  fileList.value = fileList.value.filter(f => f.uid !== file.uid)
}

// 处理分页
const handlePageChange = (page) => {
  currentPage.value = page
  fetchComments()
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  return path.startsWith('http') ? path : `${import.meta.env.VITE_STATIC_ASSETS_URL || ''}/${path}`
}

// 跳转到登录页
const goToLogin = () => {
  router.push(`/auth/login?redirect=${encodeURIComponent(router.currentRoute.value.fullPath)}`)
}

// 页面加载时获取评论
onMounted(() => {
  fetchComments()
})
</script>

<style lang="scss" scoped>
.comment-list-component {
  margin: 20px 0;
  
  .comment-list-header {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    
    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: bold;
    }
    
    .comment-count {
      margin-left: auto;
      color: #909399;
    }
  }
  
  .comment-input-container {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    
    .comment-input-wrapper {
      flex: 1;
      
      .login-tip {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f8f8f8;
        padding: 15px;
        border-radius: 4px;
        
        span {
          color: #606266;
          
          .el-button {
            margin: 0 5px;
          }
        }
      }
      
      .comment-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
        
        .button-container {
          margin-left: auto;
          display: flex;
          gap: 10px;
        }
      }
    }
  }
  
  .comments-container {
    margin-top: 24px;
    
    .comment-item {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      
      .comment-content {
        flex: 1;
        
        .comment-header {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
          
          .author-name {
            font-weight: bold;
            color: #303133;
          }
          
          .comment-time {
            margin-left: auto;
            font-size: 12px;
            color: #909399;
          }
        }
        
        .comment-text {
          line-height: 1.6;
          margin-bottom: 8px;
          word-break: break-word;
        }
        
        .comment-images {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 8px;
          
          .comment-image {
            width: 100px;
            height: 100px;
            border-radius: 4px;
            object-fit: cover;
          }
        }
        
        .comment-actions {
          display: flex;
          gap: 16px;
          margin-top: 8px;
          
          .delete-btn {
            color: #F56C6C;
          }
        }
      }
    }
  }
  
  .reply-container {
    margin: 12px 0;
    background-color: #f7f7f7;
    padding: 12px;
    border-radius: 4px;
    
    .reply-input-wrapper {
      .reply-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 10px;
      }
    }
  }
  
  .replies-container {
    margin-top: 12px;
    background-color: #f7f7f7;
    padding: 12px;
    border-radius: 4px;
    
    .reply-item {
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .reply-content {
        flex: 1;
        
        .reply-header {
          display: flex;
          align-items: center;
          margin-bottom: 4px;
          
          .author-name {
            font-weight: bold;
            font-size: 14px;
            color: #303133;
          }
          
          .reply-time {
            margin-left: auto;
            font-size: 12px;
            color: #909399;
          }
        }
        
        .reply-text {
          line-height: 1.5;
          font-size: 14px;
          word-break: break-word;
        }
        
        .reply-actions {
          display: flex;
          gap: 16px;
          margin-top: 4px;
          
          .delete-btn {
            color: #F56C6C;
          }
        }
      }
    }
  }
  
  .pagination-container {
    margin-top: 24px;
    display: flex;
    justify-content: center;
  }
  
  .comment-loading {
    padding: 20px 0;
  }
}
</style> 