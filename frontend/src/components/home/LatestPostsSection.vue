<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useContentStore } from '@/stores/content.api'
import { useI18n } from 'vue-i18n'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import { Icon } from '@iconify/vue'

const { t, locale } = useI18n()
const contentStore = useContentStore()

onMounted(() => {
  contentStore.loadAllContent()
})

const latestPosts = computed(() => {
  return contentStore
    .postsByLocale(locale.value as 'zh' | 'en')
    .slice(0, 5)
})

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return locale.value === 'zh'
    ? date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
    : date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<template>
  <section class="max-w-container mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between mb-8">
      <h2 class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary">
        {{ t('home.latestPosts') }}
      </h2>
      <RouterLink
        to="/blog"
        class="text-sm font-medium text-primary-from
               hover:text-primary-to transition-colors duration-150"
      >
        {{ t('home.viewAll') }} →
      </RouterLink>
    </div>

    <div class="space-y-4">
      <RouterLink
        v-for="(post, index) in latestPosts"
        :key="post.slug"
        :to="`/blog/${post.slug}`"
        class="group block"
      >
        <article
          class="flex flex-col sm:flex-row sm:items-center gap-4 p-4
                 rounded-xl border border-light-border dark:border-dark-border
                 hover:bg-light-bg dark:hover:bg-dark-bg
                 hover:border-primary-from/30
                 transition-all duration-300"
        >
          <!-- Index Badge -->
          <div
            class="hidden sm:flex w-10 h-10 shrink-0
                   items-center justify-center
                   rounded-lg
                   bg-gradient-to-br from-primary-from/10 to-primary-to/10
                   text-primary-from font-bold text-lg"
          >
            {{ String(index + 1).padStart(2, '0') }}
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0 space-y-1">
            <h3 class="text-lg font-semibold
                       text-light-text-primary dark:text-dark-text-primary
                       group-hover:text-primary-from transition-colors duration-150
                       line-clamp-1">
              {{ post.title }}
            </h3>
            <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary
                        line-clamp-1">
              {{ post.description }}
            </p>
            <div class="flex flex-wrap items-center gap-3 text-xs
                          text-light-text-muted dark:text-dark-text-muted">
              <span class="flex items-center gap-1">
                <Icon icon="lucide:calendar" class="w-3.5 h-3.5" />
                {{ formatDate(post.date) }}
              </span>
              <span v-if="post.readingTime" class="flex items-center gap-1">
                <Icon icon="lucide:clock" class="w-3.5 h-3.5" />
                {{ t('home.readingTime', { minutes: post.readingTime }) }}
              </span>
            </div>
          </div>

          <!-- Tags -->
          <div v-if="post.tags.length > 0" class="hidden sm:flex flex-wrap gap-2">
            <BaseBadge
              v-for="tag in post.tags.slice(0, 2)"
              :key="tag"
              variant="gray"
              size="sm"
            >
              #{{ tag }}
            </BaseBadge>
          </div>

          <!-- Arrow -->
          <Icon
            icon="lucide:chevron-right"
            class="w-5 h-5 shrink-0
                   text-light-text-muted dark:text-dark-text-muted
                   group-hover:text-primary-from
                   group-hover:translate-x-1
                   transition-all duration-300"
          />
        </article>
      </RouterLink>
    </div>
  </section>
</template>
