<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useContentStore } from '@/stores/content.api'
import { useI18n } from 'vue-i18n'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import TiltCard from '@/components/effects/TiltCard.vue'
import { Icon } from '@iconify/vue'

const { t } = useI18n()
const contentStore = useContentStore()

onMounted(() => {
  contentStore.loadAllContent()
})

const featuredPosts = computed(() => contentStore.featuredPosts.slice(0, 3))
</script>

<template>
  <section class="max-w-container mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between mb-8">
      <h2 class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary">
        {{ t('home.featured') }}
      </h2>
      <RouterLink
        to="/blog"
        class="text-sm font-medium text-primary-from
               hover:text-primary-to transition-colors duration-150"
      >
        {{ t('home.viewAll') }} →
      </RouterLink>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <RouterLink
        v-for="(post, index) in featuredPosts"
        :key="post.slug"
        :to="`/blog/${post.slug}`"
        class="group"
      >
        <ScrollReveal :class="`delay-${index * 100}`">
          <TiltCard>
            <BaseCard
              variant="gradient"
              padding="lg"
              hoverable
              class="h-full"
            >
          <article class="space-y-4">
            <!-- Icon based on index -->
            <div class="w-12 h-12 rounded-xl
                        bg-gradient-to-br from-primary-from to-primary-to
                        flex items-center justify-center
                        text-white shadow-glow">
              <Icon
                :icon="index === 0 ? 'lucide:star' : index === 1 ? 'lucide:zap' : 'lucide:flame'"
                class="w-6 h-6"
              />
            </div>

            <!-- Title -->
            <h3 class="text-xl font-bold
                       text-light-text-primary dark:text-dark-text-primary
                       group-hover:text-primary-from transition-colors duration-150">
              {{ post.title }}
            </h3>

            <!-- Description -->
            <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary
                        line-clamp-2">
              {{ post.description }}
            </p>

            <!-- Meta -->
            <div class="flex items-center gap-3 text-xs
                          text-light-text-muted dark:text-dark-text-muted">
              <span class="flex items-center gap-1">
                <Icon icon="lucide:calendar" class="w-3.5 h-3.5" />
                {{ new Date(post.date).toLocaleDateString() }}
              </span>
              <span v-if="post.readingTime" class="flex items-center gap-1">
                <Icon icon="lucide:clock" class="w-3.5 h-3.5" />
                {{ post.readingTime }}m
              </span>
            </div>

            <!-- Tags -->
            <div v-if="post.tags.length > 0" class="flex flex-wrap gap-2">
              <BaseBadge
                v-for="tag in post.tags.slice(0, 2)"
                :key="tag"
                variant="primary"
                size="sm"
              >
                #{{ tag }}
              </BaseBadge>
            </div>
          </article>
        </BaseCard>
          </TiltCard>
        </ScrollReveal>
      </RouterLink>
    </div>
  </section>
</template>
