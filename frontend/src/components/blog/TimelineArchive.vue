<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { PostSummary } from '@/types/content'
import { Icon } from '@iconify/vue'

const props = defineProps<{
  posts: PostSummary[]
}>()

// 按年份和月份分组
const groupedPosts = computed(() => {
  const groups = new Map<string, Map<string, PostSummary[]>>()

  props.posts.forEach(post => {
    const date = new Date(post.date)
    const year = date.getFullYear().toString()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')

    if (!groups.has(year)) {
      groups.set(year, new Map())
    }

    const yearMap = groups.get(year)!
    if (!yearMap.has(month)) {
      yearMap.set(month, [])
    }

    yearMap.get(month)!.push(post)
  })

  // 转换为数组并排序
  const result = Array.from(groups.entries())
    .map(([year, months]) => ({
      year,
      months: Array.from(months.entries())
        .map(([month, posts]) => ({
          month,
          posts: posts.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        }))
        .sort((a, b) => b.month.localeCompare(a.month))
    }))
    .sort((a, b) => b.year.localeCompare(a.year))

  return result
})

// 格式化月份名称
const formatMonth = (month: string) => {
  return `${month}月`
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
}
</script>

<template>
  <div class="timeline-archive">
    <!-- 头部 -->
    <div class="flex items-center gap-2 mb-6">
      <Icon icon="lucide:calendar" class="w-5 h-5 text-primary-from" />
      <h3 class="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary">
        时间轴
      </h3>
    </div>

    <!-- 时间轴内容 -->
    <div class="space-y-6">
      <!-- 年份 -->
      <div v-for="yearGroup in groupedPosts" :key="yearGroup.year" class="space-y-4">
        <!-- 年份标题 -->
        <div class="flex items-center gap-3">
          <div class="text-2xl font-bold text-primary-from">
            {{ yearGroup.year }}
          </div>
          <div class="flex-1 h-px bg-light-border dark:border-dark-border border-t"></div>
        </div>

        <!-- 月份列表 -->
        <div class="ml-4 space-y-3">
          <div
            v-for="monthGroup in yearGroup.months"
            :key="`${yearGroup.year}-${monthGroup.month}`"
            class="space-y-2"
          >
            <!-- 月份标题 -->
            <div class="flex items-center gap-2 text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary">
              <Icon icon="lucide:calendar-days" class="w-4 h-4" />
              {{ formatMonth(monthGroup.month) }}
            </div>

            <!-- 文章列表 -->
            <div class="ml-6 space-y-1">
              <RouterLink
                v-for="post in monthGroup.posts"
                :key="post.slug"
                :to="`/blog/${post.slug}`"
                class="block group"
              >
                <div
                  class="flex items-start gap-3 p-2 rounded-lg
                         hover:bg-gray-50 dark:hover:bg-gray-800
                         transition-colors"
                >
                  <div class="w-2 h-2 rounded-full bg-primary-from mt-2 flex-shrink-0"></div>
                  <div class="flex-1 min-w-0">
                    <div class="text-sm font-medium text-light-text-primary dark:text-dark-text-primary
                                 group-hover:text-primary-from transition-colors
                                 truncate">
                      {{ post.title }}
                    </div>
                    <div class="text-xs text-light-text-muted dark:text-dark-text-muted mt-0.5">
                      {{ formatDate(post.date) }}
                    </div>
                  </div>
                  <Icon
                    icon="lucide:chevron-right"
                    class="w-4 h-4 text-light-text-muted dark:text-dark-text-muted
                          group-hover:text-primary-from transition-colors flex-shrink-0"
                  />
                </div>
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="groupedPosts.length === 0" class="text-center py-8">
      <Icon icon="lucide:calendar-x" class="w-12 h-12 mx-auto mb-3 text-light-text-muted dark:text-dark-text-muted" />
      <p class="text-sm text-light-text-muted dark:text-dark-text-muted">
        暂无文章
      </p>
    </div>
  </div>
</template>

<style scoped>
.timeline-archive {
  @apply sticky top-20;
}
</style>
