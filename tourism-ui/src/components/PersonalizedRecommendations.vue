<template>
  <section class="personalized-section" v-if="isLoggedIn">
    <div class="section-header">
      <h2 class="section-title">
        <el-icon><Magic /></el-icon>
        猜你喜欢
      </h2>
      <p class="section-subtitle">根据您的喜好，为您精选内容</p>
    </div>

    <el-tabs v-model="currentType" class="recommendation-tabs">
<!--      <el-tab-pane label="景点" name="attraction">-->
<!--        <el-row :gutter="20" v-loading="loading">-->
<!--          <el-col -->
<!--            v-for="item in filteredRecommendations" -->
<!--            :key="item.id"-->
<!--            :xs="24" -->
<!--            :sm="12" -->
<!--            :md="8" -->
<!--            :lg="6"-->
<!--          >-->
<!--            <el-card -->
<!--              class="recommendation-card" -->
<!--              shadow="hover"-->
<!--              @click="handleItemClick(item)"-->
<!--            >-->
<!--              <el-image :src="staticBaseUrl + '/' + item.cover_image" fit="cover" />-->
<!--              <div class="card-content">-->
<!--                <h3 class="title">{{ item.name }}</h3>-->
<!--                <div class="score">-->
<!--                  <el-rate-->
<!--                    v-model="item.score"-->
<!--                    disabled-->
<!--                    text-color="#ff9900"-->
<!--                    :max="5"-->
<!--                    :score="item.score"-->
<!--                  />-->
<!--                </div>-->
<!--                <div class="stats">-->
<!--                  <span>-->
<!--                    <el-icon><View /></el-icon>-->
<!--                    {{ item.view_count || 0 }}-->
<!--                  </span>-->
<!--                  <span>-->
<!--                    <el-icon><Star /></el-icon>-->
<!--                    {{ item.collection_count || 0 }}-->
<!--                  </span>-->
<!--                  <span>-->
<!--                    <el-icon><ChatRound /></el-icon>-->
<!--                    {{ item.comment_count || 0 }}-->
<!--                  </span>-->
<!--                </div>-->
<!--              </div>-->
<!--            </el-card>-->
<!--          </el-col>-->
<!--        </el-row>-->
<!--      </el-tab-pane>-->
      <el-row :gutter="20" v-loading="loading">
        <el-col
            v-for="item in filteredRecommendations"
            :key="item.id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
        >
          <el-card
              class="recommendation-card"
              shadow="hover"
              @click="handleItemClick(item)"
          >
            <el-image :src="staticBaseUrl + '/' + item.cover_image" fit="cover" />
            <div class="card-content">
              <h3 class="title">{{ item.title }}</h3>
              <div class="score">
                <el-rate
                    v-model="item.score"
                    disabled
                    text-color="#ff9900"
                    :max="5"
                    :score="item.score"
                />
              </div>
              <div class="stats">
                  <span>
                    <el-icon><View /></el-icon>
                    {{ item.view_count || 0 }}
                  </span>
                <span>
                    <el-icon><Star /></el-icon>
                    {{ item.collection_count || 0 }}
                  </span>
                <span>
                    <el-icon><ChatRound /></el-icon>
                    {{ item.comment_count || 0 }}
                  </span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
<!--      <el-tab-pane label="攻略" name="guide">-->
<!--        <el-row :gutter="20" v-loading="loading">-->
<!--          <el-col -->
<!--            v-for="item in filteredRecommendations" -->
<!--            :key="item.id"-->
<!--            :xs="24" -->
<!--            :sm="12" -->
<!--            :md="8" -->
<!--            :lg="6"-->
<!--          >-->
<!--            <el-card -->
<!--              class="recommendation-card" -->
<!--              shadow="hover"-->
<!--              @click="handleItemClick(item)"-->
<!--            >-->
<!--              <el-image :src="staticBaseUrl + '/' + item.cover_image" fit="cover" />-->
<!--              <div class="card-content">-->
<!--                <h3 class="title">{{ item.name }}</h3>-->
<!--                <div class="score">-->
<!--                  <el-rate-->
<!--                    v-model="item.score"-->
<!--                    disabled-->
<!--                    text-color="#ff9900"-->
<!--                    :max="5"-->
<!--                    :score="item.score"-->
<!--                  />-->
<!--                </div>-->
<!--                <div class="stats">-->
<!--                  <span>-->
<!--                    <el-icon><View /></el-icon>-->
<!--                    {{ item.view_count || 0 }}-->
<!--                  </span>-->
<!--                  <span>-->
<!--                    <el-icon><Star /></el-icon>-->
<!--                    {{ item.collection_count || 0 }}-->
<!--                  </span>-->
<!--                  <span>-->
<!--                    <el-icon><ChatRound /></el-icon>-->
<!--                    {{ item.comment_count || 0 }}-->
<!--                  </span>-->
<!--                </div>-->
<!--              </div>-->
<!--            </el-card>-->
<!--          </el-col>-->
<!--        </el-row>-->
<!--      </el-tab-pane>-->

<!--      <el-tab-pane label="游记" name="note">-->
<!--        <el-row :gutter="20" v-loading="loading">-->
<!--          <el-col -->
<!--            v-for="item in filteredRecommendations" -->
<!--            :key="item.id"-->
<!--            :xs="24" -->
<!--            :sm="12" -->
<!--            :md="8" -->
<!--            :lg="6"-->
<!--          >-->
<!--            <el-card -->
<!--              class="recommendation-card" -->
<!--              shadow="hover"-->
<!--              @click="handleItemClick(item)"-->
<!--            >-->
<!--              <el-image :src="staticBaseUrl + '/' + item.cover_image" fit="cover" />-->
<!--              <div class="card-content">-->
<!--                <h3 class="title">{{ item.name }}</h3>-->
<!--                <div class="score">-->
<!--                  <el-rate-->
<!--                    v-model="item.score"-->
<!--                    disabled-->
<!--                    text-color="#ff9900"-->
<!--                    :max="5"-->
<!--                    :score="item.score"-->
<!--                  />-->
<!--                </div>-->
<!--                <div class="stats">-->
<!--                  <span>-->
<!--                    <el-icon><View /></el-icon>-->
<!--                    {{ item.view_count || 0 }}-->
<!--                  </span>-->
<!--                  <span>-->
<!--                    <el-icon><Star /></el-icon>-->
<!--                    {{ item.collection_count || 0 }}-->
<!--                  </span>-->
<!--                  <span>-->
<!--                    <el-icon><ChatRound /></el-icon>-->
<!--                    {{ item.comment_count || 0 }}-->
<!--                  </span>-->
<!--                </div>-->
<!--              </div>-->
<!--            </el-card>-->
<!--          </el-col>-->
<!--        </el-row>-->
<!--      </el-tab-pane>-->
    </el-tabs>

    <el-empty v-if="!loading && isEmpty" description="暂无推荐内容" />
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Mic as Magic, View, Star, ChatRound } from '@element-plus/icons-vue'
import { getRecommendations } from '@/api/recommendation'
import type { RecommendationResponse, RecommendationParams } from '@/types/recommendation'

const staticBaseUrl = import.meta.env.VITE_STATIC_ASSETS_URL
const router = useRouter()
const userStore = useUserStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)

const loading = ref(false)
const currentType = ref<'attraction' | 'guide' | 'note'>('attraction')
const recommendations = ref<any[]>([])

// 根据当前类型过滤推荐内容
const filteredRecommendations = computed(() => {
  if (!recommendations.value) return []
  return recommendations.value.filter(item => item.type === currentType.value)
})

// 判断是否为空
const isEmpty = computed(() => {
  if (!recommendations.value) return true
  return filteredRecommendations.value.length === 0
})

// 获取推荐数据
const fetchRecommendations = async () => {
  if (!isLoggedIn.value) return
  
  loading.value = true
  try {
    const params: RecommendationParams = {
      type: currentType.value,
      limit: 8
    }
    console.log('Fetching recommendations with params:', params)
    const res = await getRecommendations(params)
    console.log('Recommendations response:', res)
    if (res.code === 200 && res.data) {
      recommendations.value = res.data
      console.log('Filtered recommendations:', filteredRecommendations.value)
    }
  } catch (error) {
    console.error('获取推荐失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理推荐项点击
const handleItemClick = (item: any) => {
  if (item.type === 'attraction') {
    router.push('/attractions/' + item.id)
  } else if (item.type === 'guide') {
    router.push('/travel-guides/' + item.id)
  } else {
    router.push('/travel-notes/' + item.id)
  }
}

// 监听类型变化
watch(currentType, () => {
  fetchRecommendations()
})

onMounted(() => {
  if (isLoggedIn.value) {
    fetchRecommendations()
  }
})
</script>

<style lang="scss" scoped>
.personalized-section {
  padding: 40px 0;
  background: #fff;

  .section-header {
    text-align: center;
    margin-bottom: 30px;

    .section-title {
      font-size: 28px;
      font-weight: 600;
      color: #333;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;

      .el-icon {
        font-size: 28px;
        color: #1abc9c;
      }
    }

    .section-subtitle {
      font-size: 16px;
      color: #666;
    }
  }

  .recommendation-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 20px;

      .el-tabs__nav-wrap {
        &::after {
          display: none;
        }
      }

      .el-tabs__nav {
        border: none;
      }

      .el-tabs__item {
        font-size: 16px;
        padding: 0 20px;
        height: 40px;
        line-height: 40px;
        transition: all 0.3s;

        &.is-active {
          color: #1abc9c;
          font-weight: 500;
        }
      }
    }
  }

  .recommendation-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }

    .el-image {
      width: 100%;
      height: 200px;
      border-radius: 8px 8px 0 0;
    }

    .card-content {
      padding: 15px;

      .title {
        font-size: 16px;
        font-weight: 500;
        color: #333;
        margin: 0 0 10px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .score {
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;

        .el-rate {
          height: 20px;
          line-height: 20px;
        }
      }

      .stats {
        display: flex;
        gap: 15px;
        font-size: 14px;
        color: #666;

        span {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .personalized-section {
    padding: 20px 0;

    .section-header {
      .section-title {
        font-size: 24px;
      }

      .section-subtitle {
        font-size: 14px;
      }
    }

    .recommendation-tabs {
      :deep(.el-tabs__item) {
        font-size: 14px;
        padding: 0 15px;
      }
    }
  }
}
</style> 