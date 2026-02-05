<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const progress = ref(0)

// 计算阅读进度
const updateProgress = () => {
  const windowHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight - windowHeight
  const scrolled = window.scrollY

  const percentage = (scrolled / documentHeight) * 100
  progress.value = Math.min(100, Math.max(0, percentage))
}

// 节流函数
const throttle = (func: () => void, delay: number) => {
  let lastCall = 0
  return () => {
    const now = Date.now()
    if (now - lastCall >= delay) {
      lastCall = now
      func()
    }
  }
}

const throttledUpdate = throttle(updateProgress, 50)

onMounted(() => {
  window.addEventListener('scroll', throttledUpdate)
  updateProgress() // 初始化
})

onUnmounted(() => {
  window.removeEventListener('scroll', throttledUpdate)
})
</script>

<template>
  <!-- 顶部进度条 -->
  <div
    class="fixed top-0 left-0 right-0 h-1 bg-gray-200 dark:bg-gray-800 z-50"
  >
    <div
      class="h-full bg-gradient-to-r from-primary-from to-primary-to
             transition-all duration-150 ease-out"
      :style="{ width: `${progress}%` }"
    />
  </div>
</template>
