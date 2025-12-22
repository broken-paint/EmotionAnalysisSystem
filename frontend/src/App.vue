<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'
import dataJson from './data/stream_results.json'
import MyEmotionScore from './components/EmotionScore.vue'
import MyEmotionCount from './components/EmotionCount.vue'


</script>

<template>
  <div class="ml-37.5 mr-37.5 flex gap-12.5 justify-around flex-wrap">
    <MyEmotionScore class="max-w-[60%] grow"></MyEmotionScore>
    <MyEmotionCount class="max-w-[40%] grow"></MyEmotionCount>
  </div>
</template>

<style scoped>
</style>
