<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useScroll } from '@vueuse/core'

const props = defineProps<{
  headings: Array<{
    id: string
    text: string
    level: number
  }>
  activeId?: string
}>()

const emit = defineEmits<{
  (e: 'heading-click', id: string): void
}>()

const { y } = useScroll(window)

// Calculate active heading based on scroll
const activeHeading = computed(() => {
  if (props.activeId) return props.activeId

  // Find heading that's currently in view
  for (const heading of props.headings) {
    const element = document.getElementById(heading.id)
    if (element) {
      const rect = element.getBoundingClientRect()
      if (rect.top >= 0 && rect.top < 200) {
        return heading.id
      }
    }
  }

  return props.headings[0]?.id || ''
})

// Scroll to heading
const scrollToHeading = (id: string) => {
  const element = document.getElementById(id)
  if (element) {
    const offset = 80 // navbar height + spacing
    const top = element.getBoundingClientRect().top + window.scrollY - offset
    window.scrollTo({ top, behavior: 'smooth' })
    emit('heading-click', id)
  }
}

// Filter headings by level (show h2 and h3)
const visibleHeadings = computed(() => {
  return props.headings.filter(h => h.level >= 2 && h.level <= 3)
})
</script>

<template>
  <nav class="space-y-2">
    <h4 class="text-xs font-semibold uppercase tracking-wider
                text-light-text-muted dark:text-dark-text-muted mb-4">
      {{ $t('post.tableOfContents') }}
    </h4>

    <ul class="space-y-2 text-sm">
      <li
        v-for="heading in visibleHeadings"
        :key="heading.id"
        class="relative"
      >
        <button
          @click="scrollToHeading(heading.id)"
          class="block w-full text-left py-1 px-2 rounded
                 transition-all duration-150
                 text-light-text-secondary dark:text-dark-text-secondary
                 hover:text-primary-from hover:bg-light-bg dark:hover:bg-dark-bg
                 border-l-2 border-transparent"
          :class="{
            'text-primary-from font-medium border-primary-from':
              activeHeading === heading.id,
            'ml-0': heading.level === 2,
            'ml-4': heading.level === 3,
          }"
        >
          {{ heading.text }}
        </button>
      </li>
    </ul>
  </nav>
</template>
