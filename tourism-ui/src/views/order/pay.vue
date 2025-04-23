<template>
  <div class="order-pay page-container">
    <div class="container">
      <div class="breadcrumb mb-md">
        <el-breadcrumb>
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/order' }">订单</el-breadcrumb-item>
          <el-breadcrumb-item>订单支付</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <el-card v-loading="loading">
        <template v-if="order">
          <h1 class="page-title">订单支付</h1>
          
          <!-- 订单信息 -->
          <div class="order-info">
            <div class="info-item">
              <span class="label">订单编号：</span>
              <span class="value">{{ order.order_no }}</span>
            </div>
            <div class="info-item">
              <span class="label">景点名称：</span>
              <span class="value">{{ order.attraction_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">门票类型：</span>
              <span class="value">{{ order.ticket_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">游玩日期：</span>
              <span class="value">{{ order.visit_date }}</span>
            </div>
            <div class="info-item">
              <span class="label">购买数量：</span>
              <span class="value">{{ order.quantity }}张</span>
            </div>
            <div class="info-item">
              <span class="label">游客姓名：</span>
              <span class="value">{{ order.visitor_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">联系电话：</span>
              <span class="value">{{ order.visitor_phone }}</span>
            </div>
            <div class="info-item">
              <span class="label">订单金额：</span>
              <span class="value price">¥{{ order.total_amount }}</span>
            </div>
          </div>

          <!-- 支付方式选择 -->
          <div class="payment-methods">
            <h2 class="section-title">选择支付方式</h2>
            <el-radio-group v-model="paymentMethod">
              <el-radio label="wechat" class="payment-radio">
                <i class="payment-icon wechat"></i>
                微信支付
              </el-radio>
              <el-radio label="alipay" class="payment-radio">
                <i class="payment-icon alipay"></i>
                支付宝
              </el-radio>
            </el-radio-group>
          </div>

          <!-- 支付按钮 -->
          <div class="actions">
            <el-button type="primary" :loading="paying" @click="handlePay">
              立即支付
            </el-button>
            <el-button @click="$router.push('/order')">返回订单列表</el-button>
          </div>
        </template>
        <template v-else>
          <el-empty description="未找到订单信息" />
        </template>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOrderDetail, payOrder } from '@/api/order'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const paying = ref(false)
const order = ref(null)
const paymentMethod = ref('wechat')

// 获取订单详情
const fetchOrderDetail = async () => {
  loading.value = true
  try {
    const res = await getOrderDetail(route.query.orderNo)
    if (res.code === 200 && res.data) {
      order.value = res.data
    } else {
      ElMessage.error('获取订单信息失败')
      router.push('/order')
    }
  } catch (error) {
    ElMessage.error(error.message || '获取订单信息失败')
    router.push('/order')
  } finally {
    loading.value = false
  }
}

// 处理支付
const handlePay = async () => {
  if (!order.value || !paymentMethod.value) return
  
  paying.value = true
  try {
    const res = await payOrder({
      order_no: order.value.order_no,
      payment_method: paymentMethod.value
    })
    
    if (res.code === 200 && res.data?.payment_url) {
      // 跳转到支付页面
      window.location.href = res.data.payment_url
    } else {
      ElMessage.error(res.message || '发起支付失败')
    }
  } catch (error) {
    ElMessage.error(error.message || '发起支付失败')
  } finally {
    paying.value = false
  }
}

// 初始化
onMounted(() => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  if (!route.query.orderNo) {
    ElMessage.error('参数错误')
    router.push('/order')
    return
  }

  fetchOrderDetail()
})
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin: 30px 0 20px;
}

.order-info {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
}

.info-item {
  margin-bottom: 15px;
  line-height: 24px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  color: #666;
  margin-right: 10px;
}

.info-item .value {
  color: #333;
}

.info-item .price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
}

.payment-methods {
  margin: 30px 0;
}

.payment-radio {
  display: block;
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: all 0.3s;
}

.payment-radio:hover {
  border-color: #409eff;
}

.payment-icon {
  display: inline-block;
  width: 24px;
  height: 24px;
  margin-right: 10px;
  vertical-align: middle;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.payment-icon.wechat {
  background-image: url('@/assets/images/wechat-pay.png');
}

.payment-icon.alipay {
  background-image: url('@/assets/images/alipay.png');
}

.actions {
  margin-top: 30px;
  text-align: center;
}
</style> 