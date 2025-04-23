<template>
  <div class="notification-page">
    <div class="container">
      <el-card class="notification-card">
        <template #header>
          <div class="card-header">
            <h2>通知中心</h2>
            <div class="header-actions">
              <el-radio-group v-model="filterType" @change="handleFilterChange">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="unread">未读</el-radio-button>
              </el-radio-group>
              <el-button 
                type="primary" 
                plain
                @click="handleMarkAllRead"
                :disabled="!hasUnread"
              >
                全部标记为已读
              </el-button>
            </div>
          </div>
        </template>

        <div class="notification-list" v-loading="loading">
          <el-empty v-if="!loading && notifications.length === 0" description="暂无通知" />

          <div v-else class="notification-items">
            <div 
              v-for="notification in notifications" 
              :key="notification.id" 
              class="notification-item"
              :class="{ unread: !notification.read_at }"
            >
              <div class="notification-icon">
                <el-icon :size="24">
                  <component :is="getNotificationIcon(notification.type)" />
                </el-icon>
              </div>

              <div class="notification-content" @click="handleReadNotification(notification)">
                <div class="notification-header">
                  <span class="title">{{ notification.title }}</span>
                  <span class="time">{{ formatDate(notification.created_at) }}</span>
                </div>
                <div class="notification-body">
                  {{ notification.content }}
                </div>
                <div class="notification-footer" v-if="notification.action_url">
                  <el-button 
                    type="primary" 
                    link 
                    @click.stop="handleAction(notification)"
                  >
                    查看详情
                  </el-button>
                </div>
              </div>

              <div class="notification-actions">
                <el-button 
                  type="danger" 
                  link
                  @click="handleDelete(notification)"
                >
                  删除
                </el-button>
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Bell,
  Message,
  Tickets,
  User,
  Calendar,
  Location,
  InfoFilled
} from '@element-plus/icons-vue'
import {
  getNotifications,
  markAsRead,
  deleteNotification
} from '@/api/notification'
import { formatDate } from '@/utils/date'

const router = useRouter()

// 状态数据
const loading = ref(false)
const notifications = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filterType = ref('all')

// 计算属性
const hasUnread = computed(() => {
  return notifications.value.some(item => !item.read_at)
})

// 获取通知图标
const getNotificationIcon = (type) => {
  const iconMap = {
    system: InfoFilled,
    message: Message,
    order: Tickets,
    user: User,
    activity: Calendar,
    attraction: Location,
    default: Bell
  }
  return iconMap[type] || iconMap.default
}

// 加载通知列表
const loadNotifications = async () => {
  loading.value = true
  try {
    const res = await getNotifications({
      page: page.value,
      per_page: pageSize.value,
      unread: filterType.value === 'unread'
    })
    notifications.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('获取通知列表失败:', error)
    ElMessage.error('获取通知列表失败')
  } finally {
    loading.value = false
  }
}

// 处理筛选变化
const handleFilterChange = () => {
  page.value = 1
  loadNotifications()
}

// 处理页码变化
const handleCurrentChange = (val) => {
  page.value = val
  loadNotifications()
}

// 处理每页数量变化
const handleSizeChange = (val) => {
  pageSize.value = val
  page.value = 1
  loadNotifications()
}

// 标记单个通知为已读
const handleReadNotification = async (notification) => {
  if (notification.read_at) return
  
  try {
    await markAsRead(notification.id)
    notification.read_at = new Date().toISOString()
  } catch (error) {
    console.error('标记已读失败:', error)
    ElMessage.error('标记已读失败')
  }
}

// 标记所有通知为已读
const handleMarkAllRead = async () => {
  try {
    await markAsRead()
    notifications.value = notifications.value.map(item => ({
      ...item,
      read_at: item.read_at || new Date().toISOString()
    }))
    ElMessage.success('已全部标记为已读')
  } catch (error) {
    console.error('标记全部已读失败:', error)
    ElMessage.error('标记全部已读失败')
  }
}

// 处理通知动作
const handleAction = (notification) => {
  if (notification.action_url) {
    router.push(notification.action_url)
  }
}

// 删除通知
const handleDelete = async (notification) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条通知吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    try {
      await deleteNotification(notification.id)
      ElMessage.success('删除成功')
      loadNotifications()
    } catch (error) {
      console.error('删除通知失败:', error)
      ElMessage.error('删除通知失败')
    }
  } catch {
    // 用户取消操作
  }
}

// 页面加载时获取通知列表
onMounted(() => {
  loadNotifications()
})
</script>

<style lang="scss" scoped>
.notification-page {
  padding: 30px 0;

  .notification-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h2 {
        margin: 0;
        font-size: 20px;
      }

      .header-actions {
        display: flex;
        gap: 15px;
      }
    }
  }

  .notification-list {
    .notification-items {
      .notification-item {
        display: flex;
        align-items: flex-start;
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

        &.unread {
          background-color: #f0f9ff;

          &:hover {
            background-color: #ecf5ff;
          }

          .notification-content {
            .notification-header {
              .title {
                font-weight: bold;
              }
            }
          }
        }

        .notification-icon {
          margin-right: 15px;
          color: #409eff;
        }

        .notification-content {
          flex: 1;
          min-width: 0;

          .notification-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;

            .title {
              font-size: 16px;
              color: #303133;
            }

            .time {
              font-size: 12px;
              color: #909399;
            }
          }

          .notification-body {
            color: #606266;
            line-height: 1.5;
            margin-bottom: 8px;
          }

          .notification-footer {
            display: flex;
            justify-content: flex-end;
          }
        }

        .notification-actions {
          margin-left: 15px;
          opacity: 0;
          transition: opacity 0.3s;
        }

        &:hover {
          .notification-actions {
            opacity: 1;
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

@media (max-width: 768px) {
  .notification-page {
    padding: 15px;

    .notification-card {
      .card-header {
        flex-direction: column;
        gap: 15px;

        .header-actions {
          width: 100%;
          flex-direction: column;
          gap: 10px;

          .el-radio-group {
            width: 100%;
            display: flex;

            .el-radio-button {
              flex: 1;

              :deep(.el-radio-button__inner) {
                width: 100%;
              }
            }
          }

          .el-button {
            width: 100%;
          }
        }
      }
    }

    .notification-list {
      .notification-items {
        .notification-item {
          padding: 15px;

          .notification-content {
            .notification-header {
              flex-direction: column;
              align-items: flex-start;
              gap: 5px;
            }
          }

          .notification-actions {
            opacity: 1;
          }
        }
      }
    }
  }
}
</style> 