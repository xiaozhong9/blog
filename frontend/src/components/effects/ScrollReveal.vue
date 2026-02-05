<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isVisible = ref(false)
const elementRef = ref<HTMLElement>()

// 使用 Intersection Observer 检测元素是否进入视口
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        isVisible.value = true
        observer.disconnect() // 只触发一次
      }
    })
  },
  {
    threshold: 0.1, // 10% 可见时触发
    rootMargin: '0px 0px -50px 0px', // 底部提前触发
  }
)

onMounted(() => {
  // 立即显示内容，不需要等待动画
  // 使用 requestAnimationFrame 确保在下一帧渲染
  requestAnimationFrame(() => {
    isVisible.value = true
  })

  // 备用方案：如果 observer 触发了，设置可见
  if (elementRef.value) {
    observer.observe(elementRef.value)
  }
})

onUnmounted(() => {
  observer.disconnect()
})
</script>

<template>
  <div
    ref="elementRef"
    class="scroll-reveal"
    :class="{ 'is-visible': isVisible }"
  >
    <slot />
  </div>
</template>

<style scoped>
.scroll-reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.scroll-reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* 延迟变体 */
.scroll-reveal.delay-100 {
  transition-delay: 100ms;
}

.scroll-reveal.delay-200 {
  transition-delay: 200ms;
}

.scroll-reveal.delay-300 {
  transition-delay: 300ms;
}

/* 从左侧进入 */
.scroll-reveal.from-left {
  transform: translateX(-50px);
}

/* 从右侧进入 */
.scroll-reveal.from-right {
  transform: translateX(50px);
}

/* 从缩放进入 */
.scroll-reveal.from-scale {
  transform: scale(0.9);
}

@media (prefers-reduced-motion: reduce) {
  .scroll-reveal {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>
