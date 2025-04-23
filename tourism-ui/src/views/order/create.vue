<template>
  <div class="order-create page-container">
    <div class="container">
      <div class="breadcrumb mb-md">
        <el-breadcrumb>
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/attractions' }">景点</el-breadcrumb-item>
          <el-breadcrumb-item>创建订单</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <el-card v-loading="loading">
        <template v-if="attraction && tickets.length">
          <h1 class="page-title">{{ attraction.name }} - 门票预订</h1>
          
          <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" class="mt-lg">
            <!-- 门票选择 -->
            <el-form-item label="门票类型" prop="ticket_id">
              <el-radio-group v-model="form.ticket_id">
                <el-radio 
                  v-for="ticket in tickets" 
                  :key="ticket.id" 
                  :label="ticket.id"
                  class="ticket-radio"
                >
                  <div class="ticket-info">
                    <div class="ticket-name">{{ ticket.name }}</div>
                    <div class="ticket-price">¥{{ ticket.price }}</div>
                    <div class="ticket-desc">{{ ticket.description }}</div>
                  </div>
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <!-- 游玩日期 -->
            <el-form-item label="游玩日期" prop="visit_date">
              <el-date-picker
                v-model="form.visit_date"
                type="date"
                placeholder="选择游玩日期"
                :disabled-date="disabledDate"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>

            <!-- 购买数量 -->
            <el-form-item label="购买数量" prop="quantity">
              <el-input-number
                v-model="form.quantity"
                :min="1"
                :max="10"
                @change="calculateTotal"
              />
            </el-form-item>

            <!-- 游客信息 -->
            <el-form-item label="游客姓名" prop="visitor_name">
              <el-input v-model="form.visitor_name" placeholder="请输入游客姓名" />
            </el-form-item>

            <el-form-item label="联系电话" prop="visitor_phone">
              <el-input v-model="form.visitor_phone" placeholder="请输入联系电话" />
            </el-form-item>

            <el-form-item label="身份证号" prop="visitor_id_card">
              <el-input v-model="form.visitor_id_card" placeholder="请输入身份证号" />
            </el-form-item>

            <!-- 订单金额 -->
            <el-form-item>
              <div class="order-total">
                <span class="label">订单总额：</span>
                <span class="price">¥{{ totalPrice }}</span>
              </div>
            </el-form-item>

            <!-- 提交按钮 -->
            <el-form-item>
              <el-button type="primary" @click="submitOrder" :loading="submitting">
                提交订单
              </el-button>
              <el-button @click="$router.back()">返回</el-button>
            </el-form-item>
          </el-form>
        </template>
        <template v-else>
          <el-empty description="未找到相关景点或门票信息" />
        </template>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getAttractionDetail, getAttractionTickets } from '@/api/attraction'
import { createOrder } from '@/api/order'
import { useUserStore } from '@/store/user'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)

const loading = ref(false)
const submitting = ref(false)
const attraction = ref(null)
const tickets = ref([])

// 表单数据
const form = ref({
  attraction_id: route.query.attractionId,
  ticket_id: '',
  quantity: 1,
  visit_date: '',
  visitor_name: '',
  visitor_phone: '',
  visitor_id_card: ''
})

// 表单验证规则
const rules = {
  ticket_id: [{ required: true, message: '请选择门票类型', trigger: 'change' }],
  visit_date: [{ required: true, message: '请选择游玩日期', trigger: 'change' }],
  quantity: [{ required: true, message: '请选择购买数量', trigger: 'change' }],
  visitor_name: [{ required: true, message: '请输入游客姓名', trigger: 'blur' }],
  visitor_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  visitor_id_card: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
  ]
}

// 计算订单总额
const totalPrice = computed(() => {
  const ticket = tickets.value.find(t => t.id === form.value.ticket_id)
  return ticket ? (ticket.price * form.value.quantity).toFixed(2) : '0.00'
})

// 禁用的日期（今天之前的日期）
const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7
}

// 获取景点和门票信息
const fetchData = async () => {
  loading.value = true
  try {
    // 获取景点详情
    const attractionRes = await getAttractionDetail(form.value.attraction_id)
    if (attractionRes.code === 200 && attractionRes.data) {
      attraction.value = attractionRes.data
    } else {
      ElMessage.error('获取景点信息失败')
      return
    }

    // 获取门票信息
    const ticketsRes = await getAttractionTickets(form.value.attraction_id)
    if (ticketsRes.code === 200 && ticketsRes.data?.items) {
      tickets.value = ticketsRes.data.items
      if (tickets.value.length > 0) {
        form.value.ticket_id = tickets.value[0].id
      }
    } else {
      ElMessage.error('获取门票信息失败')
    }
  } catch (error) {
    ElMessage.error(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

// 提交订单
const submitOrder = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitting.value = true
    const res = await createOrder(form.value)
    
    if (res.code === 200 && res.data?.order_no) {
      ElMessage.success('订单创建成功')
      router.push(`/order/pay?orderNo=${res.data.order_no}`)
    } else {
      ElMessage.error(res.message || '创建订单失败')
    }
  } catch (error) {
    ElMessage.error(error.message || '创建订单失败')
  } finally {
    submitting.value = false
  }
}

// 初始化
onMounted(() => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再预订门票')
    router.push('/login')
    return
  }
  
  if (!form.value.attraction_id) {
    ElMessage.error('参数错误')
    router.push('/')
    return
  }

  fetchData()
})
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
}

.ticket-radio {
  display: block;
  margin-bottom: 15px;
}

.ticket-info {
  display: inline-block;
  margin-left: 10px;
}

.ticket-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.ticket-price {
  color: #f56c6c;
  font-size: 16px;
  margin-bottom: 5px;
}

.ticket-desc {
  color: #666;
  font-size: 13px;
}

.order-total {
  text-align: right;
  font-size: 16px;
}

.order-total .label {
  color: #666;
}

.order-total .price {
  color: #f56c6c;
  font-size: 24px;
  font-weight: bold;
  margin-left: 10px;
}
</style> 