<template>
  <div class="verify-code" @click="refreshCode">
    <canvas ref="codeCanvas" :width="width" :height="height"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 定义组件名称
defineOptions({
  name: 'VerifyCode'
})

const props = defineProps({
  width: {
    type: Number,
    default: 120
  },
  height: {
    type: Number,
    default: 40
  }
})

const emit = defineEmits(['update:code'])
const codeCanvas = ref<HTMLCanvasElement | null>(null)
const code = ref('')

// 生成随机验证码
const generateCode = () => {
  const chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
  let result = ''
  for (let i = 0; i < 4; i++) {
    result += chars[Math.floor(Math.random() * chars.length)]
  }
  return result
}

// 绘制验证码
const drawCode = () => {
  if (!codeCanvas.value) return
  
  const ctx = codeCanvas.value.getContext('2d')
  if (!ctx) return

  // 生成新的验证码
  code.value = generateCode()
  emit('update:code', code.value)

  // 清空画布
  ctx.clearRect(0, 0, props.width, props.height)

  // 绘制背景
  ctx.fillStyle = '#f5f5f5'
  ctx.fillRect(0, 0, props.width, props.height)

  // 绘制文字
  ctx.font = '24px Arial'
  ctx.textBaseline = 'middle'
  
  // 随机颜色和位置绘制每个字符
  for (let i = 0; i < code.value.length; i++) {
    ctx.fillStyle = `rgb(${Math.random() * 100 + 50}, ${Math.random() * 100 + 50}, ${Math.random() * 100 + 50})`
    ctx.setTransform(
      1 + Math.random() * 0.2 - 0.1, // 水平缩放
      Math.random() * 0.2 - 0.1,     // 水平倾斜
      Math.random() * 0.2 - 0.1,     // 垂直倾斜
      1 + Math.random() * 0.2 - 0.1, // 垂直缩放
      props.width * (i + 1) / 5,     // 水平位置
      props.height / 2               // 垂直位置
    )
    ctx.fillText(code.value[i], 0, 0)
  }

  // 绘制干扰线
  for (let i = 0; i < 3; i++) {
    ctx.beginPath()
    ctx.strokeStyle = `rgba(${Math.random() * 120 + 40}, ${Math.random() * 120 + 40}, ${Math.random() * 120 + 40}, 0.3)`
    ctx.moveTo(Math.random() * props.width, Math.random() * props.height)
    ctx.lineTo(Math.random() * props.width, Math.random() * props.height)
    ctx.stroke()
  }

  // 绘制干扰点
  for (let i = 0; i < 30; i++) {
    ctx.fillStyle = `rgba(${Math.random() * 120 + 40}, ${Math.random() * 120 + 40}, ${Math.random() * 120 + 40}, 0.3)`
    ctx.beginPath()
    ctx.arc(Math.random() * props.width, Math.random() * props.height, 1, 0, 2 * Math.PI)
    ctx.fill()
  }

  // 重置变换
  ctx.setTransform(1, 0, 0, 1, 0, 0)
}

// 刷新验证码
const refreshCode = () => {
  drawCode()
}

// 组件挂载时生成验证码
onMounted(() => {
  drawCode()
})

// 暴露方法和属性
defineExpose({
  refresh: refreshCode,
  code
})
</script>

<style lang="scss" scoped>
.verify-code {
  display: inline-block;
  cursor: pointer;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  
  canvas {
    display: block;
  }
  
  &:hover {
    opacity: 0.9;
  }
}
</style> 