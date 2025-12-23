<script setup lang="ts">
</script>

<template>
  <header class="bg-white shadow-sm sticky top-0 z-50 h-16">
    <div class="container mx-auto px-4 h-full flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <h1 class="text-xl font-bold text-gray-800">表情分析系统</h1>
        <nav class="flex items-center space-x-2">
          <RouterLink to="/welcome" class="px-3 py-2 rounded hover:bg-gray-100">欢迎</RouterLink>
          <RouterLink to="/home" class="px-3 py-2 rounded hover:bg-gray-100">首页</RouterLink>
          <RouterLink to="/results" class="px-3 py-2 rounded hover:bg-gray-100">结果</RouterLink>
          <RouterLink to="/about" class="px-3 py-2 rounded hover:bg-gray-100">关于</RouterLink>
        </nav>
      </div>
      <div class="text-sm text-gray-500">v1.0</div>
    </div>
  </header>

  <main class="app-content">
    <RouterView />
  </main>
</template>

<style scoped>
.app-content {
  min-height: calc(100vh - 64px); /* viewport minus header (h-16 = 64px) */
}
</style>
