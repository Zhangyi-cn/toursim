<!-- 旅游指南详情页 -->
<template>
  <div class="guide-detail-container">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <div v-else-if="error" class="error-container">
      <el-empty description="加载失败" :image-size="200">
        <el-button type="primary" @click="loadGuideDetail">重试</el-button>
      </el-empty>
    </div>
    
    <template v-else-if="guide && guide.id">
      <!-- 头部信息 -->
      <div class="detail-header">
        <h1 class="guide-title">{{ guide.title }}</h1>
        
        <div class="guide-meta">
          <div class="category">
            <el-tag size="small" effect="plain" type="success">{{ guide.category_name }}</el-tag>
          </div>
          
          <div class="publish-info">
            <span class="date">发布时间：{{ formatDate(guide.created_at) }}</span>
            <span class="author">作者：{{ guide.user_name || '游客' }}</span>
          </div>
          
          <div class="stats">
            <el-tooltip content="浏览量" placement="top">
              <span class="stat-item"><el-icon><View /></el-icon> {{ guide.view_count }}</span>
            </el-tooltip>
            <el-tooltip content="点赞数" placement="top">
              <span class="stat-item"><el-icon><Star /></el-icon> {{ guide.like_count }}</span>
            </el-tooltip>
            <el-tooltip content="收藏数" placement="top">
              <span class="stat-item"><el-icon><Collection /></el-icon> {{ guide.collection_count }}</span>
            </el-tooltip>
            <el-tooltip content="评论数" placement="top">
              <span class="stat-item"><el-icon><ChatRound /></el-icon> {{ guide.comment_count }}</span>
            </el-tooltip>
          </div>
        </div>
      </div>
      
      <!-- 封面图 -->
      <div class="cover-image">
        <el-image
          :src="guide.cover_image"
          fit="cover"
          :preview-src-list="[guide.cover_image]"
        >
          <template #error>
            <div class="image-slot">
              <el-icon><Picture /></el-icon>
            </div>
          </template>
        </el-image>
      </div>
      
      <!-- 内容 -->
      <div class="guide-content" v-html="guide.content"></div>
      
      <!-- 操作栏 -->
      <div class="action-bar">
        <el-button 
          :type="isLiked ? 'danger' : 'default'" 
          @click="handleLike"
        >
          <el-icon v-if="isLiked"><StarFilled /></el-icon>
          <el-icon v-else><Star /></el-icon>
          {{ isLiked ? '已点赞' : '点赞' }}
        </el-button>
        
        <el-button 
          :type="isCollected ? 'warning' : 'default'" 
          @click="handleCollect"
        >
          <el-icon v-if="isCollected"><CollectionTag /></el-icon>
          <el-icon v-else><Collection /></el-icon>
          {{ isCollected ? '已收藏' : '收藏' }}
        </el-button>
      </div>
      
      <!-- 评论区 -->
      <div class="comment-section">
        <h3 class="section-title">评论（{{ guide.comment_count || 0 }}）</h3>
        
        <!-- 评论输入框 -->
        <div class="comment-input">
          <div v-if="replyingToComment" class="replying-info">
            <span>回复给：{{ replyingToComment.user?.username || '游客' }}</span>
            <el-button type="text" @click="cancelReply">取消回复</el-button>
          </div>
          <el-input
            v-model="commentContent"
            type="textarea"
            :rows="3"
            :placeholder="replyingToComment ? '请输入回复内容' : '请输入您的评论'"
            maxlength="500"
            show-word-limit
          ></el-input>
          <div class="comment-buttons">
            <el-button type="primary" @click="submitComment" :disabled="!commentContent.trim()">
              {{ replyingToComment ? '发布回复' : '发布评论' }}
            </el-button>
          </div>
        </div>
        
        <!-- 评论列表 -->
        <div v-if="comments.length > 0" class="comment-list" v-loading="commentsLoading">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-avatar">
              <el-avatar :size="40" :src="comment.user?.avatar || ''">
                {{ comment.user?.username?.charAt(0) || 'U' }}
              </el-avatar>
            </div>
            <div class="comment-content">
              <div class="comment-header">
                <span class="comment-user">{{ comment.user?.username || '游客' }}</span>
                <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
              </div>
              <div class="comment-text">{{ comment.content }}</div>
              <div class="comment-footer">
                <span class="action-item" @click="handleReply(comment)">回复{{ comment.reply_count ? `(${comment.reply_count})` : '' }}</span>
                <!-- 可以添加查看回复功能 -->
                <span v-if="comment.reply_count > 0" class="action-item" @click="loadReplies(comment)">
                  {{ showingRepliesFor === comment.id ? '收起回复' : '查看回复' }}
                </span>
              </div>
              
              <!-- 回复列表 -->
              <div v-if="showingRepliesFor === comment.id && commentReplies.length > 0" class="replies-list">
                <div v-for="reply in commentReplies" :key="reply.id" class="reply-item">
                  <div class="reply-avatar">
                    <el-avatar :size="30" :src="reply.user?.avatar || ''">
                      {{ reply.user?.username?.charAt(0) || 'U' }}
                    </el-avatar>
                  </div>
                  <div class="reply-content">
                    <div class="reply-header">
                      <span class="reply-user">{{ reply.user?.username || '游客' }}</span>
                      <span class="reply-time">{{ formatDate(reply.created_at) }}</span>
                    </div>
                    <div class="reply-text">{{ reply.content }}</div>
                    <div class="reply-actions">
                      <span class="action-item" @click="handleReply(reply)">回复</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="!commentsLoading" class="empty-comments">
          <el-empty description="暂无评论" :image-size="100">
            <template #description>
              <p>暂无评论，快来发表第一条评论吧！</p>
            </template>
          </el-empty>
        </div>
        
        <!-- 评论分页 -->
        <div v-if="commentTotal > commentPageSize" class="comment-pagination">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="commentTotal"
            :page-size="commentPageSize"
            :current-page="commentPage"
            @current-change="handleCommentPageChange"
          ></el-pagination>
        </div>
      </div>
    </template>
    
    <div v-else-if="!loading && !error" class="error-container">
      <el-empty description="攻略不存在或已被删除" :image-size="200">
        <el-button type="primary" @click="router.push('/travel-guides')">返回攻略列表</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Star, StarFilled, Collection, CollectionTag, ChatRound, Picture } from '@element-plus/icons-vue'
import type { TravelGuide } from '@/types/travel-guide'
import {
  getGuideDetail,
  getGuideComments,
  addComment,
  likeGuide,
  unlikeGuide,
  collectGuide,
  uncollectGuide,
  checkGuideStatus,
  getRecommendedGuides,
  AddCommentParams
} from '@/api/travel-guide'
import { formatDate } from '@/utils/date'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 状态数据
const loading = ref(false)
const commentsLoading = ref(false)
const error = ref(false)
const guide = ref<any>({})
const recommendedGuides = ref<any[]>([])
const isLiked = ref(false)
const isCollected = ref(false)
const commentContent = ref('')
const comments = ref<any[]>([])
const commentPage = ref(1)
const commentTotal = ref(0)
const commentPageSize = ref(10)
const replyingToComment = ref<any | null>(null)
const showingRepliesFor = ref<string | null>(null)
const commentReplies = ref<any[]>([])

// 加载指南详情
const loadGuideDetail = async () => {
  const id = route.params.id as string
  if (!id) {
    ElMessage.error('指南ID不存在')
    router.push('/travel-guides')
    return
  }
  
  loading.value = true
  error.value = false
  
  try {
    const res = await getGuideDetail(parseInt(id))
    if (res.code === 200 && res.success && res.data) {
      guide.value = res.data
      
      // 设置点赞和收藏状态
      isLiked.value = !!guide.value.has_liked
      isCollected.value = !!guide.value.has_collected
      
      // 加载评论
      loadComments()
    } else {
      // 请求成功但返回错误信息或数据为空
      guide.value = {}
      error.value = true
      ElMessage.error(res.message || '加载指南详情失败')
    }
  } catch (err: any) {
    // 请求失败
    guide.value = {}
    console.error('加载指南详情失败:', err)
    error.value = true
    ElMessage.error(err.message || '加载指南详情失败')
  } finally {
    loading.value = false
  }
}

// 加载推荐指南
const loadRecommendedGuides = async () => {
  try {
    const res = await getRecommendedGuides(5)
    if (res.code === 200 && res.success) {
      recommendedGuides.value = res.data.filter((item: any) => item.id !== guide.value?.id)
    }
  } catch (error: any) {
    console.error('获取推荐指南失败:', error)
  }
}

// 加载评论
const loadComments = async () => {
  const id = route.params.id as string
  if (!id) return
  
  commentsLoading.value = true
  
  try {
    const res = await getGuideComments(parseInt(id), {
      page: commentPage.value,
      per_page: commentPageSize.value,
      sort_by: 'latest'
    })
    
    if (res.code === 200 && res.success) {
      comments.value = res.data.items
      commentTotal.value = res.data.total
      commentPage.value = res.data.page
      commentPageSize.value = res.data.per_page
    } else {
      ElMessage.error(res.message || '加载评论失败')
    }
  } catch (err: any) {
    console.error('加载评论失败:', err)
    ElMessage.error(err.message || '加载评论失败')
  } finally {
    commentsLoading.value = false
  }
}

// 处理点赞
const handleLike = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  
  const id = parseInt(route.params.id as string)
  
  try {
    let res
    if (isLiked.value) {
      res = await unlikeGuide(id)
    } else {
      res = await likeGuide(id)
    }
    
    if (res.code === 200 && res.success) {
      // 更新状态和点赞数
      isLiked.value = !isLiked.value
      
      if (guide.value) {
        // 更新点赞状态
        guide.value.has_liked = isLiked.value
        
        // 更新点赞数
        if (guide.value.like_count !== undefined) {
          if (isLiked.value) {
            guide.value.like_count += 1
            ElMessage.success('点赞成功')
          } else {
            guide.value.like_count -= 1
            ElMessage.success('取消点赞成功')
          }
        }
      }
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (err: any) {
    console.error('点赞操作失败:', err)
    ElMessage.error(err.message || '操作失败')
  }
}

// 处理收藏
const handleCollect = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  
  const id = parseInt(route.params.id as string)
  
  try {
    let res
    if (isCollected.value) {
      res = await uncollectGuide(id)
    } else {
      res = await collectGuide(id)
    }
    
    if (res.code === 200 && res.success) {
      // 更新状态和收藏数
      isCollected.value = !isCollected.value
      
      if (guide.value) {
        // 更新收藏状态
        guide.value.has_collected = isCollected.value
        
        // 更新收藏数
        if (guide.value.collection_count !== undefined) {
          if (isCollected.value) {
            guide.value.collection_count += 1
            ElMessage.success('收藏成功')
          } else {
            guide.value.collection_count -= 1
            ElMessage.success('取消收藏成功')
          }
        }
      }
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (err: any) {
    console.error('收藏操作失败:', err)
    ElMessage.error(err.message || '操作失败')
  }
}

// 处理分享
const handleShare = () => {
  // TODO: 实现分享功能
  ElMessage.info('分享功能开发中')
}

// 处理点击推荐指南
const handleGuideClick = (guide: TravelGuide) => {
  router.push(`/travel-guides/${guide.id}`)
}

// 提交评论
const submitComment = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  
  if (!commentContent.value.trim()) {
    ElMessage.warning('评论内容不能为空')
    return
  }
  
  const id = parseInt(route.params.id as string)
  const content = commentContent.value.trim()
  
  try {
    // 构建评论参数
    const commentData: AddCommentParams = {
      content
    }
    
    // 如果是回复其他评论
    if (replyingToComment.value) {
      commentData.parent_id = replyingToComment.value.id
      if (replyingToComment.value.user_id) {
        commentData.reply_to = replyingToComment.value.user_id
      }
    }
    
    const res = await addComment(id, commentData)
    
    if (res.code === 200 && res.success) {
      ElMessage.success('评论成功')
      commentContent.value = ''
      replyingToComment.value = null
      
      // 更新评论数并重新加载评论
      if (guide.value && guide.value.comment_count !== undefined) {
        guide.value.comment_count += 1
      }
      loadComments()
    } else {
      ElMessage.error(res.message || '评论失败')
    }
  } catch (err: any) {
    console.error('评论失败:', err)
    ElMessage.error(err.message || '评论失败')
  }
}

// 回复评论
const handleReply = (comment: any) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  
  commentContent.value = `@${comment.user?.username || '游客'} `
  replyingToComment.value = comment
  // 滚动到评论框
  document.querySelector('.comment-input')?.scrollIntoView({ behavior: 'smooth' })
}

// 评论分页变化
const handleCommentPageChange = (page: number) => {
  commentPage.value = page
  loadComments()
}

// 加载回复
const loadReplies = async (comment: any) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }
  
  // 如果当前已经显示这个评论的回复，则收起
  if (showingRepliesFor.value === comment.id) {
    showingRepliesFor.value = null
    return
  }
  
  // 否则加载回复并展示
  showingRepliesFor.value = comment.id
  
  try {
    const res = await getGuideComments(parseInt(route.params.id as string), {
      page: 1,
      per_page: 10,
      sort_by: 'latest',
      parent_id: comment.id
    })
    
    if (res.code === 200 && res.success) {
      commentReplies.value = res.data.items
    } else {
      ElMessage.error(res.message || '加载回复失败')
    }
  } catch (err: any) {
    console.error('加载回复失败:', err)
    ElMessage.error(err.message || '加载回复失败')
  }
}

// 取消回复
const cancelReply = () => {
  showingRepliesFor.value = null
  commentContent.value = ''
  replyingToComment.value = null
}

onMounted(() => {
  loadGuideDetail()
  loadRecommendedGuides()
})
</script>

<style scoped>
.guide-detail-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container,
.error-container {
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.detail-header {
  margin-bottom: 20px;
}

.guide-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #333;
}

.guide-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
  color: #666;
  font-size: 14px;
}

.publish-info {
  display: flex;
  gap: 15px;
}

.stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.cover-image {
  width: 100%;
  height: 400px;
  margin-bottom: 30px;
  border-radius: 8px;
  overflow: hidden;
}

.cover-image .el-image {
  width: 100%;
  height: 100%;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}

.guide-content {
  margin-bottom: 30px;
  line-height: 1.8;
  color: #333;
}

.guide-content :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 10px 0;
}

.guide-content :deep(h2) {
  font-size: 24px;
  margin: 30px 0 20px;
  color: #1e1e1e;
}

.guide-content :deep(h3) {
  font-size: 20px;
  margin: 25px 0 15px;
  color: #1e1e1e;
}

.guide-content :deep(p) {
  margin: 15px 0;
}

.guide-content :deep(ul), .guide-content :deep(ol) {
  margin: 15px 0;
  padding-left: 20px;
}

.action-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  padding: 20px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  justify-content: center;
}

.comment-section {
  margin-top: 30px;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

.comment-input {
  margin-bottom: 30px;
}

.comment-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.comment-list {
  margin-bottom: 20px;
}

.comment-item {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-user {
  font-weight: bold;
  color: #333;
}

.comment-time {
  color: #999;
  font-size: 12px;
}

.comment-text {
  line-height: 1.6;
  margin-bottom: 10px;
}

.comment-footer {
  display: flex;
  justify-content: flex-start;
  gap: 15px;
  align-items: center;
  margin-top: 10px;
  color: #409eff;
  font-size: 13px;
}

.action-item {
  cursor: pointer;
  margin-right: 15px;
}

.action-item:hover {
  text-decoration: underline;
}

.empty-comments {
  padding: 30px 0;
}

.comment-pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.replying-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f7fa;
  padding: 8px 12px;
  margin-bottom: 10px;
  border-radius: 4px;
  color: #666;
}

.replies-list {
  margin-top: 15px;
  margin-left: 20px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.reply-item {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #eee;
}

.reply-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.reply-content {
  flex: 1;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.reply-user {
  font-weight: bold;
  color: #333;
  font-size: 13px;
}

.reply-time {
  color: #999;
  font-size: 12px;
}

.reply-text {
  line-height: 1.5;
  margin-bottom: 8px;
  font-size: 13px;
}

.reply-actions {
  color: #409eff;
  font-size: 12px;
}

@media (max-width: 768px) {
  .guide-detail-container {
    padding: 15px;
  }
  
  .guide-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .cover-image {
    height: 250px;
  }
}
</style> 