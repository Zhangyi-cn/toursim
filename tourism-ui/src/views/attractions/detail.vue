<template>
  <div class="attraction-detail-page">
    <div class="container" v-loading="loading">
      <!-- 景点未找到 -->
      <el-empty v-if="!loading && !attraction.id" description="未找到该景点" />
      
      <!-- 景点详情 -->
      <template v-if="attraction.id">
        <div class="attraction-header">
          <div class="attraction-cover">
            <img :src="getImageUrl(attraction.cover_image)" :alt="attraction.name" class="cover-image">
            <div class="attraction-tags" v-if="attraction.is_hot || attraction.is_recommended">
              <el-tag type="danger" v-if="attraction.is_hot">热门</el-tag>
              <el-tag type="success" v-if="attraction.is_recommended">推荐</el-tag>
            </div>
          </div>
          
          <div class="attraction-title-section">
            <div class="title-row">
              <h1 class="attraction-title">{{ attraction.name }}</h1>
              <div class="category-tag">
                <el-tag>{{ attraction.category_name }}</el-tag>
              </div>
            </div>
            <div class="attraction-meta">
              <div class="meta-stats">
                <el-tag type="info" class="stat-tag">
                  <el-icon><View /></el-icon>
                  {{ attraction.view_count || 0 }} 浏览
                </el-tag>
                <el-tag type="info" class="stat-tag">
                  <el-icon><Star /></el-icon>
                  {{ attraction.like_count || 0 }} 点赞
                </el-tag>
                <el-tag type="info" class="stat-tag">
                  <el-icon><Collection /></el-icon>
                  {{ attraction.collection_count || 0 }} 收藏
                </el-tag>
              </div>
              <div class="meta-location">
                <el-icon><Location /></el-icon>
                {{ attraction.address }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="attraction-content">
          <el-row :gutter="30">
            <!-- 左侧景点详情 -->
            <el-col :xs="24" :md="16">
              <!-- 基本信息卡片 -->
              <el-card class="content-card">
                <template #header>
                  <div class="card-header">
                    <h2>基本信息</h2>
                  </div>
                </template>
                
                <div class="info-list">
                  <div class="info-item">
                    <span class="label">开放时间：</span>
                    <span class="value">{{ attraction.open_time || '暂无信息' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">门票信息：</span>
                    <span class="value price">{{ attraction.ticket_info || '免费' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">所属分类：</span>
                    <span class="value">{{ attraction.category?.name }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">更新时间：</span>
                    <span class="value">{{ formatDate(attraction.updated_at) }}</span>
                  </div>
                </div>
              </el-card>

              <!-- 景点介绍 -->
              <el-card class="content-card" v-if="attraction.description">
                <template #header>
                  <div class="card-header">
                    <h2>景点介绍</h2>
                  </div>
                </template>
                
                <div class="attraction-description rich-text" v-html="attraction.description"></div>
              </el-card>
              
              <!-- 景点图片 -->
              <el-card class="content-card" v-if="attraction.images?.length">
                <template #header>
                  <div class="card-header">
                    <h2>景点图片</h2>
                  </div>
                </template>
                
                <div class="attraction-images">
                  <el-image
                    v-for="(img, index) in attraction.images"
                    :key="index"
                    :src="getImageUrl(img)"
                    :preview-src-list="attraction.images.map(getImageUrl)"
                    fit="cover"
                    class="gallery-image"
                  />
                </div>
              </el-card>
              
              <!-- 游玩攻略 -->
              <el-card class="content-card" v-if="attraction.tips">
                <template #header>
                  <div class="card-header">
                    <h2>游玩攻略</h2>
                  </div>
                </template>
                
                <div class="attraction-tips rich-text" v-html="attraction.tips"></div>
              </el-card>
              
              <!-- 交通信息 -->
              <el-card class="content-card" v-if="attraction.traffic_info">
                <template #header>
                  <div class="card-header">
                    <h2>交通信息</h2>
                  </div>
                </template>
                
                <div class="attraction-traffic rich-text" v-html="attraction.traffic_info"></div>
              </el-card>

              <!-- 地理位置 -->
              <el-card class="content-card">
                <template #header>
                  <div class="card-header">
                    <h2>地理位置</h2>
                  </div>
                </template>
                
                <div id="map-container" class="map-container"></div>
              </el-card>
              
              <!-- 评论区 -->
              <el-card class="content-card">
                <template #header>
                  <div class="card-header">
                    <h2>用户评论</h2>
                  </div>
                </template>
                
                <CommentList :target-id="attractionId" title="评论" />
              </el-card>
            </el-col>
            
            <!-- 右侧信息 -->
            <el-col :xs="24" :md="8">
              <div class="sidebar-content">
                <el-card class="action-card">
                  <div class="action-buttons">
                    <div class="button-wrapper">
                      <el-button 
                        :type="attraction.is_liked ? 'danger' : 'default'"
                        @click="handleLike" 
                        :loading="likeLoading"
                        size="large"
                      >
                        <el-icon>
                          <component :is="attraction.is_liked ? 'StarFilled' : 'Star'" />
                        </el-icon>
                        <span>{{ attraction.is_liked ? '取消点赞' : '点赞景点' }}</span>
                      </el-button>
                    </div>
                    <div class="button-wrapper">
                      <el-button 
                        :type="attraction.is_collected ? 'warning' : 'default'"
                        @click="handleCollect"
                        :loading="collectLoading"
                        size="large"
                      >
                        <el-icon><component :is="attraction.is_collected ? 'Collection' : 'CollectionTag'" /></el-icon>
                        <span>{{ attraction.is_collected ? '取消收藏' : '收藏景点' }}</span>
                      </el-button>
                    </div>
                    <div class="button-wrapper">
                      <!-- <el-button 
                        type="success" 
                        @click="goToTicket" 
                        v-if="attraction.ticket_info"
                        size="large"
                      >
                        <el-icon><Ticket /></el-icon>
                        <span>预订门票</span>
                      </el-button> -->
                    </div>
                  </div>
                </el-card>

                <!-- 季节推荐 -->
                <el-card class="seasons-card" v-if="attraction.seasons?.length">
                  <template #header>
                    <div class="card-header">
                      <h3>最佳游玩季节</h3>
                    </div>
                  </template>
                  
                  <div class="seasons-list">
                    <el-tag
                      v-for="season in attraction.seasons"
                      :key="season"
                      class="season-tag"
                    >
                      {{ season }}
                    </el-tag>
                  </div>
                </el-card>
              </div>
            </el-col>
          </el-row>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location, Star, View, Ticket, Collection, StarFilled } from '@element-plus/icons-vue'
import { 
  getAttractionDetail, 
  likeAttraction, 
  unlikeAttraction, 
  collectAttraction, 
  uncollectAttraction
} from '@/api/attraction'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'
import type { Attraction } from '@/types/attraction'
import CommentList from '@/components/comment/CommentList.vue'

const staticBaseUrl = import.meta.env.VITE_STATIC_ASSETS_URL
const MAP_KEY = 'f62f6e372fa7386c2c9f6cada41260ff'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 初始化景点数据时设置默认值
const attraction = ref<Attraction>({
  id: 0,
  name: '',
  description: '',
  cover_image: '',
  address: '',
  longitude: '',
  latitude: '',
  category_id: 0,
  open_time: '',
  ticket_info: '',
  contact: '',
  tips: '',
  view_count: 0,
  like_count: 0,
  collection_count: 0,
  comment_count: 0,
  is_hot: false,
  is_recommended: false,
  is_liked: false,
  is_collected: false,
  created_at: '',
  updated_at: ''
} as Attraction)
const loading = ref(false)
const likeLoading = ref(false)
const collectLoading = ref(false)
let map = null

// 景点ID
const attractionId = computed(() => route.params.id)

// 获取景点详情
const fetchAttractionDetail = async () => {
  try {
    loading.value = true
    const id = parseInt(route.params.id as string)
    if (isNaN(id)) {
      ElMessage.error('无效的景点ID')
      return
    }
    
    console.log('用户登录状态:', userStore.isLoggedIn)
    console.log('用户Token:', localStorage.getItem('token'))
    
    const response = await getAttractionDetail(id)
    console.log('后端返回的原始数据:', response)
    
    if (response.data) {
      // 设置景点数据，包括点赞和收藏状态
      attraction.value = response.data
      console.log('景点数据:', attraction.value)
      console.log('点赞状态:', attraction.value.is_liked)
      console.log('收藏状态:', attraction.value.is_collected)

      // 初始化地图
      initMap()
    }
  } catch (error: any) {
    console.error('获取景点详情失败:', error)
    ElMessage.error(error.message || '获取景点详情失败')
  } finally {
    loading.value = false
  }
}

// 初始化地图
const initMap = () => {
  if (!attraction.value.latitude || !attraction.value.longitude) return
  
  // 确保高德地图脚本已加载
  if (!window.AMap) {
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${MAP_KEY}`
    script.async = true
    script.onload = () => {
      createMap()
    }
    document.head.appendChild(script)
  } else {
    createMap()
  }
}

// 创建地图实例
const createMap = () => {
  const center = [attraction.value.longitude, attraction.value.latitude]
  map = new window.AMap.Map('map-container', {
    zoom: 13,
    center
  })
  
  // 添加标记
  new window.AMap.Marker({
    position: center,
    map: map
  })
}

// 处理点赞
const handleLike = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    likeLoading.value = true
    console.log('当前点赞状态:', attraction.value.is_liked)
    const api = attraction.value.is_liked ? unlikeAttraction : likeAttraction
    console.log('调用API:', attraction.value.is_liked ? 'unlikeAttraction' : 'likeAttraction')
    
    const response = await api(attraction.value.id)
    
    // 更新状态
    attraction.value.is_liked = !attraction.value.is_liked
    // 使用后端返回的点赞数
    if (response.data?.like_count !== undefined) {
      attraction.value.like_count = response.data.like_count
    }
    
    console.log('操作后点赞状态:', attraction.value.is_liked)
    console.log('操作后点赞数:', attraction.value.like_count)
    
    ElMessage.success(response.msg)
  } catch (error: any) {
    console.error('点赞操作失败:', error)
    ElMessage.error(error.message || '操作失败，请稍后重试')
  } finally {
    likeLoading.value = false
  }
}

// 处理收藏
const handleCollect = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    collectLoading.value = true
    const api = attraction.value.is_collected ? uncollectAttraction : collectAttraction
    const response = await api(attraction.value.id)
    
    // 更新状态
    attraction.value.is_collected = !attraction.value.is_collected
    attraction.value.collection_count += attraction.value.is_collected ? 1 : -1
    
    ElMessage.success(response.msg)
  } catch (error: any) {
    console.error('收藏操作失败:', error)
    ElMessage.error(error.message || '操作失败，请稍后重试')
  } finally {
    collectLoading.value = false
  }
}

// 跳转到门票预订
const goToTicket = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再预订门票')
    return
  }
  router.push(`/order/create?attractionId=${route.params.id}`)
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取图片URL
const getImageUrl = (path: string) => {
  if (!path) return '/placeholder-attraction.jpg'
  return path.startsWith('http') ? path : `${staticBaseUrl}/${path}`
}

onMounted(() => {
  fetchAttractionDetail()
})
</script>

<style lang="scss" scoped>
@use "@/styles/variables" as *;

.attraction-detail-page {
  padding: $spacing-lg 0 $spacing-xxl;
}

.attraction-header {
  margin-bottom: $spacing-lg;
  
  .attraction-cover {
    position: relative;
    height: 400px;
    border-radius: $border-radius-lg;
    overflow: hidden;
    margin-bottom: $spacing-md;
    
    .cover-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .attraction-tags {
      position: absolute;
      top: $spacing-md;
      right: $spacing-md;
      display: flex;
      gap: $spacing-xs;
    }
  }
  
  .attraction-title-section {
    .title-row {
      display: flex;
      align-items: center;
      gap: $spacing-md;
      margin-bottom: $spacing-sm;

      .attraction-title {
        font-size: 32px;
        font-weight: bold;
        margin: 0;
        color: $text-primary;
      }

      .category-tag {
        margin-left: $spacing-sm;
      }
    }
    
    .attraction-meta {
      display: flex;
      flex-direction: column;
      gap: $spacing-sm;
      
      .meta-stats {
        display: flex;
        gap: $spacing-md;
        
        .stat-tag {
          display: flex;
          align-items: center;
          padding: 6px 12px;
          border-radius: 20px;
          background-color: rgba(64, 158, 255, 0.1);
          border: none;
          color: $text-secondary;
          
          .el-icon {
            margin-right: 6px;
            font-size: 16px;
          }
        }
      }
      
      .meta-location {
        display: flex;
        align-items: center;
        color: $text-secondary;
        font-size: 14px;
        
        .el-icon {
          margin-right: $spacing-xs;
          color: $primary-color;
        }
      }
    }
  }
}

.attraction-content {
  .content-card {
    margin-bottom: $spacing-lg;
    
    .card-header {
      h2, h3 {
        font-size: $font-size-lg;
        font-weight: bold;
        margin: 0;
      }
    }
  }

  .info-list {
    .info-item {
      display: flex;
      margin-bottom: $spacing-sm;
      
      .label {
        width: 100px;
        color: $text-hint;
      }
      
      .value {
        flex: 1;
        color: $text-primary;
        
        &.price {
          color: $error-color;
          font-weight: bold;
        }
      }
    }
  }
  
  .rich-text {
    line-height: 1.8;
    color: $text-secondary;
    
    :deep(p) {
      margin-bottom: $spacing-md;
    }
    
    :deep(ul) {
      padding-left: $spacing-lg;
      margin-bottom: $spacing-md;
      
      li {
        margin-bottom: $spacing-xs;
      }
    }
  }
  
  .attraction-images {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: $spacing-md;
    
    .gallery-image {
      width: 100%;
      aspect-ratio: 1;
      border-radius: $border-radius-base;
      overflow: hidden;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }

  .map-container {
    height: 400px;
    border-radius: $border-radius-base;
    overflow: hidden;
  }
  
  .sidebar-content {
    position: sticky;
    top: $spacing-xl;
    
    .action-card {
      margin-bottom: $spacing-lg;
      
      :deep(.el-card__body) {
        padding: 20px;
      }
      
      .action-buttons {
        display: flex;
        flex-direction: column;
        gap: $spacing-sm;

        .button-wrapper {
          width: 100%;

          :deep(.el-button) {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;

            .el-icon {
              margin-right: 8px;
            }
          }
        }
      }
    }

    .seasons-card {
      .seasons-list {
        display: flex;
        flex-wrap: wrap;
        gap: $spacing-xs;
        
        .season-tag {
          margin-bottom: $spacing-xs;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .attraction-header {
    .attraction-cover {
      height: 200px;
    }
    
    .attraction-title-section {
      .title-row {
        flex-direction: column;
        align-items: flex-start;
        gap: $spacing-xs;
        
        .category-tag {
          margin-left: 0;
        }
      }
      
      .attraction-meta {
        .meta-stats {
          flex-wrap: wrap;
          gap: $spacing-sm;
        }
      }
    }
  }
  
  .sidebar-content {
    margin-top: $spacing-lg;
    position: static;
  }

  .map-container {
    height: 300px;
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-left: auto;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-info {
  display: flex;
  gap: 12px;
  margin-left: auto;
  
  .stat-tag {
    display: flex;
    align-items: center;
    gap: 4px;
    
    .el-icon {
      margin-right: 2px;
    }
  }
}
</style> 