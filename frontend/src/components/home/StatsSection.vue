<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import { statsService } from '@/api/services'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'

const { t } = useI18n()

const stats = ref({
  blog: 0,
  projects: 0,
  life: 0,
  total: 0
})

const loading = ref(true)

onMounted(async () => {
  try {
    const data = await statsService.getOverview()
    stats.value = {
      blog: data.category_stats?.blog || 0,
      projects: data.category_stats?.projects || 0,
      life: data.category_stats?.life || 0,
      total: data.total_articles || 0
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
})

const statItems = computed(() => [
  {
    key: 'blog',
    icon: 'lucide:book-open',
    label: '博客文章',
    value: stats.value.blog,
    color: 'from-blue-500 to-cyan-500',
    link: '/blog'
  },
  {
    key: 'projects',
    icon: 'lucide:folder-code',
    label: '项目展示',
    value: stats.value.projects,
    color: 'from-purple-500 to-pink-500',
    link: '/projects'
  },
  {
    key: 'life',
    icon: 'lucide:heart',
    label: '生活随笔',
    value: stats.value.life,
    color: 'from-orange-500 to-red-500',
    link: '/life'
  },
  {
    key: 'total',
    icon: 'lucide:database',
    label: '总计',
    value: stats.value.total,
    color: 'from-green-500 to-emerald-500',
    link: '#'
  }
])
</script>

<template>
  <section class="max-w-container mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <ScrollReveal>
      <div class="text-center mb-10">
        <h2 class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-2">
          内容统计
        </h2>
        <p class="text-light-text-secondary dark:text-dark-text-secondary">
          记录我的创作与成长
        </p>
      </div>

      <div v-if="!loading" class="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <a
          v-for="(item, index) in statItems"
          :key="item.key"
          :href="item.link"
          class="group"
        >
          <div
            class="relative overflow-hidden rounded-2xl
                   bg-light-bg dark:bg-dark-bg
                   border border-light-border dark:border-dark-border
                   p-6
                   hover:border-primary-from transition-all duration-300
                   hover:shadow-lg hover:shadow-primary-from/10"
            :style="{ transitionDelay: `${index * 50}ms` }"
          >
            <!-- 背景渐变 -->
            <div
              :class="[
                'absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-300',
                'bg-gradient-to-br', item.color
              ]"
            />

            <!-- 内容 -->
            <div class="relative">
              <!-- 图标 -->
              <div
                :class="[
                  'w-12 h-12 rounded-xl mb-4',
                  'bg-gradient-to-br', item.color,
                  'flex items-center justify-center',
                  'text-white shadow-lg'
                ]"
              >
                <Icon :icon="item.icon" class="w-6 h-6" />
              </div>

              <!-- 数量 -->
              <div class="text-3xl font-bold gradient-text mb-1">
                {{ item.value }}
              </div>

              <!-- 标签 -->
              <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
                {{ item.label }}
              </div>
            </div>
          </div>
        </a>
      </div>

      <!-- 加载状态 -->
      <div v-else class="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          v-for="i in 4"
          :key="i"
          class="h-32 rounded-2xl bg-light-bg dark:bg-dark-bg
                 border border-light-border dark:border-dark-border
                 animate-pulse"
        />
      </div>
    </ScrollReveal>
  </section>
</template>
