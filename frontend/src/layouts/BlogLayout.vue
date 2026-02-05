<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const isScrolled = ref(false)

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
  <div class="min-h-screen flex flex-col">
    <AppNavbar :class="{ 'scrolled': isScrolled }" />

    <main class="flex-1 max-w-container mx-auto px-4 sm:px-6 lg:px-8 py-12 pt-20">
      <slot />
    </main>

    <AppFooter />
  </div>
</template>
