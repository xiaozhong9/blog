<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'

const isVisible = ref(false)
const scrollProgress = ref(0)

// 计算滚动进度
const updateScrollProgress = () => {
  const scrollTop = window.scrollY
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  scrollProgress.value = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0

  // 超过 300px 显示按钮
  isVisible.value = scrollTop > 300
}

// 滚动到顶部
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  })
}

// 环形进度计算
const circumference = 2 * Math.PI * 22 // r=22
const strokeDashoffset = computed(() => {
  return circumference - (scrollProgress.value / 100) * circumference
})

onMounted(() => {
  window.addEventListener('scroll', updateScrollProgress)
  updateScrollProgress() // 初始化
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateScrollProgress)
})
</script>

<template>
  <Transition
    enter-active-class="transition-all duration-300"
    enter-from-class="opacity-0 translate-y-4"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition-all duration-200"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 translate-y-4"
  >
    <button
      v-if="isVisible"
      @click="scrollToTop"
      class="fixed bottom-8 right-8 z-40 group"
      title="回到顶部"
    >
      <!-- 环形进度条 -->
      <svg class="w-14 h-14 transform -rotate-90" viewBox="0 0 50 50">
        <!-- 背景圆环 -->
        <circle
          cx="25"
          cy="25"
          r="22"
          fill="none"
          stroke="currentColor"
          :stroke-width="3"
          class="text-light-border dark:text-dark-border opacity-20"
        />
        <!-- 进度圆环 -->
        <circle
          cx="25"
          cy="25"
          r="22"
          fill="none"
          stroke="url(#gradient)"
          stroke-width="3"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="strokeDashoffset"
          stroke-linecap="round"
          class="transition-all duration-300"
        />
        <!-- 渐变定义 -->
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#60A5FA" />
            <stop offset="100%" stop-color="#A78BFA" />
          </linearGradient>
        </defs>
      </svg>

      <!-- 向上箭头 -->
      <div class="absolute inset-0 flex items-center justify-center">
        <Icon
          icon="lucide:chevron-up"
          class="w-5 h-5 text-primary-from transform rotate-90 group-hover:-translate-y-0.5 transition-transform duration-200"
        />
      </div>
    </button>
  </Transition>
</template>

<style scoped>
button {
  cursor: pointer;
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
  }
}
</style>
