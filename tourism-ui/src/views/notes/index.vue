<template>
  <div class="notes-page">
    <div class="page-header">
      <div class="header-bg" style="background-image: url('/notes-banner.jpg')">
        <div class="header-content container">
          <h1 class="page-title">旅行笔记</h1>
          <p class="page-desc">分享你的旅行故事，记录精彩瞬间</p>
          
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              placeholder="搜索笔记标题、内容..."
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
    </div>
    
    <div class="page-container container">
      <!-- 游记顶部筛选部分 -->
      <div class="notes-filter">
        <div class="filter-item search-box">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索游记标题"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #suffix>
              <el-icon class="search-icon" @click="handleSearch">
                <Search />
              </el-icon>
            </template>
          </el-input>
        </div>
        
        <div class="filter-item">
          <el-select
            v-model="filters.destination"
            placeholder="目的地筛选"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="item in popularLocations"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </div>
        
        <div class="filter-item">
          <el-select
            v-model="filters.sort"
            placeholder="排序方式"
            @change="handleFilterChange"
          >
            <el-option label="最新发布" value="newest" />
            <el-option label="最热门" value="hottest" />
            <el-option label="最多浏览" value="most_viewed" />
            <el-option label="最多点赞" value="most_liked" />
            <el-option label="最多收藏" value="most_collected" />
          </el-select>
        </div>
      </div>
      
      <!-- 笔记列表 -->
      <div class="notes-list" v-loading="loading">
        <template v-if="notesList.length > 0">
          <div class="notes-grid">
            <el-card 
              v-for="note in notesList" 
              :key="note.id" 
              class="note-card"
              @click="goToDetail(note.id)"
            >
              <div class="card-cover">
                <el-image 
                  :src="note.cover_image" 
                  :alt="note.title"
                  fit="cover"
                />
                <div class="card-location" v-if="note.location">
                  <el-icon><Location /></el-icon>
                  <span>{{ note.location }}</span>
                </div>
              </div>
              
              <div class="card-content">
                <h3 class="note-title">{{ note.title }}</h3>
                
                <div class="travel-info" v-if="note.trip_days || note.trip_cost">
                  <span v-if="note.trip_days" class="info-item">
                    <el-icon><Calendar /></el-icon> {{ note.trip_days }}天
                  </span>
                  <span v-if="note.trip_cost" class="info-item">
                    <el-icon><Money /></el-icon> ¥{{ note.trip_cost }}
                  </span>
                </div>
                
                <p class="note-description">{{ note.description || '暂无描述' }}</p>
                
                <div class="note-footer">
                  <div class="author-info">
                    <el-avatar :size="24" :src="note.user_avatar"></el-avatar>
                    <span class="author-name">{{ note.user_name }}</span>
                  </div>
                  
                  <div class="note-stats">
                    <span class="stat-item">
                      <el-icon><View /></el-icon> {{ formatNumber(note.views) }}
                    </span>
                    <span class="stat-item">
                      <el-icon><Star /></el-icon> {{ formatNumber(note.collections) }}
                    </span>
                    <span class="stat-item">
                      <el-icon><ChatLineRound /></el-icon> {{ formatNumber(note.comments) }}
                    </span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.per_page"
              :page-sizes="[12, 24, 36, 48]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="pagination.total"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </template>
        
        <el-empty v-else description="暂无游记" />
      </div>
      
      <!-- 写笔记按钮 -->
      <div class="floating-button" v-if="userStore.isLoggedIn">
        <el-button type="primary" size="large" circle @click="goToWrite">
          <el-icon><Edit /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Location, Calendar, Money, View, Star, ChatLineRound, Edit } from '@element-plus/icons-vue'
import { getNotes } from '@/api/note'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const searchQuery = ref('')
const loading = ref(false)
const notesList = ref([])

// 热门目的地
const popularLocations = ref(['北京', '上海', '广州', '深圳', '杭州', '成都', '重庆', '西安', '三亚', '厦门'])

// 分页信息
const pagination = reactive({
  page: 1,
  per_page: 12,
  total: 0,
  total_pages: 0,
  has_next: false,
  has_prev: false
})

// 筛选条件
const filters = reactive({
  keyword: '',
  destination: '',
  sort: 'newest',
})

// 加载笔记列表
const loadNotes = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      keyword: filters.keyword,
      destination: filters.destination,
      sort: filters.sort
    }
    
    const res = await getNotes(params)
    
    if (res.code === 0 || res.code === 200) {
      notesList.value = res.data.items || []
      
      // 更新分页信息
      pagination.total = res.data.pagination.total
      pagination.page = res.data.pagination.page
      pagination.per_page = res.data.pagination.per_page
      pagination.total_pages = res.data.pagination.total_pages
      pagination.has_next = res.data.pagination.has_next
      pagination.has_prev = res.data.pagination.has_prev
      
      // 更新目的地列表
      if (res.data.filters && res.data.filters.destinations) {
        popularLocations.value = res.data.filters.destinations
      }
    } else {
      ElMessage.error(res.message || '获取游记列表失败')
    }
  } catch (error) {
    console.error('获取游记列表失败:', error)
    // 检查错误对象是否包含code为0的情况（被拦截器拒绝但实际成功的请求）
    if (error && typeof error === 'object' && 'code' in error && error.code === 0 && error.data) {
      notesList.value = error.data.items || []
      
      // 更新分页信息
      if (error.data.pagination) {
        pagination.total = error.data.pagination.total
        pagination.page = error.data.pagination.page
        pagination.per_page = error.data.pagination.per_page
        pagination.total_pages = error.data.pagination.total_pages
        pagination.has_next = error.data.pagination.has_next
        pagination.has_prev = error.data.pagination.has_prev
      }
      
      // 更新目的地列表
      if (error.data.filters && error.data.filters.destinations) {
        popularLocations.value = error.data.filters.destinations
      }
    } else {
      ElMessage.error('获取游记列表失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  pagination.page = 1
  loadNotes()
}

// 处理每页显示数量变化
const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  loadNotes()
}

// 处理页码变化
const handleCurrentChange = (page) => {
  pagination.page = page
  loadNotes()
}

// 跳转到笔记详情
const goToDetail = (id) => {
  router.push(`/note/${id}`)
}

// 跳转到写笔记页面
const goToWrite = () => {
  router.push('/notes/write')
}

// 处理过滤条件变化
const handleFilterChange = () => {
  pagination.page = 1
  loadNotes()
}

// 格式化数字
const formatNumber = (num) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num
}

onMounted(() => {
  loadNotes()
})
</script>

<style lang="scss" scoped>
@use "@/styles/variables" as *;

.notes-page {
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
  
  .notes-filter {
    margin-bottom: $spacing-lg;
    
    .filter-item {
      margin-bottom: $spacing-md;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
  
  .notes-list {
    .notes-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    
    .note-card {
      cursor: pointer;
      transition: transform 0.3s, box-shadow 0.3s;
      overflow: hidden;
      height: 100%;
      
      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
      }
      
      .card-cover {
        position: relative;
        height: 180px;
        overflow: hidden;
        
        .el-image {
          width: 100%;
          height: 100%;
        }
        
        .card-location {
          position: absolute;
          bottom: 10px;
          left: 10px;
          background-color: rgba(0, 0, 0, 0.6);
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
      
      .card-content {
        padding: 15px;
        
        .note-title {
          font-size: 16px;
          line-height: 1.4;
          margin: 0 0 10px;
          max-height: 44px;
          overflow: hidden;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }
        
        .travel-info {
          margin-bottom: 10px;
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          
          .info-item {
            font-size: 12px;
            color: #606266;
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
        
        .note-description {
          margin-bottom: 15px;
          font-size: 14px;
          color: #606266;
        }
        
        .note-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          
          .author-info {
            display: flex;
            align-items: center;
            gap: 8px;
            
            .author-name {
              font-size: 13px;
              color: #606266;
            }
          }
          
          .note-stats {
            display: flex;
            gap: 10px;
            
            .stat-item {
              display: flex;
              align-items: center;
              gap: 4px;
              font-size: 12px;
              color: #909399;
            }
          }
        }
      }
    }
    
    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 30px;
    }
  }
  
  .floating-button {
    position: fixed;
    right: $spacing-xl;
    bottom: $spacing-xl;
    z-index: 100;
    
    .el-button {
      width: 60px;
      height: 60px;
      box-shadow: $box-shadow-lg;
      
      .el-icon {
        font-size: 24px;
      }
    }
  }
}

@media (max-width: 768px) {
  .notes-page {
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
    
    .notes-filter {
      flex-direction: column;
      align-items: flex-start;
      
      .filter-item {
        margin-bottom: $spacing-xs;
      }
    }
    
    .notes-grid {
      grid-template-columns: 1fr !important;
    }
  }
}
</style> 