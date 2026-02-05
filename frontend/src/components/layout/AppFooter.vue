<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { Icon } from '@iconify/vue'

const { t } = useI18n()

const currentYear = new Date().getFullYear()

const socialLinks = [
  { name: 'GitHub', icon: 'lucide:github', href: 'https://github.com' },
  { name: 'Twitter', icon: 'lucide:twitter', href: 'https://twitter.com' },
  { name: 'Email', icon: 'lucide:mail', href: 'mailto:hello@nanobanana.dev' },
]
</script>

<template>
  <footer class="border-t border-light-border dark:border-dark-border
                bg-light-bg dark:bg-dark-bg">
    <div class="max-w-container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Brand -->
        <div class="space-y-4">
          <RouterLink to="/" class="inline-block">
            <span class="text-xl font-bold gradient-text">{{ t('nav.logo') }}</span>
          </RouterLink>
          <p class="text-sm text-light-text-muted dark:text-dark-text-muted max-w-sm">
            A world-class personal blog system built with Vue 3,
            designed for sharing knowledge and showcasing projects.
          </p>
        </div>

        <!-- Navigation -->
        <div>
          <h3 class="text-sm font-semibold text-light-text-primary dark:text-dark-text-primary mb-4">
            {{ t('nav.logo') }}
          </h3>
          <ul class="space-y-2">
            <li>
              <RouterLink
                to="/blog"
                class="text-sm text-light-text-secondary dark:text-dark-text-secondary
                       hover:text-primary-from transition-colors duration-150"
              >
                {{ t('nav.blog') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink
                to="/projects"
                class="text-sm text-light-text-secondary dark:text-dark-text-secondary
                       hover:text-primary-from transition-colors duration-150"
              >
                {{ t('nav.projects') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink
                to="/about"
                class="text-sm text-light-text-secondary dark:text-dark-text-secondary
                       hover:text-primary-from transition-colors duration-150"
              >
                {{ t('nav.about') }}
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Social Links -->
        <div>
          <h3 class="text-sm font-semibold text-light-text-primary dark:text-dark-text-primary mb-4">
            Connect
          </h3>
          <div class="flex space-x-4">
            <a
              v-for="link in socialLinks"
              :key="link.name"
              :href="link.href"
              :title="link.name"
              target="_blank"
              rel="noopener noreferrer"
              class="p-2 rounded-lg text-light-text-secondary dark:text-dark-text-secondary
                     hover:bg-light-bg dark:hover:bg-dark-bg
                     hover:text-primary-from
                     transition-all duration-150"
            >
              <Icon :icon="link.icon" class="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>

      <!-- Bottom -->
      <div class="mt-12 pt-8 border-t border-light-border dark:border-dark-border">
        <p class="text-sm text-center text-light-text-muted dark:text-dark-text-muted">
          © {{ currentYear }} Nano Banana. Built with Vue 3 & Tailwind CSS.
        </p>
      </div>
    </div>
  </footer>
</template>
