<template>
  <section class="page-banner">
    <div class="banner-bg" :style="{ backgroundImage: `url(${backgroundImage})` }">
      <div class="banner-content container">
        <h1 class="page-title">{{ title }}</h1>
        <p class="page-desc">{{ description }}</p>
        
        <div v-if="showSearch" class="search-box">
          <el-input
            v-model="searchValue"
            :placeholder="searchPlaceholder"
            class="search-input"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  backgroundImage: {
    type: String,
    default: '/banner-bg.jpg'
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  searchPlaceholder: {
    type: String,
    default: '搜索...'
  },
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'search'])

const searchValue = ref(props.modelValue)

// 监听外部值的变化
watch(() => props.modelValue, (newVal) => {
  searchValue.value = newVal
})

// 监听内部值的变化
watch(searchValue, (newVal) => {
  emit('update:modelValue', newVal)
})

// 处理搜索
const handleSearch = () => {
  emit('search', searchValue.value)
}
</script>

<style lang="scss" scoped>
.page-banner {
  width: 100%;
  position: relative;
  margin-bottom: 40px;
  
  .banner-bg {
    width: 100%;
    min-height: 300px;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    position: relative;
    display: flex;
    align-items: center;
    padding: 60px 0;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(to bottom, rgba(0,0,0,0.5), rgba(0,0,0,0.3));
    }
  }
  
  .banner-content {
    position: relative;
    z-index: 1;
    color: #fff;
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
    padding: 0 20px;
    
    .page-title {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 1rem;
      text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .page-desc {
      font-size: 1.1rem;
      margin-bottom: 2rem;
      opacity: 0.9;
      text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .search-box {
      display: flex;
      gap: 12px;
      max-width: 600px;
      margin: 0 auto;
      
      .search-input {
        :deep(.el-input__wrapper) {
          background: rgba(255,255,255,0.95);
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
          
          &:hover {
            background: #fff;
          }
          
          &.is-focus {
            background: #fff;
          }
        }
        
        :deep(.el-input__inner) {
          height: 44px;
        }
      }
      
      .el-button {
        height: 44px;
        padding: 0 24px;
        font-size: 1rem;
      }
    }
  }
}

@media (max-width: 768px) {
  .page-banner {
    .banner-bg {
      min-height: 250px;
      padding: 40px 0;
    }
    
    .banner-content {
      .page-title {
        font-size: 2rem;
      }
      
      .page-desc {
        font-size: 1rem;
      }
      
      .search-box {
        flex-direction: column;
        
        .el-button {
          width: 100%;
        }
      }
    }
  }
}
</style> 