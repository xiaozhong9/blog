<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps<{
  code: string
  language?: string
}>()

const copied = ref(false)
const timeoutId = ref<number | null>(null)

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true

    // 重置状态
    if (timeoutId.value) clearTimeout(timeoutId.value)
    timeoutId.value = window.setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<template>
  <button
    @click="copyToClipboard"
    class="code-copy-btn"
    :title="copied ? '已复制!' : '复制代码'"
    :class="{ 'copied': copied }"
  >
    <Icon
      :icon="copied ? 'lucide:check' : 'lucide:copy'"
      class="w-4 h-4"
    />
  </button>
</template>

<style scoped>
.code-copy-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: white;
  opacity: 0;
  transform: translateY(-4px);
  transition: all 0.2s ease;
}

.code-copy-btn:hover {
  background: rgba(96, 165, 250, 0.9);
  border-color: rgba(96, 165, 250, 0.9);
}

.code-copy-btn.copied {
  background: rgba(34, 197, 94, 0.9);
  border-color: rgba(34, 197, 94, 0.9);
}

pre:hover .code-copy-btn,
.code-copy-btn:focus {
  opacity: 1;
  transform: translateY(0);
}

.code-copy-btn.copied:focus {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  .code-copy-btn {
    transition: none;
  }
}
</style>
