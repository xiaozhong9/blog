import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { useColorMode } from '@vueuse/core'
import type { Theme } from '@/types/theme'

export const useThemeStore = defineStore('theme', () => {
  // VueUse color mode
  const mode = useColorMode({
    attribute: 'class',
    initialValue: 'system',
    modes: {
      light: 'light',
      dark: 'dark',
      system: 'system',
    },
  })

  // Current theme state
  const currentTheme = ref<Theme>(mode.value as Theme)

  // Initialize theme from localStorage or system preference
  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme') as Theme | null

    if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
      currentTheme.value = savedTheme
      mode.value = savedTheme
    } else {
      // Default to system preference
      currentTheme.value = 'system'
      mode.value = 'system'
    }
  }

  // Set theme
  const setTheme = (theme: Theme) => {
    currentTheme.value = theme
    mode.value = theme
    localStorage.setItem('theme', theme)
  }

  // Toggle between light and dark
  const toggleTheme = () => {
    const newTheme: Theme = currentTheme.value === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
  }

  // Watch for theme changes
  watch(currentTheme, (newTheme) => {
    localStorage.setItem('theme', newTheme)
  })

  // Get actual theme (resolves 'system' to 'light' or 'dark')
  const getResolvedTheme = (): 'light' | 'dark' => {
    if (currentTheme.value === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return currentTheme.value
  }

  return {
    currentTheme,
    initTheme,
    setTheme,
    toggleTheme,
    getResolvedTheme,
  }
})
