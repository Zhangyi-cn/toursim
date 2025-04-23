<!-- 旅游指南列表页 -->
<template>
  <div class="travel-guide-page">
    <div class="container">
      <div class="guide-header">
        <h1>旅游指南</h1>
        <p class="description">为您提供最实用的旅游攻略和建议</p>
      </div>

      <div class="guide-filter">
        <el-radio-group v-model="currentCategory" @change="handleCategoryChange">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button 
            v-for="category in categories" 
            :key="category.id" 
            :label="category.id"
          >
            {{ category.name }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <div class="guide-content" v-loading="loading">
        <el-button
          v-if="isLoggedIn"
          class="add-guide-btn"
          type="primary"
          :icon="Plus"
          round
          @click="handleAddGuide"
        >
          写攻略
        </el-button>

        <el-empty v-if="!loading && guides.length === 0" description="暂无相关指南" />

        <el-row :gutter="20" v-else>
          <el-col 
            v-for="guide in guides" 
            :key="guide.id" 
            :xs="24" 
            :sm="12" 
            :md="8" 
            :lg="6"
          >
            <el-card 
              class="guide-card" 
              :body-style="{ padding: '0px' }"
              @click="handleGuideClick(guide)"
            >
              <el-image 
                :src="guide.cover_image || '/placeholder.jpg'" 
                class="guide-image"
                fit="cover"
              />
              <div class="guide-info">
                <h3 class="title">{{ guide.title }}</h3>
                <div class="category">
                  <el-tag size="small" type="info">{{ guide.category_name }}</el-tag>
                  <el-tag 
                    v-if="guide.is_hot" 
                    size="small" 
                    type="danger"
                    class="ml-2"
                  >
                    热门
                  </el-tag>
                  <el-tag 
                    v-if="guide.is_official" 
                    size="small" 
                    type="success"
                    class="ml-2"
                  >
                    官方
                  </el-tag>
                </div>
                <div class="meta">
                  <div class="stats">
                    <span class="stat-item">
                      <el-icon><View /></el-icon>
                      {{ guide.view_count }}
                    </span>
                    <span class="stat-item">
                      <el-icon><Star /></el-icon>
                      {{ guide.like_count }}
                    </span>
                  </div>
                  <span class="date">{{ formatDate(guide.created_at) }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <div class="pagination" v-if="total > 0">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 36, 48]"
            :total="total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View, Star, Plus } from '@element-plus/icons-vue'
import { getGuides, getGuideCategories } from '@/api/travel-guide'
import type { GuideCategory } from '@/api/travel-guide'
import { formatDate } from '@/utils/date'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 计算属性：判断用户是否登录
const isLoggedIn = computed(() => userStore.isLoggedIn)

// 状态数据
const loading = ref(false)
const guides = ref<any[]>([])
const categories = ref<GuideCategory[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)
const currentCategory = ref<number | ''>('')

// 加载指南分类
const loadCategories = async () => {
  try {
    const res = await getGuideCategories()
    if (res.code === 200 && res.success) {
      categories.value = res.data
    } else {
      ElMessage.error(res.message || '获取指南分类失败')
    }
  } catch (error: any) {
    console.error('获取指南分类失败:', error)
    ElMessage.error(error.message || '获取指南分类失败')
  }
}

// 加载指南列表
const loadGuides = async () => {
  loading.value = true
  try {
    const res = await getGuides({
      page: page.value,
      per_page: pageSize.value,
      category_id: currentCategory.value || undefined,
      order_by: 'created_at',
      order: 'desc'
    })
    
    if (res.code === 200 && res.success) {
      guides.value = res.data.guides
      total.value = res.data.pagination.total
    } else {
      ElMessage.error(res.message || '获取指南列表失败')
    }
  } catch (error: any) {
    console.error('获取指南列表失败:', error)
    ElMessage.error(error.message || '获取指南列表失败')
  } finally {
    loading.value = false
  }
}

// 处理分类变化
const handleCategoryChange = () => {
  page.value = 1
  loadGuides()
}

// 处理页码变化
const handleCurrentChange = (val: number) => {
  page.value = val
  loadGuides()
}

// 处理每页数量变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  page.value = 1
  loadGuides()
}

// 处理点击指南卡片
const handleGuideClick = (guide: any) => {
  router.push(`/travel-guides/${guide.id}`)
}

// 处理添加攻略
const handleAddGuide = () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录后再写攻略')
    router.push('/auth/login')
    return
  }
  router.push('/travel-guides/create')
}

// 页面加载时获取数据
onMounted(() => {
  loadCategories()
  loadGuides()
})
</script>

<style lang="scss" scoped>
.travel-guide-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  padding: 40px 0;

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
  }

  .guide-header {
    text-align: center;
    margin-bottom: 40px;
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: -15px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 3px;
      background: #1abc9c;
      border-radius: 2px;
    }

    h1 {
      font-size: 36px;
      color: #1abc9c;
      margin: 0 0 15px;
      font-weight: 600;
      letter-spacing: 1px;
      text-shadow: 0 2px 4px rgba(26, 188, 156, 0.15);
    }

    .description {
      font-size: 18px;
      color: var(--el-text-color-secondary);
      margin: 0;
      font-weight: 300;
    }
  }

  .guide-filter {
    margin-bottom: 40px;
    display: flex;
    justify-content: center;

    .el-radio-group {
      background: white;
      padding: 8px;
      border-radius: 8px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      overflow-x: auto;
      white-space: nowrap;
      
      &::-webkit-scrollbar {
        height: 6px;
      }

      &::-webkit-scrollbar-thumb {
        background-color: rgba(26, 188, 156, 0.3);
        border-radius: 3px;
      }

      &::-webkit-scrollbar-track {
        background-color: rgba(26, 188, 156, 0.1);
      }

      .el-radio-button__inner {
        border: none;
        padding: 8px 20px;
        transition: all 0.3s ease;
        
        &:hover {
          color: #1abc9c;
          background: rgba(26, 188, 156, 0.1);
        }
      }

      .el-radio-button__original-radio:checked + .el-radio-button__inner {
        background: #1abc9c;
        box-shadow: none;
      }
    }
  }

  .guide-content {
    position: relative;

    .add-guide-btn {
      position: fixed;
      right: 40px;
      bottom: 40px;
      background: #1abc9c;
      border-color: #1abc9c;
      font-size: 16px;
      padding: 12px 24px;
      z-index: 100;
      transition: all 0.3s ease;
      box-shadow: 0 4px 12px rgba(26, 188, 156, 0.3);

      &:hover {
        transform: translateY(-2px);
        background: #15a589;
        border-color: #15a589;
        box-shadow: 0 6px 16px rgba(26, 188, 156, 0.4);
      }

      .el-icon {
        margin-right: 8px;
        font-size: 18px;
      }
    }

    .guide-card {
      height: 100%;
      margin-bottom: 25px;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border: none;
      cursor: pointer;

      &:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 24px rgba(26, 188, 156, 0.2);

        .guide-image {
          transform: scale(1.05);
        }
      }

      .guide-image {
        width: 100%;
        height: 220px;
        transition: transform 0.6s ease;
        object-fit: cover;
      }

      .guide-info {
        padding: 20px;
        background: white;

        .title {
          font-size: 18px;
          font-weight: 600;
          margin: 0 0 15px;
          color: var(--el-text-color-primary);
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          line-height: 1.5;
          min-height: 54px;

          &:hover {
            color: #1abc9c;
          }
        }

        .category {
          margin-bottom: 15px;
          display: flex;
          flex-wrap: wrap;
          gap: 8px;

          .el-tag {
            border-radius: 4px;
            padding: 0 10px;
            height: 24px;
            line-height: 24px;
            border: none;

            &.el-tag--info {
              background: rgba(26, 188, 156, 0.1);
              color: #1abc9c;
            }

            &.el-tag--danger {
              background: var(--el-color-danger-light-8);
              color: var(--el-color-danger);
            }

            &.el-tag--success {
              background: var(--el-color-success-light-8);
              color: var(--el-color-success);
            }
          }
        }

        .meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 12px;
          border-top: 1px solid var(--el-border-color-lighter);
          font-size: 14px;
          color: var(--el-text-color-secondary);

          .stats {
            display: flex;
            gap: 16px;
          }

          .stat-item {
            display: flex;
            align-items: center;
            gap: 6px;
            
            .el-icon {
              font-size: 16px;
              color: #1abc9c;
            }
          }

          .date {
            font-size: 13px;
            color: var(--el-text-color-secondary);
          }
        }
      }
    }
  }

  .pagination {
    margin-top: 40px;
    display: flex;
    justify-content: center;

    :deep(.el-pagination) {
      --el-pagination-hover-color: #1abc9c;

      .el-pagination__sizes {
        margin-right: 15px;
      }

      button:not(:disabled) {
        background: transparent;
        
        &:hover {
          color: #1abc9c;
        }
      }

      .el-pager li:not(.is-disabled) {
        &:hover {
          color: #1abc9c;
        }

        &.is-active {
          background: #1abc9c;
          color: white;
        }
      }
    }
  }
}
</style> 