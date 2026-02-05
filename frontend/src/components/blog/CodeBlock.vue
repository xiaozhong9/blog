<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps<{
  code: string
  language?: string
}>()

const isCopied = ref(false)

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    isCopied.value = true

    // 2秒后重置状态
    setTimeout(() => {
      isCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('复制失败:', err)
  }
}
</script>

<template>
  <div class="code-block-wrapper relative group">
    <!-- 语言标签 -->
    <div
      v-if="language"
      class="absolute top-3 right-14 px-2 py-1 text-xs font-medium rounded
             bg-gray-200 dark:bg-gray-700
             text-gray-600 dark:text-gray-300
             select-none"
    >
      {{ language }}
    </div>

    <!-- 复制按钮 -->
    <button
      @click="copyToClipboard"
      class="absolute top-3 right-3 p-2 rounded-lg
             bg-gray-200 dark:bg-gray-700
             text-gray-600 dark:text-gray-300
             hover:bg-gray-300 dark:hover:bg-gray-600
             transition-colors
             opacity-0 group-hover:opacity-100
             focus:opacity-100"
      :title="isCopied ? '已复制！' : '复制代码'"
    >
      <Icon
        :icon="isCopied ? 'lucide:check' : 'lucide:copy'"
        class="w-4 h-4"
        :class="{ 'text-green-600 dark:text-green-400': isCopied }"
      />
    </button>

    <!-- 代码内容 -->
    <pre
      class="!mt-0 !rounded-lg"
    ><slot /></pre>
  </div>
</template>

<style scoped>
.code-block-wrapper {
  position: relative;
}
</style>
