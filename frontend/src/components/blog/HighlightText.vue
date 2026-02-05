<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  text: string
  query: string
}>()

// 高亮关键词
const highlightedText = computed(() => {
  if (!props.query.trim()) {
    return props.text
  }

  // 转义特殊字符
  const escapedQuery = props.query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

  // 创建正则表达式（不区分大小写）
  const regex = new RegExp(`(${escapedQuery})`, 'gi')

  // 替换匹配的文本为高亮版本
  return props.text.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-900/50 text-current rounded px-0.5">$1</mark>')
})
</script>

<template>
  <span v-html="highlightedText" />
</template>
