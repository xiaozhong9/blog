<script setup lang="ts">
import { computed, onMounted, reactive, watch } from 'vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { useContentStore } from '@/stores/content.api'
import { useI18n } from 'vue-i18n'
import LifeCard from '@/components/life/LifeCard.vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import TiltCard from '@/components/effects/TiltCard.vue'
import LifeFilters from '@/components/filters/LifeFilters.vue'
import { Icon } from '@iconify/vue'
import type { ContentFilter } from '@/types/content'

const { t } = useI18n()
const contentStore = useContentStore()

onMounted(async () => {
  await contentStore.loadAllContent()
})

// 筛选器状态
interface FilterState {
  year?: number
  month?: number
  selectedTags?: string[]
}

const filterState = reactive<FilterState>({
  year: undefined,
  month: undefined,
  selectedTags: [],
})

// 获取所有可用标签
const availableTags = computed(() => {
  const allPosts = contentStore.postsByCategory('life')
  const tags = new Set<string>()
  allPosts.forEach(post => {
    post.tags.forEach(tag => tags.add(tag))
  })
  return Array.from(tags).sort()
})

// 获取所有可用年份
const availableYears = computed(() => {
  const allPosts = contentStore.postsByCategory('life')
  const years = new Set<number>()
  allPosts.forEach(post => {
    const year = new Date(post.date).getFullYear()
    years.add(year)
  })
  // 返回降序排列的年份
  return Array.from(years).sort((a, b) => b - a)
})

// 监听筛选器状态变化（仅用于调试）
// watch(() => filterState, (newState) => {
//   console.log('🎛️ 筛选器状态变化:', { year: newState.year, month: newState.month, tags: newState.selectedTags })
// }, { deep: true })

// 筛选后的文章
const filteredPosts = computed(() => {
  const filter: ContentFilter = {
    category: 'life',
    draft: false,
  }

  // 添加日期范围筛选
  if (filterState.year) {
    // 计算开始日期：指定年份的1月1日，或指定月份的1日
    const startMonth = filterState.month ? filterState.month - 1 : 0
    const startDate = new Date(filterState.year, startMonth, 1)

    // 计算结束日期：如果指定了月份，是该月最后一天；否则是该年最后一天
    let endDate: Date
    if (filterState.month) {
      // 获取该月最后一天（下个月第0天）
      endDate = new Date(filterState.year, filterState.month, 0)
    } else {
      // 全年最后一天（12月31日）
      endDate = new Date(filterState.year, 11, 31)
    }

    // 本地日期格式化函数
    const formatDate = (date: Date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    filter.dateFrom = formatDate(startDate)
    filter.dateTo = formatDate(endDate)
  }

  // 添加标签筛选
  if (filterState.selectedTags && filterState.selectedTags.length > 0) {
    filter.tags = filterState.selectedTags
  }

  return contentStore.filterPosts(filter)
})
</script>

<template>
  <DefaultLayout>
    <div class="max-w-container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header -->
      <ScrollReveal>
        <header class="text-center mb-12">
          <h1 class="text-4xl sm:text-5xl font-bold mb-4
                     text-light-text-primary dark:text-dark-text-primary">
            {{ t('life.title') }}
          </h1>
          <p class="text-lg text-light-text-secondary dark:text-dark-text-secondary">
            {{ t('life.subtitle') }}
          </p>
        </header>
      </ScrollReveal>

      <!-- 侧边栏布局 -->
      <div class="flex flex-col lg:flex-row gap-8">
        <!-- 左侧筛选器 -->
        <aside class="lg:w-72 flex-shrink-0">
          <LifeFilters
            v-model="filterState"
            :available-tags="availableTags"
            :available-years="availableYears"
          />
        </aside>

        <!-- 右侧内容列表 -->
        <main class="flex-1 min-w-0">
          <!-- 结果统计 -->
          <div class="mb-6 flex items-center justify-between">
            <p class="text-sm text-light-text-muted dark:text-dark-text-muted">
              找到 <span class="font-semibold text-light-text-primary dark:text-dark-text-primary">{{ filteredPosts.length }}</span> 篇记录
            </p>
          </div>

          <!-- Life Grid (Masonry-like) -->
          <div v-if="filteredPosts.length > 0" :key="`${filterState.year}-${filterState.month}-${filterState.selectedTags?.join('-')}`" class="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
            <ScrollReveal
              v-for="(post, index) in filteredPosts"
              :key="post.slug"
              :class="`delay-${Math.min(index * 100, 300)}`"
            >
              <TiltCard>
                <LifeCard :post="post" />
              </TiltCard>
            </ScrollReveal>
          </div>

          <!-- 空状态 -->
          <div v-else class="card p-12 text-center">
            <Icon icon="lucide:calendar-x" class="w-16 h-16 mx-auto mb-4 text-light-text-muted dark:text-dark-text-muted" />
            <h3 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-2">
              没有找到记录
            </h3>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              试试调整筛选条件
            </p>
          </div>
        </main>
      </div>
    </div>
  </DefaultLayout>
</template>
