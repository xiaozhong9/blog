<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { PostSummary } from '@/types/content'
import BaseBadge from '@/components/ui/BaseBadge.vue'

defineProps<{
  post: PostSummary
}>()
</script>

<template>
  <RouterLink
    :to="`/life/${post.slug}`"
    class="group break-inside-avoid block"
  >
    <div
      class="card card-hover overflow-hidden
             p-5 space-y-3"
    >
      <!-- Cover Image -->
      <div
        v-if="post.image"
        class="w-full h-40 rounded-lg overflow-hidden mb-3"
      >
        <img
          :src="post.image"
          :alt="post.title"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
      <div
        v-else
        class="w-full h-40 rounded-lg overflow-hidden mb-3 bg-gradient-to-br from-primary-from/20 to-primary-to/20 flex items-center justify-center"
      >
        <span class="text-4xl">{{ post.title[0] }}</span>
      </div>

      <!-- Date -->
      <div class="text-xs font-medium text-primary-from">
        {{ new Date(post.date).toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }) }}
      </div>

      <!-- Title -->
      <h3 class="text-lg font-bold
                 text-light-text-primary dark:text-dark-text-primary
                 group-hover:text-primary-from transition-colors duration-150
                 line-clamp-2">
        {{ post.title }}
      </h3>

      <!-- Description -->
      <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary
                  line-clamp-3">
        {{ post.description }}
      </p>

      <!-- Tags -->
      <div v-if="post.tags.length > 0" class="flex flex-wrap gap-2">
        <BaseBadge
          v-for="tag in post.tags.slice(0, 3)"
          :key="tag"
          variant="gray"
          size="sm"
        >
          #{{ tag }}
        </BaseBadge>
      </div>
    </div>
  </RouterLink>
</template>
