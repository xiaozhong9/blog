<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'

interface FilterOptions {
  year?: number
  month?: number
  selectedTags?: string[]
}

const props = defineProps<{
  availableTags: string[]
  availableYears: number[]
  modelValue: FilterOptions
}>()

const emit = defineEmits<{
  'update:modelValue': [value: FilterOptions]
}>()

// 本地状态
const localYear = ref(props.modelValue.year)
const localMonth = ref(props.modelValue.month)
const localSelectedTags = ref<string[]>(props.modelValue.selectedTags || [])

// 最新的一年（用于默认选中）
const latestYear = computed(() => {
  return props.availableYears.length > 0
    ? Math.max(...props.availableYears)
    : new Date().getFullYear()
})

// 展开/折叠状态
const isExpanded = ref(true)

// 月份选项
const monthOptions = [
  { value: 0, label: '全部' },
  { value: 1, label: '一月' },
  { value: 2, label: '二月' },
  { value: 3, label: '三月' },
  { value: 4, label: '四月' },
  { value: 5, label: '五月' },
  { value: 6, label: '六月' },
  { value: 7, label: '七月' },
  { value: 8, label: '八月' },
  { value: 9, label: '九月' },
  { value: 10, label: '十月' },
  { value: 11, label: '十一月' },
  { value: 12, label: '十二月' },
]

// 监听 props 变化，同步到本地状态
watch(() => props.modelValue, (newValue) => {
  localYear.value = newValue.year
  localMonth.value = newValue.month
  localSelectedTags.value = newValue.selectedTags || []
}, { deep: true })

// 监听本地状态变化并同步到父组件
watch([localYear, localMonth, localSelectedTags], () => {
  const newValue = {
    year: localYear.value,
    month: localMonth.value,
    selectedTags: localSelectedTags.value,
  }
  emit('update:modelValue', newValue)
}, { deep: true })

// 切换标签选择
const toggleTag = (tag: string) => {
  const index = localSelectedTags.value.indexOf(tag)
  if (index > -1) {
    localSelectedTags.value.splice(index, 1)
  } else {
    localSelectedTags.value.push(tag)
  }
}

// 处理月份点击
const handleMonthClick = (monthValue: number) => {
  if (monthValue === 0) {
    // 点击"全部"，清空月份
    localMonth.value = undefined
  } else {
    // 点击具体月份
    // 如果当前年份未选中，自动选中最新的一年
    if (localYear.value === undefined) {
      localYear.value = latestYear.value
    }
    localMonth.value = monthValue
  }
}

// 清空所有筛选
const clearFilters = () => {
  localYear.value = undefined
  localMonth.value = undefined
  localSelectedTags.value = []
}

// 计算活动筛选数量
const activeFilterCount = computed(() => {
  let count = 0
  if (localYear.value) count++
  if (localMonth.value) count++
  if (localSelectedTags.value.length > 0) count++
  return count
})
</script>

<template>
  <div class="life-filters">
    <!-- 头部 -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary flex items-center gap-2">
        <Icon icon="lucide:calendar" class="w-5 h-5" />
        日期筛选
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
      <!-- 年份筛选 -->
      <div v-if="availableYears.length > 0">
        <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
          年份
        </label>
        <div class="flex flex-wrap gap-2">
          <button
            @click="localYear = undefined"
            class="px-3 py-1.5 text-sm rounded-lg transition-colors"
            :class="localYear === undefined
              ? 'bg-primary-from text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary'"
          >
            全部
          </button>
          <button
            v-for="year in availableYears.sort((a, b) => b - a)"
            :key="year"
            @click="localYear = year"
            class="px-3 py-1.5 text-sm rounded-lg transition-colors"
            :class="localYear === year
              ? 'bg-primary-from text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary'"
          >
            {{ year }}
          </button>
        </div>
      </div>

      <!-- 月份筛选 -->
      <div>
        <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
          月份
        </label>
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="month in monthOptions"
            :key="month.value"
            @click="handleMonthClick(month.value)"
            class="px-3 py-2 text-xs rounded-lg transition-colors"
            :class="localMonth === month.value || (localMonth === undefined && month.value === 0)
              ? 'bg-primary-from text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary'"
          >
            {{ month.label }}
          </button>
        </div>
      </div>

      <!-- 标签筛选 -->
      <div v-if="availableTags.length > 0">
        <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
          标签
        </label>
        <div class="flex flex-wrap gap-2">
          <BaseBadge
            v-for="tag in availableTags"
            :key="tag"
            @click="toggleTag(tag)"
            :variant="localSelectedTags.includes(tag) ? 'primary' : 'gray'"
            size="sm"
            class="cursor-pointer hover:opacity-80 transition-opacity"
          >
            #{{ tag }}
          </BaseBadge>
        </div>
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
.life-filters {
  @apply sticky top-20;
}
</style>
