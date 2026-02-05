<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useThemeStore } from '@/stores/theme'
import { useSearchStore } from '@/stores/search'
import { Icon } from '@iconify/vue'

const route = useRoute()
const { t, locale } = useI18n()
const themeStore = useThemeStore()
const searchStore = useSearchStore()

const isMobileMenuOpen = ref(false)
const isScrolled = ref(false)

// Nav links
const navLinks = computed(() => [
  { href: '/', label: t('nav.logo') },
  { href: '/blog', label: t('nav.blog') },
  { href: '/projects', label: t('nav.projects') },
  { href: '/life', label: t('nav.life') },
  { href: '/about', label: t('nav.about') },
])

// Toggle theme
const toggleTheme = () => {
  themeStore.toggleTheme()
}

// Get theme icon
const themeIcon = computed(() => {
  const theme = themeStore.getResolvedTheme()
  return theme === 'dark' ? 'lucide:sun' : 'lucide:moon'
})

// Toggle language
const toggleLocale = () => {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
}

// Open search (Cmd+K)
const openSearch = () => {
  searchStore.open()
}

// Keyboard shortcuts
const handleKeydown = (e: KeyboardEvent) => {
  // Cmd/Ctrl + K for search
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    openSearch()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

// Close mobile menu on route change
watch(() => route.path, () => {
  isMobileMenuOpen.value = false
})
</script>

<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 glass-nav"
    :class="{ 'scrolled shadow-soft': isScrolled }"
  >
    <div class="max-w-container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center space-x-2 flex-shrink-0">
          <span class="text-xl font-bold gradient-text">{{ t('nav.logo') }}</span>
        </RouterLink>

        <!-- Desktop Navigation -->
        <nav class="hidden lg:flex items-center space-x-8">
          <RouterLink
            v-for="link in navLinks.slice(1)"
            :key="link.href"
            :to="link.href"
            class="text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary
                   hover:text-primary-from dark:hover:text-primary-to
                   transition-colors duration-150"
            :class="{ 'text-primary-from': route.path === link.href }"
          >
            {{ link.label }}
          </RouterLink>
        </nav>

        <!-- Right side actions -->
        <div class="flex items-center space-x-2 lg:space-x-4">
          <!-- Search -->
          <button
            @click="openSearch"
            class="hidden md:flex items-center space-x-2 px-3 py-1.5
                   rounded-lg bg-light-bg dark:bg-dark-bg
                   border border-light-border dark:border-dark-border
                   text-sm text-light-text-muted dark:text-dark-text-muted
                   hover:border-primary-from hover:text-primary-from
                   transition-all duration-150 flex-shrink-0"
          >
            <Icon icon="lucide:search" class="w-4 h-4" />
            <span class="hidden xl:inline">{{ t('nav.search') }}</span>
            <kbd
              class="hidden 2xl:inline-block px-1.5 py-0.5 text-xs
                     bg-light-surface dark:bg-dark-surface
                     border border-light-border dark:border-dark-border
                     rounded"
            >⌘K</kbd>
          </button>

          <!-- Language Toggle -->
          <button
            @click="toggleLocale"
            class="p-2 rounded-lg text-light-text-secondary dark:text-dark-text-secondary
                   hover:bg-light-bg dark:hover:bg-dark-bg
                   transition-colors duration-150"
            :title="locale === 'zh' ? 'Switch to English' : '切换到中文'"
          >
            <span class="text-sm font-medium">{{ locale === 'zh' ? 'EN' : '中文' }}</span>
          </button>

          <!-- Theme Toggle -->
          <button
            @click="toggleTheme"
            class="p-2 rounded-lg text-light-text-secondary dark:text-dark-text-secondary
                   hover:bg-light-bg dark:hover:bg-dark-bg
                   transition-colors duration-150"
            :title="t('theme.system')"
          >
            <Icon :icon="themeIcon" class="w-5 h-5" />
          </button>

          <!-- Mobile Menu Button -->
          <button
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="lg:hidden p-2 rounded-lg
                   text-light-text-secondary dark:text-dark-text-secondary
                   hover:bg-light-bg dark:hover:bg-dark-bg
                   transition-colors duration-150"
          >
            <Icon
              :icon="isMobileMenuOpen ? 'lucide:x' : 'lucide:menu'"
              class="w-5 h-5"
            />
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <Transition
        enter-active-class="transition-all-300"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <nav
          v-if="isMobileMenuOpen"
          class="lg:hidden py-4 border-t border-light-border dark:border-dark-border
                 bg-light-surface/95 dark:bg-dark-surface/95 backdrop-blur-glass"
        >
          <div class="flex flex-col space-y-2">
            <RouterLink
              v-for="link in navLinks.slice(1)"
              :key="link.href"
              :to="link.href"
              class="px-3 py-2 rounded-lg text-sm font-medium
                     text-light-text-secondary dark:text-dark-text-secondary
                     hover:bg-light-bg dark:hover:bg-dark-bg
                     hover:text-primary-from
                     transition-colors duration-150"
              :class="{ 'bg-light-bg dark:bg-dark-bg text-primary-from': route.path === link.href }"
            >
              {{ link.label }}
            </RouterLink>

            <!-- Mobile Search -->
            <button
              @click="openSearch"
              class="flex items-center space-x-3 px-3 py-2 rounded-lg text-left
                     text-light-text-secondary dark:text-dark-text-secondary
                     hover:bg-light-bg dark:hover:bg-dark-bg
                     transition-colors duration-150"
            >
              <Icon icon="lucide:search" class="w-4 h-4" />
              <span class="text-sm">{{ t('nav.search') }}</span>
            </button>
          </div>
        </nav>
      </Transition>
    </div>
  </header>
</template>
