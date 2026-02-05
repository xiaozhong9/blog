<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'

interface FilterOptions {
  sortBy?: 'date' | 'popularity' | 'readingTime'
  sortOrder?: 'asc' | 'desc'
  featuredOnly?: boolean
}

const props = defineProps<{
  modelValue: FilterOptions
}>()

const emit = defineEmits<{
  'update:modelValue': [value: FilterOptions]
}>()

const { t } = useI18n()

// 排序选项（移除标题排序）
const sortOptions = [
  { value: 'date', label: '最新发布', icon: 'lucide:clock' },
  { value: 'popularity', label: '热度最高', icon: 'lucide:flame' },
  { value: 'readingTime', label: '阅读时长', icon: 'lucide:book-open' },
]

// 本地状态
const localSortBy = ref(props.modelValue.sortBy || 'date')
const localSortOrder = ref(props.modelValue.sortOrder || 'desc')
const localFeaturedOnly = ref(props.modelValue.featuredOnly || false)

// 展开/折叠状态
const isExpanded = ref(true)

// 监听变化并同步
watch([localSortBy, localSortOrder, localFeaturedOnly], () => {
  emit('update:modelValue', {
    sortBy: localSortBy.value as any,
    sortOrder: localSortOrder.value as any,
    featuredOnly: localFeaturedOnly.value,
  })
})

// 清空所有筛选
const clearFilters = () => {
  localSortBy.value = 'date'
  localSortOrder.value = 'desc'
  localFeaturedOnly.value = false
}

// 计算活动筛选数量
const activeFilterCount = computed(() => {
  let count = 0
  if (localFeaturedOnly.value) count++
  return count
})
</script>

<template>
  <div class="post-filters">
    <!-- 头部 -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary flex items-center gap-2">
        <Icon icon="lucide:filter" class="w-5 h-5" />
        筛选
        <span v-if="activeFilterCount > 0" class="px-2 py-0.5 text-xs rounded-full bg-primary-from text-white">
          {{ activeFilterCount }}
        </span>
      </h3>
      <button
        @click="isExpanded = !isExpanded"
        class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        <Icon
          :icon="isExpanded ? 'lucide:chevron-up' : 'lucide:chevron-down'"
          class="w-5 h-5 text-light-text-secondary dark:text-dark-text-secondary"
        />
      </button>
    </div>

    <!-- 筛选内容 -->
    <div v-show="isExpanded" class="space-y-6">
      <!-- 排序方式 -->
      <div>
        <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
          排序方式
        </label>
        <div class="space-y-2">
          <button
            v-for="option in sortOptions"
            :key="option.value"
            @click="localSortBy = option.value as any"
            class="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors"
            :class="localSortBy === option.value
              ? 'bg-primary-from/10 text-primary-from'
              : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-light-text-primary dark:text-dark-text-primary'"
          >
            <Icon :icon="option.icon" class="w-4 h-4" />
            <span class="flex-1 text-left text-sm">{{ option.label }}</span>
            <Icon
              v-if="localSortBy === option.value"
              icon="lucide:check"
              class="w-4 h-4"
            />
          </button>
        </div>
      </div>

      <!-- 排序顺序 -->
      <div>
        <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
          排序顺序
        </label>
        <div class="flex gap-2">
          <button
            @click="localSortOrder = 'desc'"
            class="flex-1 px-3 py-2 text-sm rounded-lg transition-colors"
            :class="localSortOrder === 'desc'
              ? 'bg-primary-from text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary'"
          >
            降序
          </button>
          <button
            @click="localSortOrder = 'asc'"
            class="flex-1 px-3 py-2 text-sm rounded-lg transition-colors"
            :class="localSortOrder === 'asc'
              ? 'bg-primary-from text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary'"
          >
            升序
          </button>
        </div>
      </div>

      <!-- 精选文章 -->
      <div>
        <label class="flex items-center gap-3 cursor-pointer">
          <input
            v-model="localFeaturedOnly"
            type="checkbox"
            class="w-4 h-4 rounded border-gray-300 text-primary-from focus:ring-primary-from"
          />
          <span class="text-sm text-light-text-primary dark:text-dark-text-primary">
            仅显示精选文章
          </span>
        </label>
      </div>

      <!-- 清空筛选 -->
      <button
        v-if="activeFilterCount > 0"
        @click="clearFilters"
        class="w-full px-4 py-2 text-sm rounded-lg border border-light-border dark:border-dark-border
               text-light-text-primary dark:text-dark-text-primary
               hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
      >
        清空所有筛选
      </button>
    </div>
  </div>
</template>

<style scoped>
.post-filters {
  @apply sticky top-20;
}
</style>
