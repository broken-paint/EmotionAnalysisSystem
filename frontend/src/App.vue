<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'
import dataJson from './data/stream_results.json'
import MyEmotionScore from './components/EmotionScore.vue'
import MyEmotionCount from './components/EmotionCount.vue'


</script>

<template>
  <div class="container">
    <span>
      <MyEmotionScore class="item"></MyEmotionScore>
    </span>
    <span>
      <MyEmotionCount class="item"></MyEmotionCount>
    </span>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  gap: 20px;
}
.item {
  flex-grow: 1;
}
</style>
