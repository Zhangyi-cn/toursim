<template>
  <div class="dashboard-container">
    <!-- 数据概览 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>总用户数</span>
              <el-tag type="success" size="small">{{ userTrend }}</el-tag>
            </div>
          </template>
          <div class="card-body">
            <div class="number">{{ dashboardData.userCount }}</div>
            <div class="chart">
              <small-line-chart :data="userChartData" />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>总订单数</span>
              <el-tag type="warning" size="small">{{ orderTrend }}</el-tag>
            </div>
          </template>
          <div class="card-body">
            <div class="number">{{ dashboardData.orderCount }}</div>
            <div class="chart">
              <small-line-chart :data="orderChartData" />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>总收入</span>
              <el-tag type="danger" size="small">{{ revenueTrend }}</el-tag>
            </div>
          </template>
          <div class="card-body">
            <div class="number">¥{{ dashboardData.totalRevenue }}</div>
            <div class="chart">
              <small-line-chart :data="revenueChartData" />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="data-card">
          <template #header>
            <div class="card-header">
              <span>总景点数</span>
              <el-tag type="info" size="small">{{ attractionTrend }}</el-tag>
            </div>
          </template>
          <div class="card-body">
            <div class="number">{{ dashboardData.attractionCount }}</div>
            <div class="chart">
              <small-line-chart :data="attractionChartData" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>订单趋势</span>
              <el-radio-group v-model="orderTimeRange" size="small">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
                <el-radio-button label="year">本年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <line-chart :data="orderTrendData" />
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>收入趋势</span>
              <el-radio-group v-model="revenueTimeRange" size="small">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
                <el-radio-button label="year">本年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <line-chart :data="revenueTrendData" />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 热门景点和最新订单 -->
    <el-row :gutter="20" class="data-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>热门景点</span>
              <el-button type="text" @click="handleViewMore('attractions')">查看更多</el-button>
            </div>
          </template>
          <el-table :data="hotAttractions" stripe style="width: 100%">
            <el-table-column prop="name" label="景点名称" />
            <el-table-column prop="orderCount" label="订单数" width="100" />
            <el-table-column prop="revenue" label="收入" width="120">
              <template #default="{ row }">
                ¥{{ row.revenue }}
              </template>
            </el-table-column>
            <el-table-column prop="rating" label="评分" width="100">
              <template #default="{ row }">
                <el-rate v-model="row.rating" disabled text-color="#ff9900" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最新订单</span>
              <el-button type="text" @click="handleViewMore('orders')">查看更多</el-button>
            </div>
          </template>
          <el-table :data="latestOrders" stripe style="width: 100%">
            <el-table-column prop="orderNo" label="订单号" width="120" />
            <el-table-column prop="attractionName" label="景点" />
            <el-table-column prop="amount" label="金额" width="100">
              <template #default="{ row }">
                ¥{{ row.amount }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getOrderStatusType(row.status)">
                  {{ getOrderStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardData } from '@/api/dashboard'
import SmallLineChart from './components/SmallLineChart.vue'
import LineChart from './components/LineChart.vue'

const router = useRouter()

// 仪表盘数据
const dashboardData = ref({
  userCount: 0,
  orderCount: 0,
  totalRevenue: 0,
  attractionCount: 0
})

// 趋势标签
const userTrend = ref('↑ 12%')
const orderTrend = ref('↑ 8%')
const revenueTrend = ref('↑ 15%')
const attractionTrend = ref('↑ 5%')

// 小图表数据
const userChartData = ref([30, 40, 35, 50, 45, 55, 70])
const orderChartData = ref([100, 120, 110, 130, 125, 135, 150])
const revenueChartData = ref([5000, 6000, 5500, 7000, 6500, 7500, 8000])
const attractionChartData = ref([50, 52, 53, 54, 55, 57, 60])

// 时间范围选择
const orderTimeRange = ref('week')
const revenueTimeRange = ref('week')

// 趋势图数据
const orderTrendData = ref({
  labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  datasets: [{
    label: '订单数',
    data: [100, 120, 110, 130, 125, 135, 150],
    borderColor: '#409EFF',
    fill: false
  }]
})

const revenueTrendData = ref({
  labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  datasets: [{
    label: '收入',
    data: [5000, 6000, 5500, 7000, 6500, 7500, 8000],
    borderColor: '#67C23A',
    fill: false
  }]
})

// 热门景点数据
const hotAttractions = ref([
  { name: '故宫', orderCount: 1200, revenue: 120000, rating: 4.8 },
  { name: '长城', orderCount: 1000, revenue: 100000, rating: 4.7 },
  { name: '西湖', orderCount: 800, revenue: 80000, rating: 4.6 },
  { name: '黄山', orderCount: 600, revenue: 60000, rating: 4.5 },
  { name: '张家界', orderCount: 500, revenue: 50000, rating: 4.4 }
])

// 最新订单数据
const latestOrders = ref([
  { orderNo: 'DD20240101001', attractionName: '故宫', amount: 100, status: 1 },
  { orderNo: 'DD20240101002', attractionName: '长城', amount: 200, status: 2 },
  { orderNo: 'DD20240101003', attractionName: '西湖', amount: 150, status: 3 },
  { orderNo: 'DD20240101004', attractionName: '黄山', amount: 300, status: 4 },
  { orderNo: 'DD20240101005', attractionName: '张家界', amount: 250, status: 5 }
])

// 获取订单状态类型
const getOrderStatusType = (status: number) => {
  const types = {
    1: 'warning',   // 待支付
    2: 'success',   // 已支付
    3: 'primary',   // 已使用
    4: 'info',      // 已完成
    5: 'danger'     // 已取消
  }
  return types[status] || 'info'
}

// 获取订单状态文本
const getOrderStatusText = (status: number) => {
  const texts = {
    1: '待支付',
    2: '已支付',
    3: '已使用',
    4: '已完成',
    5: '已取消'
  }
  return texts[status] || '未知'
}

// 查看更多
const handleViewMore = (type: string) => {
  router.push(`/${type}`)
}

// 获取仪表盘数据
const fetchDashboardData = async () => {
  try {
    const res = await getDashboardData()
    dashboardData.value = res.data
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
  
  .el-row {
    margin-bottom: 20px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .data-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .card-body {
      position: relative;
      height: 100px;
      
      .number {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
      }
      
      .chart {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 50px;
      }
    }
  }
  
  .chart-row {
    .chart-container {
      height: 300px;
    }
  }
  
  .data-row {
    .el-card {
      margin-bottom: 0;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
}
</style> 