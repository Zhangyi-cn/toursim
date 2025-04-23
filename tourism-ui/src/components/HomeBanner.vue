<template>
  <section class="banner-section">
    <!-- 轮播图 -->
    <el-carousel 
      height="100vh" 
      :interval="5000" 
      arrow="hover" 
      indicator-position="none"
      v-loading="loading"
    >
      <el-carousel-item v-for="banner in banners" :key="banner.id">
        <div class="banner-item" :style="{ backgroundImage: `url(${getImageUrl(banner.image_url)})` }">
          <div class="banner-overlay"></div>
          <div class="banner-content container">
            <h2 class="banner-title">{{ banner.title }}</h2>
            <p class="banner-desc">{{ banner.description }}</p>
            <el-button 
              v-if="banner.link_url" 
              type="primary" 
              class="banner-btn"
              @click="handleBannerClick(banner.link_url)"
            >
              了解更多
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </el-carousel-item>
    </el-carousel>
    
    <!-- 搜索框 -->
    <div class="search-container">
      <div class="search-box">
        <div class="search-form">
          <div class="form-row">
            <el-input
              v-model="searchValue"
              :placeholder="searchPlaceholder"
              class="form-item"
            >
              <template #prefix>
                <el-icon><Location /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" class="search-btn" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </div>
        </div>
        <div class="hot-destinations">
          <span class="label">热门目的地：</span>
          <div class="tag-list">
            <el-tag
              v-for="tag in hotDestinations"
              :key="tag"
              class="hot-tag"
              @click="handleTagClick(tag)"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { Location, Search, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getBanners } from '@/api/banner'
import { getNotes } from '@/api/note'
import type { Banner } from '@/types/banner'
import request from '@/utils/request'

// 获取路由器实例
const router = useRouter()

// 静态资源基础URL
const staticBaseUrl = import.meta.env.VITE_STATIC_ASSETS_URL

// Props定义
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  searchPlaceholder: {
    type: String,
    default: '输入目的地、景点或关键词'
  }
})

// 城市数据
const hotDestinations = ref<string[]>([
  '北京', '上海', '广州', '深圳', '杭州', '成都', '重庆', '西安', '三亚', '厦门'
])

const emit = defineEmits(['update:modelValue', 'search', 'banner-click', 'tag-click'])

// 加载状态
const loading = ref(false)

// 轮播图数据
const banners = ref<Banner[]>([])

// 搜索相关
const searchValue = ref(props.modelValue)

// 获取城市列表
const fetchDestinations = async () => {
  try {
    // 从系统区域接口获取城市列表
    const response = await request.get('/api/system/regions')
    
    if (response.code === 200 || response.code === 0) {
      // 提取所有城市名称
      const extractCityNames = (regions, cities = []) => {
        if (!regions) return cities;
        
        regions.forEach(region => {
          // 只收集省级和直辖市
          if (region.level <= 1) {
            cities.push(region.name);
          }
          // 递归处理下级城市
          if (region.children && region.children.length > 0) {
            extractCityNames(region.children, cities);
          }
        });
        
        return cities;
      };
      
      // 提取所有城市名称
      const allCities = extractCityNames(response.data);
      console.log('获取到城市列表:', allCities);
      
      // 如果城市数量超过10个，随机选择10个
      if (allCities.length > 10) {
        // 创建数组副本，避免修改原数组
        const shuffled = [...allCities]
        
        // 打乱数组
        for (let i = shuffled.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
        }
        
        // 取前10个
        hotDestinations.value = shuffled.slice(0, 10)
      } else {
        // 如果不超过10个，全部使用
        hotDestinations.value = allCities
      }
    }
  } catch (error) {
    console.error('获取目的地列表失败:', error)
    // 保留默认城市列表
  }
}

// 获取轮播图数据
const fetchBanners = async () => {
  loading.value = true
  try {
    const response = await getBanners()
    if (response.success && response.data.items) {
      banners.value = response.data.items
        .filter(banner => banner.is_active)
        .sort((a, b) => b.sort_order - a.sort_order)
    } else {
      console.error('Banner data format is incorrect:', response)
      ElMessage.error('获取轮播图数据格式错误')
    }
  } catch (error) {
    console.error('Failed to fetch banners:', error)
    ElMessage.error('获取轮播图数据失败')
  } finally {
    loading.value = false
  }
}

watch(() => props.modelValue, (newVal: string) => {
  searchValue.value = newVal
})

watch(searchValue, (newVal: string) => {
  emit('update:modelValue', newVal)
})

// 事件处理
const handleSearch = () => {
  if (!searchValue.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  // 使用路由器跳转到适当的页面，如城市、景点或活动列表页
  router.push({
    path: '/attractions',
    query: { keyword: searchValue.value }
  })
  
  emit('search', searchValue.value)
}

const handleBannerClick = (url: string) => {
  emit('banner-click', url)
}

const handleTagClick = (tag: string) => {
  searchValue.value = tag
  
  // 使用与搜索按钮相同的路由跳转
  router.push({
    path: '/attractions',
    query: { keyword: tag }
  })
  
  emit('tag-click', tag)
}

// 处理图片URL
const getImageUrl = (url: string) => {
  if (!url) return '';
  if (url.startsWith('http')) {
    return url;
  }
  // 确保静态资源基础URL和图片路径之间有斜杠
  const baseUrl = staticBaseUrl.endsWith('/') ? staticBaseUrl : `${staticBaseUrl}/`;
  return `${baseUrl}${url}`;
}

// 初始化
onMounted(() => {
  fetchBanners()
  fetchDestinations()
})
</script>

<style lang="scss" scoped>
.banner-section {
  position: relative;
  height: 100vh;
  
  .banner-item {
    height: 100%;
    background-size: cover;
    background-position: center;
    position: relative;
    
    .banner-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(
        to bottom,
        rgba(0, 0, 0, 0.1),
        rgba(0, 0, 0, 0.5)
      );
    }
    
    .banner-content {
      position: absolute;
      bottom: 15%;
      left: 50%;
      transform: translateX(-50%);
      color: #fff;
      text-align: center;
      width: 100%;
      max-width: 1000px;
      z-index: 1;
      padding: 0 20px;
      
      .banner-title {
        font-size: 48px;
        font-weight: 700;
        margin-bottom: 20px;
        text-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        opacity: 0;
        transform: translateY(30px);
        animation: fadeInUp 0.8s forwards;
        letter-spacing: 2px;
        line-height: 1.2;
        background: linear-gradient(180deg, #ffffff, rgba(255, 255, 255, 0.8));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;

        &::after {
          content: '';
          display: block;
          width: 60px;
          height: 3px;
          background: linear-gradient(90deg, #1abc9c, transparent);
          margin: 16px auto 0;
        }
      }
      
      .banner-desc {
        font-size: 20px;
        line-height: 1.6;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
        opacity: 0;
        transform: translateY(30px);
        animation: fadeInUp 0.8s 0.2s forwards;
        margin: 0 auto;
        max-width: 800px;
        font-weight: 300;
        margin-bottom: 32px;
        color: rgba(255, 255, 255, 0.95);
        letter-spacing: 1px;
      }

      .banner-btn {
        opacity: 0;
        transform: translateY(30px);
        animation: fadeInUp 0.8s 0.4s forwards;
        padding: 12px 36px;
        font-size: 18px;
        font-weight: 600;
        border-radius: 50px;
        background: linear-gradient(135deg, #1abc9c, #16a085);
        border: none;
        color: #fff;
        transition: all 0.4s ease;
        letter-spacing: 1px;
        text-transform: uppercase;
      }
    }
  }
  
  .search-container {
    position: absolute;
    top: 35%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 800px;
    z-index: 2;
    
    .search-box {
      background: rgba(255, 255, 255, 0.98);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 32px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
      
      .search-form {
        .form-row {
          display: flex;
          gap: 12px;
          margin-bottom: 20px;
          
          .form-item {
            flex: 1;
            
            :deep(.el-input__wrapper) {
              box-shadow: none !important;
              border: 1px solid #e0e0e0;
              border-radius: 8px;
              padding: 8px 16px;
              transition: all 0.3s;
              
              &:hover, &:focus-within {
                border-color: #1abc9c;
              }
              
              .el-input__inner {
                height: 24px;
                font-size: 16px;
                
                &::placeholder {
                  color: #999;
                }
              }
              
              .el-input__prefix {
                margin-right: 8px;
                
                .el-icon {
                  font-size: 18px;
                  color: #666;
                }
              }
            }
          }
          
          .search-btn {
            padding: 0 32px;
            height: 42px;
            font-size: 16px;
            border-radius: 8px;
            background: linear-gradient(135deg, #1abc9c, #16a085);
            border: none;
            transition: all 0.3s ease;
            
            .el-icon {
              margin-right: 6px;
              font-size: 18px;
            }
            
            &:hover {
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(26, 188, 156, 0.3);
            }
          }
        }
      }
      
      .hot-destinations {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid rgba(0, 0, 0, 0.06);
        
        .label {
          font-size: 14px;
          color: #666;
          margin-right: 12px;
        }
        
        .tag-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 8px;
          
          .hot-tag {
            cursor: pointer;
            background: rgba(26, 188, 156, 0.1);
            border: none;
            color: #1abc9c;
            transition: all 0.3s ease;
            padding: 6px 16px;
            border-radius: 16px;
            font-size: 13px;
            
            &:hover {
              background: rgba(26, 188, 156, 0.2);
              transform: translateY(-2px);
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .banner-section {
    .banner-item {
      .banner-content {
        bottom: 20%;
        
        .banner-title {
          font-size: 36px;
          letter-spacing: 2px;
          
          &::after {
            width: 60px;
            margin: 12px auto 0;
          }
        }
        
        .banner-desc {
          font-size: 18px;
          line-height: 1.6;
          margin-bottom: 32px;
        }

        .banner-btn {
          padding: 12px 32px;
          font-size: 16px;
        }
      }
    }
    
    .search-container {
      top: 30%;
      padding: 0 20px;
      
      .search-box {
        padding: 20px;
        
        .search-form {
          .form-row {
            flex-direction: column;
            
            .search-btn {
              width: 100%;
            }
          }
        }
      }
    }
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 