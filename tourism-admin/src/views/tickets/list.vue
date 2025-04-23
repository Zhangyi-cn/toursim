<template>
  <div class="tickets-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>门票列表</span>
          <el-button type="primary" @click="handleAdd">新增门票</el-button>
        </div>
      </template>

      <el-table :data="tickets" v-loading="loading" border>
        <el-table-column prop="name" label="门票名称" />
        <el-table-column prop="attraction" label="所属景点" />
        <el-table-column prop="type" label="门票类型">
          <template #default="{ row }">
            <el-tag>{{ row.type === 1 ? '成人票' : '儿童票' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格">
          <template #default="{ row }">
            ¥{{ row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '在售' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="primary" link @click="handleDelete(row)">删除</el-button>
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
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增门票' : '编辑门票'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="门票名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入门票名称" />
        </el-form-item>
        <el-form-item label="所属景点" prop="attractionId">
          <el-select v-model="form.attractionId" placeholder="请选择景点">
            <el-option
              v-for="item in attractions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="门票类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择门票类型">
            <el-option label="成人票" :value="1" />
            <el-option label="儿童票" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number
            v-model="form.price"
            :precision="2"
            :step="0.1"
            :min="0"
          />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="form.stock" :min="0" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="form.status"
            :active-value="1"
            :inactive-value="0"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tickets = ref([])
const attractions = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const dialogType = ref('add')
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  attractionId: '',
  type: 1,
  price: 0,
  stock: 0,
  status: 1
})

const rules = {
  name: [
    { required: true, message: '请输入门票名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  attractionId: [
    { required: true, message: '请选择所属景点', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请选择门票类型', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' }
  ],
  stock: [
    { required: true, message: '请输入库存', trigger: 'blur' }
  ]
}

// 获取门票列表
const getTickets = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取门票列表
    loading.value = false
  } catch (error) {
    loading.value = false
    ElMessage.error('获取门票列表失败')
  }
}

// 获取景点列表
const getAttractions = async () => {
  try {
    // TODO: 调用API获取景点列表
  } catch (error) {
    ElMessage.error('获取景点列表失败')
  }
}

// 处理新增门票
const handleAdd = () => {
  dialogType.value = 'add'
  form.name = ''
  form.attractionId = ''
  form.type = 1
  form.price = 0
  form.stock = 0
  form.status = 1
  dialogVisible.value = true
}

// 处理编辑门票
const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  form.name = row.name
  form.attractionId = row.attractionId
  form.type = row.type
  form.price = row.price
  form.stock = row.stock
  form.status = row.status
  dialogVisible.value = true
}

// 处理删除门票
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确认删除该门票吗？', '提示', {
      type: 'warning'
    })
    // TODO: 调用API删除门票
    ElMessage.success('删除成功')
    getTickets()
  } catch {
    // 用户取消删除
  }
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // TODO: 调用API保存门票
        ElMessage.success(dialogType.value === 'add' ? '新增成功' : '编辑成功')
        dialogVisible.value = false
        getTickets()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '新增失败' : '编辑失败')
      }
    }
  })
}

// 处理每页数量变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  getTickets()
}

// 处理页码变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  getTickets()
}

onMounted(() => {
  getTickets()
  getAttractions()
})
</script>

<style scoped>
.tickets-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 