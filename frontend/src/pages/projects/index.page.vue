<script setup lang="ts">
import { computed, onMounted } from 'vue'
import ProjectLayout from '@/layouts/ProjectLayout.vue'
import { useContentStore } from '@/stores/content.api'
import { useI18n } from 'vue-i18n'
import ProjectCard from '@/components/projects/ProjectCard.vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import TiltCard from '@/components/effects/TiltCard.vue'

const { t } = useI18n()
const contentStore = useContentStore()

onMounted(() => {
  contentStore.loadAllContent()
})

// 使用 computed 确保响应式更新
const projects = computed(() => contentStore.postsByCategory('projects'))

// 获取项目统计数据
const stats = computed(() => contentStore.projectStats)
</script>

<template>
  <ProjectLayout>
    <div class="max-w-container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header -->
      <ScrollReveal>
        <header class="text-center mb-16">
          <h1 class="text-4xl sm:text-5xl font-bold mb-4
                     text-light-text-primary dark:text-dark-text-primary">
            {{ t('project.title') }}
          </h1>
          <p class="text-lg text-light-text-secondary dark:text-dark-text-secondary max-w-2xl mx-auto">
            {{ t('project.description') }}
          </p>
        </header>
      </ScrollReveal>

      <!-- Stats -->
      <ScrollReveal class="delay-100">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div class="card text-center p-6">
            <div class="text-3xl font-bold text-primary-from mb-2">{{ stats.total }}</div>
            <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">项目总数</div>
          </div>
          <div class="card text-center p-6">
            <div class="text-3xl font-bold text-primary-to mb-2">{{ stats.totalStars }}</div>
            <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">GitHub Stars</div>
          </div>
          <div class="card text-center p-6">
            <div class="text-3xl font-bold text-green-500 mb-2">{{ stats.totalForks }}</div>
            <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">GitHub Forks</div>
          </div>
        </div>
      </ScrollReveal>

      <!-- Projects Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ScrollReveal
          v-for="(project, index) in projects"
          :key="project.slug"
          :class="`delay-${Math.min(index * 100, 300)}`"
        >
          <TiltCard>
            <ProjectCard :project="project" />
          </TiltCard>
        </ScrollReveal>
      </div>
    </div>
  </ProjectLayout>
</template>
