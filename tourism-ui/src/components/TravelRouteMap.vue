<template>
  <div class="travel-route-map">
    <el-dialog
      v-model="visible"
      title="添加旅游路线地图"
      width="80%"
      :before-close="handleClose"
    >
      <div class="map-container">
        <div class="route-inputs">
          <div class="input-group">
            <div class="input-label">起点：</div>
            <div class="location-input">
              <el-input v-model="startPoint" placeholder="请输入起点" />
            </div>
          </div>
          
          <div class="waypoints-container">
            <div v-for="(point, index) in waypoints" :key="index" class="input-group waypoint">
              <div class="input-label">途经点 {{ index + 1 }}：</div>
              <div class="location-input">
                <el-input v-model="waypoints[index]" placeholder="请输入途经点" />
                <el-button type="danger" circle @click="removeWaypoint(index)" size="small">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            
            <el-button type="primary" @click="addWaypoint" size="small">
              <el-icon><Plus /></el-icon> 添加途经点
            </el-button>
          </div>
          
          <div class="input-group">
            <div class="input-label">终点：</div>
            <div class="location-input">
              <el-input v-model="endPoint" placeholder="请输入终点" />
            </div>
          </div>
          
          <div class="route-preview">
            <h3>路线预览</h3>
            <div class="route-list">
              <div class="route-item start">
                <div class="route-icon">起</div>
                <div class="route-name">{{ startPoint || '请输入起点' }}</div>
              </div>
              
              <div v-for="(point, index) in validWaypoints" :key="`waypoint-${index}`" class="route-connection">
                <div class="route-line"></div>
                <div class="route-item waypoint">
                  <div class="route-icon">{{ index + 1 }}</div>
                  <div class="route-name">{{ point }}</div>
                </div>
              </div>
              
              <div class="route-connection" v-if="startPoint && endPoint">
                <div class="route-line"></div>
                <div class="route-item end">
                  <div class="route-icon">终</div>
                  <div class="route-name">{{ endPoint || '请输入终点' }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="input-group">
            <div class="input-label">地图缩放级别：</div>
            <el-slider v-model="mapZoom" :min="1" :max="18" :step="1" :format-tooltip="formatZoom" />
          </div>
          
          <el-button type="primary" @click="generateMap" :disabled="!startPoint || !endPoint">
            生成地图
          </el-button>
        </div>
        
        <div class="map-preview">
          <div v-if="mapImageUrl" class="preview-image">
            <img :src="mapImageUrl" alt="旅游路线地图预览" />
          </div>
          <div v-else class="empty-preview">
            <p>填写路线信息后点击"生成地图"查看预览</p>
          </div>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" @click="insertMap" :disabled="!mapImageUrl">
            插入地图
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, defineExpose } from 'vue'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Plus } from '@element-plus/icons-vue'

// 高德地图 Key
const MAP_KEY = 'f62f6e372fa7386c2c9f6cada41260ff'

// 定义事件
const emit = defineEmits(['insert'])

// 状态变量
const visible = ref(false)
const startPoint = ref('')
const endPoint = ref('')
const waypoints = ref<string[]>([])
const mapZoom = ref(12)
const mapImageUrl = ref('')

// 有效的途经点（过滤掉空的）
const validWaypoints = computed(() => {
  return waypoints.value.filter((point: string) => point.trim() !== '')
})

// 格式化缩放级别提示
const formatZoom = (val: number) => {
  if (val <= 3) return '国家'
  if (val <= 7) return '省级'
  if (val <= 10) return '城市'
  if (val <= 13) return '区县'
  if (val <= 15) return '街道'
  return '详细'
}

// 打开对话框
const open = () => {
  visible.value = true
}

// 添加途经点
const addWaypoint = () => {
  waypoints.value.push('')
}

// 移除途经点
const removeWaypoint = (index: number) => {
  waypoints.value.splice(index, 1)
}

// 生成地图
const generateMap = () => {
  if (!startPoint.value || !endPoint.value) {
    ElMessage.warning('请输入起点和终点')
    return
  }

  try {
    // 直接使用Canvas生成地图，避免API限制和跨域问题
    createBackupMap()
    ElMessage.success('地图生成成功')
  } catch (error) {
    console.error('生成地图出错:', error)
    ElMessage.error('生成地图出错')
  }
}

// 创建备用地图 - 使用Canvas直接生成地图
const createBackupMap = () => {
  // 创建一个简单的文本路线地图（纯HTML5 Canvas）
  const canvas = document.createElement('canvas')
  canvas.width = 800
  canvas.height = 500
  const ctx = canvas.getContext('2d')
  
  if (ctx) {
    // 绘制背景 - 使用更美观的背景
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height)
    gradient.addColorStop(0, '#f8f8f8')
    gradient.addColorStop(1, '#e8e8e8')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // 绘制网格
    ctx.strokeStyle = '#ddd'
    ctx.lineWidth = 0.5
    for (let i = 50; i < canvas.width; i += 50) {
      ctx.beginPath()
      ctx.moveTo(i, 0)
      ctx.lineTo(i, canvas.height)
      ctx.stroke()
    }
    for (let i = 50; i < canvas.height; i += 50) {
      ctx.beginPath()
      ctx.moveTo(0, i)
      ctx.lineTo(canvas.width, i)
      ctx.stroke()
    }
    
    // 绘制标题框
    ctx.fillStyle = '#fff'
    ctx.shadowColor = 'rgba(0,0,0,0.1)'
    ctx.shadowBlur = 10
    ctx.shadowOffsetX = 0
    ctx.shadowOffsetY = 2
    roundRect(ctx, canvas.width/2 - 150, 15, 300, 50, 5, true)
    ctx.shadowBlur = 0
    
    // 标题
    ctx.fillStyle = '#333'
    ctx.font = 'bold 24px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('旅游路线地图', canvas.width/2, 48)
    
    // 设置路线点
    const points = [startPoint.value, ...validWaypoints.value, endPoint.value]
    const pointCount = points.length
    
    // 计算路线分布
    const startX = 100
    const endX = canvas.width - 100
    const centerY = canvas.height / 2 + 20
    
    // 绘制连接线 - 使用曲线连接
    ctx.beginPath()
    ctx.moveTo(startX, centerY)
    
    // 如果有多个点，使用贝塞尔曲线
    if (pointCount > 2) {
      for (let i = 1; i < pointCount - 1; i++) {
        const x = startX + (endX - startX) * (i / (pointCount - 1))
        const prevX = startX + (endX - startX) * ((i - 1) / (pointCount - 1))
        const nextX = startX + (endX - startX) * ((i + 1) / (pointCount - 1))
        
        const cp1x = (x + prevX) / 2
        const cp2x = (x + nextX) / 2
        
        if (i === 1) {
          ctx.quadraticCurveTo(cp1x, centerY - 40, x, centerY)
        } else {
          ctx.bezierCurveTo(cp1x, centerY - 20, cp2x, centerY - 20, x, centerY)
        }
      }
      ctx.quadraticCurveTo((endX + startX + (endX - startX) * ((pointCount - 2) / (pointCount - 1))) / 2, centerY + 40, endX, centerY)
    } else {
      // 只有起点和终点，使用简单曲线
      ctx.quadraticCurveTo((startX + endX) / 2, centerY - 50, endX, centerY)
    }
    
    ctx.strokeStyle = '#3388ff'
    ctx.lineWidth = 4
    ctx.stroke()
    
    // 在曲线上绘制箭头
    for (let i = 1; i < pointCount; i++) {
      const startPointX = startX + (endX - startX) * ((i - 1) / (pointCount - 1))
      const endPointX = startX + (endX - startX) * (i / (pointCount - 1))
      const midX = (startPointX + endPointX) / 2
      
      // 绘制箭头
      drawArrow(ctx, midX, centerY, 0, '#3388ff')
    }
    
    // 绘制点和文本
    for (let i = 0; i < pointCount; i++) {
      const x = startX + (endX - startX) * (i / (pointCount - 1))
      
      // 外部圆圈
      ctx.beginPath()
      ctx.arc(x, centerY, 18, 0, Math.PI * 2)
      ctx.fillStyle = '#fff'
      ctx.fill()
      ctx.strokeStyle = i === 0 ? '#3366FF' : (i === pointCount - 1 ? '#FF0000' : '#00CC33')
      ctx.lineWidth = 3
      ctx.stroke()
      
      // 内部圆圈
      ctx.beginPath()
      ctx.arc(x, centerY, 14, 0, Math.PI * 2)
      
      if (i === 0) {
        ctx.fillStyle = '#3366FF' // 起点
      } else if (i === pointCount - 1) {
        ctx.fillStyle = '#FF0000' // 终点
      } else {
        ctx.fillStyle = '#00CC33' // 途经点
      }
      
      ctx.fill()
      
      // 添加标签（起点/途经点/终点）
      ctx.fillStyle = '#fff'
      ctx.font = 'bold 14px Arial'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      let label = ''
      if (i === 0) {
        label = '起'
      } else if (i === pointCount - 1) {
        label = '终'
      } else {
        label = `${i}`
      }
      
      ctx.fillText(label, x, centerY)
      
      // 添加地点文本
      ctx.fillStyle = '#333'
      ctx.font = '16px Arial'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'
      
      const pointText = points[i]
      // 截断过长的文本
      const displayText = pointText.length > 10 ? pointText.substring(0, 10) + '...' : pointText
      
      // 添加文本背景
      const textWidth = ctx.measureText(displayText).width
      ctx.fillStyle = 'rgba(255,255,255,0.8)'
      roundRect(ctx, x - textWidth/2 - 5, centerY + 25, textWidth + 10, 28, 5, true)
      
      // 添加文本
      ctx.fillStyle = '#333'
      ctx.fillText(displayText, x, centerY + 30)
      
      // 添加位置标签
      let locationLabel = ''
      if (i === 0) {
        locationLabel = '起点'
        ctx.fillStyle = '#3366FF'
      } else if (i === pointCount - 1) {
        locationLabel = '终点'
        ctx.fillStyle = '#FF0000'
      } else {
        locationLabel = `途经点 ${i}`
        ctx.fillStyle = '#00CC33'
      }
      
      ctx.font = 'bold 14px Arial'
      ctx.textBaseline = 'bottom'
      ctx.fillText(locationLabel, x, centerY - 25)
    }
    
    // 添加比例尺和指南针
    drawScale(ctx, 50, canvas.height - 50)
    drawCompass(ctx, canvas.width - 50, 50)
    
    // 添加版权信息
    ctx.fillStyle = '#999'
    ctx.font = '12px Arial'
    ctx.textAlign = 'right'
    ctx.textBaseline = 'bottom'
    ctx.fillText('© 旅游攻略生成工具 ' + new Date().getFullYear(), canvas.width - 20, canvas.height - 20)
    
    // 转换为图片URL
    mapImageUrl.value = canvas.toDataURL('image/png')
  } else {
    // 如果Canvas上下文无法获取，使用纯文本
    ElMessage.warning('无法创建地图，将使用文本描述')
    mapImageUrl.value = ''
  }
}

// 辅助函数 - 绘制圆角矩形
function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number, fill: boolean, stroke = false) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
  ctx.lineTo(x + radius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
  if (fill) {
    ctx.fill()
  }
  if (stroke) {
    ctx.stroke()
  }
}

// 辅助函数 - 绘制箭头
function drawArrow(ctx: CanvasRenderingContext2D, x: number, y: number, angle: number, color: string) {
  ctx.save()
  ctx.translate(x, y)
  ctx.rotate(angle)
  
  // 箭头
  ctx.beginPath()
  ctx.moveTo(0, 0)
  ctx.lineTo(-10, -5)
  ctx.lineTo(-10, 5)
  ctx.closePath()
  
  ctx.fillStyle = color
  ctx.fill()
  
  ctx.restore()
}

// 辅助函数 - 绘制比例尺
function drawScale(ctx: CanvasRenderingContext2D, x: number, y: number) {
  ctx.fillStyle = 'rgba(255,255,255,0.8)'
  roundRect(ctx, x - 10, y - 40, 150, 30, 5, true)
  
  ctx.beginPath()
  ctx.moveTo(x, y - 20)
  ctx.lineTo(x + 100, y - 20)
  ctx.strokeStyle = '#333'
  ctx.lineWidth = 2
  ctx.stroke()
  
  // 刻度
  for (let i = 0; i <= 100; i += 25) {
    ctx.beginPath()
    ctx.moveTo(x + i, y - 15)
    ctx.lineTo(x + i, y - 25)
    ctx.stroke()
  }
  
  ctx.fillStyle = '#333'
  ctx.font = '12px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'top'
  ctx.fillText('0', x, y - 30)
  ctx.fillText('50km', x + 50, y - 30)
  ctx.fillText('100km', x + 100, y - 30)
}

// 辅助函数 - 绘制指南针
function drawCompass(ctx: CanvasRenderingContext2D, x: number, y: number) {
  // 背景圆
  ctx.beginPath()
  ctx.arc(x, y, 30, 0, Math.PI * 2)
  ctx.fillStyle = 'rgba(255,255,255,0.8)'
  ctx.fill()
  ctx.strokeStyle = '#ccc'
  ctx.lineWidth = 1
  ctx.stroke()
  
  // 内部圆
  ctx.beginPath()
  ctx.arc(x, y, 25, 0, Math.PI * 2)
  ctx.strokeStyle = '#999'
  ctx.stroke()
  
  // 指针
  // 北
  ctx.beginPath()
  ctx.moveTo(x, y - 20)
  ctx.lineTo(x - 5, y)
  ctx.lineTo(x + 5, y)
  ctx.closePath()
  ctx.fillStyle = '#FF0000'
  ctx.fill()
  
  // 南
  ctx.beginPath()
  ctx.moveTo(x, y + 20)
  ctx.lineTo(x - 5, y)
  ctx.lineTo(x + 5, y)
  ctx.closePath()
  ctx.fillStyle = '#3366FF'
  ctx.fill()
  
  // 方向文字
  ctx.fillStyle = '#333'
  ctx.font = 'bold 12px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('N', x, y - 15)
  ctx.fillText('S', x, y + 15)
  ctx.fillText('E', x + 15, y)
  ctx.fillText('W', x - 15, y)
}

// 将地图插入编辑器
const insertMap = () => {
  if (!mapImageUrl.value) {
    ElMessage.warning('请先生成地图')
    return
  }
  
  try {
    console.log('准备插入图片URL:', mapImageUrl.value)
    
    // 只发送纯图片URL作为dataUrl属性
    emit('insert', { dataUrl: mapImageUrl.value })
    
    // 显示成功消息
    ElMessage.success('已发送地图数据')
    
    // 关闭对话框
    handleClose()
  } catch (error) {
    console.error('插入地图出错:', error)
    ElMessage.error('插入地图出错：' + (error instanceof Error ? error.message : String(error)))
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  startPoint.value = ''
  endPoint.value = ''
  waypoints.value = []
  mapImageUrl.value = ''
}

// 暴露组件接口
defineExpose({
  open
})
</script>

<style scoped>
.map-container {
  display: flex;
  height: 500px;
  gap: 20px;
}

.route-inputs {
  width: 300px;
  padding: 10px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.map-preview {
  flex: 1;
  height: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.preview-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.empty-preview {
  color: #999;
  text-align: center;
  padding: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.input-label {
  font-weight: 500;
  margin-bottom: 5px;
}

.waypoints-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
  border: 1px dashed #ddd;
  border-radius: 4px;
}

.waypoint {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.location-input {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 5px;
}

.location-input .el-input {
  flex: 1;
}

.route-preview {
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 10px;
  margin-top: 10px;
}

.route-preview h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #333;
}

.route-list {
  display: flex;
  flex-direction: column;
}

.route-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.route-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.route-item.start .route-icon {
  background-color: #3366CC;
}

.route-item.waypoint .route-icon {
  background-color: #00CC33;
}

.route-item.end .route-icon {
  background-color: #CC0000;
}

.route-name {
  font-size: 14px;
}

.route-connection {
  display: flex;
  flex-direction: column;
}

.route-line {
  width: 2px;
  height: 20px;
  background-color: #ddd;
  margin-left: 12px;
}
</style> 