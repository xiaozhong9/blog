<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { useContentStore } from '@/stores/content.api'
import MarkdownRenderer from '@/components/content/MarkdownRenderer.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import CommentForm from '@/components/comments/CommentForm.vue'
import CommentList from '@/components/comments/CommentList.vue'
import { Icon } from '@iconify/vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import { articleService } from '@/api/services'

const route = useRoute()
const { t, locale } = useI18n()
const contentStore = useContentStore()

const slug = computed(() => route.params.slug as string)
const post = ref<Awaited<ReturnType<typeof contentStore.getPostBySlug>> | null>(null)
const articleId = ref<number | null>(null)

onMounted(async () => {
  post.value = await contentStore.getPostBySlug(slug.value)

  // 获取文章 ID（用于评论）
  try {
    const articleData = await articleService.getDetail(slug.value)
    articleId.value = (articleData as any).id
  } catch (e) {
    console.warn('Failed to get article ID:', e)
  }
})

// Format date
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return locale.value === 'zh'
    ? date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
    : date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <DefaultLayout v-if="post">
    <div class="max-w-container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header -->
      <ScrollReveal>
        <RouterLink
          to="/projects"
          class="inline-flex items-center gap-2 text-sm text-primary-from
                 hover:text-primary-to transition-colors duration-150 mb-6"
        >
          <Icon icon="lucide:arrow-left" class="w-4 h-4" />
          返回项目列表
        </RouterLink>
      </ScrollReveal>

      <!-- Project Header -->
      <ScrollReveal class="delay-100">
        <div class="card p-8 mb-8">
          <div class="flex flex-col lg:flex-row gap-8">
            <!-- Left: Icon -->
            <div class="flex-shrink-0">
              <div class="w-24 h-24 rounded-2xl
                          bg-gradient-to-br from-primary-from to-primary-to
                          flex items-center justify-center
                          text-white shadow-glow">
                <Icon icon="lucide:folder" class="w-12 h-12" />
              </div>
            </div>

            <!-- Right: Content -->
            <div class="flex-1 space-y-4">
              <h1 class="text-3xl sm:text-4xl font-bold
                         text-light-text-primary dark:text-dark-text-primary">
                {{ post.frontmatter.title }}
              </h1>

              <p class="text-lg text-light-text-secondary dark:text-dark-text-secondary">
                {{ post.frontmatter.description }}
              </p>

              <!-- Tech Stack -->
              <div v-if="'techStack' in post.frontmatter" class="flex flex-wrap gap-2">
                <BaseBadge
                  v-for="tech in (post.frontmatter as any).techStack"
                  :key="tech"
                  variant="default"
                >
                  {{ tech }}
                </BaseBadge>
              </div>

              <!-- Meta -->
              <div class="flex flex-wrap items-center gap-6 text-sm
                            text-light-text-muted dark:text-dark-text-muted pt-4
                            border-t border-light-border dark:border-dark-border">
                <span v-if="'stars' in post.frontmatter" class="flex items-center gap-2">
                  <Icon icon="lucide:star" class="w-5 h-5 text-yellow-500" />
                  <span class="font-semibold">{{ (post.frontmatter as any).stars }}</span>
                  Stars
                </span>
                <span v-if="'forks' in post.frontmatter" class="flex items-center gap-2">
                  <Icon icon="lucide:git-fork" class="w-5 h-5 text-green-500" />
                  <span class="font-semibold">{{ (post.frontmatter as any).forks }}</span>
                  Forks
                </span>
                <span v-if="'status' in post.frontmatter" class="flex items-center gap-2">
                  <span
                    class="px-3 py-1 rounded-full text-xs font-semibold"
                    :class="(post.frontmatter as any).status === 'active'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'"
                  >
                    {{ (post.frontmatter as any).status === 'active' ? '活跃开发中' : '维护模式' }}
                  </span>
                </span>
                <span class="flex items-center gap-2 ml-auto">
                  <Icon icon="lucide:calendar" class="w-4 h-4" />
                  {{ formatDate(post.frontmatter.date) }}
                </span>
              </div>

              <!-- Links -->
              <div v-if="'repo' in post.frontmatter || 'demo' in post.frontmatter"
                   class="flex flex-wrap gap-4 pt-4">
                <a
                  v-if="'repo' in post.frontmatter && (post.frontmatter as any).repo"
                  :href="(post.frontmatter as any).repo"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-2 px-4 py-2 rounded-lg
                         bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900
                         hover:opacity-90 transition-opacity"
                >
                  <Icon icon="lucide:github" class="w-5 h-5" />
                  GitHub 仓库
                  <Icon icon="lucide:external-link" class="w-4 h-4" />
                </a>
                <a
                  v-if="'demo' in post.frontmatter && (post.frontmatter as any).demo"
                  :href="(post.frontmatter as any).demo"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-2 px-4 py-2 rounded-lg
                         bg-gradient-to-r from-primary-from to-primary-to
                         text-white hover:opacity-90 transition-opacity"
                >
                  <Icon icon="lucide:rocket" class="w-5 h-5" />
                  在线演示
                  <Icon icon="lucide:external-link" class="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </ScrollReveal>

      <!-- Project Content -->
      <ScrollReveal class="delay-200">
        <div class="card p-8">
          <MarkdownRenderer :content="post.content" />
        </div>
      </ScrollReveal>

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
        <RouterLink
          to="/projects"
          class="inline-flex items-center gap-2 text-sm text-primary-from
                 hover:text-primary-to transition-colors duration-150"
        >
          <Icon icon="lucide:arrow-left" class="w-4 h-4" />
          返回项目列表
        </RouterLink>
      </footer>
    </div>
  </DefaultLayout>

  <!-- Loading State -->
  <DefaultLayout v-else>
    <div class="flex items-center justify-center min-h-[50vh]">
      <div class="text-center">
        <Icon icon="lucide:loader-2" class="w-8 h-8 animate-spin mx-auto mb-4 text-primary-from" />
        <p class="text-light-text-secondary dark:text-dark-text-secondary">
          {{ t('common.loading') }}
        </p>
      </div>
    </div>
  </DefaultLayout>
</template>
