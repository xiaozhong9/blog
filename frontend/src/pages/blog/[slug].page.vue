<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ReadingLayout from '@/layouts/ReadingLayout.vue'
import { useContentStore } from '@/stores/content.api'
import TableOfContents from '@/components/content/TableOfContents.vue'
import MarkdownRenderer from '@/components/content/MarkdownRenderer.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import ReadingProgress from '@/components/blog/ReadingProgress.vue'
import RelatedPosts from '@/components/blog/RelatedPosts.vue'
import CommentForm from '@/components/comments/CommentForm.vue'
import CommentList from '@/components/comments/CommentList.vue'
import { Icon } from '@iconify/vue'
import { articleService } from '@/api/services'
import { formatDate } from '@/utils/dateFormatter'

const route = useRoute()
const { t, locale } = useI18n()
const contentStore = useContentStore()

const slug = computed(() => route.params.slug as string)
const post = ref<Awaited<ReturnType<typeof contentStore.getPostBySlug>> | null>(null)
const articleId = ref<number | null>(null)
const isLoading = ref(true)
const loadError = ref<string | null>(null)

// Get views from post frontmatter
const postViews = computed(() => {
  return post.value?.frontmatter?.views || 0
})

// Extract headings from content
const headings = computed(() => {
  if (!post.value) return []

  // This is a simplified version - in production, extract from actual markdown
  return [
    { id: 'introduction', text: 'Introduction', level: 2 },
    { id: 'features', text: 'Features', level: 2 },
    { id: 'conclusion', text: 'Conclusion', level: 2 },
  ]
})

onMounted(async () => {
  try {
    post.value = await contentStore.getPostBySlug(slug.value)

    if (!post.value) {
      loadError.value = '文章不存在或已删除'
      return
    }

    // 获取文章 ID（用于评论）
    try {
      const articleData = await articleService.getDetail(slug.value)
      articleId.value = (articleData as any).id
    } catch (e) {
      // 忽略错误
    }

    // 增加浏览数
    contentStore.incrementViews(post.value.slug)
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '加载失败'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <ReadingLayout v-if="post" :headings="headings">
    <div class="max-w-reading">
      <!-- Header -->
      <header class="mb-12">
        <RouterLink
          to="/blog"
          class="inline-flex items-center gap-2 text-sm text-primary-from
                 hover:text-primary-to transition-colors duration-150 mb-6"
        >
          <Icon icon="lucide:arrow-left" class="w-4 h-4" />
          {{ t('post.backToList') }}
        </RouterLink>

        <h1 class="text-4xl sm:text-5xl font-bold mb-4
                   text-light-text-primary dark:text-dark-text-primary">
          {{ post.frontmatter.title }}
        </h1>

        <p class="text-xl text-light-text-secondary dark:text-dark-text-secondary mb-6">
          {{ post.frontmatter.description }}
        </p>

        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex flex-wrap items-center gap-4 text-sm text-light-text-muted dark:text-dark-text-muted">
            <span class="flex items-center gap-1.5">
              <Icon icon="lucide:calendar" class="w-4 h-4" />
              {{ formatDate(post.frontmatter.date) }}
            </span>
            <span v-if="post.frontmatter.readingTime" class="flex items-center gap-1.5">
              <Icon icon="lucide:clock" class="w-4 h-4" />
              {{ t('home.readingTime', { minutes: post.frontmatter.readingTime }) }}
            </span>
            <span class="flex items-center gap-1.5">
              <Icon icon="lucide:eye" class="w-4 h-4" />
              {{ postViews }} 次浏览
            </span>
          </div>
        </div>

        <div v-if="post.frontmatter.tags.length > 0" class="flex flex-wrap gap-2 mt-4">
          <BaseBadge
            v-for="tag in post.frontmatter.tags"
            :key="tag"
            variant="primary"
            size="sm"
          >
            #{{ tag }}
          </BaseBadge>
        </div>
      </header>

      <!-- Cover Image -->
      <div v-if="post.frontmatter.image" class="mb-12 rounded-2xl overflow-hidden">
        <img
          :src="post.frontmatter.image"
          :alt="post.frontmatter.title"
          class="w-full h-auto"
        />
      </div>

      <!-- Reading Progress Bar -->
      <ReadingProgress />

      <!-- Content -->
      <MarkdownRenderer :content="post.content" />

      <!-- 相关文章推荐 -->
      <RelatedPosts
        :current-slug="post.slug"
        :tags="post.frontmatter.tags"
        category="blog"
        :max-count="4"
      />

      <!-- 评论表单 -->
      <section v-if="articleId" class="mt-12">
        <CommentForm :article-id="articleId" @submitted="() => {}" />
      </section>

      <!-- 评论列表 -->
      <section v-if="articleId" class="mt-12">
        <CommentList :article-id="articleId" />
      </section>

      <!-- Footer -->
      <footer class="mt-16 pt-8 border-t border-light-border dark:border-dark-border">
        <div class="flex items-center justify-between">
          <RouterLink
            to="/blog"
            class="inline-flex items-center gap-2 text-sm text-primary-from
                   hover:text-primary-to transition-colors duration-150"
          >
            <Icon icon="lucide:arrow-left" class="w-4 h-4" />
            {{ t('post.backToList') }}
          </RouterLink>
        </div>
      </footer>
    </div>
  </ReadingLayout>

  <!-- Loading State -->
  <div v-else-if="isLoading" class="flex items-center justify-center min-h-[50vh]">
    <div class="text-center">
      <Icon icon="lucide:loader-2" class="w-12 h-12 animate-spin mx-auto mb-4 text-primary-from" />
      <p class="text-light-text-secondary dark:text-dark-text-secondary">
        加载中...
      </p>
    </div>
  </div>

  <!-- Error State -->
  <div v-else-if="loadError" class="flex items-center justify-center min-h-[50vh]">
    <div class="text-center max-w-md">
      <Icon icon="lucide:alert-circle" class="w-12 h-12 mx-auto mb-4 text-red-500" />
      <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-2">
        加载失败
      </h2>
      <p class="text-light-text-secondary dark:text-dark-text-secondary mb-6">
        {{ loadError }}
      </p>
      <RouterLink
        to="/blog"
        class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90 transition-opacity"
      >
        <Icon icon="lucide:arrow-left" class="w-4 h-4" />
        返回文章列表
      </RouterLink>
    </div>
  </div>
</template>
