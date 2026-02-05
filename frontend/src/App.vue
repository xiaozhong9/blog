<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useSearchStore } from '@/stores/search'
import { useAuthStore } from '@/stores/auth.api'
import { useI18n } from 'vue-i18n'
import SearchModal from '@/components/search/SearchModal.vue'
import AIChatAssistant from '@/components/ai/AIChatAssistant.vue'
import BackToTop from '@/components/effects/BackToTop.vue'
import ToastNotifications from '@/components/ui/ToastNotifications.vue'
import DebugPanel from '@/components/dev/DebugPanel.vue'

const { locale } = useI18n()
const themeStore = useThemeStore()
const searchStore = useSearchStore()
const authStore = useAuthStore()

// Initialize on mount
onMounted(async () => {
  themeStore.initTheme()
  searchStore.loadHistory()

  // Initialize authentication state
  await authStore.initializeAuth()
})

// Update HTML lang when locale changes
watch(locale, (newLocale) => {
  document.documentElement.lang = newLocale
}, { immediate: true })
</script>

<template>
  <!-- 主应用 -->
  <RouterView />

  <!-- 全局组件 -->
  <SearchModal />
  <AIChatAssistant />
  <BackToTop />
  <ToastNotifications />
  <DebugPanel />
</template>

<style>
/* Global styles */
</style>
