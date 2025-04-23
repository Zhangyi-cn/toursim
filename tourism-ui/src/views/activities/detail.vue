<template>
  <div class="activity-detail page-container">
    <div class="container">
      <div class="breadcrumb mb-md">
        <el-breadcrumb>
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/activities' }">活动</el-breadcrumb-item>
          <el-breadcrumb-item>活动详情</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <el-card v-loading="loading">
        <template v-if="activity">
          <div class="activity-header">
            <h1 class="title">{{ activity.title }}</h1>
            <div class="meta flex-between">
              <div class="info">
                <span>活动时间：{{ formatDate(activity.start_time) }} - {{ formatDate(activity.end_time) }}</span>
                <span class="ml-lg">活动地点：{{ activity.location }}</span>
                <span class="ml-lg">报名人数：{{ activity.current_participants }}/{{ activity.max_participants || '不限' }}</span>
              </div>
              <div class="actions">
                <el-button type="primary" @click="handleEnroll" :disabled="!canEnroll" :loading="enrolling">
                  {{ enrollButtonText }}
                </el-button>
              </div>
            </div>
          </div>

          <el-divider />

          <div class="activity-content">
            <div class="images mb-lg" v-if="activity.images?.length">
              <el-carousel height="400px">
                <el-carousel-item v-for="image in activity.images" :key="image">
                  <img :src="image" class="image-cover" />
                </el-carousel-item>
              </el-carousel>
            </div>

            <div class="description">
              <h2 class="section-title">活动介绍</h2>
              <div class="content" v-html="activity.description"></div>
            </div>

            <div class="notice mt-xl">
              <h2 class="section-title">活动须知</h2>
              <div class="content" v-html="activity.notice"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <el-empty description="未找到活动信息" />
        </template>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getActivityDetail, joinActivity } from '@/api/activity'
import { useUserStore } from '@/store/user'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const enrolling = ref(false)
const activity = ref(null)

// 获取活动详情
const fetchActivityDetail = async () => {
  loading.value = true
  try {
    const res = await getActivityDetail(route.params.id)
    if (res.code === 200 && res.data) {
      activity.value = res.data
    } else {
      ElMessage.error(res.message || '获取活动详情失败')
      router.push('/activities')
    }
  } catch (error) {
    ElMessage.error(error.message || '获取活动详情失败')
    router.push('/activities')
  } finally {
    loading.value = false
  }
}

// 判断是否可以报名
const canEnroll = computed(() => {
  if (!activity.value) return false
  if (activity.value.is_joined) return false
  if (activity.value.status !== 'upcoming') return false
  return activity.value.current_participants < activity.value.max_participants
})

// 报名按钮文字
const enrollButtonText = computed(() => {
  if (!activity.value) return '报名参加'
  if (activity.value.is_joined) return '已报名'
  if (activity.value.status === 'ended') return '活动已结束'
  if (activity.value.status === 'ongoing') return '活动进行中'
  if (activity.value.current_participants >= activity.value.max_participants) return '名额已满'
  return '报名参加'
})

// 报名活动
const handleEnroll = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再报名')
    router.push('/login')
    return
  }

  enrolling.value = true
  try {
    const res = await joinActivity(activity.value.id)
    if (res.code === 200) {
      ElMessage.success('报名成功')
      fetchActivityDetail()
    } else {
      ElMessage.error(res.message || '报名失败')
    }
  } catch (error) {
    ElMessage.error(error.message || '报名失败')
  } finally {
    enrolling.value = false
  }
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 初始化
onMounted(() => {
  fetchActivityDetail()
})
</script>

<style lang="scss" scoped>
@use "@/styles/variables" as *;

.activity-detail {
  padding: $spacing-lg 0;
}

.activity-header {
  margin-bottom: $spacing-lg;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #666;
  font-size: 14px;

  .info {
    span + span {
      margin-left: 20px;
    }
  }
}

.activity-content {
  .images {
    margin-bottom: 30px;

    .image-cover {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .section-title {
    font-size: 20px;
    font-weight: bold;
    margin: 30px 0 20px;
  }

  .content {
    line-height: 1.8;
    color: #333;
  }
}

.notice {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;

    .info {
      span {
        display: block;
        margin: 5px 0;

        & + span {
          margin-left: 0;
        }
      }
    }

    .actions {
      width: 100%;

      .el-button {
        width: 100%;
      }
    }
  }
}
</style> 