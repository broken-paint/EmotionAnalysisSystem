<script lang="ts">
  export default {
    name:'MyEmotionCount'
  }
</script>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'
import dataJson from '../data/stream_results.json'

Chart.register(...registerables)

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

onMounted(() => {
  const frames = (dataJson as any).frames || []
  
  // 统计各个情绪的数量
  const emotionCount: { [key: string]: number } = {
    angry: 0,
    disgust: 0,
    fear: 0,
    happy: 0,
    neutral: 0,
    sad: 0,
    surprise: 0
  }
  
  frames.forEach((frame: any) => {
    if (frame.faces && Array.isArray(frame.faces)) {
      frame.faces.forEach((face: any) => {
        if (face.emotion && emotionCount.hasOwnProperty(face.emotion)) {
          (emotionCount[face.emotion] as any)++
        }
      })
    }
  })
  
  const labels = Object.keys(emotionCount)
  const data = Object.values(emotionCount)
  
  const colors = [
    'rgba(255,99,132,0.6)',    // angry
    'rgba(75,192,192,0.6)',    // disgust
    'rgba(153,102,255,0.6)',   // fear
    'rgba(255,206,86,0.6)',    // happy
    'rgba(54,162,235,0.6)',    // neutral
    'rgba(100,100,100,0.6)',   // sad
    'rgba(255,159,64,0.6)'     // surprise
  ]
  
  const borderColors = [
    'rgba(255,99,132,1)',
    'rgba(75,192,192,1)',
    'rgba(153,102,255,1)',
    'rgba(255,206,86,1)',
    'rgba(54,162,235,1)',
    'rgba(100,100,100,1)',
    'rgba(255,159,64,1)'
  ]
  
  if (canvasRef.value) {
    chart = new Chart(canvasRef.value, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [
          {
            label: '情绪统计',
            data: data,
            backgroundColor: colors,
            borderColor: borderColors,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'right'
          },
          title: {
            display: true,
            text: '情绪分布统计'
          }
        }
      }
    })
  }
})

onBeforeUnmount(() => {
  if (chart) {
    chart.destroy()
  }
})
</script>

<template>
  <div class="emotion-count-container">
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<style scoped>
.emotion-count-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height:500px; 
  padding:12px;
}

div {
  background: #fff; 
  border-radius: 20px; 
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

canvas { 
  width: 100%; 
  height: 100%; 
}
</style>