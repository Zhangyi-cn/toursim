<template>
  <div class="home-page">
    <!-- 使用HeaderNav组件 -->
    <HeaderNav />
    
    <!-- 使用HomeBanner组件 -->
    <HomeBanner
                      v-model="searchForm.keyword"
      @search="handleSearch"
      @banner-click="handleBannerClick"
      @tag-click="handleTagClick"
    />
    
    <!-- 今日推荐 -->
    <Recommendations />
    
    <!-- 个性化推荐 -->
    <PersonalizedRecommendations />
    
<!--    &lt;!&ndash; 目的地导航 &ndash;&gt;-->
<!--    <section class="destinations-section">-->
<!--      <div class="container">-->
<!--        <div class="section-header">-->
<!--          <h2 class="section-title">热门目的地</h2>-->
<!--          <p class="section-subtitle">探索世界各地的精彩景点</p>-->
<!--        </div>-->
<!--        -->
<!--        <div class="destination-tabs">-->
<!--          <el-tabs v-model="activeDestinationTab">-->
<!--            <el-tab-pane label="国内热门" name="domestic">-->
<!--              <div class="destination-grid">-->
<!--                <div class="destination-item featured" @click="handleDestinationClick('三亚')">-->
<!--                  <img src="/placeholder-destination.jpg" alt="三亚">-->
<!--                  <div class="destination-overlay">-->
<!--                    <div class="destination-content">-->
<!--                      <h3>三亚</h3>-->
<!--                      <p>阳光、沙滩、椰风海韵</p>-->
<!--                      <div class="destination-meta">-->
<!--                        <span class="price">¥2999起</span>-->
<!--                        <span class="duration">3-7天行程</span>-->
<!--                      </div>-->
<!--                    </div>-->
<!--                  </div>-->
<!--                </div>-->
<!--                <div class="destination-grid-small">-->
<!--                  <div class="destination-item" v-for="dest in domesticDestinations" :key="dest.id" @click="handleDestinationClick(dest.name)">-->
<!--                    <img :src="dest.image || '/placeholder-destination.jpg'" :alt="dest.name">-->
<!--                    <div class="destination-overlay">-->
<!--                      <div class="destination-content">-->
<!--                        <h3>{{ dest.name }}</h3>-->
<!--                        <div class="destination-meta">-->
<!--                          <span class="price">¥{{ dest.price_from }}起</span>-->
<!--                        </div>-->
<!--                      </div>-->
<!--                    </div>-->
<!--                  </div>-->
<!--                </div>-->
<!--              </div>-->
<!--            </el-tab-pane>-->
<!--            <el-tab-pane label="东南亚" name="southeast_asia">-->
<!--              <div class="destination-grid">-->
<!--                &lt;!&ndash; 相似结构 &ndash;&gt;-->
<!--              </div>-->
<!--            </el-tab-pane>-->
<!--            <el-tab-pane label="日本韩国" name="japan_korea">-->
<!--              <div class="destination-grid">-->
<!--                &lt;!&ndash; 相似结构 &ndash;&gt;-->
<!--              </div>-->
<!--            </el-tab-pane>-->
<!--            <el-tab-pane label="欧洲" name="europe">-->
<!--              <div class="destination-grid">-->
<!--                &lt;!&ndash; 相似结构 &ndash;&gt;-->
<!--              </div>-->
<!--            </el-tab-pane>-->
<!--          </el-tabs>-->
<!--        </div>-->
<!--      </div>-->
<!--    </section>-->
    


  </div>
</template>

<script setup lang="ts">
import * as Vue from 'vue'
import { useRouter } from 'vue-router'
import { 
  Search, 
  View, 
  ChatDotRound, 
  Star, 
  ArrowRight, 
  More,
  Message,
  Phone,
  ChatDotSquare,
  Share,
  Platform
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import HeaderNav from '@/layout/components/HeaderNav.vue'
import Recommendations from '@/components/Recommendations.vue'
import PersonalizedRecommendations from '@/components/PersonalizedRecommendations.vue'
import HomeBanner from '@/components/HomeBanner.vue'
import request from '@/utils/request'
import type { Banner, BannerResponse } from '@/types/banner'

const router = useRouter()
const userStore = useUserStore()

// 用户登录状态
const isLoggedIn = Vue.computed(() => userStore.isLoggedIn)
const userInfo = Vue.computed(() => userStore.userInfo)

const searchQuery = Vue.ref('')

// 加载状态
const loading = Vue.ref(false)

// Banner数据
const banners = Vue.ref<Banner[]>([])

// 获取轮播图数据
const fetchBanners = async () => {
  try {
    loading.value = true
    const response = await request.get<BannerResponse>('/api/system/banners')
    if (response.code === 200) {
      // 处理图片路径
      banners.value = response.data.items
        .filter((item: Banner) => item.is_active)
        .sort((a: Banner, b: Banner) => b.sort_order - a.sort_order)
        .map(banner => ({
          ...banner,
          image_url: banner.image_url.startsWith('http') 
            ? banner.image_url 
            : `${import.meta.env.VITE_STATIC_ASSETS_URL}${banner.image_url}`
        }))
    }
  } catch (error) {
    console.error('获取轮播图失败:', error)
  } finally {
    loading.value = false
  }
}

// 推荐景点数据
const featuredAttractions = Vue.ref([
  {
    id: 1,
    name: "西湖",
    description: "浙江杭州最著名的景点，中国十大风景名胜之一",
    cover_image: "/placeholder-image.jpg",
    price_start: 80,
    rating: 4.8,
    is_hot: true,
    is_recommended: true
  },
  {
    id: 2,
    name: "故宫",
    description: "中国明清两代的皇家宫殿，世界上现存最大的宫殿建筑群",
    cover_image: "/placeholder-image.jpg",
    price_start: 120,
    rating: 4.9,
    is_hot: true,
    is_recommended: true
  },
  {
    id: 3,
    name: "黄山",
    description: "安徽省著名的山岳景区，以奇松、怪石、云海、温泉闻名",
    cover_image: "/placeholder-image.jpg",
    price_start: 230,
    rating: 4.7,
    is_hot: true,
    is_recommended: true
  },
  {
    id: 4,
    name: "张家界",
    description: "湖南省著名的自然景区，以独特的石英砂岩峰林地貌闻名",
    cover_image: "/placeholder-image.jpg",
    price_start: 248,
    rating: 4.6,
    is_hot: true,
    is_recommended: false
  }
])

// 推荐游记数据
const featuredNotes = Vue.ref([
  {
    id: 1,
    title: "漫步西湖，寻觅诗意江南",
    description: "春日里的西湖，粼粼波光，杨柳依依，让人不禁想起那些传颂千年的诗句...",
    cover_image: "/placeholder-image.jpg",
    author: {
      nickname: "旅行诗人",
      avatar: "/placeholder-avatar.jpg"
    },
    views: 12580,
    likes: 2390,
    comments: 158,
    created_at: "2024-03-15"
  },
  {
    id: 2,
    title: "黄山三日行，云海日出皆入镜",
    description: "经过三天的跋涉，终于拍到了最完美的黄山日出，云海翻腾，蔚为壮观...",
    cover_image: "/placeholder-image.jpg",
    author: {
      nickname: "摄影师小王",
      avatar: "/placeholder-avatar.jpg"
    },
    views: 8920,
    likes: 1678,
    comments: 89,
    created_at: "2024-03-14"
  }
])

// 推荐指南数据
const recommendedGuides = Vue.ref([
  {
    id: 1,
    title: "杭州三日游完全攻略",
    description: "详细的杭州三日游行程规划，包含景点推荐、美食指南和交通建议",
    cover: "/placeholder-image.jpg",
    author_name: "资深玩家",
    author_avatar: "/placeholder-avatar.jpg",
    duration: "3",
    category: "城市游",
    rating: 4.8,
    views: 25890,
    likes: 3560,
    created_at: "2024-03-10"
  },
  {
    id: 2,
    title: "北京故宫深度游攻略",
    description: "带你了解故宫的历史文化，探索不为人知的精彩角落",
    cover: "/placeholder-image.jpg",
    author_name: "历史达人",
    author_avatar: "/placeholder-avatar.jpg",
    duration: "1",
    category: "文化游",
    rating: 4.9,
    views: 31280,
    likes: 4230,
    created_at: "2024-03-12"
  }
])

// 搜索相关
const searchForm = Vue.reactive({
  keyword: ''
})

const hotDestinations = Vue.ref([
  '三亚',
  '丽江',
  '张家界',
  '九寨沟',
  '黄山',
  '桂林'
])

// 目的地数据
const activeDestinationTab = Vue.ref('domestic')
const domesticDestinations = [
  {
    id: 1,
    name: '丽江',
    image: '/placeholder-image.jpg',
    price_from: 1999
  },
  {
    id: 2,
    name: '张家界',
    image: '/placeholder-image.jpg',
    price_from: 2499
  },
  {
    id: 3,
    name: '九寨沟',
    image: '/placeholder-image.jpg',
    price_from: 3299
  },
  {
    id: 4,
    name: '桂林',
    image: '/placeholder-image.jpg',
    price_from: 1799
  }
]

// 主题数据
const travelThemes = Vue.ref([
  {
    id: 1,
    name: '亲子游',
    description: '欢乐亲子时光，共创美好回忆',
    image: '/placeholder-image.jpg',
    icon: 'UserFilled'
  },
  {
    id: 2,
    name: '蜜月游',
    description: '浪漫之旅，记录甜蜜时刻',
    image: '/placeholder-image.jpg',
    icon: 'Star'
  },
  {
    id: 3,
    name: '摄影游',
    description: '捕捉美景，留住精彩瞬间',
    image: '/placeholder-image.jpg',
    icon: 'Camera'
  },
  {
    id: 4,
    name: '美食游',
    description: '寻觅美味，品味人生',
    image: '/placeholder-image.jpg',
    icon: 'Food'
  }
])

// 页面跳转
const navigateTo = (path: string) => {
  if (!path) return
  if (path.startsWith('http')) {
    window.open(path, '_blank')
  } else {
    router.push(path)
  }
}

// 景点详情页跳转
const goToAttractionDetail = (id: number) => {
  router.push({
    name: 'AttractionDetail',
    params: { id: String(id) }
  })
}

// 游记详情页跳转
const goToNoteDetail = (id: number) => {
  router.push({
    name: 'NoteDetail',
    params: { id: String(id) }
  })
}

// 推荐指南详情页跳转
const goToGuideDetail = (id: number) => {
  router.push(`/guides/${id}`)
}

// 处理目的地点击
const handleDestinationClick = (name: string) => {
  router.push({
    path: '/destinations',
    query: { keyword: name }
  })
}

// 处理主题点击
const handleThemeClick = (themeId: number) => {
  router.push({
    path: '/themes',
    query: { id: themeId }
  })
}

// 处理标签点击
const handleTagClick = (tag: string) => {
  searchForm.keyword = tag
  handleSearch()
}

// 处理搜索
const handleSearch = () => {
  if (!searchForm.keyword.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  router.push({
    name: 'Attractions',
    query: { keyword: searchForm.keyword }
  })
}

// 格式化数字
const formatNumber = (num: number | undefined) => {
  if (num === undefined || num === null) {
    return '0'
  }
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 日期格式化
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD')
}

// 处理用户菜单命令
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'orders':
      router.push('/user/orders')
      break
    case 'collections':
      router.push('/user/collections')
      break
    case 'settings':
      router.push('/user/settings')
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('退出登录成功')
      router.push('/')
      break
  }
}

// 处理轮播图点击
const handleBannerClick = (url: string) => {
  if (url.startsWith('http')) {
    window.open(url, '_blank')
  } else {
    router.push(url)
  }
}

Vue.onMounted(() => {
  fetchBanners()
})
</script>

<style lang="scss" scoped>
@use "@/styles/variables" as *;

.home-page {
  padding-bottom: $spacing-xxl;
}

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

.quick-entries {
  position: relative;
  margin-top: 120px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 30px;
  padding: 0 20px;
  
  .entry-item {
    background: #fff;
    border-radius: 15px;
    padding: 30px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    
    &:hover {
      transform: translateY(-10px);
      box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
      
      .entry-icon {
        transform: scale(1.1);
        
        .el-icon {
          transform: scale(1.2);
        }
      }
    }
    
    .entry-icon {
      width: 80px;
      height: 80px;
      margin: 0 auto 20px;
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      
      .el-icon {
        font-size: 36px;
        color: #fff;
        transition: all 0.3s ease;
      }
      
      &.attractions {
        background: linear-gradient(45deg, #4481eb, #04befe);
      }
      
      &.activities {
        background: linear-gradient(45deg, #11998e, #38ef7d);
      }
      
      &.guides {
        background: linear-gradient(45deg, #f857a6, #ff5858);
      }
      
      &.notes {
        background: linear-gradient(45deg, #fc4a1a, #f7b733);
      }
    }
    
    .entry-title {
      font-size: 20px;
      font-weight: bold;
      color: #333;
      margin-bottom: 10px;
    }
    
    .entry-desc {
      font-size: 14px;
      color: #666;
      line-height: 1.5;
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
    }
  }
  
  .quick-entries {
    grid-template-columns: repeat(2, 1fr);
    margin-top: 40px;
    gap: 20px;
    
    .entry-item {
      padding: 20px;
      
      .entry-icon {
        width: 60px;
        height: 60px;
        
        .el-icon {
          font-size: 28px;
        }
      }
      
      .entry-title {
        font-size: 16px;
      }
      
      .entry-desc {
        font-size: 12px;
      }
    }
  }
}

// 通用部分
.section-title {
  text-align: center;
  font-size: 32px;
  font-weight: bold;
  color: $text-primary;
  margin-bottom: $spacing-xs;
  
  &::after {
    content: '';
    display: block;
    width: 50px;
    height: 3px;
    background-color: #1abc9c;
    margin: $spacing-xs auto $spacing-sm;
  }
}

.section-subtitle {
  text-align: center;
  font-size: $font-size-lg;
  color: $text-hint;
  margin-bottom: $spacing-xl;
}

.view-more {
  text-align: center;
  margin-top: $spacing-xl;
}

// 目的地部分样式
.destinations-section {
  padding: 80px 0;
  background: linear-gradient(180deg, #fff 0%, #f8f9fa 100%);
  
  .destination-tabs {
    margin-top: 40px;
    
    :deep(.el-tabs__header) {
      margin-bottom: 30px;
      border: none;
      
      .el-tabs__nav-wrap::after {
        display: none;
      }
      
      .el-tabs__nav {
        display: flex;
        justify-content: center;
        gap: 40px;
      }
      
      .el-tabs__item {
        font-size: 18px;
        padding: 0 12px;
        color: #666;
        transition: all 0.3s;
        
        &:hover {
          color: #1abc9c;
        }
        
        &.is-active {
          color: #1abc9c;
          font-weight: 500;
          
          &::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 24px;
            height: 3px;
            border-radius: 2px;
            background: #1abc9c;
          }
        }
      }
    }
  }
  
  .destination-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 24px;
    
    .destination-item {
      position: relative;
      border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
      
      &.featured {
        height: 520px;
      }
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.6s ease;
      }
      
      .destination-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.7));
        padding: 32px;
        display: flex;
        align-items: flex-end;
        opacity: 1;
        transition: all 0.3s ease;
        
        .destination-content {
          color: #fff;
          transform: translateY(0);
          transition: all 0.3s ease;
          
          h3 {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 12px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
          }
          
          p {
            font-size: 16px;
            margin-bottom: 16px;
            opacity: 0.9;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
          }
          
          .destination-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            
            .price {
              font-size: 20px;
              font-weight: bold;
              color: #fff;
              text-shadow: 0 2px 4px rgba(0,0,0,0.2);
              
              &::before {
                content: '¥';
                font-size: 14px;
                margin-right: 2px;
              }
            }
            
            .duration {
              font-size: 14px;
              opacity: 0.9;
              padding: 4px 12px;
              background: rgba(255,255,255,0.2);
              border-radius: 12px;
            }
          }
        }
      }
    
    &:hover {
        img {
          transform: scale(1.1);
        }
        
        .destination-overlay {
          background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.8));
        }
      }
    }
    
    .destination-grid-small {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 24px;
      
      .destination-item {
        height: 248px;
        
        .destination-overlay {
          padding: 24px;
          
          .destination-content {
            h3 {
              font-size: 20px;
            }
            
            .destination-meta {
              .price {
                font-size: 16px;
              }
            }
          }
        }
      }
    }
  }
}

// 主题旅游部分样式
.themes-section {
  padding: 80px 0;
  background: #fff;
  
  .themes-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    margin-top: 40px;
    
    .theme-item {
      position: relative;
      border-radius: 16px;
      overflow: hidden;
      cursor: pointer;
      height: 380px;
      
      .theme-image {
        height: 100%;
        
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.6s ease;
        }
      }
      
      .theme-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.8));
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 32px;
        opacity: 0;
        transition: all 0.3s ease;
        
        .theme-content {
          text-align: center;
          color: #fff;
          transform: translateY(20px);
          transition: all 0.3s ease;
          
          .theme-icon {
            width: 64px;
            height: 64px;
            margin: 0 auto 24px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(4px);
            
            .el-icon {
              font-size: 32px;
              color: #fff;
            }
          }
          
          h3 {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 16px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
          }
          
          p {
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 28px;
            opacity: 0.9;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
          }
          
          .theme-btn {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.4);
            color: #fff;
            padding: 10px 28px;
            font-size: 14px;
            backdrop-filter: blur(4px);
            
            &:hover {
              background: rgba(255,255,255,0.3);
              transform: translateY(-2px);
            }
            
            .el-icon {
              transition: transform 0.3s ease;
            }
            
            &:hover .el-icon {
              transform: translateX(5px);
            }
          }
        }
      }
      
      &:hover {
        .theme-image img {
          transform: scale(1.1);
        }
        
        .theme-overlay {
          opacity: 1;
          
          .theme-content {
            transform: translateY(0);
        }
      }
    }
  }
}

@media (max-width: 768px) {
    .themes-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      
      .theme-item {
        height: 280px;
        
        .theme-overlay {
          padding: 20px;
          
          .theme-content {
            .theme-icon {
              width: 48px;
              height: 48px;
              margin-bottom: 16px;
              
              .el-icon {
                font-size: 24px;
              }
            }
            
            h3 {
              font-size: 20px;
              margin-bottom: 12px;
            }
            
            p {
              font-size: 14px;
              margin-bottom: 20px;
            }
            
            .theme-btn {
              padding: 8px 20px;
              font-size: 13px;
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

// 游记部分样式
.travel-notes-section {
  padding: 80px 0;
  background: #fff;
  
  .notes-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 30px;
    margin-top: 40px;
    
    .featured-note {
      position: relative;
      height: 600px;
      border-radius: 12px;
      overflow: hidden;
      cursor: pointer;
      
      .note-image {
        height: 100%;
        
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.6s ease;
        }
      }
      
      .note-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.8));
        padding: 40px;
        display: flex;
        align-items: flex-end;
        
        .note-content {
          color: #fff;
          max-width: 600px;
          
          .note-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
            margin-bottom: 20px;
          
            .author-info {
            display: flex;
            align-items: center;
              gap: 10px;
            
            .author-name {
                font-size: 16px;
                color: #fff;
            }
          }
          
            .note-stats {
            display: flex;
            gap: 15px;
            
            .stat-item {
              display: flex;
              align-items: center;
              gap: 4px;
                font-size: 14px;
                opacity: 0.9;
                color: #fff;
                
                .el-icon {
                  font-size: 16px;
                  color: #1abc9c;
                }
              }
            }
          }
          
          .note-title {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 15px;
            line-height: 1.4;
            color: #fff;
          }
          
          .note-desc {
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 25px;
            opacity: 0.9;
            color: #fff;
          }
          
          .read-more-btn {
            background: #1abc9c;
            border: none;
            color: #fff;
            padding: 12px 30px;
            
            &:hover {
              background: #16a085;
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(26, 188, 156, 0.3);
            }
            
            .el-icon {
              transition: transform 0.3s ease;
            }
            
            &:hover .el-icon {
              transform: translateX(5px);
            }
          }
        }
      }
      
      &:hover {
        .note-image img {
          transform: scale(1.1);
        }
      }
    }
    
    .notes-list {
      display: flex;
      flex-direction: column;
      gap: 20px;
  
  .note-card {
    background: #fff;
        border-radius: 12px;
    overflow: hidden;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    cursor: pointer;
        transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-5px);
          box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
      
          .note-image img {
            transform: scale(1.1);
      }
    }
    
        .note-image {
      height: 180px;
      overflow: hidden;
          
          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.6s ease;
          }
        }
        
        .note-content {
          padding: 20px;
          
          .note-header {
        display: flex;
            justify-content: space-between;
        align-items: center;
            margin-bottom: 15px;
            
            .author-info {
              display: flex;
              align-items: center;
              gap: 8px;
        
        .author-name {
                font-size: 14px;
                color: #1abc9c;
              }
        }
        
        .publish-time {
              font-size: 12px;
              color: #666;
            }
          }
          
          .note-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
            line-height: 1.4;
            
            &:hover {
              color: #1abc9c;
            }
          }
          
          .note-desc {
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
            line-height: 1.6;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          
          .note-footer {
      .note-stats {
        display: flex;
              gap: 15px;
        
        .stat-item {
          display: flex;
          align-items: center;
                gap: 4px;
                font-size: 13px;
                color: #666;
          
                &:hover {
                  color: #1abc9c;
                }
          
          .el-icon {
                  font-size: 16px;
                  color: #1abc9c;
                }
              }
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .travel-notes-section {
    .notes-grid {
      grid-template-columns: 1fr;
      
      .featured-note {
        height: 400px;
        
        .note-overlay {
          padding: 20px;
          
          .note-content {
            .note-title {
              font-size: 24px;
            }
            
            .note-desc {
              font-size: 14px;
            }
          }
        }
      }
    }
  }
}

.featured-section {
  padding: 80px 0;
  background: #f8f9fa;
  
  .attraction-card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    cursor: pointer;
    animation: fadeInUp 0.6s backwards;
    
    &:hover {
      transform: translateY(-6px);
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
      
      .card-image {
        .image-cover {
          transform: scale(1.08);
        }
        
        .card-overlay {
    opacity: 1;
          
          .view-detail-btn {
            transform: translateY(0);
            opacity: 1;
          }
        }
      }
    }
    
    .card-image {
      position: relative;
      height: 220px;
      overflow: hidden;
      
      .image-cover {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.6s ease;
      }
      
      .card-tags {
        position: absolute;
        top: 12px;
        left: 12px;
        z-index: 1;
        display: flex;
        gap: 8px;
        
        .tag {
          padding: 4px 12px;
          border-radius: 4px;
          font-size: 12px;
          color: #fff;
          backdrop-filter: blur(4px);
          
          &.hot {
            background: rgba(255, 59, 48, 0.8);
          }
          
          &.recommend {
            background: rgba(38, 129, 255, 0.8);
          }
        }
      }
      
      .card-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: all 0.3s ease;
        
        .view-detail-btn {
          transform: translateY(20px);
          opacity: 0;
          transition: all 0.3s ease;
          background: #fff;
          color: #333;
          border: none;
          padding: 8px 24px;
          font-size: 14px;
          
          &:hover {
            background: #1abc9c;
            color: #fff;
          }
        }
      }
    }
    
    .card-content {
      padding: 16px;
      
      .card-title {
        font-size: 18px;
        font-weight: 500;
        color: #333;
        margin-bottom: 8px;
        line-height: 1.4;
      }
      
      .card-desc {
        font-size: 14px;
        color: #666;
        margin-bottom: 12px;
        line-height: 1.6;
      }
      
      .card-info {
        display: flex;
        align-items: center;
        justify-content: space-between;
        
        .price {
          color: #ff385c;
          font-size: 16px;
          font-weight: 500;
        }
        
        .rating {
          :deep(.el-rate__icon) {
            font-size: 14px;
            margin-right: 4px;
          }
        }
      }
    }
  }
}


</style> 