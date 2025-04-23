<template>
  <div class="guide-detail-page">
    <div class="container" v-loading="loading">
      <template v-if="guide">
        <div class="guide-header">
          <el-breadcrumb>
            <el-breadcrumb-item to="/guides">旅游指南</el-breadcrumb-item>
            <el-breadcrumb-item>{{ guide.title }}</el-breadcrumb-item>
          </el-breadcrumb>

          <h1 class="title">{{ guide.title }}</h1>
          
          <div class="meta">
            <el-tag size="small" type="info">{{ guide.category_name }}</el-tag>
            <span class="date">发布时间：{{ formatDate(guide.created_at) }}</span>
            <span class="views">
              <el-icon><View /></el-icon>
              {{ guide.views }}
            </span>
          </div>
        </div>

        <el-row :gutter="20">
          <el-col :xs="24" :sm="24" :md="16">
            <el-card class="guide-content">
              <div class="cover" v-if="guide.cover">
                <el-image :src="guide.cover" fit="cover" />
              </div>

              <div class="content" v-html="guide.content"></div>

              <div class="tags" v-if="guide.tags?.length">
                <span class="label">标签：</span>
                <el-tag
                  v-for="tag in guide.tags"
                  :key="tag"
                  size="small"
                  effect="plain"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="24" :md="8">
            <el-affix :offset="80">
              <div class="guide-sidebar">
                <el-card class="author-card" v-if="guide.author">
                  <div class="author-info">
                    <el-avatar :size="64" :src="guide.author.avatar" />
                    <div class="info">
                      <h3>{{ guide.author.nickname }}</h3>
                      <p>{{ guide.author.bio || '暂无简介' }}</p>
                    </div>
                  </div>
                </el-card>

                <el-card class="related-card">
                  <template #header>
                    <div class="card-header">
                      <h3>相关指南</h3>
                    </div>
                  </template>

                  <div class="related-list">
                    <el-empty v-if="!relatedGuides.length" description="暂无相关指南" />

                    <div 
                      v-for="item in relatedGuides" 
                      :key="item.id"
                      class="related-item"
                      @click="handleRelatedClick(item)"
                    >
                      <el-image 
                        :src="item.cover || '/placeholder.jpg'" 
                        class="item-image"
                        fit="cover"
                      />
                      <div class="item-info">
                        <h4>{{ item.title }}</h4>
                        <p>{{ item.description }}</p>
                      </div>
                    </div>
                  </div>
                </el-card>
              </div>
            </el-affix>
          </el-col>
        </el-row>
      </template>

      <el-empty v-else-if="!loading" description="指南不存在" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import { getGuideDetail, getGuides } from '@/api/guide'
import { formatDate } from '@/utils/date'

const route = useRoute()
const router = useRouter()

// 状态数据
const loading = ref(false)
const guide = ref(null)
const relatedGuides = ref([])

// 加载指南详情
const loadGuideDetail = async () => {
  loading.value = true
  try {
    const res = await getGuideDetail(route.params.id)
    guide.value = res.data
    loadRelatedGuides()
  } catch (error) {
    console.error('获取指南详情失败:', error)
    ElMessage.error('获取指南详情失败')
  } finally {
    loading.value = false
  }
}

// 加载相关指南
const loadRelatedGuides = async () => {
  if (!guide.value?.category_id) return

  try {
    const res = await getGuides({
      page: 1,
      per_page: 5,
      category: guide.value.category_id,
      exclude_id: guide.value.id
    })
    relatedGuides.value = res.data.items
  } catch (error) {
    console.error('获取相关指南失败:', error)
  }
}

// 处理点击相关指南
const handleRelatedClick = (item) => {
  router.push(`/guides/${item.id}`)
}

// 页面加载时获取数据
onMounted(() => {
  loadGuideDetail()
})
</script>

<style lang="scss" scoped>
.guide-detail-page {
  padding: 30px 0;

  .guide-header {
    margin-bottom: 30px;

    .title {
      font-size: 28px;
      color: #303133;
      margin: 20px 0;
    }

    .meta {
      display: flex;
      align-items: center;
      gap: 15px;
      color: #909399;
      font-size: 14px;

      .views {
        display: flex;
        align-items: center;
        gap: 5px;
      }
    }
  }

  .guide-content {
    margin-bottom: 30px;

    .cover {
      margin: -20px -20px 20px;

      .el-image {
        width: 100%;
        height: 400px;
      }
    }

    .content {
      line-height: 1.8;
      color: #303133;

      :deep(img) {
        max-width: 100%;
        height: auto;
      }

      :deep(h1),
      :deep(h2),
      :deep(h3),
      :deep(h4),
      :deep(h5),
      :deep(h6) {
        margin: 1.5em 0 0.5em;
      }

      :deep(p) {
        margin: 1em 0;
      }
    }

    .tags {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #eee;

      .label {
        color: #909399;
        margin-right: 10px;
      }

      .el-tag {
        margin: 0 5px 5px 0;
      }
    }
  }

  .guide-sidebar {
    .author-card {
      margin-bottom: 20px;

      .author-info {
        display: flex;
        align-items: flex-start;
        gap: 15px;

        .info {
          flex: 1;
          min-width: 0;

          h3 {
            margin: 0 0 5px;
            font-size: 16px;
            color: #303133;
          }

          p {
            margin: 0;
            font-size: 14px;
            color: #606266;
          }
        }
      }
    }

    .related-card {
      .card-header {
        h3 {
          margin: 0;
          font-size: 16px;
          color: #303133;
        }
      }

      .related-list {
        .related-item {
          display: flex;
          gap: 10px;
          padding: 10px 0;
          border-bottom: 1px solid #eee;
          cursor: pointer;
          transition: background-color 0.3s;

          &:last-child {
            border-bottom: none;
          }

          &:hover {
            background-color: #f5f7fa;
          }

          .item-image {
            width: 80px;
            height: 60px;
            border-radius: 4px;
            flex-shrink: 0;
          }

          .item-info {
            flex: 1;
            min-width: 0;

            h4 {
              margin: 0 0 5px;
              font-size: 14px;
              color: #303133;
              display: -webkit-box;
              -webkit-box-orient: vertical;
              -webkit-line-clamp: 1;
              overflow: hidden;
            }

            p {
              margin: 0;
              font-size: 12px;
              color: #909399;
              display: -webkit-box;
              -webkit-box-orient: vertical;
              -webkit-line-clamp: 2;
              overflow: hidden;
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .guide-detail-page {
    padding: 15px;

    .guide-header {
      margin-bottom: 20px;

      .title {
        font-size: 20px;
        margin: 15px 0;
      }

      .meta {
        flex-wrap: wrap;
        gap: 10px;
      }
    }

    .guide-content {
      .cover {
        .el-image {
          height: 200px;
        }
      }
    }

    .guide-sidebar {
      margin-top: 20px;
    }
  }
}
</style> 