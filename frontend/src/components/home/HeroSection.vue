<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'

const { t } = useI18n()

const techTags = ref<string[]>([])
const allTechTags = ['Vue.js', 'TypeScript', 'Vite', 'Tailwind CSS', 'Pinia', 'Vue Router']

// Animate tech tags on mount
onMounted(() => {
  let index = 0
  const interval = setInterval(() => {
    if (index < allTechTags.length) {
      techTags.value.push(allTechTags[index])
      index++
    } else {
      clearInterval(interval)
    }
  }, 100)
})
</script>

<template>
  <section class="min-h-[70vh] flex items-center justify-center
                    px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto text-center space-y-8">
      <!-- Avatar -->
      <div class="relative inline-block">
        <div class="w-32 h-32 rounded-full
                    bg-gradient-to-br from-primary-from to-primary-to
                    p-1 animate-pulse-soft">
          <div class="w-full h-full rounded-full
                      bg-light-surface dark:bg-dark-surface
                      flex items-center justify-center text-5xl font-bold
                      gradient-text">
            NB
          </div>
        </div>
        <div class="absolute -bottom-2 -right-2 px-3 py-1
                    bg-gradient-to-r from-primary-from to-primary-to
                    text-white text-xs font-semibold rounded-full
                    shadow-glow">
          👋 Welcome
        </div>
      </div>

      <!-- Greeting -->
      <div class="space-y-4">
        <p class="text-lg text-light-text-secondary dark:text-dark-text-secondary">
          {{ t('home.hero.greeting') }}
        </p>
        <h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold
                   text-light-text-primary dark:text-dark-text-primary
                   animate-slide-up">
          {{ t('home.hero.name') }}
        </h1>
        <p class="text-xl sm:text-2xl text-light-text-secondary dark:text-dark-text-secondary">
          {{ t('home.hero.tagline') }}
        </p>
      </div>

      <!-- Tech Tags -->
      <div class="flex flex-wrap justify-center gap-3 pt-4">
        <TransitionGroup
          enter-active-class="transition-all duration-300"
          enter-from-class="opacity-0 scale-75"
          enter-to-class="opacity-100 scale-100"
        >
          <span
            v-for="(tag, index) in techTags"
            :key="tag"
            class="inline-flex items-center gap-1.5 px-3 py-1.5
                   bg-light-bg dark:bg-dark-bg
                   border border-light-border dark:border-dark-border
                   rounded-lg text-sm font-medium
                   text-light-text-secondary dark:text-dark-text-secondary
                   hover:border-primary-from hover:text-primary-from
                   transition-colors duration-150"
            :style="{ transitionDelay: `${index * 50}ms` }"
          >
            <Icon icon="lucide:code-2" class="w-3.5 h-3.5" />
            {{ tag }}
          </span>
        </TransitionGroup>
      </div>

      <!-- CTA Buttons -->
      <div class="flex flex-wrap justify-center gap-4 pt-4">
        <a
          href="/blog"
          class="inline-flex items-center gap-2 px-6 py-3
                 bg-gradient-to-r from-primary-from to-primary-to
                 text-white rounded-xl font-medium
                 hover:opacity-90 transition-opacity duration-150
                 shadow-soft"
        >
          <Icon icon="lucide:book-open" class="w-5 h-5" />
          {{ t('nav.blog') }}
        </a>
        <a
          href="/projects"
          class="inline-flex items-center gap-2 px-6 py-3
                 bg-light-bg dark:bg-dark-bg
                 text-light-text-primary dark:text-dark-text-primary
                 rounded-xl font-medium
                 hover:bg-light-border dark:hover:bg-dark-border
                 transition-colors duration-150
                 border border-light-border dark:border-dark-border"
        >
          <Icon icon="lucide:folder" class="w-5 h-5" />
          {{ t('nav.projects') }}
        </a>
      </div>
    </div>
  </section>
</template>
