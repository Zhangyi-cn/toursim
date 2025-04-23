<template>
  <div class="banners">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>轮播图管理</span>
          <el-button type="primary" @click="handleAdd">新增轮播图</el-button>
        </div>
      </template>

      <el-table :data="banners" v-loading="loading" border>
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column label="图片" width="200">
          <template #default="{ row }">
            <el-image
              :src="row.image_url"
              :preview-src-list="[row.image_url]"
              class="banner-image"
              @error="handleImageError(row)"
            >
              <template #error>
                <div class="image-error">
                  <el-icon><PictureFilled /></el-icon>
                  <span>加载失败</span>
                </div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column prop="link_url" label="链接" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="100" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              :active-value="true"
              :inactive-value="false"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增轮播图' : '编辑轮播图'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="图片" prop="image_url">
          <el-upload
            class="banner-uploader"
            :show-file-list="false"
            :before-upload="beforeImageUpload"
            :http-request="customImageUpload"
          >
            <el-image
              v-if="form.image_url && !uploading"
              :src="form.image_url"
              fit="cover"
              class="banner-image"
            />
            <div v-else-if="uploading" class="upload-loading">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <span>上传中...</span>
            </div>
            <el-icon v-else class="banner-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="链接" prop="link_url">
          <el-input v-model="form.link_url" placeholder="请输入链接" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="99" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="form.is_active"
            :active-value="true"
            :inactive-value="false"
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
import type { FormInstance, UploadProps } from 'element-plus'
import { Plus, Loading, PictureFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBannerList, createBanner, updateBanner, deleteBanner } from '../../api/banner'
import { uploadImage } from '../../api/upload'
import type { Banner, BannerForm } from '../../api/banner'
import { handleApiError, withErrorHandling } from '@/utils/error-handler'

const loading = ref(false)
const uploading = ref(false)
const banners = ref<Banner[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const isInitialLoad = ref(true)

const form = reactive<BannerForm>({
  title: '',
  image_url: '',
  link_url: '',
  description: '',
  sort_order: 0,
  is_active: true
})

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  image_url: [
    { required: true, message: '请上传图片', trigger: 'change' }
  ],
  link_url: [
    { required: true, message: '请输入链接', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入描述', trigger: 'blur' }
  ],
  sort_order: [
    { required: true, message: '请输入排序', trigger: 'blur' }
  ]
}

// 处理图片加载错误
const handleImageError = (row: Banner) => {
  console.error('图片加载失败:', row.image_url)
}

// 获取轮播图列表
const getBanners = async () => {
  loading.value = true
  console.log('开始加载轮播图列表...')
  try {
    const { data } = await getBannerList({
      page: currentPage.value,
      pageSize: pageSize.value
    })
    console.log('轮播图列表加载成功:', data)
    
    // 处理每个轮播图的图片URL
    banners.value = data.items.map((item: Banner) => {
      if (item.image_url) {
        console.log('原始图片URL:', item.image_url)
        
        // 如果是相对路径且不以/开头
        if (!item.image_url.startsWith('http') && !item.image_url.startsWith('/')) {
          item.image_url = '/' + item.image_url;
        }
        
        // 添加服务器地址前缀
        if (!item.image_url.startsWith('http')) {
          item.image_url = `http://localhost:5000/static/images${item.image_url}`
        }
        
        console.log('处理后图片URL:', item.image_url)
        
        // 验证URL是否可访问
        const img = new Image();
        img.src = item.image_url;
        img.onerror = () => {
          console.error('图片URL不可访问:', item.image_url);
        };
      } else {
        console.warn('轮播图缺少图片URL:', item.title)
      }
      return item
    })
    
    console.log('处理后的轮播图列表:', banners.value)
    total.value = data.pagination.total
    setTimeout(() => {
      isInitialLoad.value = false
    }, 500)
  } catch (error) {
    console.error('获取轮播图列表失败:', error)
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

// 图片上传前校验
const beforeImageUpload: UploadProps['beforeUpload'] = (file) => {
  console.log('上传前校验图片:', file.name, file.type, file.size)
  const isImage = /^image\//.test(file.type)
  if (!isImage) {
    console.warn('上传文件不是图片类型')
    ElMessage.error('只能上传图片文件！')
    return false
  }

  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    console.warn('上传图片超过2MB限制')
    ElMessage.error('图片大小不能超过 2MB！')
    return false
  }

  console.log('图片校验通过')
  return true
}

// 自定义图片上传
const customImageUpload = async (options: any) => {
  console.log('开始上传图片:', options.file.name)
  uploading.value = true
  try {
    const { data } = await uploadImage(options.file)
    console.log('图片上传成功, 返回数据:', data)
    
    // 确保URL格式正确
    let imageUrl = data.url;
    if (!imageUrl.startsWith('/') && !imageUrl.startsWith('http')) {
      imageUrl = '/' + imageUrl;
    }
    
    // 添加服务器地址前缀
    if (!imageUrl.startsWith('http')) {
      imageUrl = `http://localhost:5000/static/images${imageUrl}`;
    }
    
    form.image_url = imageUrl;
    console.log('设置表单图片URL:', form.image_url)
    
    // 验证URL
    const img = new Image();
    img.src = form.image_url;
    img.onload = () => console.log('图片URL有效，可以正常加载');
    img.onerror = () => console.error('图片URL无法加载');
    
  } catch (error) {
    console.error('上传图片失败:', error)
    handleApiError(error)
  } finally {
    uploading.value = false
  }
}

// 新增轮播图
const handleAdd = () => {
  console.log('打开新增轮播图表单')
  dialogType.value = 'add'
  form.title = ''
  form.image_url = ''
  form.link_url = ''
  form.description = ''
  form.sort_order = 0
  form.is_active = true
  dialogVisible.value = true
}

// 编辑轮播图
const handleEdit = (row: Banner) => {
  console.log('打开编辑轮播图表单:', row)
  dialogType.value = 'edit'
  Object.assign(form, row)
  dialogVisible.value = true
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      console.log('表单验证通过, 准备提交:', form)
      try {
        if (dialogType.value === 'add') {
          console.log('发送创建轮播图请求')
          await createBanner(form)
          console.log('创建轮播图成功')
          ElMessage.success('新增成功')
        } else {
          console.log('发送更新轮播图请求')
          await updateBanner(form)
          console.log('更新轮播图成功')
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        getBanners()
      } catch (error) {
        console.error(dialogType.value === 'add' ? '新增失败:' : '更新失败:', error)
        handleApiError(error)
      }
    } else {
      console.warn('表单验证失败')
    }
  })
}

// 处理删除
const handleDelete = async (row: Banner) => {
  console.log('准备删除轮播图:', row)
  try {
    await ElMessageBox.confirm('确认删除该轮播图吗？', '提示', {
      type: 'warning'
    })
    console.log('用户确认删除, 发送删除请求')
    await deleteBanner(row.id)
    console.log('删除轮播图成功')
    ElMessage.success('删除成功')
    getBanners()
  } catch (error) {
    console.log('删除操作取消或失败:', error)
    // 用户取消操作
  }
}

// 处理状态变更
const handleStatusChange = async (row: Banner) => {
  if (isInitialLoad.value) return
  
  console.log('状态变更:', row.title, '新状态:', row.is_active)
  
  const originalStatus = row.is_active
  
  await withErrorHandling(async () => {
    await updateBanner({ ...row, is_active: row.is_active })
    console.log('状态更新成功')
    ElMessage.success('更新成功')
  }).catch(() => {
    // 如果发生错误,恢复状态
    row.is_active = !originalStatus
    console.log('已恢复状态为:', row.is_active)
  })
}

// 处理每页数量变化
const handleSizeChange = (val: number) => {
  console.log('每页数量变更为:', val)
  pageSize.value = val
  getBanners()
}

// 处理页码变化
const handleCurrentChange = (val: number) => {
  console.log('页码变更为:', val)
  currentPage.value = val
  getBanners()
}

// 初始化
onMounted(() => {
  console.log('轮播图组件已挂载, 初始化加载数据')
  getBanners()
})
</script>

<style scoped>
.banners {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.banner-image {
  width: 160px;
  height: 90px;
  border-radius: 4px;
  object-fit: cover;
  display: block;
}

.banner-uploader {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.banner-uploader:hover {
  border-color: var(--el-color-primary);
}

.banner-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 160px;
  height: 90px;
  text-align: center;
  line-height: 90px;
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

.upload-loading {
  width: 160px;
  height: 90px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
}

.loading-icon {
  font-size: 24px;
  animation: rotate 1.5s linear infinite;
  margin-bottom: 8px;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.image-error {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 12px;
}

.image-error i {
  font-size: 24px;
  margin-bottom: 8px;
}
</style> 