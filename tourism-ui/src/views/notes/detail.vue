<template>
  <div class="note-detail-page">
    <div class="page-container container" v-loading="loading">
      <!-- 笔记内容 -->
      <div class="note-content">
        <el-card class="main-content">
          <!-- 标题区域 -->
          <div class="note-header">
            <h1 class="note-title">{{ note.title }}</h1>
            <div class="note-meta">
              <div class="author-info">
                <el-avatar :size="40" :src="note.user_avatar"></el-avatar>
                <div class="author-detail">
                  <div class="author-name">{{ note.user_name }}</div>
                  <div class="publish-time">{{ formatDate(note.created_at) }}</div>
                </div>
              </div>
              <div class="meta-row">
                <span class="meta-item" v-if="note.trip_start_date && note.trip_end_date">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatDate(note.trip_start_date) }} 至 {{ formatDate(note.trip_end_date) }}</span>
                </span>
                <span class="meta-item" v-if="note.trip_days">
                  <el-icon><Timer /></el-icon>
                  <span>{{ note.trip_days }}天</span>
                </span>
                <span class="meta-item" v-if="note.trip_season">
                  <el-icon><Sunny /></el-icon>
                  <span>{{ note.trip_season }}</span>
                </span>
              </div>
              <div class="meta-row">
                <span class="meta-item" v-if="note.location">
                  <el-icon><Location /></el-icon>
                  <span>{{ note.location }}</span>
                </span>
                <span class="meta-item" v-if="note.trip_type">
                  <el-icon><Van /></el-icon>
                  <span>{{ note.trip_type }}</span>
                </span>
                <span class="meta-item" v-if="note.trip_people">
                  <el-icon><User /></el-icon>
                  <span>{{ note.trip_people }}人</span>
                </span>
                <span class="meta-item" v-if="note.trip_cost">
                  <el-icon><Money /></el-icon>
                  <span>¥{{ note.trip_cost }}</span>
                </span>
              </div>
            </div>
          </div>

          <!-- 封面图 -->
          <div class="note-cover" v-if="note.cover_image">
            <img :src="note.cover_image" :alt="note.title">
          </div>

          <!-- 正文内容 -->
          <div class="note-body" v-html="note.content"></div>

          <!-- 社交统计 -->
          <div class="note-stats">
            <div class="stat-item">
              <el-icon><View /></el-icon>
              <span>{{ note.views || 0 }}次阅读</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 侧边栏 -->
      <div class="note-sidebar">
        <!-- 作者信息卡片 -->
        <el-card class="author-card">
          <div class="author-header">
            <el-avatar :size="64" :src="note.user_avatar || '/default-avatar.png'"></el-avatar>
            <div class="author-info">
              <div class="author-name">{{ note.user_name || '游客' }}</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { View, Calendar, Timer, Location, Money } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getNoteDetail } from '@/api/note'
import { formatDate } from '@/utils/date'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 数据
const loading = ref(false)
const note = ref({})

// 加载笔记详情
const loadNoteDetail = async () => {
  loading.value = true
  try {
    const res = await getNoteDetail(route.params.id)
    if (res.code === 0 || res.code === 200) {
      note.value = res.data
      // 如果缺少前端显示需要的字段，进行补充
      if (!note.value.user_name) {
        note.value.user_name = "游客"
      }
      if (!note.value.user_avatar) {
        note.value.user_avatar = "/default-avatar.png"
      }
      // 计算旅行天数（如果API未返回）
      if (!note.value.trip_days && note.value.trip_start_date && note.value.trip_end_date) {
        note.value.trip_days = calculateTripDays(note.value.trip_start_date, note.value.trip_end_date)
      }
    } else {
      ElMessage.error(res.message || '获取游记详情失败')
    }
  } catch (error) {
    console.error('获取笔记详情失败:', error)
    // 检查错误对象是否包含code为0的情况（被拦截器拒绝但实际成功的请求）
    if (error && typeof error === 'object' && 'code' in error && error.code === 0 && error.data) {
      note.value = error.data
      // 如果缺少前端显示需要的字段，进行补充
      if (!note.value.user_name) {
        note.value.user_name = "游客"
      }
      if (!note.value.user_avatar) {
        note.value.user_avatar = "/default-avatar.png"
      }
      // 计算旅行天数（如果API未返回）
      if (!note.value.trip_days && note.value.trip_start_date && note.value.trip_end_date) {
        note.value.trip_days = calculateTripDays(note.value.trip_start_date, note.value.trip_end_date)
      }
    } else {
      ElMessage.error('获取游记详情失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

// 计算旅行天数
const calculateTripDays = (startDate, endDate) => {
  if (!startDate || !endDate) return 0
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffTime = Math.abs(end - start)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays + 1 // 包含首尾两天
}

onMounted(() => {
  loadNoteDetail()
})
</script>

<style lang="scss" scoped>
@use "@/styles/variables" as *;

.note-detail-page {
  padding: $spacing-lg 0;
  
  .page-container {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: $spacing-lg;
  }
  
  .note-content {
    .main-content {
      margin-bottom: $spacing-lg;
      
      .note-header {
        margin-bottom: $spacing-lg;
        
        .note-title {
          font-size: 28px;
          font-weight: bold;
          margin-bottom: $spacing-md;
          color: $text-primary;
        }
        
        .note-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          
          .author-info {
            display: flex;
            align-items: center;
            
            .author-detail {
              margin-left: $spacing-sm;
              
              .author-name {
                font-size: $font-size-base;
                font-weight: bold;
                color: $text-primary;
              }
              
              .publish-time {
                font-size: $font-size-sm;
                color: $text-secondary;
                margin-top: 2px;
              }
            }
          }
          
          .meta-row {
            display: flex;
            gap: $spacing-md;
            
            .meta-item {
              display: flex;
              align-items: center;
              font-size: $font-size-sm;
              color: $text-secondary;
              
              .el-icon {
                margin-right: 4px;
              }
            }
          }
        }
      }
      
      .note-cover {
        margin: 0 (-$spacing-md) $spacing-lg;
        
        img {
          width: 100%;
          max-height: 500px;
          object-fit: cover;
        }
      }
      
      .note-body {
        font-size: $font-size-base;
        line-height: 1.8;
        color: $text-primary;
        
        :deep(img) {
          max-width: 100%;
          height: auto;
          margin: $spacing-md 0;
        }
        
        :deep(p) {
          margin: $spacing-md 0;
        }
      }
      
      .note-stats {
        display: flex;
        gap: $spacing-md;
        justify-content: center;
        margin-top: $spacing-xl;
        padding-top: $spacing-lg;
        border-top: 1px solid $border-color;
      }
    }
  }
  
  .comments-section {
    .comments-header {
      h3 {
        margin: 0;
        font-size: $font-size-lg;
      }
    }
    
    .comment-input {
      margin-bottom: $spacing-lg;
      
      .comment-submit {
        margin-top: $spacing-sm;
        text-align: right;
      }
    }
    
    .login-tip {
      text-align: center;
      color: $text-secondary;
      padding: $spacing-md 0;
    }
    
    .comments-list {
      .comment-item {
        padding: $spacing-md 0;
        border-bottom: 1px solid $divider-color;
        
        &:last-child {
          border-bottom: none;
        }
        
        .comment-user {
          display: flex;
          align-items: center;
          margin-bottom: $spacing-sm;
          
          .comment-info {
            margin-left: $spacing-sm;
            
            .comment-name {
              font-size: $font-size-base;
              font-weight: bold;
              color: $text-primary;
            }
            
            .comment-time {
              font-size: $font-size-sm;
              color: $text-secondary;
              margin-top: 2px;
            }
          }
        }
        
        .comment-content {
          font-size: $font-size-base;
          color: $text-primary;
          line-height: 1.6;
        }
      }
    }
    
    .comments-pagination {
      margin-top: $spacing-lg;
      display: flex;
      justify-content: center;
    }
  }
  
  .note-sidebar {
    .author-card {
      margin-bottom: $spacing-lg;
      
      .author-header {
        display: flex;
        align-items: center;
        margin-bottom: $spacing-lg;
        
        .author-info {
          margin-left: $spacing-md;
          
          .author-name {
            font-size: $font-size-lg;
            font-weight: bold;
            color: $text-primary;
            margin-bottom: 4px;
          }
        }
      }
    }
    
    .related-notes {
      .card-header {
        h3 {
          margin: 0;
          font-size: $font-size-lg;
        }
      }
      
      .related-note-item {
        display: flex;
        padding: $spacing-sm 0;
        cursor: pointer;
        
        &:hover {
          .note-title {
            color: $primary-color;
          }
        }
        
        .note-cover {
          width: 80px;
          height: 60px;
          margin-right: $spacing-sm;
          
          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: $border-radius-sm;
          }
        }
        
        .note-info {
          flex: 1;
          min-width: 0;
          
          .note-title {
            font-size: $font-size-base;
            color: $text-primary;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          
          .note-meta {
            font-size: $font-size-sm;
            color: $text-secondary;
            
            span {
              margin-right: $spacing-md;
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .note-detail-page {
    .page-container {
      grid-template-columns: 1fr;
    }
    
    .note-content {
      .main-content {
        .note-header {
          .note-title {
            font-size: 24px;
          }
          
          .note-meta {
            flex-direction: column;
            align-items: flex-start;
            
            .meta-row {
              margin-top: $spacing-sm;
            }
          }
        }
      }
    }
  }
}
</style> 