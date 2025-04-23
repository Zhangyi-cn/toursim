<template>
  <div class="order-page">
    <div class="container">
      <el-card class="order-card">
        <template #header>
          <div class="card-header">
            <h2>我的订单</h2>
            <el-tabs v-model="activeTab" @tab-change="handleTabChange">
              <el-tab-pane label="全部" name="all" />
              <el-tab-pane label="待支付" name="unpaid" />
              <el-tab-pane label="已支付" name="paid" />
              <el-tab-pane label="已完成" name="completed" />
              <el-tab-pane label="已取消" name="cancelled" />
            </el-tabs>
          </div>
        </template>

        <div class="order-list" v-loading="loading">
          <el-empty
            v-if="!loading && !orders.length"
            :description="getEmptyText()"
          />

          <div v-else class="order-items">
            <div v-for="order in orders" :key="order.id" class="order-item">
              <div class="order-header">
                <div class="order-info">
                  <span class="order-number">订单号：{{ order.order_no }}</span>
                  <span class="order-time">下单时间：{{ formatDate(order.create_time) }}</span>
                </div>
                <el-tag :type="getStatusType(order.status)">
                  {{ getStatusText(order.status) }}
                </el-tag>
              </div>

              <div class="order-content">
                <div class="product-info">
                  <el-image
                    :src="order.attraction_image || '/placeholder.jpg'"
                    fit="cover"
                    class="product-image"
                  />
                  <div class="product-detail">
                    <h3>{{ order.attraction_name }}</h3>
                    <p class="description">{{ order.ticket_name }}</p>
                    <div class="specs">
                      <el-tag size="small" effect="plain">
                        游玩日期: {{ order.visit_date }}
                      </el-tag>
                      <el-tag size="small" effect="plain">
                        游客: {{ order.visitor_name }}
                      </el-tag>
                      <el-tag size="small" effect="plain">
                        电话: {{ order.visitor_phone }}
                      </el-tag>
                    </div>
                  </div>
                </div>

                <div class="order-amount">
                  <div class="price">
                    <span class="label">订单金额：</span>
                    <span class="amount">¥{{ order.total_amount.toFixed(2) }}</span>
                  </div>
                  <div class="quantity">
                    <span class="label">数量：</span>
                    <span>{{ order.quantity }}</span>
                  </div>
                </div>
              </div>

              <div class="order-footer">
                <div class="actions">
                  <el-button
                    v-if="order.status === 'unpaid'"
                    type="primary"
                    @click="handlePay(order)"
                  >
                    立即支付
                  </el-button>
                  <el-button
                    v-if="order.status === 'unpaid'"
                    @click="handleCancel(order)"
                  >
                    取消订单
                  </el-button>
                  <el-button
                    v-if="order.status === 'paid' || order.status === 'completed'"
                    @click="handleViewTicket(order)"
                  >
                    查看门票
                  </el-button>
                  <el-button
                    v-if="order.status === 'cancelled'"
                    type="danger"
                    @click="handleDelete(order)"
                  >
                    删除订单
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <div class="pagination" v-if="total > 0">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50]"
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

    <!-- 支付对话框 -->
    <el-dialog
      v-model="payDialogVisible"
      title="订单支付"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="pay-dialog">
        <div class="pay-amount">
          <span class="label">支付金额：</span>
          <span class="amount">¥{{ currentOrder?.amount.toFixed(2) }}</span>
        </div>

        <div class="pay-method">
          <h4>选择支付方式：</h4>
          <el-radio-group v-model="payMethod">
            <el-radio label="alipay">支付宝支付</el-radio>
            <el-radio label="wechat">微信支付</el-radio>
          </el-radio-group>
        </div>

        <div class="agreement">
          <el-checkbox v-model="payAgreement">
            我已阅读并同意《支付服务协议》
          </el-checkbox>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="payDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :disabled="!payMethod || !payAgreement"
            :loading="payLoading"
            @click="confirmPay"
          >
            确认支付
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Order } from '@/types/order'
import {
  getOrders,
  payOrder,
  cancelOrder,
  deleteOrder,
  getOrderPaymentStatus
} from '@/api/order'
import { formatDate } from '@/utils/date'
import { useRouter } from 'vue-router'

// 状态数据
const loading = ref(false)
const orders = ref<Order[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const activeTab = ref('all')

// 支付相关
const payDialogVisible = ref(false)
const payMethod = ref('')
const payAgreement = ref(false)
const payLoading = ref(false)
const currentOrder = ref<Order | null>(null)

const router = useRouter()

// 获取订单列表
const loadOrders = async () => {
  loading.value = true
  try {
    const res = await getOrders({
      page: currentPage.value,
      page_size: pageSize.value,
      status: activeTab.value === 'all' ? undefined : activeTab.value as Order['status']
    })
    orders.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (error: any) {
    console.error('获取订单列表失败:', error)
    ElMessage.error(error.message || '获取订单列表失败')
  } finally {
    loading.value = false
  }
}

// 处理分页变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadOrders()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadOrders()
}

// 处理标签页切换
const handleTabChange = () => {
  currentPage.value = 1
  loadOrders()
}

// 获取状态文本和类型
const getStatusText = (status: Order['status']) => {
  const statusMap: Record<Order['status'], string> = {
    pending: '待支付',
    paid: '已支付',
    completed: '已完成',
    cancelled: '已取消',
    refunded: '已退款'
  }
  return statusMap[status] || status
}

const getStatusType = (status: Order['status']) => {
  const typeMap: Record<Order['status'], string> = {
    pending: 'warning',
    paid: 'success',
    completed: 'success',
    cancelled: 'info',
    refunded: 'info'
  }
  return typeMap[status] || 'info'
}

// 处理支付
const handlePay = (order: Order) => {
  currentOrder.value = order
  payDialogVisible.value = true
}

// 确认支付
const confirmPay = async () => {
  if (!currentOrder.value || !payMethod.value) return
  
  payLoading.value = true
  try {
    await payOrder(currentOrder.value.id, payMethod.value)
    ElMessage.success('支付成功')
    payDialogVisible.value = false
    loadOrders()
  } catch (error: any) {
    ElMessage.error(error.message || '支付失败')
  } finally {
    payLoading.value = false
  }
}

// 取消订单
const handleCancel = async (order: Order) => {
  try {
    await ElMessageBox.confirm('确定要取消该订单吗？', '提示', {
      type: 'warning'
    })
    await cancelOrder(order.id)
    ElMessage.success('订单已取消')
    loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '取消订单失败')
    }
  }
}

// 查看门票
const handleViewTicket = (order: Order) => {
  router.push(`/order/${order.id}/ticket`)
}

// 删除订单
const handleDelete = async (order: Order) => {
  try {
    await ElMessageBox.confirm('确定要删除该订单吗？删除后无法恢复', '提示', {
      type: 'warning'
    })
    await deleteOrder(order.id)
    ElMessage.success('订单已删除')
    loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除订单失败')
    }
  }
}

// 获取空状态文本
const getEmptyText = () => {
  const textMap: Record<string, string> = {
    all: '暂无订单',
    unpaid: '暂无待支付订单',
    paid: '暂无已支付订单',
    completed: '暂无已完成订单',
    cancelled: '暂无已取消订单'
  }
  return textMap[activeTab.value] || '暂无订单'
}

onMounted(() => {
  loadOrders()
})
</script>

<style lang="scss" scoped>
.order-page {
  padding: 30px 0;

  .order-card {
    .card-header {
      h2 {
        margin: 0 0 20px;
        font-size: 20px;
        color: #303133;
      }
    }

    .order-list {
      min-height: 300px;

      .order-items {
        .order-item {
          border: 1px solid #ebeef5;
          border-radius: 4px;
          margin-bottom: 20px;
          overflow: hidden;

          .order-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background-color: #f5f7fa;

            .order-info {
              .order-number {
                margin-right: 20px;
                color: #303133;
              }

              .order-time {
                color: #909399;
              }
            }
          }

          .order-content {
            padding: 20px;
            display: flex;
            gap: 20px;

            .product-info {
              flex: 1;
              display: flex;
              gap: 15px;

              .product-image {
                width: 120px;
                height: 90px;
                border-radius: 4px;
                flex-shrink: 0;
              }

              .product-detail {
                flex: 1;
                min-width: 0;

                h3 {
                  margin: 0 0 10px;
                  font-size: 16px;
                  color: #303133;
                }

                .description {
                  margin: 0 0 10px;
                  font-size: 14px;
                  color: #606266;
                }

                .specs {
                  .el-tag {
                    margin: 0 5px 5px 0;
                  }
                }
              }
            }

            .order-amount {
              width: 200px;
              text-align: right;
              flex-shrink: 0;

              .price {
                margin-bottom: 10px;

                .label {
                  color: #909399;
                }

                .amount {
                  font-size: 18px;
                  color: #f56c6c;
                  margin-left: 5px;
                }
              }

              .quantity {
                color: #606266;

                .label {
                  color: #909399;
                }
              }
            }
          }

          .order-footer {
            padding: 15px 20px;
            border-top: 1px solid #ebeef5;
            display: flex;
            justify-content: flex-end;

            .actions {
              .el-button {
                margin-left: 10px;
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

.pay-dialog {
  .pay-amount {
    margin-bottom: 20px;
    text-align: center;

    .label {
      font-size: 16px;
      color: #606266;
    }

    .amount {
      font-size: 24px;
      color: #f56c6c;
      margin-left: 10px;
    }
  }

  .pay-method {
    margin-bottom: 20px;

    h4 {
      margin: 0 0 10px;
      font-size: 14px;
      color: #606266;
    }
  }

  .agreement {
    color: #606266;
  }
}

@media (max-width: 768px) {
  .order-page {
    padding: 15px;

    .order-card {
      .order-list {
        .order-items {
          .order-item {
            .order-header {
              flex-direction: column;
              align-items: flex-start;
              gap: 10px;
            }

            .order-content {
              flex-direction: column;

              .order-amount {
                width: 100%;
                text-align: left;
                display: flex;
                justify-content: space-between;
                align-items: center;
              }
            }
          }
        }
      }
    }
  }
}
</style>
 