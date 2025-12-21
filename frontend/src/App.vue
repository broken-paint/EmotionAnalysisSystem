<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'
import dataJson from './data/stream_results.json'
import MyEmotionScore from './components/EmotionScore.vue'
import MyEmotionCount from './components/EmotionCount.vue'


</script>

<template>
  <div class="ml-[150px] mr-[150px] flex gap-[50px] justify-around flex-wrap">
    <MyEmotionScore class="max-w-[60%] flex-grow"></MyEmotionScore>
    <MyEmotionCount class="max-w-[40%] flex-grow"></MyEmotionCount>
  </div>
</template>

<style scoped>
@import "tailwindcss";
</style>
