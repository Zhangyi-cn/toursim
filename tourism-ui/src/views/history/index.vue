<template>
  <div class="history-page">
    <div class="container">
      <el-card class="history-card">
        <template #header>
          <div class="card-header">
            <h2>浏览历史</h2>
            <div class="header-actions">
              <el-button 
                type="danger" 
                plain
                @click="handleClear"
                :disabled="!hasHistory"
              >
                清空历史记录
              </el-button>
            </div>
          </div>
        </template>

        <div class="history-list" v-loading="loading">
          <el-empty v-if="!loading && history.length === 0" description="暂无浏览记录" />

          <div v-else class="history-items">
            <div 
              v-for="item in history" 
              :key="item.id" 
              class="history-item"
              @click="handleItemClick(item)"
            >
              <el-image 
                :src="item.cover || '/placeholder.jpg'" 
                class="item-image"
                fit="cover"
              />

              <div class="item-content">
                <div class="item-header">
                  <span class="title">{{ item.title }}</span>
                  <span class="time">{{ formatDate(item.visited_at) }}</span>
                </div>
                <div class="item-type">
                  <el-tag :type="getTypeTag(item.type)" size="small">
                    {{ getTypeText(item.type) }}
                  </el-tag>
                </div>
                <div class="item-desc" v-if="item.description">
                  {{ item.description }}
                </div>
              </div>
            </div>
          </div>

          <div class="pagination" v-if="total > 0">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 30, 50]"
              :total="total"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </el-card>
    </div>

    <el-dialog
      v-model="clearDialogVisible"
      title="确认清空"
      width="400px"
    >
      <div class="clear-dialog-content">
        <el-icon class="warning-icon" :size="64">
          <Warning />
        </el-icon>
        <p>确定要清空所有浏览记录吗？此操作不可恢复。</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="clearDialogVisible = false">取消</el-button>
          <el-button
            type="danger"
            @click="confirmClear"
            :loading="clearing"
          >
            确定清空
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning } from '@element-plus/icons-vue'
import { getBrowseHistory, clearBrowseHistory } from '@/api/history'
import { formatDate } from '@/utils/date'

const router = useRouter()

// 状态数据
const loading = ref(false)
const clearing = ref(false)
const history = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const clearDialogVisible = ref(false)

// 计算属性
const hasHistory = computed(() => history.value.length > 0)

// 获取类型标签样式
const getTypeTag = (type) => {
  const tagMap = {
    attraction: '',
    activity: 'success',
    note: 'warning',
    guide: 'info'
  }
  return tagMap[type] || 'info'
}

// 获取类型文本
const getTypeText = (type) => {
  const textMap = {
    attraction: '景点',
    activity: '活动',
    note: '游记',
    guide: '指南'
  }
  return textMap[type] || type
}

// 加载浏览历史
const loadHistory = async () => {
  loading.value = true
  try {
    const res = await getBrowseHistory({
      page: page.value,
      per_page: pageSize.value
    })
    history.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('获取浏览历史失败:', error)
    ElMessage.error('获取浏览历史失败')
  } finally {
    loading.value = false
  }
}

// 处理页码变化
const handleCurrentChange = (val) => {
  page.value = val
  loadHistory()
}

// 处理每页数量变化
const handleSizeChange = (val) => {
  pageSize.value = val
  page.value = 1
  loadHistory()
}

// 处理点击历史记录项
const handleItemClick = (item) => {
  const routeMap = {
    attraction: `/attractions/${item.target_id}`,
    activity: `/activities/${item.target_id}`,
    note: `/notes/${item.target_id}`,
    guide: `/guides/${item.target_id}`
  }
  
  const route = routeMap[item.type]
  if (route) {
    router.push(route)
  }
}

// 处理清空历史
const handleClear = () => {
  clearDialogVisible.value = true
}

// 确认清空
const confirmClear = async () => {
  clearing.value = true
  try {
    await clearBrowseHistory()
    ElMessage.success('清空成功')
    clearDialogVisible.value = false
    history.value = []
    total.value = 0
  } catch (error) {
    console.error('清空历史记录失败:', error)
    ElMessage.error('清空历史记录失败')
  } finally {
    clearing.value = false
  }
}

// 页面加载时获取浏览历史
onMounted(() => {
  loadHistory()
})
</script>

<style lang="scss" scoped>
.history-page {
  padding: 30px 0;

  .history-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h2 {
        margin: 0;
        font-size: 20px;
      }
    }
  }

  .history-list {
    .history-items {
      .history-item {
        display: flex;
        padding: 20px;
        border-bottom: 1px solid #eee;
        transition: background-color 0.3s;
        cursor: pointer;

        &:last-child {
          border-bottom: none;
        }

        &:hover {
          background-color: #f5f7fa;
        }

        .item-image {
          width: 200px;
          height: 120px;
          border-radius: 4px;
          margin-right: 20px;
          flex-shrink: 0;
        }

        .item-content {
          flex: 1;
          min-width: 0;

          .item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;

            .title {
              font-size: 16px;
              font-weight: bold;
              color: #303133;
            }

            .time {
              font-size: 12px;
              color: #909399;
            }
          }

          .item-type {
            margin-bottom: 10px;
          }

          .item-desc {
            color: #606266;
            font-size: 14px;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            -webkit-line-clamp: 2;
            overflow: hidden;
          }
        }
      }
    }

    .pagination {
      margin-top: 20px;
      display: flex;
      justify-content: center;
    }
  }
}

.clear-dialog-content {
  text-align: center;
  padding: 20px 0;

  .warning-icon {
    color: #e6a23c;
    margin-bottom: 15px;
  }

  p {
    margin: 0;
    font-size: 16px;
    color: #606266;
  }
}

@media (max-width: 768px) {
  .history-page {
    padding: 15px;

    .history-list {
      .history-items {
        .history-item {
          flex-direction: column;
          padding: 15px;

          .item-image {
            width: 100%;
            height: 180px;
            margin: 0 0 15px 0;
          }

          .item-content {
            .item-header {
              flex-direction: column;
              align-items: flex-start;
              gap: 5px;
            }
          }
        }
      }
    }
  }
}
</style> 