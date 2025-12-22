<script setup lang="ts">
  const goToHome = () => {
    
  }
</script>

<template>
  <body class="bg-gray-50 min-h-screen flex items-center justify-center p-4">
    <!-- 主容器 -->
    <div class="w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden">
      <!-- 顶部横幅 -->
      <div class="bg-gradient-custom text-white p-8 md:p-12">
        <div class="flex flex-col items-center text-center">
          <!-- 标题 -->
          <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 leading-tight">
            left-behind children's emotion analysis system
          </h1>
          <!-- 副标题 -->
          <p class="text-lg md:text-xl opacity-80 mb-8 max-w-2xl">
            Intelligent emotion recognition and analysis system for left-behind children
          </p>
          <!-- 跳转按钮 -->
          <button @click="goToHome" class="btn-hover-effect bg-yellow-400 text-gray-800 font-bold py-4 px-10 rounded-full text-xl shadow-lg">
            Get Started
          </button>
        </div>
      </div>

      <!-- 底部信息栏 -->
      <div class="bg-gray-100 p-6 text-center text-gray-600">
        <p class="font-medium">
          Based on FER2013 Dataset & Machine Learning
        </p>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="absolute bottom-4 text-gray-500 text-sm">
      © 2025 Left-behind Children's Emotion Analysis System
    </footer>
  </body>
</template>

<style scoped>
</style>
