<template>
  <div class="guide-edit-page">
    <div class="page-header">
      <h1>{{ isEdit ? '编辑攻略' : '创建攻略' }}</h1>
    </div>

    <div class="edit-content" v-loading="loading">
      <el-form 
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        class="guide-form"
      >
        <!-- 标题 -->
        <el-form-item label="标题" prop="title">
          <el-input 
            v-model="formData.title" 
            placeholder="请输入攻略标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <!-- 分类 -->
        <el-form-item label="分类" prop="category_id">
          <el-select 
            v-model="formData.category_id" 
            placeholder="请选择分类"
            class="category-select"
          >
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <!-- 封面图片 -->
        <el-form-item label="封面图片" prop="cover_image">
          <el-upload
            class="cover-upload"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :before-upload="beforeUpload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :http-request="customUpload"
          >
            <div 
              class="upload-area"
              :class="{ 'has-image': formData.cover_image }"
            >
              <el-image
                v-if="formData.cover_image"
                :src="formData.cover_image"
                fit="cover"
                class="preview-image"
              />
              <div v-else class="upload-placeholder">
                <el-icon><Plus /></el-icon>
                <span>点击上传封面图片</span>
              </div>
            </div>
          </el-upload>
          <div class="upload-tip">建议尺寸: 1200x675px，支持 jpg、png 格式</div>
        </el-form-item>

        <!-- 内容编辑器 -->
        <el-form-item label="正文内容" prop="content">
          <div class="editor-wrapper">
            <div v-if="!editorReady" class="editor-loading">
              <el-skeleton :rows="10" animated />
              <div class="loading-text">编辑器加载中...</div>
            </div>
            <div v-else>
              <Toolbar
                :editor="editorRef"
                :defaultConfig="toolbarConfig"
                :mode="mode"
                style="border-bottom: 1px solid #ccc"
              />
              <Editor
                v-model="formData.content"
                :defaultConfig="editorConfig"
                :mode="mode"
                @onCreated="handleCreated"
                style="height: 500px"
              />
            </div>
          </div>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item class="form-actions">
          <el-button @click="handleCancel">取消</el-button>
          <el-button 
            type="primary" 
            :loading="submitting"
            @click="handleSubmit"
          >
            {{ isEdit ? '保存修改' : '发布攻略' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 添加地图组件 -->
    <TravelRouteMap ref="travelRouteMapRef" @insert="handleMapInsert" />
  </div>
</template>

<script setup lang="ts">
import { ref, shallowRef, onBeforeUnmount, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, UploadProps } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { getGuideCategories, createGuide, updateGuide, getGuideDetail } from '@/api/travel-guide'
import type { GuideCategory } from '@/api/travel-guide'
import type { IDomEditor, IEditorConfig, IToolbarConfig } from '@wangeditor/editor'
import request from '@/utils/request'
import TravelRouteMap from '@/components/TravelRouteMap.vue'
import { insertTravelRouteMenuConf } from '@/utils/editor/travelRouteMap'
import { Boot } from '@wangeditor/editor'

// 添加Vue TypeScript定义
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    // ...
  }
}

// 添加AMap全局声明
declare global {
  interface Window {
    AMap: any;
    wangEditor?: any;
  }
}

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()

// 是否是编辑模式
const isEdit = computed(() => route.name === 'EditGuide')

// 状态数据
const loading = ref(false)
const submitting = ref(false)
const categories = ref<GuideCategory[]>([])

// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef<IDomEditor>()

// 添加编辑器初始化完成状态
const editorReady = ref(false)

// 表单数据
const formData = ref({
  title: '',
  category_id: undefined as number | undefined,
  cover_image: '',
  content: ''
})

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 5, max: 100, message: '标题长度应在 5 到 100 个字符之间', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' },
    { min: 100, message: '内容至少需要 100 个字符', trigger: 'blur' }
  ]
}

// 上传相关配置
const uploadUrl = '/api/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

// 上传前检查
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = /^image\/(jpeg|png)$/.test(file.type)
  if (!isImage) {
    ElMessage.error('只能上传 jpg 或 png 格式的图片！')
    return false
  }
  
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB！')
    return false
  }
  
  return true
}

// 上传成功回调
const handleUploadSuccess = (response: any) => {
  if (response.code === 200 && response.success) {
    formData.value.cover_image = `http://localhost:5000${response.data.url}`
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 上传失败回调
const handleUploadError = () => {
  ElMessage.error('上传失败，请重试')
}

// 加载分类列表
const loadCategories = async () => {
  try {
    const res = await getGuideCategories()
    if (res.code === 200 && res.success) {
      categories.value = res.data
    } else {
      ElMessage.error(res.message || '获取分类失败')
    }
  } catch (error: any) {
    console.error('获取分类失败:', error)
    ElMessage.error(error.message || '获取分类失败')
  }
}

// 添加地图组件引用
const travelRouteMapRef = ref<InstanceType<typeof TravelRouteMap> | null>(null)

// 注册自定义菜单
const openMapDialog = () => {
  travelRouteMapRef.value?.open()
}

// 注册菜单项
Boot.registerMenu(insertTravelRouteMenuConf)

// 工具栏配置
const toolbarConfig: Partial<IToolbarConfig> = {
  excludeKeys: [
    'group-video',
    'insertTable', 
    'group-code',
    'todo',
    'group-indent'
  ],
  insertKeys: {
    index: 11, // 在第11个位置插入
    keys: ['insertTravelRoute'] // 使用自定义菜单的key
  }
}

// 编辑器模式
const mode = 'default'

// 自定义上传方法
const customUpload = async (options: any) => {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    
    const res = await request.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    options.onSuccess(res)
  } catch (error) {
    options.onError(error)
  }
}

// 编辑器配置
const editorConfig: Partial<IEditorConfig> = {
  placeholder: '请输入攻略内容...',
  MENU_CONF: {
    uploadImage: {
      customUpload: async (file: File, insertFn: any) => {
        try {
          const formData = new FormData()
          formData.append('file', file)
          
          const res = await request.post<any>('/api/upload', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
          
          if (res.code === 200 && res.success) {
            insertFn(`http://localhost:5000${res.data.url}`)
          } else {
            ElMessage.error(res.message || '上传失败')
          }
        } catch (error: any) {
          console.error('上传失败:', error)
          ElMessage.error(error.message || '上传失败')
        }
      }
    },
    insertTravelRoute: {
      openMapDialog
    }
  }
}

// 组件销毁时，也及时销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})

const handleCreated = (editor: IDomEditor) => {
  editorRef.value = editor
  
  // 设置编辑器已准备好
  setTimeout(() => {
    editorReady.value = true
    console.log('编辑器初始化完成')
  }, 200)
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const apiCall = isEdit.value
      ? updateGuide(Number(route.params.id), formData.value)
      : createGuide(formData.value)
      
    const res = await apiCall
    if (res.code === 200 && res.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '发布成功')
      router.push('/user/guides')
    } else {
      ElMessage.error(res.message || (isEdit.value ? '更新失败' : '发布失败'))
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error(error.message || '提交失败')
    }
  } finally {
    submitting.value = false
  }
}

// 取消编辑
const handleCancel = () => {
  router.back()
}

// 加载攻略详情
const loadGuideDetail = async () => {
  if (!isEdit.value) return
  
  try {
    loading.value = true
    const res = await getGuideDetail(Number(route.params.id))
    if (res.code === 200 && res.success) {
      const { title, content, category_id, cover_image, status } = res.data
      formData.value = {
        title,
        content,
        category_id,
        cover_image,
        status: status || 1
      }
    } else {
      ElMessage.error(res.message || '获取攻略详情失败')
    }
  } catch (error: any) {
    console.error('获取攻略详情失败:', error)
    ElMessage.error(error.message || '获取攻略详情失败')
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadCategories()
  loadGuideDetail()
  
  // 确保编辑器在DOM渲染后初始化
  setTimeout(() => {
    editorReady.value = true
    console.log('开始加载编辑器...')
  }, 200)
})

// 处理地图插入
const handleMapInsert = (data: any) => {
  // 获取编辑器实例
  const editor = editorRef.value
  
  console.log('接收到地图数据')
  
  if (!editor) {
    console.error('编辑器实例不存在')
    ElMessage.error('编辑器未初始化，无法插入地图')
    return
  }
  
  try {
    if (typeof data === 'object' && data.dataUrl) {
      // 获取编辑器当前选区
      editor.focus()
      
      // 使用标准的图片插入接口
      const imgInfo = {
        src: data.dataUrl,
        alt: '旅游路线图'
      }
      
      // 调用wangEditor的标准图片插入接口
      editor.getMenuConstructorList().forEach(item => {
        if (item.key === 'insertImage') {
          const insertFn = item.factory()
          if (insertFn && typeof insertFn.exec === 'function') {
            insertFn.exec(editor, imgInfo)
            console.log('通过标准菜单API插入图片')
            ElMessage.success('地图已插入')
            return
          }
        }
      })
      
      // 如果上面的方法失败，回退到简单API插入
      editor.insertNode({
        type: 'image',
        src: data.dataUrl,
        alt: '旅游路线图'
      })
      
      console.log('通过insertNode插入图片')
      ElMessage.success('地图已插入')
    } else {
      console.error('未接收到正确的地图数据')
      ElMessage.error('地图数据格式错误') 
    }
  } catch (error) {
    console.error('插入地图错误:', error)
    
    // 最终回退：直接在选区处插入HTML
    try {
      if (typeof data === 'object' && data.dataUrl) {
        const imgHtml = `<img src="${data.dataUrl}" alt="旅游路线图" style="max-width:100%;" />`
        editor.focus()
        editor.dangerouslyInsertHtml(imgHtml)
        console.log('通过insertHtml插入图片 (最终回退)')
        ElMessage.success('地图已插入')
      }
    } catch (backupError) {
      console.error('所有图片插入方法均失败:', backupError)
      ElMessage.error('插入地图失败，请联系管理员')
    }
  }
}
</script>

<style lang="scss" scoped>
.guide-edit-page {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 30px;

    h1 {
      font-size: 28px;
      color: #1abc9c;
      margin: 0;
      font-weight: 600;
      position: relative;
      padding-left: 16px;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 24px;
        background: #1abc9c;
        border-radius: 2px;
      }
    }
  }

  .edit-content {
    background: white;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);

    .guide-form {
      max-width: 800px;
      margin: 0 auto;

      .category-select {
        width: 100%;
      }

      .cover-upload {
        width: 100%;

        .upload-area {
          width: 100%;
          aspect-ratio: 16/9;
          max-width: 500px;
          margin: 0 auto;
          border: 2px dashed var(--el-border-color);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;

          &:hover {
            border-color: #1abc9c;
            background: rgba(26, 188, 156, 0.02);
          }

          &.has-image {
            border-style: solid;
            border-color: #1abc9c;

            &:hover {
              .preview-image {
                transform: scale(1.05);
              }
            }
          }

          .preview-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
          }

          .upload-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            color: var(--el-text-color-secondary);

            .el-icon {
              font-size: 24px;
            }
          }
        }

        .upload-tip {
          margin-top: 8px;
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }

      .editor-wrapper {
        border: 1px solid var(--el-border-color);
        border-radius: 8px;
        overflow: hidden;
        
        .editor-loading {
          padding: 20px;
          
          .loading-text {
            text-align: center;
            margin-top: 15px;
            color: var(--el-text-color-secondary);
            font-size: 14px;
          }
        }
      }

      .form-actions {
        margin-top: 40px;
        display: flex;
        justify-content: center;
        gap: 20px;

        .el-button {
          min-width: 120px;
          
          &--primary {
            background: #1abc9c;
            border-color: #1abc9c;

            &:hover {
              background: #15a589;
              border-color: #15a589;
            }
          }
        }
      }
    }
  }
}
</style> 