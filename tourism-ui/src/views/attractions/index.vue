<template>
  <div class="attractions-page">
    <!-- 使用HomeBanner组件 -->
    <HomeBanner
      v-model="searchQuery"
      @search="handleSearch"
      @banner-click="handleBannerClick"
      @tag-click="handleTagClick"
    />
    
    <!-- 内容区域 -->
    <div class="page-container">
      <!-- 筛选器 -->
      <div class="filter-section container">
        <!-- 分类选择 -->
        <div class="category-cards">
          <div
            v-for="category in categories"
            :key="category.id"
            class="category-card"
            :class="{ active: filters.category_id === category.id }"
            @click="handleCategoryChange(category.id)"
          >
            <div class="card-icon">
              <el-icon>
                <component :is="getCategoryIcon(category.name)" />
              </el-icon>
            </div>
            <h3 class="card-title">{{ category.name }}</h3>
            <p class="card-desc">{{ category.description }}</p>
          </div>
        </div>
        
        <div class="filter-group">
          <span class="filter-label">排序：</span>
          <div class="filter-options">
            <el-radio-group v-model="filters.order_by" @change="handleFilterChange" size="large">
              <el-radio-button label="created_at">
                <el-icon><Sort /></el-icon> 默认
              </el-radio-button>
              <el-radio-button label="views">
                <el-icon><View /></el-icon> 热门
              </el-radio-button>
              <el-radio-button label="rating">
                <el-icon><Star /></el-icon> 好评
              </el-radio-button>
            </el-radio-group>
          </div>
        </div>
        
        <div class="filter-tags">
          <el-checkbox v-model="filters.is_recommended" @change="handleFilterChange">
            <el-tag type="success" effect="plain">
              <el-icon><Trophy /></el-icon> 推荐景点
            </el-tag>
          </el-checkbox>
          <el-checkbox v-model="filters.is_hot" @change="handleFilterChange">
            <el-tag type="danger" effect="plain">
              <el-icon><Histogram /></el-icon> 热门景点
            </el-tag>
          </el-checkbox>
        </div>
      </div>
      
      <!-- 景点列表 -->
      <div class="attractions-list container">
        <el-empty v-if="attractions.length === 0" description="暂无符合条件的景点" />
        
        <el-row :gutter="24" v-else>
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in attractions" :key="item.id">
            <div class="attraction-card" @click="goToDetail(item.id)">
              <div class="card-image">
                <el-image 
                  :src="getImageUrl(item.cover_image)" 
                  :alt="item.name"
                  fit="cover"
                  loading="lazy"
                >
                  <template #placeholder>
                    <div class="image-placeholder">
                      <el-icon><Picture /></el-icon>
                    </div>
                  </template>
                </el-image>
                <div class="card-tags" v-if="item.is_hot || item.is_recommended">
                  <el-tag class="tag hot" v-if="item.is_hot" type="danger" effect="dark">
                    <el-icon><Histogram /></el-icon> 热门
                  </el-tag>
                  <el-tag class="tag recommend" v-if="item.is_recommended" type="success" effect="dark">
                    <el-icon><Trophy /></el-icon> 推荐
                  </el-tag>
                </div>
              </div>
              <div class="card-content">
                <h3 class="card-title ellipsis">{{ item.name }}</h3>
                <p class="card-location ellipsis">
                  <el-icon><Location /></el-icon>
                  {{ item.address }}
                </p>
                <div class="card-footer">
                  <div class="price-rating">
                    <span class="price">¥{{ getPrice(item.ticket_info) }}起</span>
                    <div class="view-count">
                      <el-icon><View /></el-icon>
                      {{ item.view_count || 0 }}
                    </div>
                  </div>
                  <el-button type="primary" text>
                    查看详情 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <!-- 分页器 -->
        <div class="pagination-container">
          <el-pagination
            background
            :current-page="pagination.page"
            :page-size="pagination.per_page"
            :page-sizes="[12, 24, 36, 48]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            :pager-count="7"
            prev-text="上一页"
            next-text="下一页"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          >
            <template #total>
              共 <span class="total-number">{{ pagination.total }}</span> 条
            </template>
          </el-pagination>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Location, 
  Picture,
  View,
  Star,
  Sort,
  Trophy,
  Histogram,
  ArrowRight,
  Grid,
  Sunny,
  House,
  Place,
  Ship,
  SwitchButton
} from '@element-plus/icons-vue'
import HomeBanner from '@/components/HomeBanner.vue'
import { getAttractions, getAttractionCategories } from '@/api/attraction'
import type { Category } from '@/types/category'
import type { Attraction } from '@/types/attraction'

const router = useRouter()

// 静态资源基础URL
const staticBaseUrl = import.meta.env.VITE_STATIC_ASSETS_URL

// 加载状态
const loading = ref(false)

// 搜索查询
const searchQuery = ref('')

// 分类数据
const categories = ref<Category[]>([])

// 景点列表
const attractions = ref<Attraction[]>([])

// 筛选条件
const filters = reactive({
  category_id: 0,
  is_hot: false,
  is_recommended: false,
  order_by: 'created_at',
  order: 'desc' as 'asc' | 'desc'
})

// 分页信息
const pagination = reactive({
  page: 1,
  per_page: 12,
  total: 0
})

// 获取分类数据
const fetchCategories = async () => {
  try {
    const response = await getAttractionCategories()
    if (response.success) {
      categories.value = response.data
        .filter(category => category.type === 1)
        .sort((a, b) => a.sort_order - b.sort_order)
    }
  } catch (error) {
    console.error('Failed to fetch categories:', error)
    ElMessage.error('获取分类数据失败')
  }
}

// 加载景点数据
const loadAttractions = async () => {
  loading.value = true
  try {
    const response = await getAttractions({
      page: pagination.page,
      per_page: pagination.per_page,
      ...filters,
      keyword: searchQuery.value
    })
    
    if (response.code === 200) {
      attractions.value = response.data.items
      pagination.total = response.data.pagination.total
    } else {
      ElMessage.error(response.message || '加载景点数据失败')
    }
  } catch (error) {
    console.error('Failed to load attractions:', error)
    ElMessage.error('加载景点数据失败')
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  pagination.page = 1
  loadAttractions()
}

// 处理轮播图点击
const handleBannerClick = (url: string) => {
  if (url.startsWith('http')) {
    window.open(url, '_blank')
  } else {
    router.push(url)
  }
}

// 处理标签点击
const handleTagClick = (tag: string) => {
  searchQuery.value = tag
  handleSearch()
}

// 跳转到详情页
const goToDetail = (id: number) => {
  router.push(`/attractions/${id}`)
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pagination.per_page = size
  loadAttractions()
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadAttractions()
}

// 处理筛选条件变化
const handleFilterChange = () => {
  pagination.page = 1
  loadAttractions()
}

// 获取分类图标
const getCategoryIcon = (name: string) => {
  // 根据分类名称的特征来选择合适的图标
  if (name.includes('自然') || name.includes('风光')) {
    return 'Sunny'
  } else if (name.includes('历史') || name.includes('古迹') || name.includes('文化')) {
    return 'House'
  } else if (name.includes('主题') || name.includes('乐园')) {
    return 'Place'
  } else if (name.includes('海') || name.includes('海洋')) {
    return 'Ship'
  } else if (name.includes('温泉') || name.includes('度假')) {
    return 'SwitchButton'
  }
  return 'Place'
}

// 获取分类类型
const getCategoryType = (name: string) => {
  const typeMap: Record<string, string> = {
    '自然景观': 'nature',
    '文化古迹': 'culture',
    '主题乐园': 'adventure',
    '海滨度假': 'leisure'
  }
  return typeMap[name] || 'default'
}

// 处理分类变化
const handleCategoryChange = (categoryId: number) => {
  filters.category_id = categoryId
  handleFilterChange()
}

// 处理图片URL
const getImageUrl = (path: string) => {
  if (!path) return '/placeholder-image.jpg'
  if (path.startsWith('http')) return path
  return `${staticBaseUrl}/${path}`
}

// 处理价格信息
const getPrice = (ticketInfo: string) => {
  if (!ticketInfo) return '免费'
  const match = ticketInfo.match(/价格:\s*(\d+)/)
  return match ? match[1] : '免费'
}

// 处理描述文本
const formatDescription = (text: string) => {
  if (!text) return ''
  // 移除HTML标签
  const plainText = text.replace(/<[^>]+>/g, '')
  // 限制长度为50个字符
  return plainText.length > 50 ? plainText.slice(0, 50) + '...' : plainText
}

// 初始化
onMounted(() => {
  fetchCategories()
  loadAttractions()
})
</script>

<style lang="scss" scoped>
.page-container {
  padding: 24px 0 48px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 64px);
}

// 筛选区域
.filter-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

  .filter-group {
    display: flex;
    align-items: flex-start;
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    .filter-label {
      font-size: 15px;
      color: #606266;
      margin-right: 24px;
      min-width: 56px;
      padding-top: 8px;
    }

    .filter-options {
      flex: 1;

      :deep(.el-radio) {
        margin-right: 16px;
        margin-bottom: 12px;
        
        .el-tag {
          margin-right: 0;
          cursor: pointer;
          transition: all 0.3s;
          
          &:hover {
            transform: translateY(-2px);
          }
        }
        
        &.is-checked {
          .el-tag {
            transform: translateY(-2px);
          }
        }
      }
      
      .all-tag {
        min-width: 60px;
        text-align: center;
      }
    }
  }

  .filter-tags {
    display: flex;
    align-items: center;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;

    :deep(.el-checkbox) {
      margin-right: 24px;
      
      .el-tag {
        cursor: pointer;
        transition: all 0.3s;
        
        .el-icon {
          margin-right: 4px;
        }
        
        &:hover {
          transform: translateY(-2px);
        }
      }
    }
  }
}

// 分类卡片样式
.category-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
  
  .category-card {
    background: #fff;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
      border-color: var(--el-color-primary-light-5);
      
      .card-icon {
        background: var(--el-color-primary-light-8);
        color: var(--el-color-primary);
      }
    }
    
    &.active {
      background: var(--el-color-primary-light-9);
      border-color: var(--el-color-primary);
      
      .card-icon {
        background: var(--el-color-primary);
        color: #fff;
      }
      
      .card-title {
        color: var(--el-color-primary);
      }
    }
    
    .card-icon {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: #f5f7fa;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 16px;
      transition: all 0.3s ease;
      
      .el-icon {
        font-size: 24px;
      }
    }
    
    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 8px;
      transition: color 0.3s;
    }
    
    .card-desc {
      font-size: 13px;
      color: #909399;
      margin: 0;
      line-height: 1.4;
    }
  }
}

// 景点卡片
.attractions-list {
  .attraction-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    margin-bottom: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    border: 1px solid #ebeef5;
    
    &:hover {
      transform: translateY(-6px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
      
      .el-image {
        transform: scale(1.05);
      }
      
      .card-title {
        color: var(--el-color-primary);
      }
    }
    
    .card-image {
      position: relative;
      height: 200px;
      overflow: hidden;
      
      .el-image {
        width: 100%;
        height: 100%;
        transition: transform 0.6s ease;
      }
      
      .image-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f5f7fa;
        
        .el-icon {
          font-size: 48px;
          color: #909399;
        }
      }
      
      .card-tags {
        position: absolute;
        top: 12px;
        right: 12px;
        display: flex;
        gap: 8px;
        
        .tag {
          padding: 0 12px;
          height: 28px;
          line-height: 28px;
          border: none;
          
          .el-icon {
            margin-right: 4px;
          }
        }
      }
    }
    
    .card-content {
      padding: 20px;
      display: flex;
      flex-direction: column;
      flex: 1;
      
      .card-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 12px;
        color: #303133;
        transition: color 0.3s;
      }
      
      .card-location {
        display: flex;
        align-items: center;
        font-size: 14px;
        color: #909399;
        margin-bottom: 16px;
        
        .el-icon {
          margin-right: 4px;
          font-size: 16px;
        }
      }
      
      .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-top: auto;
        
        .price-rating {
          .price {
            font-size: 20px;
            color: #f56c6c;
            font-weight: 600;
            margin-bottom: 8px;
            display: block;
          }
          
          .view-count {
            display: flex;
            align-items: center;
            color: #909399;
            font-size: 14px;
            
            .el-icon {
              margin-right: 4px;
            }
          }
        }
      }
    }
  }
  
  .pagination-container {
    margin-top: 32px;
    display: flex;
    justify-content: center;
    
    :deep(.el-pagination) {
      .el-pagination__total {
        margin-right: 16px;
      }
      
      .total-number {
        color: #1abc9c;
        font-weight: 600;
        margin: 0 4px;
      }
      
      .el-pagination__sizes {
        margin-right: 16px;
      }
      
      .el-pager li {
        &:not(.is-disabled) {
          &.is-active {
            background-color: #1abc9c;
          }
          
          &:hover {
            color: #1abc9c;
          }
        }
      }
      
      .btn-prev, .btn-next {
        &:hover {
          color: #1abc9c;
        }
      }
      
      .el-pagination__jump {
        .el-pagination__editor {
          &:focus {
            border-color: #1abc9c;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .filter-section {
    padding: 16px;
    
    .filter-group {
      flex-direction: column;
      margin-bottom: 16px;
      
      .filter-label {
        margin-bottom: 12px;
      }
    }
  }
  
  .attractions-list {
    .attraction-card {
      .card-image {
        height: 160px;
      }
      
      .card-content {
        padding: 16px;
        
        .card-title {
          font-size: 16px;
        }
      }
    }
  }
  
  .category-cards {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
    
    .category-card {
      padding: 16px;
      
      .card-icon {
        width: 40px;
        height: 40px;
        margin-bottom: 12px;
        
        .el-icon {
          font-size: 20px;
        }
      }
      
      .card-title {
        font-size: 14px;
        margin-bottom: 4px;
      }
      
      .card-desc {
        font-size: 12px;
      }
    }
  }
}

.category-card {
  &.active {
    background: rgba(26, 188, 156, 0.1);
    border-color: #1abc9c;
    
    .card-icon {
      background: #1abc9c;
      color: #fff;
    }
    
    .card-title {
      color: #1abc9c;
    }
  }
  
  &:hover {
    border-color: #1abc9c;
    
    .card-icon {
      background: rgba(26, 188, 156, 0.1);
      color: #1abc9c;
    }
  }
}

.attraction-card {
  &:hover {
    .card-title {
      color: #1abc9c;
    }
  }
}
</style> 