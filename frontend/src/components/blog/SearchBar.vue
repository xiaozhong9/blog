<script setup lang="ts">
import { ref, watch } from 'vue'
import { Icon } from '@iconify/vue'

// 简单的 debounce 工具函数
function debounce<T extends (...args: any[]) => any>(func: T, delay: number): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null

  return function(this: any, ...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      func.apply(this, args)
    }, delay)
  }
}

const props = defineProps<{
  modelValue: string
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'search': [query: string]
}>()

const searchQuery = ref(props.modelValue)
const isFocused = ref(false)

// 防抖搜索
const debouncedSearch = debounce((query: string) => {
  emit('search', query)
}, 300)

// 监听输入变化
watch(searchQuery, (newValue) => {
  emit('update:modelValue', newValue)
  debouncedSearch(newValue)
})

// 监听 props 变化
watch(() => props.modelValue, (newValue) => {
  searchQuery.value = newValue
})

// 处理失焦事件（延迟隐藏下拉建议）
const handleBlur = () => {
  setTimeout(() => {
    isFocused.value = false
  }, 200)
}

// 清空搜索
const clearSearch = () => {
  searchQuery.value = ''
  emit('search', '')
}

// 获取热门搜索关键词
const popularSearches = ['Vue', 'TypeScript', 'Tailwind CSS', 'Vite']
const recentSearches = ref<string[]>([])

// 从 localStorage 加载最近搜索
const loadRecentSearches = () => {
  try {
    const stored = localStorage.getItem('nano_banana_recent_searches')
    if (stored) {
      recentSearches.value = JSON.parse(stored)
    }
  } catch (err) {
    console.error('Failed to load recent searches:', err)
  }
}

// 保存搜索关键词
const saveSearch = (query: string) => {
  if (!query.trim()) return

  try {
    const searches = [...recentSearches.value]
    const index = searches.indexOf(query)

    // 移除重复项
    if (index > -1) {
      searches.splice(index, 1)
    }

    // 添加到开头
    searches.unshift(query)

    // 保留最近 5 条
    recentSearches.value = searches.slice(0, 5)

    localStorage.setItem('nano_banana_recent_searches', JSON.stringify(recentSearches.value))
  } catch (err) {
    console.error('Failed to save recent search:', err)
  }
}

// 点击热门搜索
const onPopularSearch = (keyword: string) => {
  searchQuery.value = keyword
  saveSearch(keyword)
  emit('search', keyword)
}

// 点击最近搜索
const onRecentSearch = (keyword: string) => {
  searchQuery.value = keyword
  emit('search', keyword)
}

// 初始化
loadRecentSearches()
</script>

<template>
  <div class="search-bar-container">
    <!-- 搜索输入框 -->
    <div class="relative">
      <Icon
        icon="lucide:search"
        class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-light-text-muted dark:text-dark-text-muted"
      />

      <input
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder || '搜索文章标题、描述或内容...'"
        @focus="isFocused = true"
        @blur="handleBlur"
        @keydown.enter="emit('search', searchQuery); saveSearch(searchQuery)"
        class="w-full pl-10 pr-12 py-3 rounded-lg border border-light-border dark:border-dark-border
               bg-white dark:bg-gray-800
               text-light-text-primary dark:text-dark-text-primary
               placeholder-light-text-muted dark:placeholder-dark-text-muted
               focus:outline-none focus:ring-2 focus:ring-primary-from focus:border-transparent
               transition-shadow"
      />

      <!-- 清空按钮 -->
      <button
        v-if="searchQuery"
        @click="clearSearch"
        class="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded
               text-light-text-muted dark:text-dark-text-muted
               hover:text-light-text-primary dark:hover:text-dark-text-primary
               transition-colors"
      >
        <Icon icon="lucide:x" class="w-5 h-5" />
      </button>
    </div>

    <!-- 下拉建议 -->
    <div
      v-if="isFocused && (recentSearches.length > 0 || popularSearches.length > 0)"
      class="absolute z-50 w-full mt-2 bg-white dark:bg-gray-800 rounded-lg
             border border-light-border dark:border-dark-border
             shadow-lg overflow-hidden"
    >
      <!-- 最近搜索 -->
      <div v-if="recentSearches.length > 0" class="p-2">
        <div class="px-3 py-2 text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase">
          最近搜索
        </div>
        <div class="space-y-1">
          <button
            v-for="item in recentSearches"
            :key="item"
            @click="onRecentSearch(item)"
            class="w-full px-3 py-2 text-left rounded-lg
                   text-light-text-primary dark:text-dark-text-primary
                   hover:bg-gray-100 dark:hover:bg-gray-700
                   transition-colors flex items-center gap-2"
          >
            <Icon icon="lucide:clock" class="w-4 h-4 text-light-text-muted dark:text-dark-text-muted" />
            <span class="flex-1 truncate">{{ item }}</span>
          </button>
        </div>
      </div>

      <!-- 热门搜索 -->
      <div v-if="popularSearches.length > 0" class="p-2 border-t border-light-border dark:border-dark-border">
        <div class="px-3 py-2 text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase">
          热门搜索
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="keyword in popularSearches"
            :key="keyword"
            @click="onPopularSearch(keyword)"
            class="px-3 py-1.5 text-sm rounded-lg
                   bg-gray-100 dark:bg-gray-700
                   text-light-text-primary dark:text-dark-text-primary
                   hover:bg-gray-200 dark:hover:bg-gray-600
                   transition-colors"
          >
            {{ keyword }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-bar-container {
  position: relative;
}
</style>
