<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  maxTilt?: number
  perspective?: number
  scale?: number
}>()

const cardRef = ref<HTMLElement>()
const isHovering = ref(false)
const transform = ref('')

const maxTilt = props.maxTilt || 15
const perspective = props.perspective || 1000
const scale = props.scale || 1.05

const handleMouseMove = (e: MouseEvent) => {
  if (!cardRef.value) return

  const rect = cardRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  const centerX = rect.width / 2
  const centerY = rect.height / 2

  const rotateX = ((y - centerY) / centerY) * maxTilt
  const rotateY = ((x - centerX) / centerX) * -maxTilt

  transform.value = `
    perspective(${perspective}px)
    rotateX(${rotateX}deg)
    rotateY(${rotateY}deg)
    scale3d(${scale}, ${scale}, ${scale})
  `
}

const handleMouseLeave = () => {
  isHovering.value = false
  transform.value = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)'
}

const handleMouseEnter = () => {
  isHovering.value = true
}
</script>

<template>
  <div
    ref="cardRef"
    class="tilt-card"
    :style="{ transform }"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
    @mouseenter="handleMouseEnter"
  >
    <slot />
  </div>
</template>

<style scoped>
.tilt-card {
  transition: transform 0.1s ease-out;
  transform-style: preserve-3d;
  will-change: transform;
}

.tilt-card:hover {
  z-index: 10;
}

/* 子元素保持 3D 效果 */
.tilt-card > * {
  transform: translateZ(20px);
}

@media (prefers-reduced-motion: reduce) {
  .tilt-card {
    transform: none !important;
  }
}
</style>
