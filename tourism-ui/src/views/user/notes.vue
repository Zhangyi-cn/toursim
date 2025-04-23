<template>
  <div class="user-notes-page">
    <div class="container">
      <el-card class="notes-card">
        <template #header>
          <div class="card-header">
            <h2>我的游记</h2>
            <el-button type="primary" @click="handleCreate">
              写游记
            </el-button>
          </div>
        </template>

        <div class="notes-list" v-loading="loading">
          <el-empty
            v-if="!loading && !notes.length"
            description="暂无游记"
          >
            <template #extra>
              <el-button type="primary" @click="handleCreate">
                立即写游记
              </el-button>
            </template>
          </el-empty>

          <div v-else class="notes-grid">
            <el-row :gutter="20">
              <el-col
                v-for="note in notes"
                :key="note.id"
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
              >
                <div class="note-item">
                  <el-card :body-style="{ padding: '0px' }">
                    <el-image
                      :src="note.cover || '/placeholder.jpg'"
                      class="item-image"
                      fit="cover"
                      @click="handleView(note)"
                    />
                    <div class="item-info">
                      <h3 @click="handleView(note)">{{ note.title }}</h3>
                      <p class="description">{{ note.description }}</p>
                      <div class="meta">
                        <div class="stats">
                          <span class="views">
                            <el-icon><View /></el-icon>
                            {{ note.views }}
                          </span>
                          <span class="likes">
                            <el-icon><Star /></el-icon>
                            {{ note.likes }}
                          </span>
                        </div>
                        <div class="actions">
                          <el-button
                            type="primary"
                            link
                            @click="handleEdit(note)"
                          >
                            编辑
                          </el-button>
                          <el-button
                            type="danger"
                            link
                            @click="handleDelete(note)"
                          >
                            删除
                          </el-button>
                        </div>
                      </div>
                    </div>
                  </el-card>
                </div>
              </el-col>
            </el-row>
          </div>

          <div class="pagination" v-if="total > 0">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              :page-sizes="[12, 24, 36]"
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Star } from '@element-plus/icons-vue'
import { getUserNotes, deleteNote } from '@/api/note'

const router = useRouter()

// 状态数据
const loading = ref(false)
const notes = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)

// 获取游记列表
const loadNotes = async () => {
  loading.value = true
  try {
    const res = await getUserNotes({
      page: currentPage.value,
      per_page: pageSize.value
    })
    notes.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('获取游记列表失败:', error)
    ElMessage.error('获取游记列表失败')
  } finally {
    loading.value = false
  }
}

// 处理分页变化
const handleSizeChange = (size) => {
  pageSize.value = size
  loadNotes()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadNotes()
}

// 创建游记
const handleCreate = () => {
  router.push('/notes/create')
}

// 查看游记
const handleView = (note) => {
  router.push(`/note/${note.id}`)
}

// 编辑游记
const handleEdit = (note) => {
  router.push(`/notes/edit/${note.id}`)
}

// 删除游记
const handleDelete = async (note) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这篇游记吗？删除后无法恢复',
      '删除游记',
      {
        type: 'warning'
      }
    )

    await deleteNote(note.id)
    ElMessage.success('游记已删除')
    loadNotes()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除游记失败:', error)
      ElMessage.error('删除游记失败')
    }
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadNotes()
})
</script>

<style lang="scss" scoped>
.user-notes-page {
  padding: 30px 0;

  .notes-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h2 {
        margin: 0;
        font-size: 20px;
        color: #303133;
      }
    }

    .notes-list {
      min-height: 300px;

      .notes-grid {
        .note-item {
          margin-bottom: 20px;

          .item-image {
            width: 100%;
            height: 200px;
            cursor: pointer;
            transition: opacity 0.3s;

            &:hover {
              opacity: 0.8;
            }
          }

          .item-info {
            padding: 15px;

            h3 {
              margin: 0 0 10px;
              font-size: 16px;
              color: #303133;
              cursor: pointer;
              display: -webkit-box;
              -webkit-box-orient: vertical;
              -webkit-line-clamp: 1;
              overflow: hidden;

              &:hover {
                color: #409eff;
              }
            }

            .description {
              margin: 0 0 10px;
              font-size: 14px;
              color: #606266;
              display: -webkit-box;
              -webkit-box-orient: vertical;
              -webkit-line-clamp: 2;
              overflow: hidden;
              height: 40px;
            }

            .meta {
              display: flex;
              justify-content: space-between;
              align-items: center;
              font-size: 14px;
              color: #909399;

              .stats {
                display: flex;
                gap: 15px;

                .views,
                .likes {
                  display: flex;
                  align-items: center;
                  gap: 5px;
                }
              }

              .actions {
                display: flex;
                gap: 10px;
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

@media (max-width: 768px) {
  .user-notes-page {
    padding: 15px;

    .notes-card {
      .notes-list {
        .notes-grid {
          .note-item {
            .item-image {
              height: 160px;
            }
          }
        }
      }
    }
  }
}
</style> 