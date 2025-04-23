<template>
  <div class="note-write-page">
    <div class="page-container">
      <div class="form-container">
        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent>
          <div class="form-header">
            <div class="form-title">
              <h1>{{ isEdit ? '编辑游记' : '写游记' }}</h1>
              <p>分享你的旅行故事和体验</p>
            </div>
            <div class="form-actions">
              <el-button type="primary" @click="handlePublish">发布</el-button>
            </div>
          </div>

          <div class="form-main">
            <div class="form-section">
              <div class="section-title">基本信息</div>
              <div class="section-content">
                <el-form-item prop="title" class="title-input">
                  <el-input
                    v-model="form.title"
                    placeholder="请输入游记标题（最多50个字符）"
                    maxlength="50"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item prop="coverImage" class="cover-upload">
                  <div class="upload-label">游记封面</div>
                  <el-upload
                    class="upload-container"
                    :headers="uploadHeaders"
                    :show-file-list="false"
                    :on-success="handleCoverSuccess"
                    :before-upload="beforeUpload"
                    :http-request="customUpload"
                  >
                    <div v-if="!form.coverImage" class="upload-placeholder">
                      <el-icon class="upload-icon"><Plus /></el-icon>
                      <div class="upload-text">上传封面图片</div>
                      <div class="upload-tip">推荐尺寸：1200 x 800px</div>
                    </div>
                    <div v-else class="preview">
                      <img :src="form.coverImage" alt="封面图片" />
                      <div class="preview-mask">
                        <el-icon class="change-icon"><Edit /></el-icon>
                        <span>更换封面</span>
                      </div>
                    </div>
                  </el-upload>
                </el-form-item>
              </div>
            </div>

            <div class="form-section">
              <div class="section-title">旅行信息</div>
              <div class="section-content">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item prop="destination" label="目的地">
                      <el-cascader
                        v-model="form.destination"
                        :options="destinationOptions"
                        placeholder="选择旅行目的地"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item prop="dateRange" label="旅行日期">
                      <el-date-picker
                        v-model="form.dateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item prop="tags" label="标签">
                  <el-select
                    v-model="form.tags"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    placeholder="请选择或创建标签"
                  >
                    <el-option
                      v-for="tag in tagOptions"
                      :key="tag.value"
                      :label="tag.label"
                      :value="tag.value"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item prop="cost" label="人均花费">
                  <el-input-number v-model="form.cost" :min="0" :precision="0" :step="100" />
                  <span class="cost-unit">元</span>
                </el-form-item>
              </div>
            </div>

            <div class="form-section">
              <div class="section-title">游记正文</div>
              <div class="section-content">
                <el-form-item prop="content">
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
                        v-model="form.content"
                        :defaultConfig="editorConfig"
                        :mode="mode"
                        @onCreated="handleCreated"
                        style="height: 500px"
                      />
                    </div>
                  </div>
                </el-form-item>
              </div>
            </div>
          </div>
        </el-form>
      </div>
    </div>

    <el-dialog
      v-model="previewVisible"
      title="预览"
      width="800px"
      class="preview-dialog"
      fullscreen
    >
      <div class="preview-content">
        <div class="preview-title">{{ form.title }}</div>
        <div class="preview-meta">
          <div class="preview-author">
            <img :src="userAvatar" alt="作者头像" class="author-avatar" />
            <span>{{ userName }}</span>
          </div>
          <div class="preview-info">
            <span v-if="form.destination && form.destination.length > 0">
              <el-icon><Location /></el-icon>
              {{ getDestinationText() }}
            </span>
            <span v-if="form.dateRange && form.dateRange.length === 2">
              <el-icon><Calendar /></el-icon>
              {{ form.dateRange[0] }} 至 {{ form.dateRange[1] }}
            </span>
            <span v-if="form.cost">
              <el-icon><Money /></el-icon>
              ¥{{ form.cost }}/人
            </span>
          </div>
          <div class="preview-tags" v-if="form.tags && form.tags.length > 0">
            <el-tag
              v-for="tag in form.tags"
              :key="tag"
              size="small"
              effect="plain"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
        <div class="preview-cover" v-if="form.coverImage">
          <img :src="form.coverImage" alt="封面图片" />
        </div>
        <div class="preview-content-html" v-html="form.content"></div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="previewVisible = false">返回编辑</el-button>
          <el-button type="primary" @click="publishFromPreview">确认发布</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, shallowRef, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Location, Calendar, Money } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { createNote, updateNote, getNoteDetail } from '@/api/note'
import request from '@/utils/request'

// 添加缺失的函数
const fetchDestinations = async () => {
  try {
    const response = await request.get('/api/system/regions');
    // 处理返回格式，适配code=200的情况
    if (response.code === 200 || response.code === 0) {
      // 处理层级数据结构，符合级联选择器的格式要求
      const formatRegions = (regions) => {
        if (!regions) return [];
        
        return regions.map(region => ({
          value: region.id,
          label: region.name,
          children: formatRegions(region.children)
        }));
      };
      
      console.log('地区数据:', response.data);
      
      return {
        code: 0,
        message: 'success',
        data: formatRegions(response.data)
      };
    }
    return {
      code: -1,
      message: response.message || '获取目的地失败',
      data: []
    };
  } catch (error) {
    console.error('获取目的地数据失败', error);
    return {
      code: -1,
      message: '获取目的地失败',
      data: []
    };
  }
};

const getTags = async () => {
  // 使用静态标签数据代替API请求
  return {
    code: 0,
    message: 'success',
    data: [
      { name: '美食', value: '美食', label: '美食' },
      { name: '风景', value: '风景', label: '风景' },
      { name: '人文', value: '人文', label: '人文' },
      { name: '购物', value: '购物', label: '购物' },
      { name: '摄影', value: '摄影', label: '摄影' },
      { name: '徒步', value: '徒步', label: '徒步' },
      { name: '自驾', value: '自驾', label: '自驾' },
      { name: '家庭游', value: '家庭游', label: '家庭游' },
      { name: '蜜月', value: '蜜月', label: '蜜月' },
      { name: '海岛', value: '海岛', label: '海岛' },
      { name: '古镇', value: '古镇', label: '古镇' },
      { name: '自然', value: '自然', label: '自然' },
      { name: '名胜古迹', value: '名胜古迹', label: '名胜古迹' },
      { name: '民族风情', value: '民族风情', label: '民族风情' },
      { name: '度假', value: '度假', label: '度假' },
      { name: '探险', value: '探险', label: '探险' },
      { name: '节庆', value: '节庆', label: '节庆' },
      { name: '亲子', value: '亲子', label: '亲子' },
      { name: '户外', value: '户外', label: '户外' },
      { name: '小众', value: '小众', label: '小众' },
      { name: '温泉', value: '温泉', label: '温泉' },
      { name: '赏花', value: '赏花', label: '赏花' },
      { name: '滑雪', value: '滑雪', label: '滑雪' },
      { name: '潜水', value: '潜水', label: '潜水' }
    ]
  };
};

export default {
  name: 'NoteWrite',
  components: {
    Editor,
    Toolbar,
    Plus,
    Edit,
    Location,
    Calendar,
    Money
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const userStore = useUserStore()
    const formRef = ref(null)
    const isEdit = computed(() => !!route.params.id)
    const previewVisible = ref(false)
    
    // 表单数据
    const form = reactive({
      title: '',
      coverImage: '',
      destination: [],
      dateRange: [],
      tags: [],
      cost: 0,
      content: ''
    })
    
    // 表单验证规则
    const rules = {
      title: [
        { required: true, message: '请输入游记标题', trigger: 'blur' },
        { min: 5, max: 50, message: '标题长度应在5-50个字符之间', trigger: 'blur' }
      ],
      coverImage: [
        { required: true, message: '请上传封面图片', trigger: 'change' }
      ],
      destination: [
        { required: true, message: '请选择旅行目的地', trigger: 'change' },
        { type: 'array', min: 1, message: '请选择旅行目的地', trigger: 'change' }
      ],
      dateRange: [
        { required: true, message: '请选择旅行日期', trigger: 'change' },
        { type: 'array', len: 2, message: '请选择完整的日期范围', trigger: 'change' }
      ],
      content: [
        { required: true, message: '请输入游记内容', trigger: 'blur' },
        { min: 100, message: '游记内容不能少于100个字符', trigger: 'blur' }
      ]
    }
    
    // 编辑器实例，必须用 shallowRef
    const editorRef = shallowRef()
    
    // 编辑器准备状态
    const editorReady = ref(false)
    
    // 编辑器模式
    const mode = 'default'
    
    // 工具栏配置
    const toolbarConfig = {
      excludeKeys: [
        'group-video',
        'insertTable', 
        'group-code',
        'todo',
        'group-indent'
      ]
    }
    
    // 上传相关配置
    const uploadHeaders = computed(() => ({
      Authorization: `Bearer ${localStorage.getItem('token')}`
    }))
    
    // 定义上传URL，与攻略页面保持一致，使用环境变量
    const uploadUrl = import.meta.env.VITE_UPLOAD_URL || 'http://localhost:5000/api/upload'
    
    // 编辑器配置
    const editorConfig = {
      placeholder: '请输入游记内容...',
      MENU_CONF: {
        uploadImage: {
          customUpload: async (file, insertFn) => {
            try {
              const formData = new FormData()
              formData.append('file', file)
              formData.append('type', 'image')
              formData.append('folder', 'notes')
              
              const res = await request.post('/api/upload', formData, {
                headers: {
                  'Content-Type': 'multipart/form-data'
                }
              })
              
              if (res.code === 0 || res.code === 200) {
                // 直接使用完整的URL路径
                insertFn(`http://localhost:5000${res.data.url}`)
                ElMessage.success('图片上传成功')
              } else {
                ElMessage.error(res.message || '上传失败')
              }
            } catch (error) {
              console.error('上传失败:', error)
              ElMessage.error('图片上传失败')
            }
          }
        }
      }
    }
    
    // 创建编辑器时的回调函数
    const handleCreated = (editor) => {
      editorRef.value = editor
      console.log('编辑器创建成功');
      
      setTimeout(() => {
        editorReady.value = true
        console.log('编辑器已准备好')
      }, 200)
    }
    
    // 组件销毁时，也及时销毁编辑器
    onBeforeUnmount(() => {
      const editor = editorRef.value
      if (editor == null) return
      editor.destroy()
    })
    
    // 目的地选项
    const destinationOptions = ref([])
    
    // 标签选项
    const tagOptions = ref([])
    
    // 用户信息
    const userName = computed(() => userStore.userInfo.nickname || userStore.userInfo.username)
    const userAvatar = computed(() => userStore.userInfo.avatar || '/images/default-avatar.png')
    
    // 初始化数据
    onMounted(async () => {
      // 确保编辑器在DOM渲染后初始化
      console.log('开始加载编辑器...')
      
      // 设置延时加载编辑器，避免DOM未完全渲染的问题
      setTimeout(() => {
        editorReady.value = true
        console.log('编辑器已准备好')
      }, 200)
      
      // 获取标签列表
      try {
        // 获取目的地数据
        const destRes = await fetchDestinations()
        if (destRes.code === 0) {
          destinationOptions.value = destRes.data
        }
        
        // 获取标签数据
        const tagRes = await getTags()
        if (tagRes.code === 0) {
          // 标签数据已经包含label和value，可以直接使用
          tagOptions.value = tagRes.data
        }
        
        // 如果是编辑模式，获取游记详情
        if (isEdit.value) {
          const noteId = route.params.id
          const noteRes = await getNoteDetail(noteId)
          console.log('游记详情:', noteRes)
          if (noteRes.code === 0 || noteRes.code === 200) {
            const noteData = noteRes.data
            form.title = noteData.title
            form.coverImage = noteData.coverImage
            
            // 处理目的地数据，如果是字符串数组则直接使用，如果是ID数组则转换
            if (noteData.destination_ids && Array.isArray(noteData.destination_ids)) {
              form.destination = noteData.destination_ids
            } else if (noteData.destination && typeof noteData.destination === 'string') {
              // 如果是字符串，暂时留空，用户需要重新选择
              form.destination = []
            } else {
              form.destination = []
            }
            
            form.dateRange = [noteData.startDate || noteData.start_date, noteData.endDate || noteData.end_date]
            form.tags = noteData.tags || []
            form.cost = noteData.cost || noteData.trip_cost || 0
            form.content = noteData.content || ''
          } else {
            ElMessage.error('获取游记详情失败')
            router.push('/notes')
          }
        }
      } catch (error) {
        console.error('初始化数据失败', error)
        ElMessage.error('初始化数据失败')
      }
    })
    
    // 处理封面上传成功
    const handleCoverSuccess = (res, file) => {
      if (res.code === 0 || res.code === 200) {
        // 直接使用完整的URL路径
        form.coverImage = `http://localhost:5000${res.data.url}`
        ElMessage.success('封面上传成功')
      } else {
        ElMessage.error('封面上传失败')
      }
    }
    
    // 上传前检查
    const beforeUpload = (file) => {
      const isImage = file.type.startsWith('image/')
      const isLt2M = file.size / 1024 / 1024 < 2
      
      if (!isImage) {
        ElMessage.error('只能上传图片文件')
        return false
      }
      
      if (!isLt2M) {
        ElMessage.error('图片大小不能超过2MB')
        return false
      }
      
      return true
    }
    
    // 自定义上传方法
    const customUpload = async (options) => {
      try {
        if (!beforeUpload(options.file)) {
          return;
        }
        
        const formData = new FormData()
        formData.append('file', options.file)
        formData.append('type', 'image')
        formData.append('folder', 'notes')
        
        const res = await request.post('/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        options.onSuccess(res)
      } catch (error) {
        console.error('上传失败:', error)
        ElMessage.error('封面上传失败')
        options.onError(error)
      }
    }
    
    // 获取目的地文本
    const getDestinationText = () => {
      if (!form.destination || form.destination.length === 0) return ''
      
      // 根据目的地ID查找目的地名称并拼接
      const result = []
      let currentOptions = destinationOptions.value
      
      for (let i = 0; i < form.destination.length; i++) {
        const destId = form.destination[i]
        const found = currentOptions.find(opt => opt.value === destId)
        
        if (found) {
          result.push(found.label)
          currentOptions = found.children || []
        } else {
          break
        }
      }
      
      return result.join(' - ')
    }
    
    // 发布游记
    const handlePublish = async () => {
      try {
        const valid = await formRef.value.validate()
        if (!valid) return
        
        // 显示预览
        previewVisible.value = true
      } catch (error) {
        console.error('表单验证失败', error)
      }
    }
    
    // 从预览页面发布
    const publishFromPreview = async () => {
      previewVisible.value = false
      
      try {
        // 生成简短描述，从content中提取纯文本
        let description = ''
        if (form.content) {
          // 移除HTML标签，提取纯文本
          const tempDiv = document.createElement('div')
          tempDiv.innerHTML = form.content
          description = tempDiv.textContent || tempDiv.innerText || ''
          // 截取前200个字符作为描述
          description = description.substring(0, 200)
          if (description.length === 200) {
            description += '...'
          }
        }
        
        const noteData = {
          title: form.title,
          coverImage: form.coverImage,
          destination: getDestinationText(), // 使用文本表示的目的地
          destination_ids: form.destination, // 保存原始的目的地ID数组
          startDate: form.dateRange[0],
          endDate: form.dateRange[1],
          tags: form.tags,
          cost: form.cost,
          content: form.content,
          description: description, // 添加description字段
          status: 1 // 已发布状态
        }
        
        let res
        if (isEdit.value) {
          noteData.id = route.params.id
          res = await updateNote(noteData)
        } else {
          res = await createNote(noteData)
        }
        
        if (res.code === 0 || res.code === 200) {
          ElMessage.success('游记发布成功')
          router.push(`/notes/detail/${res.data.id}`)
        } else {
          ElMessage.error(res.message || '发布失败')
        }
      } catch (error) {
        console.error('发布游记失败', error)
        ElMessage.error('发布游记失败')
      }
    }
    
    return {
      formRef,
      form,
      rules,
      isEdit,
      editorRef,
      editorConfig,
      toolbarConfig,
      editorReady,
      mode,
      handleCreated,
      destinationOptions,
      tagOptions,
      userName,
      userAvatar,
      previewVisible,
      handleCoverSuccess,
      beforeUpload,
      customUpload,
      getDestinationText,
      handlePublish,
      publishFromPreview,
      uploadHeaders,
      uploadUrl
    }
  }
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.note-write-page {
  padding: $spacing-lg 0;
  
  .page-container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: $border-radius-lg;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  
  .form-container {
    padding: $spacing-xl;
  }
  
  .form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-lg;
    padding-bottom: $spacing-md;
    border-bottom: 1px solid #e8e8e8;
    
    .form-title {
      h1 {
        font-size: 24px;
        font-weight: 600;
        color: #333;
        margin: 0 0 $spacing-sm;
      }
      
      p {
        font-size: 12px;
        color: #666;
        margin: 0;
      }
    }
    
    .form-actions {
      display: flex;
      gap: 16px;
    }
  }
  
  .form-main {
    .form-section {
      margin-bottom: $spacing-xl;
      
      .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin-bottom: 16px;
        padding-left: 8px;
        border-left: 3px solid #1890ff;
      }
      
      .section-content {
        background: #f5f7fa;
        padding: 24px;
        border-radius: 4px;
      }
    }
    
    .title-input {
      margin-bottom: 24px;
      
      :deep(.el-input__wrapper) {
        padding-right: 100px;
      }
    }
    
    .cover-upload {
      .upload-label {
        font-size: 14px;
        color: #333;
        margin-bottom: 8px;
      }
      
      .upload-container {
        width: 100%;
        height: 240px;
        border: 1px dashed #e8e8e8;
        border-radius: 4px;
        overflow: hidden;
        
        :deep(.el-upload) {
          width: 100%;
          height: 100%;
          display: flex;
          justify-content: center;
          align-items: center;
        }
      }
      
      .upload-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #666;
        
        .upload-icon {
          font-size: 40px;
          margin-bottom: 10px;
        }
        
        .upload-text {
          font-size: 16px;
          margin-bottom: 8px;
        }
        
        .upload-tip {
          font-size: 12px;
          color: #c0c4cc;
        }
      }
      
      .preview {
        width: 100%;
        height: 100%;
        position: relative;
        
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        
        .preview-mask {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          opacity: 0;
          transition: opacity 0.3s;
          color: white;
          
          &:hover {
            opacity: 1;
          }
          
          .change-icon {
            font-size: 30px;
            margin-bottom: 10px;
          }
        }
      }
    }
    
    .cost-unit {
      margin-left: 8px;
      color: #666;
    }
    
    .editor-wrapper {
      border: 1px solid #e8e8e8;
      border-radius: 4px;
      overflow: hidden;
    }
    
    .editor-loading {
      padding: 24px;
      
      .loading-text {
        text-align: center;
        color: #666;
        margin-top: 16px;
      }
    }
  }
}

.preview-dialog {
  :deep(.el-dialog__header) {
    padding: 24px;
    border-bottom: 1px solid #e8e8e8;
  }
  
  :deep(.el-dialog__body) {
    padding: 0;
    height: calc(100vh - 120px);
    overflow-y: auto;
  }
  
  :deep(.el-dialog__footer) {
    padding: 16px 24px;
    border-top: 1px solid #e8e8e8;
  }
  
  .preview-content {
    padding: 32px;
    max-width: 800px;
    margin: 0 auto;
    
    .preview-title {
      font-size: 28px;
      font-weight: 600;
      color: #333;
      margin-bottom: 24px;
      text-align: center;
    }
    
    .preview-meta {
      margin-bottom: 32px;
      
      .preview-author {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
        
        .author-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          margin-right: 8px;
          object-fit: cover;
        }
      }
      
      .preview-info {
        display: flex;
        flex-wrap: wrap;
        margin-bottom: 16px;
        color: #666;
        
        span {
          display: flex;
          align-items: center;
          margin-right: 24px;
          margin-bottom: 8px;
          
          .el-icon {
            margin-right: 4px;
          }
        }
      }
      
      .preview-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        
        .tag-item {
          margin-bottom: 8px;
        }
      }
    }
    
    .preview-cover {
      margin-bottom: 32px;
      border-radius: 4px;
      overflow: hidden;
      
      img {
        width: 100%;
        display: block;
      }
    }
    
    .preview-content-html {
      line-height: 1.8;
      
      :deep(img) {
        max-width: 100%;
        height: auto;
      }
      
      :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
        margin-top: 1.5em;
        margin-bottom: 0.75em;
        color: #333;
      }
      
      :deep(p) {
        margin-bottom: 1em;
      }
      
      :deep(ul), :deep(ol) {
        margin-bottom: 1em;
        padding-left: 2em;
      }
      
      :deep(blockquote) {
        border-left: 4px solid #1890ff;
        padding-left: 1em;
        margin-left: 0;
        margin-right: 0;
        color: #666;
      }
    }
  }
}

@media (max-width: 768px) {
  .note-write-page {
    padding: 16px 0;
    
    .form-container {
      padding: 16px;
    }
    
    .form-header {
      flex-direction: column;
      align-items: flex-start;
      
      .form-title {
        margin-bottom: 16px;
      }
    }
    
    .form-main {
      .form-section {
        .section-content {
          padding: 16px;
        }
      }
    }
  }
  
  .preview-dialog {
    .preview-content {
      padding: 16px;
      
      .preview-title {
        font-size: 22px;
      }
    }
  }
}
</style> 