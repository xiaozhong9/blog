<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { PostSummary } from '@/types/content'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import { Icon } from '@iconify/vue'

defineProps<{
  project: PostSummary
}>()

const { t } = useI18n()
</script>

<template>
  <RouterLink
    :to="`/projects/${project.slug}`"
    class="group block"
  >
    <div
      class="card card-hover h-full
             p-6 space-y-4"
    >
      <!-- Icon/Header -->
      <div class="w-12 h-12 rounded-xl
                  bg-gradient-to-br from-primary-from to-primary-to
                  flex items-center justify-center
                  text-white shadow-glow">
        <Icon icon="lucide:folder" class="w-6 h-6" />
      </div>

      <!-- Title -->
      <h3 class="text-xl font-bold
                 text-light-text-primary dark:text-dark-text-primary
                 group-hover:text-primary-from transition-colors duration-150">
        {{ project.title }}
      </h3>

      <!-- Description -->
      <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary
                  line-clamp-3">
        {{ project.description }}
      </p>

      <!-- Tech Stack -->
      <div v-if="(project as any).techStack?.length" class="flex flex-wrap gap-2">
        <BaseBadge
          v-for="tech in (project as any).techStack.slice(0, 4)"
          :key="tech"
          variant="default"
          size="sm"
        >
          {{ tech }}
        </BaseBadge>
      </div>
      <div v-else-if="project.tags.length > 0" class="flex flex-wrap gap-2">
        <BaseBadge
          v-for="tag in project.tags.slice(0, 4)"
          :key="tag"
          variant="default"
          size="sm"
        >
          {{ tag }}
        </BaseBadge>
      </div>

      <!-- Meta -->
      <div class="flex items-center gap-4 text-sm
                    text-light-text-muted dark:text-dark-text-muted pt-2
                    border-t border-light-border dark:border-dark-border">
        <span v-if="'stars' in project" class="flex items-center gap-1">
          <Icon icon="lucide:star" class="w-4 h-4" />
          {{ (project as any).stars || '0' }}
        </span>
        <span v-if="'forks' in project" class="flex items-center gap-1">
          <Icon icon="lucide:git-fork" class="w-4 h-4" />
          {{ (project as any).forks || '0' }}
        </span>
        <span v-if="'status' in project" class="flex items-center gap-1 ml-auto">
          <span
            class="px-2 py-0.5 rounded text-xs font-medium"
            :class="(project as any).status === 'active'
              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
              : 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'"
          >
            {{ (project as any).status === 'active' ? '活跃' : '维护中' }}
          </span>
        </span>
      </div>
    </div>
  </RouterLink>
</template>
