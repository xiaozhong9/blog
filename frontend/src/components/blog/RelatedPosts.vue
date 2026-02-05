<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { useContentStore } from '@/stores/content.api'
import type { PostSummary } from '@/types/content'

const props = defineProps<{
  currentSlug: string
  tags: string[]
  category?: string
  maxCount?: number
}>()

const router = useRouter()
const contentStore = useContentStore()

// 计算相关文章
const relatedPosts = computed(() => {
  const allPosts = contentStore.posts || []
  const max = props.maxCount || 4

  // 获取同分类的所有文章（排除当前文章）
  const categoryPosts = allPosts.filter(
    p => p.slug !== props.currentSlug &&
           (!props.category || p.category === props.category)
  )

  // 计算每篇文章的相关性分数
  const scored = categoryPosts.map(post => {
    const commonTags = post.tags.filter(tag => props.tags.includes(tag))
    return {
      post,
      score: commonTags.length,
    }
  })

  // 按相关性分数排序，取前 N 个
  return scored
    .filter(item => item.score > 0) // 至少有一个共同标签
    .sort((a, b) => b.score - a.score)
    .slice(0, max)
    .map(item => item.post)
})

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// 导航到文章
const goToPost = (slug: string) => {
  router.push(`/blog/${slug}`)
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div v-if="relatedPosts.length > 0" class="card p-6 mt-12">
    <div class="flex items-center gap-2 mb-6">
      <Icon icon="lucide:book-open" class="w-5 h-5 text-primary-from" />
      <h3 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary">
        相关文章推荐
      </h3>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <article
        v-for="post in relatedPosts"
        :key="post.slug"
        @click="goToPost(post.slug)"
        class="p-4 rounded-lg border border-light-border dark:border-dark-border
               hover:border-primary-from dark:hover:border-primary-from
               hover:shadow-md transition-all cursor-pointer group"
      >
        <h4 class="font-medium text-light-text-primary dark:text-dark-text-primary
                   group-hover:text-primary-from transition-colors mb-2 line-clamp-2">
          {{ post.title }}
        </h4>

        <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary
                  line-clamp-2 mb-3">
          {{ post.description }}
        </p>

        <div class="flex items-center justify-between text-xs text-light-text-muted dark:text-dark-text-muted">
          <span class="flex items-center gap-1">
            <Icon icon="lucide:calendar" class="w-3 h-3" />
            {{ formatDate(post.date) }}
          </span>

          <div class="flex items-center gap-1">
            <Icon icon="lucide:tag" class="w-3 h-3" />
            <span>{{ post.tags.slice(0, 2).join(', ') }}</span>
            <span v-if="post.tags.length > 2">+{{ post.tags.length - 2 }}</span>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>
