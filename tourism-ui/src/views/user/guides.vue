<template>
  <div class="my-guides-page">
    <div class="page-header">
      <h1>我的攻略</h1>
      <el-button type="primary" :icon="Plus" @click="handleAddGuide">写攻略</el-button>
    </div>

    <div class="guides-content" v-loading="loading">
      <el-empty v-if="!loading && guides.length === 0" description="暂无攻略，快来写一篇吧！">
        <el-button type="primary" :icon="Plus" @click="handleAddGuide">写攻略</el-button>
      </el-empty>

      <el-row :gutter="20" v-else>
        <el-col 
          v-for="guide in guides" 
          :key="guide.id" 
          :xs="24" 
          :sm="12" 
          :md="8"
        >
          <el-card class="guide-card">
            <div class="guide-cover">
              <el-image 
                :src="guide.cover_image || '/placeholder.jpg'" 
                fit="cover"
              />
              <div class="guide-actions">
                <el-button-group>
                  <el-button 
                    type="primary" 
                    :icon="Edit"
                    @click.stop="handleEditGuide(guide)"
                  >
                    编辑
                  </el-button>
                  <el-button 
                    type="danger" 
                    :icon="Delete"
                    @click.stop="handleDeleteGuide(guide)"
                  >
                    删除
                  </el-button>
                </el-button-group>
              </div>
            </div>

            <div class="guide-info">
              <h3 class="title" @click="handleViewGuide(guide)">{{ guide.title }}</h3>
              <div class="meta">
                <el-tag size="small" type="info">{{ guide.category_name }}</el-tag>
                <div class="stats">
                  <span class="stat-item">
                    <el-icon><View /></el-icon>
                    {{ guide.view_count }}
                  </span>
                  <span class="stat-item">
                    <el-icon><Star /></el-icon>
                    {{ guide.like_count }}
                  </span>
                  <span class="stat-item">
                    <el-icon><ChatLineRound /></el-icon>
                    {{ guide.comment_count }}
                  </span>
                </div>
              </div>
              <div class="date">
                发布于 {{ formatDate(guide.created_at) }}
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[9, 18, 27, 36]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Star, Plus, Edit, Delete, ChatLineRound } from '@element-plus/icons-vue'
import { getMyGuides, deleteGuide } from '@/api/travel-guide'
import { formatDate } from '@/utils/date'

const router = useRouter()

// 状态数据
const loading = ref(false)
const guides = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(9)

// 加载我的攻略列表
const loadGuides = async () => {
  loading.value = true
  try {
    const res = await getMyGuides({
      page: page.value,
      per_page: pageSize.value
    })
    
    if (res.code === 200 && res.success) {
      guides.value = res.data.guides
      total.value = res.data.pagination.total
    } else {
      ElMessage.error(res.message || '获取攻略列表失败')
    }
  } catch (error: any) {
    console.error('获取攻略列表失败:', error)
    ElMessage.error(error.message || '获取攻略列表失败')
  } finally {
    loading.value = false
  }
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

// 处理添加攻略
const handleAddGuide = () => {
  router.push('/travel-guides/create')
}

// 处理查看攻略
const handleViewGuide = (guide: any) => {
  router.push(`/travel-guides/${guide.id}`)
}

// 处理编辑攻略
const handleEditGuide = (guide: any) => {
  router.push(`/travel-guides/edit/${guide.id}`)
}

// 处理删除攻略
const handleDeleteGuide = async (guide: any) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这篇攻略吗？删除后无法恢复。',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await deleteGuide(guide.id)
    if (res.code === 200 && res.success) {
      ElMessage.success('删除成功')
      loadGuides()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除攻略失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadGuides()
})
</script>

<style lang="scss" scoped>
.my-guides-page {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;

    h1 {
      font-size: 28px;
      color: #1abc9c;
      margin: 0;
      font-weight: 600;
      position: relative;
      padding-left: 16px;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 24px;
        background: #1abc9c;
        border-radius: 2px;
      }
    }
  }

  .guides-content {
    .guide-card {
      height: 100%;
      margin-bottom: 25px;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
      border: none;

      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(26, 188, 156, 0.2);

        .guide-cover {
          .guide-actions {
            opacity: 1;
            transform: translateY(0);
          }
        }
      }

      .guide-cover {
        position: relative;
        height: 200px;
        overflow: hidden;

        .el-image {
          width: 100%;
          height: 100%;
          transition: transform 0.6s ease;
        }

        .guide-actions {
          position: absolute;
          left: 0;
          right: 0;
          bottom: 0;
          padding: 15px;
          background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
          opacity: 0;
          transform: translateY(20px);
          transition: all 0.3s ease;
          display: flex;
          justify-content: center;
        }
      }

      .guide-info {
        padding: 20px;

        .title {
          font-size: 18px;
          font-weight: 600;
          margin: 0 0 15px;
          color: var(--el-text-color-primary);
          cursor: pointer;
          transition: color 0.3s ease;

          &:hover {
            color: #1abc9c;
          }
        }

        .meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          .stats {
            display: flex;
            gap: 16px;
          }

          .stat-item {
            display: flex;
            align-items: center;
            gap: 4px;
            color: var(--el-text-color-secondary);
            font-size: 14px;

            .el-icon {
              font-size: 16px;
              color: #1abc9c;
            }
          }
        }

        .date {
          font-size: 13px;
          color: var(--el-text-color-secondary);
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