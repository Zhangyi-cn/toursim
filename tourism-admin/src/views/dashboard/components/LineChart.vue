<template>
  <div ref="chartRef" class="line-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    borderColor: string
    fill: boolean
  }[]
}

const props = defineProps<{
  data: ChartData
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  
  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      top: 40,
      right: 20,
      bottom: 40,
      left: 60
    },
    xAxis: {
      type: 'category',
      data: props.data.labels,
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: '#eee'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    series: props.data.datasets.map(dataset => ({
      name: dataset.label,
      type: 'line',
      data: dataset.data,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        color: dataset.borderColor,
        width: 2
      },
      itemStyle: {
        color: dataset.borderColor,
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: dataset.fill ? {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: echarts.color.lift(dataset.borderColor, 0.3) },
          { offset: 1, color: echarts.color.lift(dataset.borderColor, 0.1) }
        ])
      } : undefined
    }))
  }
  
  chart.setOption(option)
}

const updateChart = () => {
  if (!chart) return
  
  chart.setOption({
    xAxis: {
      data: props.data.labels
    },
    series: props.data.datasets.map(dataset => ({
      name: dataset.label,
      data: dataset.data
    }))
  })
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
  
  window.addEventListener('resize', () => {
    chart?.resize()
  })
})

defineExpose({
  chart
})
</script>

<style lang="scss" scoped>
.line-chart {
  width: 100%;
  height: 100%;
}
</style> 