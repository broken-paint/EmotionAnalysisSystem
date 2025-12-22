<script setup lang="ts">
import MyEmotionScore from './EmotionScore.vue'
import MyEmotionCount from './EmotionCount.vue'
</script>

<template>
  <div class="ml-37.5 mr-37.5 flex gap-12.5 justify-around flex-wrap">
    <MyEmotionScore class="max-w-[60%] grow"></MyEmotionScore>
    <MyEmotionCount class="max-w-[40%] grow"></MyEmotionCount>
  </div>
</template>

<style scoped>
</style>
