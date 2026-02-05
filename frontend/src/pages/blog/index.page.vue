<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import BlogLayout from '@/layouts/BlogLayout.vue'
import { useContentStore } from '@/stores/content.api'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import PostFilters from '@/components/filters/PostFilters.vue'
import TimelineArchive from '@/components/blog/TimelineArchive.vue'
import SearchBar from '@/components/blog/SearchBar.vue'
import HighlightText from '@/components/blog/HighlightText.vue'
import { Icon } from '@iconify/vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import type { ContentFilter } from '@/types/content'

const { t, locale } = useI18n()
const contentStore = useContentStore()

onMounted(() => {
  contentStore.loadAllContent()
})

// 搜索关键词
const searchQuery = ref('')

// 筛选器状态
interface FilterState {
  sortBy?: 'date' | 'popularity' | 'readingTime'
  sortOrder?: 'asc' | 'desc'
  featuredOnly?: boolean
}

const filterState = reactive<FilterState>({
  sortBy: 'date',
  sortOrder: 'desc',
  featuredOnly: false,
})

// 筛选后的文章
const filteredPosts = computed(() => {
  const filter: ContentFilter = {
    category: 'blog',
    locale: locale.value as 'zh' | 'en',
    draft: false,
  }

  // 添加搜索
  if (searchQuery.value.trim()) {
    filter.search = searchQuery.value
  }

  // 添加排序
  if (filterState.sortBy) {
    filter.sortBy = filterState.sortBy
  }
  if (filterState.sortOrder) {
    filter.sortOrder = filterState.sortOrder
  }

  // 添加精选筛选
  if (filterState.featuredOnly) {
    filter.featured = true
  }

  return contentStore.filterPosts(filter)
})

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return locale.value === 'zh'
    ? date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
    : date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <BlogLayout>
    <div class="max-w-container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header -->
      <header class="mb-12">
        <h1 class="text-4xl sm:text-5xl font-bold mb-4
                   text-light-text-primary dark:text-dark-text-primary">
          {{ t('nav.blog') }}
        </h1>
        <p class="text-lg text-light-text-secondary dark:text-dark-text-secondary">
          {{ t('home.hero.description') }}
        </p>
      </header>

      <!-- 三栏布局：左侧筛选器 + 中间文章列表 + 右侧时间轴 -->
      <div class="flex flex-col xl:flex-row gap-8">
        <!-- 左侧筛选器 -->
        <aside class="xl:w-64 flex-shrink-0">
          <PostFilters v-model="filterState" />
        </aside>

        <!-- 中间文章列表 -->
        <main class="flex-1 min-w-0">
          <!-- 搜索框 -->
          <div class="mb-6">
            <SearchBar
              v-model="searchQuery"
              placeholder="搜索文章标题、描述或标签..."
            />
          </div>

          <!-- 结果统计 -->
          <div class="mb-6 flex items-center justify-between">
            <p class="text-sm text-light-text-muted dark:text-dark-text-muted">
              找到 <span class="font-semibold text-light-text-primary dark:text-dark-text-primary">{{ filteredPosts.length }}</span> 篇文章
              <span v-if="searchQuery" class="ml-2">
                匹配 "<HighlightText :text="searchQuery" :query="searchQuery" />"
              </span>
            </p>
          </div>

          <!-- Blog Posts Grid -->
          <div v-if="filteredPosts.length > 0" class="grid gap-6">
            <ScrollReveal
              v-for="(post, index) in filteredPosts"
              :key="post.slug"
              :class="`delay-${Math.min(index * 100, 300)}`"
            >
              <RouterLink
                :to="`/blog/${post.slug}`"
                class="block"
              >
                <BaseCard
                  variant="bordered"
                  padding="md"
                  hoverable
                >
                  <article class="space-y-4">
                    <!-- 精选标签 -->
                    <div v-if="post.featured" class="flex items-center gap-2">
                      <Icon icon="lucide:star" class="w-4 h-4 text-yellow-500" />
                      <span class="text-xs font-medium text-yellow-600 dark:text-yellow-400">精选</span>
                    </div>

                    <!-- Title & Meta -->
                    <div class="space-y-2">
                      <h2 class="text-2xl font-bold text-light-text-primary dark:text-dark-text-primary
                                 group-hover:text-primary-from transition-colors duration-150">
                        <HighlightText :text="post.title" :query="searchQuery" />
                      </h2>
                      <div class="flex flex-wrap items-center gap-3 text-sm
                                    text-light-text-muted dark:text-dark-text-muted">
                        <span class="flex items-center gap-1">
                          <Icon icon="lucide:calendar" class="w-4 h-4" />
                          {{ formatDate(post.date) }}
                        </span>
                        <span v-if="post.readingTime" class="flex items-center gap-1">
                          <Icon icon="lucide:clock" class="w-4 h-4" />
                          {{ t('home.readingTime', { minutes: post.readingTime }) }}
                        </span>
                      </div>
                    </div>

                    <!-- Description -->
                    <p class="text-light-text-secondary dark:text-dark-text-secondary line-clamp-2">
                      <HighlightText :text="post.description" :query="searchQuery" />
                    </p>

                    <!-- Tags -->
                    <div v-if="post.tags.length > 0" class="flex flex-wrap gap-2">
                      <BaseBadge
                        v-for="tag in post.tags"
                        :key="tag"
                        variant="primary"
                        size="sm"
                      >
                        #{{ tag }}
                      </BaseBadge>
                    </div>
                  </article>
                </BaseCard>
              </RouterLink>
            </ScrollReveal>
          </div>

          <!-- 空状态 -->
          <div v-else class="card p-12 text-center">
            <Icon icon="lucide:file-question" class="w-16 h-16 mx-auto mb-4 text-light-text-muted dark:text-dark-text-muted" />
            <h3 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-2">
              没有找到文章
            </h3>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              试试调整筛选条件
            </p>
          </div>
        </main>

        <!-- 右侧时间轴 -->
        <aside class="xl:w-72 flex-shrink-0">
          <TimelineArchive :posts="filteredPosts" />
        </aside>
      </div>
    </div>
  </BlogLayout>
</template>
