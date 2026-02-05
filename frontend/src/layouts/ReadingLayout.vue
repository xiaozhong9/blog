<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useScroll } from '@vueuse/core'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import TableOfContents from '@/components/content/TableOfContents.vue'
import ReadingProgress from '@/components/content/ReadingProgress.vue'

const props = defineProps<{
  headings: Array<{
    id: string
    text: string
    level: number
  }>
}>()

const isScrolled = ref(false)

// Reading progress
const { y, directions } = useScroll(window, { behavior: 'smooth' })

const scrollProgress = computed(() => {
  const scrollTop = y.value
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  return docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
})

const activeHeading = computed(() => {
  // Find active heading based on scroll position
  // This is a simplified version
  return props.headings[0]?.id || ''
})

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="min-h-screen">
    <AppNavbar :class="{ 'scrolled': isScrolled }" />
    <ReadingProgress :progress="scrollProgress" />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-20">
      <div class="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-12">
        <!-- Main content -->
        <main class="min-w-0">
          <slot />
        </main>

        <!-- Table of Contents (desktop) -->
        <aside class="hidden lg:block">
          <TableOfContents
            :headings="headings"
            :active-id="activeHeading"
            class="sticky top-24"
          />
        </aside>
      </div>
    </div>
  </div>
</template>
