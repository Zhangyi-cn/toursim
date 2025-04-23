<template>
  <div class="guide-page">
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
                :src="guide.cover || '/placeholder.jpg'" 
                class="guide-image"
                fit="cover"
              />
              <div class="guide-info">
                <h3 class="title">{{ guide.title }}</h3>
                <div class="category">
                  <el-tag size="small" type="info">{{ guide.category_name }}</el-tag>
                </div>
                <p class="desc">{{ guide.description }}</p>
                <div class="meta">
                  <span class="views">
                    <el-icon><View /></el-icon>
                    {{ guide.views }}
                  </span>
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

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import { getGuides, getGuideCategories } from '@/api/guide'
import { formatDate } from '@/utils/date'

const router = useRouter()

// 状态数据
const loading = ref(false)
const guides = ref([])
const categories = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)
const currentCategory = ref('')

// 加载指南分类
const loadCategories = async () => {
  try {
    const res = await getGuideCategories()
    categories.value = res.data
  } catch (error) {
    console.error('获取指南分类失败:', error)
    ElMessage.error('获取指南分类失败')
  }
}

// 加载指南列表
const loadGuides = async () => {
  loading.value = true
  try {
    const res = await getGuides({
      page: page.value,
      per_page: pageSize.value,
      category: currentCategory.value
    })
    guides.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('获取指南列表失败:', error)
    ElMessage.error('获取指南列表失败')
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
const handleCurrentChange = (val) => {
  page.value = val
  loadGuides()
}

// 处理每页数量变化
const handleSizeChange = (val) => {
  pageSize.value = val
  page.value = 1
  loadGuides()
}

// 处理点击指南卡片
const handleGuideClick = (guide) => {
  router.push(`/guides/${guide.id}`)
}

// 页面加载时获取数据
onMounted(() => {
  loadCategories()
  loadGuides()
})
</script>

<style lang="scss" scoped>
.guide-page {
  padding: 30px 0;

  .guide-header {
    text-align: center;
    margin-bottom: 30px;

    h1 {
      font-size: 32px;
      color: #303133;
      margin: 0 0 10px;
    }

    .description {
      font-size: 16px;
      color: #606266;
      margin: 0;
    }
  }

  .guide-filter {
    margin-bottom: 30px;
    display: flex;
    justify-content: center;

    .el-radio-group {
      border-radius: 4px;
      overflow-x: auto;
      white-space: nowrap;
      padding-bottom: 5px;

      &::-webkit-scrollbar {
        height: 6px;
      }

      &::-webkit-scrollbar-thumb {
        background-color: #dcdfe6;
        border-radius: 3px;
      }

      &::-webkit-scrollbar-track {
        background-color: #f5f7fa;
      }
    }
  }

  .guide-content {
    .guide-card {
      margin-bottom: 20px;
      cursor: pointer;
      transition: transform 0.3s;

      &:hover {
        transform: translateY(-5px);
      }

      .guide-image {
        width: 100%;
        height: 200px;
      }

      .guide-info {
        padding: 15px;

        .title {
          font-size: 16px;
          color: #303133;
          margin: 0 0 10px;
          display: -webkit-box;
          -webkit-box-orient: vertical;
          -webkit-line-clamp: 2;
          overflow: hidden;
          line-height: 1.5;
        }

        .category {
          margin-bottom: 10px;
        }

        .desc {
          font-size: 14px;
          color: #606266;
          margin: 0 0 10px;
          display: -webkit-box;
          -webkit-box-orient: vertical;
          -webkit-line-clamp: 2;
          overflow: hidden;
          line-height: 1.5;
        }

        .meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 12px;
          color: #909399;

          .views {
            display: flex;
            align-items: center;
            gap: 5px;
          }
        }
      }
    }

    .pagination {
      margin-top: 30px;
      display: flex;
      justify-content: center;
    }
  }
}

@media (max-width: 768px) {
  .guide-page {
    padding: 15px;

    .guide-header {
      margin-bottom: 20px;

      h1 {
        font-size: 24px;
      }

      .description {
        font-size: 14px;
      }
    }

    .guide-filter {
      margin: 0 -15px 20px;
      padding: 0 15px;
    }

    .guide-content {
      .guide-card {
        .guide-image {
          height: 160px;
        }

        .guide-info {
          padding: 10px;

          .title {
            font-size: 14px;
          }

          .desc {
            font-size: 12px;
          }
        }
      }
    }
  }
}
</style> 