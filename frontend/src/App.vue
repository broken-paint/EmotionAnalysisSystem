<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'
import dataJson from './data/stream_results.json'
import MyEmotionScore from './components/EmotionScore.vue'
import MyEmotionCount from './components/EmotionCount.vue'


</script>

<template>
  <div class="container">
    <MyEmotionScore class="item"></MyEmotionScore>
    <MyEmotionCount class="item"></MyEmotionCount>
  </div>
</template>

<style scoped>
@import "tailwindcss";

.container {
  display: flex;
  gap: 20px;
  justify-content: space-around;
  flex-wrap: wrap;
}
.item {
  flex-grow: 1;
}
</style>
