<template>
  <div class="activities-page">
    <!-- 页面头部 -->
    <section class="page-header">
      <div class="header-bg" style="background-image: url('/activities-banner.jpg')">
        <div class="header-content container">
          <h1 class="page-title">参与精彩活动</h1>
          <p class="page-desc">丰富多彩的旅行活动等你来参加，结交志同道合的伙伴，创造难忘回忆</p>
          
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              placeholder="搜索活动名称、地点、描述..."
              class="search-input"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 内容区域 -->
    <div class="page-container container">
      <!-- 筛选器 -->
      <div class="filter-section">
        <el-card>
          <div class="filter-group">
            <div class="filter-label">状态：</div>
            <div class="filter-options">
              <el-radio-group v-model="filters.status" @change="handleSearch">
                <el-radio-button v-for="option in statusOptions" :key="option.value" :label="option.value">
                  {{ option.label }}
                </el-radio-button>
              </el-radio-group>
            </div>
          </div>
          
          <div class="filter-group">
            <div class="filter-label">排序：</div>
            <div class="filter-options">
              <el-select v-model="filters.sort" @change="handleSearch" placeholder="请选择排序方式">
                <el-option v-for="option in sortOptions" :key="option.value" :label="option.label" :value="option.value" />
              </el-select>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 活动列表 -->
      <div class="activities-list">
        <el-empty v-if="!loading && activities.length === 0" description="暂无符合条件的活动" />
        
        <el-skeleton :loading="loading" animated :count="3" :throttle="500">
          <template #template>
            <div class="skeleton-item">
              <el-skeleton-item variant="image" style="width: 100%; height: 200px;" />
              <div style="padding: 14px;">
                <el-skeleton-item variant="h3" style="width: 50%" />
                <div style="display: flex; align-items: center; margin: 8px 0">
                  <el-skeleton-item variant="text" style="margin-right: 16px; width: 30%" />
                  <el-skeleton-item variant="text" style="width: 30%" />
                </div>
                <el-skeleton-item variant="text" style="width: 80%" />
                <el-skeleton-item variant="text" style="width: 60%" />
              </div>
            </div>
          </template>
          
          <template #default>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :lg="8" v-for="item in activities" :key="item.id">
                <div class="activity-card" @click="goToDetail(item.id)">
                  <div class="card-image">
                    <img :src="item.cover_image || '/placeholder-activity.jpg'" :alt="item.title" class="image-cover">
                    <div class="activity-status" :class="getStatusClass(item.status)">{{ getStatusText(item.status) }}</div>
                  </div>
                  <div class="card-content">
                    <h3 class="card-title ellipsis">{{ item.title }}</h3>
                    <p class="activity-time">
                      <el-icon><Calendar /></el-icon>
                      {{ formatDate(item.start_time) }} - {{ formatDate(item.end_time) }}
                    </p>
                    <p class="activity-location ellipsis">
                      <el-icon><Location /></el-icon>
                      {{ item.location }}
                    </p>
                    <p class="activity-desc ellipsis-2">{{ item.description }}</p>
                    <div class="activity-footer">
                      <span class="participants">{{ item.current_participants }}/{{ item.max_participants || '不限' }} 人参与</span>
                      <el-button size="small" type="primary" round>查看详情</el-button>
                    </div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </template>
        </el-skeleton>
        
        <!-- 分页器 -->
        <div class="pagination-container" v-if="!loading && activities.length > 0">
          <el-pagination
            :current-page="pagination.page"
            :page-size="pagination.page_size"
            :page-sizes="[9, 18, 36, 48]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, Calendar, Location } from '@element-plus/icons-vue'
import { getActivities } from '@/api/activity'
import { Activity, ActivityStatus } from '@/types/activity'
import { ApiResponse, PaginatedData } from '@/types/common'
import { ACTIVITY_STATUS_MAP, ACTIVITY_STATUS_CLASS } from '@/constants/activity'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const activities = ref<Activity[]>([])
const loading = ref(false)

// 筛选条件
const filters = reactive({
  status: 'all' as ActivityStatus | 'all',
  sort: 'start_time'
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 9,
  total: 0
})

// 状态选项
const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '未开始', value: 'not_started' },
  { label: '进行中', value: 'in_progress' },
  { label: '已结束', value: 'ended' }
]

// 排序选项
const sortOptions = [
  { label: '开始时间优先', value: 'start_time' },
  { label: '参与人数优先', value: 'participants' },
  { label: '最新发布', value: 'created_at' }
]

// 加载活动数据
const loadActivities = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      q: searchQuery.value
    }
    
    // 添加筛选条件
    if (filters.status !== 'all') {
      params.status = filters.status
    }
    
    if (filters.sort) {
      params.sort = filters.sort
    }
    
    const res = await getActivities(params) as ApiResponse<PaginatedData<Activity>>
    if (res.code === 200) {
      activities.value = res.data.items || []
      pagination.total = res.data.total || 0
    } else {
      ElMessage.error({
        message: res.message || '获取活动列表失败',
        duration: 5000,
        showClose: true
      })
      activities.value = []
      pagination.total = 0
    }
  } catch (error) {
    console.error('获取活动列表失败:', error)
    ElMessage.error({
      message: error instanceof Error ? error.message : '获取活动列表失败，请稍后重试',
      duration: 5000,
      showClose: true
    })
    activities.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 获取活动状态样式类
const getStatusClass = (status: ActivityStatus) => {
  return ACTIVITY_STATUS_CLASS[status] || 'upcoming'
}

// 获取活动状态文本
const getStatusText = (status: ActivityStatus) => {
  return ACTIVITY_STATUS_MAP[status] || '未知状态'
}

// 处理搜索
const handleSearch = () => {
  pagination.page = 1 // 重置页码
  loadActivities()
}

// 处理每页显示数量变化
const handleSizeChange = (size) => {
  pagination.page_size = size
  pagination.page = 1
  loadActivities()
}

// 处理页码变化
const handleCurrentChange = (page) => {
  pagination.page = page
  loadActivities()
}

// 日期格式化
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

// 跳转到详情页
const goToDetail = (id) => {
  router.push(`/activity/${id}`)
}

// 初始加载
onMounted(() => {
  // 如果URL中有查询参数，则使用这些参数
  if (route.query.q) {
    searchQuery.value = route.query.q
  }
  
  if (route.query.status) {
    filters.status = route.query.status
  }
  
  loadActivities()
})
</script>

<style lang="scss" scoped>
@use "@/styles/variables" as *;

.activities-page {
  padding-bottom: $spacing-xxl;
}

// 页面头部
.page-header {
  height: 300px;
  margin-bottom: $spacing-xl;
  
  .header-bg {
    height: 100%;
    background-size: cover;
    background-position: center;
    position: relative;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(to bottom, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.3) 100%);
    }
  }
  
  .header-content {
    position: relative;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    
    .page-title {
      font-size: 36px;
      font-weight: bold;
      color: #fff;
      margin-bottom: $spacing-sm;
    }
    
    .page-desc {
      font-size: $font-size-lg;
      color: #fff;
      margin-bottom: $spacing-xl;
      max-width: 600px;
    }
    
    .search-box {
      width: 100%;
      max-width: 600px;
      display: flex;
      
      .search-input {
        flex: 1;
        margin-right: $spacing-sm;
        
        :deep(.el-input__inner) {
          height: 44px;
          border-radius: $border-radius-base;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
      }
      
      .el-button {
        height: 44px;
        border-radius: $border-radius-base;
        padding: 0 $spacing-lg;
      }
    }
  }
}

// 筛选区域
.filter-section {
  margin-bottom: $spacing-lg;
  
  .filter-group {
    display: flex;
    align-items: center;
    margin-bottom: $spacing-md;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .filter-label {
      font-weight: bold;
      margin-right: $spacing-md;
      min-width: 60px;
    }
    
    .filter-options {
      flex: 1;
    }
  }
}

// 活动列表
.activities-list {
  .skeleton-item {
    background: #fff;
    border-radius: $border-radius-base;
    overflow: hidden;
    box-shadow: $box-shadow-base;
    margin-bottom: $spacing-md;
  }
  
  .activity-card {
    background: #fff;
    border-radius: $border-radius-base;
    overflow: hidden;
    box-shadow: $box-shadow-base;
    margin-bottom: $spacing-md;
    cursor: pointer;
    transition: all 0.3s;
    height: 100%;
    display: flex;
    flex-direction: column;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: $box-shadow-hover;
      
      .image-cover {
        transform: scale(1.05);
      }
    }
    
    .card-image {
      position: relative;
      height: 200px;
      overflow: hidden;
      
      .image-cover {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s;
      }
      
      .activity-status {
        position: absolute;
        top: $spacing-sm;
        left: $spacing-sm;
        padding: 2px 10px;
        border-radius: 2px;
        font-size: $font-size-sm;
        color: #fff;
        
        &.upcoming {
          background-color: $info-color;
        }
        
        &.ongoing {
          background-color: $success-color;
        }
        
        &.ended {
          background-color: $text-hint;
        }
      }
    }
    
    .card-content {
      padding: $spacing-md;
      flex: 1;
      display: flex;
      flex-direction: column;
      
      .card-title {
        font-size: $font-size-lg;
        font-weight: bold;
        margin-bottom: $spacing-sm;
        color: $text-primary;
      }
      
      .activity-time, .activity-location {
        display: flex;
        align-items: center;
        margin-bottom: $spacing-sm;
        color: $text-secondary;
        
        .el-icon {
          margin-right: $spacing-xs;
        }
      }
      
      .activity-desc {
        font-size: $font-size-base;
        color: $text-secondary;
        margin-bottom: auto;
        padding-bottom: $spacing-md;
      }
      
      .activity-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: auto;
        
        .participants {
          font-size: $font-size-sm;
          color: $text-hint;
        }
      }
    }
  }
  
  .pagination-container {
    margin-top: $spacing-xl;
    display: flex;
    justify-content: center;
  }
}

// 工具类
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ellipsis-2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

@media (max-width: 768px) {
  .page-header {
    height: 200px;
    
    .header-content {
      .page-title {
        font-size: 28px;
      }
      
      .page-desc {
        font-size: $font-size-base;
      }
      
      .search-box {
        width: 90%;
      }
    }
  }
  
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
    
    .filter-label {
      margin-bottom: $spacing-xs;
    }
    
    .filter-options {
      width: 100%;
    }
  }
}
</style> 