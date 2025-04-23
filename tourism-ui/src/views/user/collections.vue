<template>
  <div class="collections-page">
    <div class="container">
      <el-card class="collections-card">
        <template #header>
          <div class="card-header">
            <h2>我的收藏</h2>
            <el-tabs v-model="activeTab">
              <el-tab-pane label="景点" name="attraction" />
              <el-tab-pane label="攻略" name="guide" />
            </el-tabs>
          </div>
        </template>

        <div class="collections-list" v-loading="loading">
          <el-empty
            v-if="!loading && !collections.length"
            :description="getEmptyText()"
          />

          <template v-else>
            <!-- 景点收藏列表 -->
            <div v-if="activeTab === 'attraction'" class="attractions-list">
              <el-row :gutter="20">
                <el-col
                  v-for="item in collections"
                  :key="item.id"
                  :xs="24"
                  :sm="12"
                  :md="8"
                  :lg="6"
                >
                  <div class="attraction-item" @click="handleItemClick(item)">
                    <el-card :body-style="{ padding: '0px' }">
                      <el-image
                        :src="getItemImage(item)"
                        class="item-image"
                        fit="cover"
                      />
                      <div class="item-info">
                        <h3>{{ getItemTitle(item) }}</h3>
                        <p class="description">{{ getItemDescription(item) }}</p>
                        <div class="meta">
                          <span class="location" v-if="false">
                            <el-icon><Location /></el-icon>
                            {{ item.target_info.location }}
                          </span>
                          <el-button
                            type="danger"
                            size="small"
                            @click.stop="handleCancelCollect(item)"
                          >
                            取消收藏
                          </el-button>
                        </div>
                      </div>
                    </el-card>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 攻略收藏列表 -->
            <div v-else class="guides-list">
              <el-row :gutter="20">
                <el-col
                  v-for="item in collections"
                  :key="item.id"
                  :xs="24"
                  :sm="12"
                  :md="8"
                  :lg="6"
                >
                  <div class="guide-item" @click="handleItemClick(item)">
                    <el-card :body-style="{ padding: '0px' }">
                      <el-image
                        :src="getItemImage(item)"
                        class="item-image"
                        fit="cover"
                      />
                      <div class="item-info">
                        <h3>{{ getItemTitle(item) }}</h3>
                        <p class="description">{{ getItemDescription(item) }}</p>
                        <div class="meta">
                          <div class="author" v-if="item.target_info.user_name">
                            <el-avatar :size="24" :src="item.target_info.user_avatar || '/default-avatar.png'"></el-avatar>
                            <span>{{ item.target_info.user_name }}</span>
                          </div>
                          <el-button
                            type="danger"
                            size="small"
                            @click.stop="handleCancelCollect(item)"
                          >
                            取消收藏
                          </el-button>
                        </div>
                      </div>
                    </el-card>
                  </div>
                </el-col>
              </el-row>
            </div>
          </template>

          <div class="pagination" v-if="total > 0">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              :page-sizes="[12, 24, 36]"
              layout="total, sizes, prev, pager, next"
              @update:current-page="currentPage = $event"
              @update:page-size="pageSize = $event"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Location, Calendar } from '@element-plus/icons-vue'
import { getUserCollections, uncollectItem, uncollectAttraction } from '@/api/collection'
import { formatDate } from '@/utils/date'

// 静态资源基础URL
const staticBaseUrl = import.meta.env.VITE_STATIC_ASSETS_URL || ''

const router = useRouter()

// 状态数据
const loading = ref(false)
const activeTab = ref('attraction')
const collections = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)

// 获取收藏列表
const loadCollections = async () => {
  loading.value = true
  try {
    const res = await getUserCollections({
      type: activeTab.value,
      page: currentPage.value,
      per_page: pageSize.value
    })
    
    if (res.code === 200) {
      collections.value = res.data.items || []
      total.value = res.data.pagination?.total || 0
    } else {
      ElMessage.error(res.message || '获取收藏列表失败')
    }
  } catch (error) {
    console.error('获取收藏列表失败:', error)
    ElMessage.error('获取收藏列表失败')
  } finally {
    loading.value = false
  }
}

// 处理分页变化
const handleSizeChange = (size) => {
  pageSize.value = size
  loadCollections()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadCollections()
}

// 获取空状态文本
const getEmptyText = () => {
  switch (activeTab.value) {
    case 'attraction':
      return '暂无收藏的景点'
    case 'guide':
      return '暂无收藏的攻略'
    default:
      return '暂无收藏内容'
  }
}

// 处理取消收藏
const handleCancelCollect = async (item) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消收藏吗？',
      '取消收藏',
      {
        type: 'warning'
      }
    )

    if (item.target_type === 'attraction') {
      await uncollectAttraction(item.target_id)
    } else {
      await uncollectItem(item.target_type, item.target_id)
    }
    
    ElMessage.success('已取消收藏')
    loadCollections()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消收藏失败:', error)
      ElMessage.error('取消收藏失败')
    }
  }
}

// 获取项目图片
const getItemImage = (item) => {
  if (!item.target_info) return '/placeholder.jpg'
  
  if (item.target_type === 'attraction') {
    return item.target_info.cover ? `${staticBaseUrl}/${item.target_info.cover}` : '/placeholder.jpg'
  } else {
    return item.target_info.cover || '/placeholder.jpg'
  }
}

// 获取项目标题
const getItemTitle = (item) => {
  if (!item.target_info) return '未知标题'
  
  return item.target_info.title || '未知标题'
}

// 获取项目描述
const getItemDescription = (item) => {
  if (!item.target_info) return ''
  
  return item.target_info.description || ''
}

// 处理点击项目
const handleItemClick = (item) => {
  switch (item.target_type) {
    case 'attraction':
      router.push(`/attractions/${item.target_id}`)
      break
    case 'guide':
      router.push(`/travel-guides/${item.target_id}`)
      break
  }
}

// 监听标签页切换
watch(activeTab, () => {
  currentPage.value = 1
  loadCollections()
})

// 页面加载时获取数据
onMounted(() => {
  loadCollections()
})
</script>

<style lang="scss" scoped>
.collections-page {
  padding: 30px 0;

  .collections-card {
    .card-header {
      h2 {
        margin: 0 0 20px;
        font-size: 20px;
        color: #303133;
      }
    }

    .collections-list {
      min-height: 300px;

      .attraction-item,
      .guide-item {
        margin-bottom: 20px;
        cursor: pointer;
        transition: transform 0.3s;

        &:hover {
          transform: translateY(-5px);
        }

        .item-image {
          width: 100%;
          height: 200px;
        }

        .item-info {
          padding: 15px;

          h3 {
            margin: 0 0 10px;
            font-size: 16px;
            color: #303133;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 1;
            overflow: hidden;
          }

          .description {
            margin: 0 0 10px;
            font-size: 14px;
            color: #606266;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 2;
            overflow: hidden;
            height: 40px;
          }

          .meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            color: #909399;

            .location,
            .time,
            .author {
              display: flex;
              align-items: center;
              gap: 5px;
            }

            .author {
              .el-avatar {
                margin-right: 5px;
              }
            }

            .price {
              .amount {
                color: #f56c6c;
                font-size: 16px;
                margin-right: 2px;
              }
            }
          }
        }
      }

      .pagination {
        margin-top: 20px;
        display: flex;
        justify-content: flex-end;
      }
    }
  }
}

@media (max-width: 768px) {
  .collections-page {
    padding: 15px;

    .collections-card {
      .collections-list {
        .attraction-item,
        .guide-item {
          .item-image {
            height: 160px;
          }
        }
      }
    }
  }
}
</style> 