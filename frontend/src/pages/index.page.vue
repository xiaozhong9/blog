<script setup lang="ts">
import { onMounted } from 'vue'
import { useContentStore } from '@/stores/content.api'
import { useI18n } from 'vue-i18n'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import HeroSection from '@/components/home/HeroSection.vue'
import StatsSection from '@/components/home/StatsSection.vue'
import FeaturedSection from '@/components/home/FeaturedSection.vue'
import LatestPostsSection from '@/components/home/LatestPostsSection.vue'

const { t } = useI18n()
const contentStore = useContentStore()

onMounted(() => {
  contentStore.loadAllContent()
})
</script>

<template>
  <DefaultLayout>
    <div class="space-y-20 pb-20">
      <!-- Hero Section -->
      <HeroSection />

      <!-- Stats Section -->
      <StatsSection />

      <!-- Featured Posts -->
      <FeaturedSection />

      <!-- Latest Posts -->
      <LatestPostsSection />
    </div>
  </DefaultLayout>
</template>
