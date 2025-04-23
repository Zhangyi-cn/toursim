<template>
  <div class="orders">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
          <div class="header-operations">
            <el-input
              v-model="searchForm.keyword"
              placeholder="请输入订单号/用户名"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-select v-model="searchForm.status" placeholder="订单状态" clearable @change="handleSearch">
              <el-option label="待支付" :value="0" />
              <el-option label="已支付" :value="1" />
              <el-option label="已取消" :value="2" />
              <el-option label="已退款" :value="3" />
            </el-select>
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="handleSearch"
            />
          </div>
        </div>
      </template>

      <el-table :data="orders" v-loading="loading" border>
        <el-table-column prop="orderNo" label="订单号" width="180" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="attractionName" label="景点名称" />
        <el-table-column prop="ticketType" label="门票类型">
          <template #default="{ row }">
            <el-tag>{{ row.ticketType === 1 ? '成人票' : '儿童票' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="amount" label="金额">
          <template #default="{ row }">
            ¥{{ row.amount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleDetail(row)">详情</el-button>
              <el-button
                v-if="row.status === 1"
                type="primary"
                link
                @click="handleRefund(row)"
              >退款</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          @update:current-page="currentPage = $event"
          @update:page-size="pageSize = $event"
        />
      </div>
    </el-card>

    <!-- 订单详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="订单详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ currentOrder.orderNo }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentOrder.username }}</el-descriptions-item>
        <el-descriptions-item label="景点名称">{{ currentOrder.attractionName }}</el-descriptions-item>
        <el-descriptions-item label="门票类型">
          {{ currentOrder.ticketType === 1 ? '成人票' : '儿童票' }}
        </el-descriptions-item>
        <el-descriptions-item label="数量">{{ currentOrder.quantity }}</el-descriptions-item>
        <el-descriptions-item label="金额">¥{{ currentOrder.amount?.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentOrder.status)">
            {{ getStatusText(currentOrder.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentOrder.createTime }}</el-descriptions-item>
        <el-descriptions-item label="支付时间" v-if="currentOrder.payTime">
          {{ currentOrder.payTime }}
        </el-descriptions-item>
        <el-descriptions-item label="退款时间" v-if="currentOrder.refundTime">
          {{ currentOrder.refundTime }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const orders = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const detailVisible = ref(false)
const currentOrder = ref({})

const searchForm = reactive({
  keyword: '',
  status: '',
  dateRange: []
})

// 获取订单列表
const getOrders = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取订单列表
    loading.value = false
  } catch (error) {
    loading.value = false
    ElMessage.error('获取订单列表失败')
  }
}

// 获取状态类型
const getStatusType = (status: number) => {
  switch (status) {
    case 0:
      return 'warning'
    case 1:
      return 'success'
    case 2:
      return 'info'
    case 3:
      return ''
    default:
      return ''
  }
}

// 获取状态文本
const getStatusText = (status: number) => {
  switch (status) {
    case 0:
      return '待支付'
    case 1:
      return '已支付'
    case 2:
      return '已取消'
    case 3:
      return '已退款'
    default:
      return '未知'
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  getOrders()
}

// 处理查看详情
const handleDetail = (row: any) => {
  currentOrder.value = row
  detailVisible.value = true
}

// 处理退款
const handleRefund = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认为该订单退款吗？', '提示', {
      type: 'warning'
    })
    // TODO: 调用API处理退款
    ElMessage.success('退款成功')
    getOrders()
  } catch {
    // 用户取消退款
  }
}

// 处理每页数量变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  getOrders()
}

// 处理页码变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getOrders()
}

// 初始化
getOrders()
</script>

<style scoped>
.orders {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-operations {
  display: flex;
  gap: 10px;
  align-items: center;
}

.header-operations :deep(.el-input) {
  width: 200px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 