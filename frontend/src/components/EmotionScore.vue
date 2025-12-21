<script lang="ts">
  export default {
    name:"MyEmotionScore"
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
  const labels = frames.map((f: any) => String(f.frame_index))

  const emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
  const colors = {
    angry: 'rgba(255,99,132,0.6)',
    disgust: 'rgba(75,192,192,0.6)',
    fear: 'rgba(153,102,255,0.6)',
    happy: 'rgba(255,206,86,0.6)',
    neutral: 'rgba(54,162,235,0.6)',
    sad: 'rgba(100,100,100,0.6)',
    surprise: 'rgba(255,159,64,0.6)'
  }

  const datasets = emotions.map((emo) => ({
    label: emo,
    data: frames.map((f: any) => {
      const faces = f.faces || []
      if (faces.length === 0) return 0
      const scores = faces[0].scores || {}
      return Number((scores[emo] ?? 0) * 1)
    }),
    borderColor: colors[emo as keyof typeof colors],
    backgroundColor: (colors as any)[emo],
    tension: 0.2,
    fill: false,
    pointRadius: 2
  }))

  if (canvasRef.value) {
    chart = new Chart(canvasRef.value, {
      type: 'line',
      data: {
        labels,
        datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          title: { display: true, text: '每帧表情得分' }
        },
        scales: {
          y: { beginAtZero: true, max: 1 }
        }
      }
    })
  }
})

onBeforeUnmount(() => {
  if (chart) {
    chart.destroy()
    chart = null
  }
})
</script>

<template>
  <div style="height:500px; padding:12px;">
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<style scoped>
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
