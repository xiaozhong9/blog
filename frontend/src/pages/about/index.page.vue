<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import { userService } from '@/api/services'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import { parseMarkdown } from '@/utils/markdown'

const { t } = useI18n()

// 用户信息
const userProfile = ref<any>(null)
const loading = ref(true)

// 我的故事（渲染后的 HTML）
const storyHtml = ref('')

// 技能栈（从 API 获取，使用默认值作为后备）
const skills = ref<{ name: string; level: number }[]>([])

// 时间线（从 API 获取，使用默认值作为后备）
const timeline = ref<any[]>([])

// 加载用户信息
const loadUserProfile = async () => {
  try {
    const profile = await userService.getProfile()
    userProfile.value = profile

    // 渲染故事内容
    if (profile.story) {
      storyHtml.value = await parseMarkdown(profile.story)
    }

    // 转换技能数据（从对象转为数组）
    if (profile.skills && typeof profile.skills === 'object') {
      skills.value = Object.entries(profile.skills).map(([name, level]) => ({
        name,
        level: level as number
      }))
    } else {
      // 默认技能
      skills.value = [
        { name: 'Vue.js', level: 90 },
        { name: 'TypeScript', level: 85 },
        { name: 'React', level: 80 },
        { name: 'Node.js', level: 75 },
        { name: 'Tailwind CSS', level: 90 },
        { name: 'Vite', level: 85 },
      ]
    }

    // 转换时间线数据并按年份排序
    if (profile.timeline && Array.isArray(profile.timeline)) {
      timeline.value = [...profile.timeline].sort((a: any, b: any) => {
        const yearA = parseInt(a.year) || 0
        const yearB = parseInt(b.year) || 0
        return yearB - yearA // 降序排序
      })
    } else {
      // 默认时间线
      timeline.value = [
        {
          year: '2024',
          title: 'Senior Frontend Developer',
          company: 'Tech Company',
          description: 'Leading frontend architecture and design system development',
        },
        {
          year: '2022',
          title: 'Frontend Developer',
          company: 'Startup',
          description: 'Built modern web applications with Vue 3 and React',
        },
        {
          year: '2020',
          title: 'Junior Developer',
          company: 'Agency',
          description: 'Started my journey in web development',
        },
      ]
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    // 加载失败时使用默认值
    skills.value = [
      { name: 'Vue.js', level: 90 },
      { name: 'TypeScript', level: 85 },
    ]
    timeline.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserProfile()
})
</script>

<template>
  <DefaultLayout>
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header -->
      <ScrollReveal>
        <header class="text-center mb-16">
          <div
            class="w-24 h-24 mx-auto mb-6 rounded-full
                      bg-gradient-to-br from-primary-from to-primary-to
                      flex items-center justify-center text-white text-4xl font-bold"
          >
            <img
              v-if="userProfile?.avatar"
              :src="userProfile.avatar"
              :alt="userProfile.nickname || userProfile.username"
              class="w-full h-full rounded-full object-cover"
            />
            <span v-else>{{ (userProfile?.nickname || userProfile?.username || 'NB')[0] }}</span>
          </div>
          <h1 class="text-4xl sm:text-5xl font-bold mb-4
                     text-light-text-primary dark:text-dark-text-primary">
            {{ t('about.title') }}
          </h1>
          <p class="text-lg text-light-text-secondary dark:text-dark-text-secondary max-w-2xl mx-auto">
            {{ userProfile?.bio || t('about.subtitle') }}
          </p>
          <div v-if="userProfile?.website" class="mt-4">
            <a
              :href="userProfile.website"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 text-primary-from hover:underline"
            >
              <Icon icon="lucide:link" class="w-4 h-4" />
              {{ userProfile.website }}
            </a>
          </div>
        </header>
      </ScrollReveal>

      <!-- Story Section -->
      <ScrollReveal class="delay-100">
        <section class="mb-16">
          <h2 class="text-2xl font-bold mb-6 text-light-text-primary dark:text-dark-text-primary">
            {{ t('about.story') }}
          </h2>
          <div
            v-if="storyHtml"
            class="prose dark:prose-invert prose-p:text-light-text-secondary prose-p:dark:text-dark-text-secondary max-w-none"
            v-html="storyHtml"
          />
          <div
            v-else
            class="prose dark:prose-invert max-w-none
                        text-light-text-secondary dark:text-dark-text-secondary"
          >
            <p class="mb-4">
              Hello! I'm {{ userProfile?.nickname || userProfile?.username || 'Nano Banana' }}, a passionate developer who loves building beautiful,
              functional, and user-friendly web applications.
            </p>
            <p class="mb-4">
              My journey in web development started in 2020, and since then I've worked on
              various projects ranging from small business websites to large-scale applications.
            </p>
            <p>
              I specialize in Vue.js and modern frontend technologies, with a focus on creating
              exceptional user experiences and maintainable code.
            </p>
          </div>
        </section>
      </ScrollReveal>

      <!-- Skills Section -->
      <ScrollReveal class="delay-200">
        <section class="mb-16">
          <h2 class="text-2xl font-bold mb-6 text-light-text-primary dark:text-dark-text-primary">
            {{ t('about.skills') }}
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="skill in skills"
              :key="skill.name"
              class="space-y-2"
            >
              <div class="flex justify-between text-sm">
                <span class="font-medium text-light-text-primary dark:text-dark-text-primary">
                  {{ skill.name }}
                </span>
                <span class="text-light-text-muted dark:text-dark-text-muted">
                  {{ skill.level }}%
                </span>
              </div>
              <div class="h-2 bg-light-bg dark:bg-dark-bg rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-primary-from to-primary-to
                         transition-all duration-1000 ease-out"
                  :style="{ width: `${skill.level}%` }"
                />
              </div>
            </div>
          </div>
        </section>
      </ScrollReveal>

      <!-- Timeline Section -->
      <ScrollReveal class="delay-300">
        <section class="mb-16">
          <h2 class="text-2xl font-bold mb-6 text-light-text-primary dark:text-dark-text-primary">
            Journey
          </h2>
          <div class="space-y-8">
            <div
              v-for="(item, index) in timeline"
              :key="index"
              class="relative pl-8 border-l-2 border-light-border dark:border-dark-border"
            >
              <div class="absolute left-0 top-0 w-4 h-4 -translate-x-[9px]
                          bg-gradient-to-br from-primary-from to-primary-to
                          rounded-full border-4 border-light-bg dark:border-dark-bg" />
              <div class="mb-1">
                <span class="text-sm font-semibold text-primary-from">{{ item.year }}</span>
              </div>
              <h3 class="text-lg font-bold text-light-text-primary dark:text-dark-text-primary">
                {{ item.title }}
                <span class="text-light-text-secondary dark:text-dark-text-secondary font-normal">
                  @ {{ item.company }}
                </span>
              </h3>
              <p class="text-light-text-secondary dark:text-dark-text-secondary mt-1">
                {{ item.description }}
              </p>
            </div>
          </div>
        </section>
      </ScrollReveal>

      <!-- Contact Section -->
      <ScrollReveal class="delay-400">
        <section>
          <h2 class="text-2xl font-bold mb-6 text-light-text-primary dark:text-dark-text-primary">
            {{ t('about.contact') }}
          </h2>
          <div class="flex flex-wrap gap-4">
            <a
              v-if="userProfile?.email"
              :href="`mailto:${userProfile.email}`"
              class="inline-flex items-center gap-2 px-6 py-3
                     bg-gradient-to-r from-primary-from to-primary-to
                     text-white rounded-xl font-medium
                     hover:opacity-90 transition-opacity duration-150
                     shadow-soft"
            >
              <Icon icon="lucide:mail" class="w-5 h-5" />
              Email
            </a>
            <a
              v-if="userProfile?.website"
              :href="userProfile.website"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 px-6 py-3
                     bg-light-bg dark:bg-dark-bg
                     text-light-text-primary dark:text-dark-text-primary
                     rounded-xl font-medium
                     hover:bg-light-border dark:hover:bg-dark-border
                     transition-colors duration-150
                     border border-light-border dark:border-dark-border"
            >
              <Icon icon="lucide:globe" class="w-5 h-5" />
              Website
            </a>
            <a
              v-if="userProfile?.github_url"
              :href="userProfile.github_url"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 px-6 py-3
                     bg-light-bg dark:bg-dark-bg
                     text-light-text-primary dark:text-dark-text-primary
                     rounded-xl font-medium
                     hover:bg-light-border dark:hover:bg-dark-border
                     transition-colors duration-150
                     border border-light-border dark:border-dark-border"
            >
              <Icon icon="lucide:github" class="w-5 h-5" />
              GitHub
            </a>
            <a
              v-if="userProfile?.twitter_url"
              :href="userProfile.twitter_url"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 px-6 py-3
                     bg-light-bg dark:bg-dark-bg
                     text-light-text-primary dark:text-dark-text-primary
                     rounded-xl font-medium
                     hover:bg-light-border dark:hover:bg-dark-border
                     transition-colors duration-150
                     border border-light-border dark:border-dark-border"
            >
              <Icon icon="lucide:twitter" class="w-5 h-5" />
              Twitter
            </a>
            <a
              v-if="userProfile?.linkedin_url"
              :href="userProfile.linkedin_url"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 px-6 py-3
                     bg-light-bg dark:bg-dark-bg
                     text-light-text-primary dark:text-dark-text-primary
                     rounded-xl font-medium
                     hover:bg-light-border dark:hover:bg-dark-border
                     transition-colors duration-150
                     border border-light-border dark:border-dark-border"
            >
              <Icon icon="lucide:linkedin" class="w-5 h-5" />
              LinkedIn
            </a>
          </div>
        </section>
      </ScrollReveal>
    </div>
  </DefaultLayout>
</template>
