<template>
  <section class="recommendations-section">
    <div class="section-header">
      <h2>今日推荐</h2>
      <div class="header-divider">
        <span class="line"></span>
        <span class="dot"></span>
        <span class="line"></span>
      </div>
      <p class="subtitle">精选景点推荐，带你探索更多精彩</p>
    </div>
    
    <div class="recommendations-grid">
      <el-row :gutter="20">
        <el-col 
          :xs="24" 
          :sm="12" 
          :md="8" 
          :lg="4.8" 
          :xl="4.8"
          :span="4.8"
          class="recommendation-col" 
          v-for="item in recommendedItems" 
          :key="item.id"
        >
          <el-card class="recommendation-card" shadow="hover" @click="$router.push(`/attractions/${item.id}`)">
            <div class="card-image-wrapper">
              <img :src="item.cover_image" :alt="item.name" class="card-image">
              <div class="card-overlay">
                <el-button class="view-btn" round>
                  查看详情
                  <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="card-content">
              <h3 class="title">{{ item.name }}</h3>
              <div class="card-meta">
                <span class="location">
                  <el-icon><Location /></el-icon>
                  {{ item.address }}
                </span>
                <div class="stats">
                  <span class="views">
                    <el-icon><View /></el-icon>
                    {{ item.view_count || 0 }}
                  </span>
                  <span class="likes">
                    <el-icon><Star /></el-icon>
                    {{ item.like_count || 0 }}
                  </span>
                </div>
              </div>
              <div class="card-tags" v-if="item.is_hot || item.is_recommended">
                <el-tag size="small" type="danger" v-if="item.is_hot">热门</el-tag>
                <el-tag size="small" type="success" v-if="item.is_recommended">推荐</el-tag>
              </div>
              <div class="card-info">
                <span class="ticket-info" v-if="item.ticket_info">
                  <el-icon><Ticket /></el-icon>
                  {{ item.ticket_info }}
                </span>
                <span class="open-time" v-if="item.open_time">
                  <el-icon><Clock /></el-icon>
                  {{ item.open_time }}
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowRight, Location, View, Star, Ticket, Clock } from '@element-plus/icons-vue'
import request from '@/utils/request'
import type { Attraction } from '@/types/attraction'

interface TodayResponse {
  attractions: Attraction[]
  guides: any[]
  notes: any[]
}

const recommendedItems = ref<Attraction[]>([])

// 从票价信息中提取价格数字
const extractPrice = (ticketInfo: string): number => {
  const match = ticketInfo.match(/价格:\s*(\d+)/)
  return match ? parseInt(match[1]) : 0
}

// 处理景点数据
const processAttractionData = (attractions: any[]) => {
  const staticBaseUrl = import.meta.env.VITE_STATIC_ASSETS_URL
  
  return attractions.map(item => ({
    ...item,
    price: extractPrice(item.ticket_info),
    score: item.like_count || 0,
    popularity: item.view_count || 0,
    description: item.description || '暂无描述',
    cover_image: item.cover_image.startsWith('http') 
      ? item.cover_image 
      : `${staticBaseUrl}/${item.cover_image}`
  }))
}

const fetchRecommendations = async () => {
  try {
    const res = await request.get<{
      data: TodayResponse
      message: string
      success: boolean
    }>('/api/recommendations/today')
    if (res.success) {
      recommendedItems.value = processAttractionData(res.data.attractions)
    }
  } catch (error) {
    console.error('获取推荐景点失败:', error)
  }
}

onMounted(() => {
  fetchRecommendations()
})

defineOptions({
  name: 'Recommendations'
})
</script>

<style lang="scss" scoped>
@mixin text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommendations-section {
  padding: 80px 0;
  background: #F0FFF9;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #1abc9c, transparent);
  }
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #1abc9c, transparent);
  }
  
  .section-header {
    text-align: center;
    margin-bottom: 60px;
    
    h2 {
      font-size: 36px;
      font-weight: 600;
      color: #2c3e50;
      margin-bottom: 20px;
      position: relative;
      display: inline-block;
      
      &::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #1abc9c, #16a085);
        border-radius: 2px;
      }
    }
    
    .header-divider {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-bottom: 20px;
      
      .line {
        width: 40px;
        height: 2px;
        background: #1abc9c;
        opacity: 0.6;
      }
      
      .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #1abc9c;
      }
    }
    
    .subtitle {
      font-size: 16px;
      color: #666;
      max-width: 600px;
      margin: 0 auto;
      line-height: 1.6;
    }
  }
  
  .recommendations-grid {
    width: 100%;
    padding: 0 40px;
    
    :deep(.el-row) {
      margin: 0;
      display: flex;
      flex-wrap: nowrap;
      justify-content: center;
      gap: 20px;
    }
    
    .recommendation-col {
      flex: 0 0 calc(20% - 16px);
      max-width: calc(20% - 16px);
      min-width: 0;
      margin-bottom: 20px;
      padding: 0;
      
      :deep(.el-card) {
        border: 1px solid #edf2f7;
        border-radius: 8px;
        overflow: hidden;
        transition: all 0.3s ease;
        background: #fff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        
        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 16px rgba(26, 188, 156, 0.1);
          border-color: rgba(26, 188, 156, 0.2);
        }
        
        .el-card__body {
          padding: 0;
        }
      }
      
      .card-image-wrapper {
        position: relative;
        height: 240px;
        overflow: hidden;
        border-radius: 8px 8px 0 0;
        
        .card-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.5s ease;
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
          
          .view-btn {
            background: #fff;
            color: #333;
            border: none;
            padding: 8px 20px;
            transform: translateY(20px);
            opacity: 0;
            transition: all 0.3s ease;
            border-radius: 20px;
            
            &:hover {
              background: #1abc9c;
              color: #fff;
              transform: translateY(-2px);
            }
            
            .el-icon {
              transition: transform 0.3s ease;
            }
            
            &:hover .el-icon {
              transform: translateX(4px);
            }
          }
        }
      }
      
      .card-content {
        padding: 20px;
        background: #fff;
        border-top: 1px solid #edf2f7;
        flex: 1;
        display: flex;
        flex-direction: column;
        border-radius: 0 0 8px 8px;
        
        .card-tags {
          display: flex;
          gap: 6px;
          margin-bottom: 12px;
          
          .tag {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            
            &:first-child {
              background: rgba(255, 59, 48, 0.1);
              color: #ff3b30;
            }
            
            &:last-child {
              background: rgba(26, 188, 156, 0.1);
              color: #1abc9c;
            }
          }
        }
        
        .title {
          font-size: 16px;
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 10px;
          line-height: 1.4;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          transition: color 0.3s ease;
        }
        
        .card-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          font-size: 12px;
          color: #666;
          
          .location {
            display: flex;
            align-items: center;
            gap: 4px;
            @include text-ellipsis;
            max-width: 60%;
            transition: color 0.3s ease;
          }
          
          .stats {
            display: flex;
            gap: 8px;
            
            span {
              display: flex;
              align-items: center;
              gap: 4px;
              transition: color 0.3s ease;
            }
          }
        }
        
        .card-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
          font-size: 12px;
          color: #666;
          
          span {
            display: flex;
            align-items: center;
            gap: 4px;
            @include text-ellipsis;
            
            .el-icon {
              color: #1abc9c;
            }
          }
          
          .ticket-info {
            color: #f56c6c;
          }
        }
      }
    }
  }
}

// 响应式布局
@media screen and (max-width: 1200px) {
  .recommendations-section {
    .recommendations-grid {
      padding: 0 15px;
    }
  }
}

@media screen and (max-width: 768px) {
  .recommendations-section {
    padding: 60px 0;
    
    .recommendations-grid {
      padding: 0 12px;
    }
  }
}

@media screen and (max-width: 480px) {
  .recommendations-section {
    padding: 40px 0;
    
    .recommendations-grid {
      padding: 0 10px;
    }
  }
}
</style> 