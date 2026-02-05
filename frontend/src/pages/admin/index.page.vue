<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { useAdminContentStore } from '@/stores/content.admin'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import { commentService } from '@/api/services'
import type { Comment } from '@/api/types'
import { formatDate, formatDateTime } from '@/utils/dateFormatter'

const adminContentStore = useAdminContentStore()
const router = useRouter()

// 待审核评论
const pendingComments = ref<Comment[]>([])
const loadingComments = ref(false)

// 加载数据
onMounted(async () => {
  await adminContentStore.loadAllContent(true) // 包含草稿
  // 加载分类和标签
  await adminContentStore.loadCategories()
  await adminContentStore.loadTags()

  // 加载待审核评论
  await loadPendingComments()
})

// 加载待审核评论
const loadPendingComments = async () => {
  loadingComments.value = true
  try {
    const response = await commentService.getList({
      status: 'pending',
      page: 1,
      page_size: 5
    })

    const results = response?.results || []
    pendingComments.value = results
  } catch (error) {
    pendingComments.value = []
  } finally {
    loadingComments.value = false
  }
}

// 统计数据
const stats = computed(() => {
  const allPosts = adminContentStore.posts || []

  const blogPosts = allPosts.filter(p => p.category === 'blog')
  const projects = allPosts.filter(p => p.category === 'projects')
  const lifePosts = allPosts.filter(p => p.category === 'life')

  return {
    total: allPosts.length,
    blog: blogPosts.length,
    projects: projects.length,
    life: lifePosts.length,
    featured: allPosts.filter(p => p.featured).length,
    drafts: allPosts.filter(p => p.draft).length,
  }
})

// 最近内容（按类别显示最新的3条）
const recentPosts = computed(() => {
  const allPosts = adminContentStore.posts || []
  return {
    blog: allPosts.filter(p => p.category === 'blog').slice(0, 3),
    projects: allPosts.filter(p => p.category === 'projects').slice(0, 3),
    life: allPosts.filter(p => p.category === 'life').slice(0, 3),
  }
})

// 快速操作
const quickActions = computed(() => {
  const actions = [
    {
      label: '新建文章',
      icon: 'lucide:file-plus',
      path: '/admin/posts/new',
      color: 'from-blue-500 to-blue-600',
    },
    {
      label: '新建项目',
      icon: 'lucide:folder-plus',
      path: '/admin/projects/new',
      color: 'from-purple-500 to-purple-600',
    },
    {
      label: '新建生活记录',
      icon: 'lucide:calendar-plus',
      path: '/admin/life/new',
      color: 'from-green-500 to-green-600',
    },
  ]

  // 如果有待审核评论，添加审核按钮
  if (pendingComments.value.length > 0) {
    actions.unshift({
      label: `审核评论 (${pendingComments.value.length})`,
      icon: 'lucide:message-square-warning',
      path: '/admin/comments',
      color: 'from-orange-500 to-red-500',
    } as any)
  }

  return actions
})
</script>

<template>
  <AdminLayout>
    <div class="space-y-8">
      <!-- 标题 -->
      <ScrollReveal>
        <div>
          <h1 class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-2">
            欢迎回来
          </h1>
          <p class="text-light-text-secondary dark:text-dark-text-secondary">
            这是你的后台管理控制台
          </p>
        </div>
      </ScrollReveal>

      <!-- 待审核评论提醒 -->
      <ScrollReveal class="delay-100" v-if="pendingComments.length > 0">
        <div class="card p-6 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 border-l-4 border-orange-500">
          <div class="flex items-start justify-between">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-lg bg-orange-100 dark:bg-orange-900/50 flex items-center justify-center flex-shrink-0">
                <Icon icon="lucide:message-square-warning" class="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary mb-1">
                  有 {{ pendingComments.length }} 条评论待审核
                </h3>
                <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary mb-3">
                  请及时处理用户提交的评论
                </p>
                <div class="space-y-2">
                  <div
                    v-for="comment in pendingComments.slice(0, 3)"
                    :key="comment.id"
                    class="p-3 rounded-lg bg-white dark:bg-gray-800 text-sm"
                  >
                    <div class="flex items-start justify-between gap-2 mb-1">
                      <div class="flex flex-col">
                        <span class="font-medium text-light-text-primary dark:text-dark-text-primary">
                          {{ comment.author ? comment.author.nickname || comment.author.username : comment.guest_name }}
                        </span>
                        <span class="text-xs text-light-text-muted dark:text-dark-text-muted">
                          {{ comment.author ? comment.author.email : comment.guest_email }}
                        </span>
                      </div>
                      <span class="text-xs text-light-text-muted dark:text-dark-text-muted flex-shrink-0">
                        {{ formatDateTime(comment.created_at) }}
                      </span>
                    </div>
                    <div class="text-light-text-secondary dark:text-dark-text-secondary line-clamp-2">
                      {{ comment.content }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <button
              @click="router.push('/admin/comments')"
              class="px-4 py-2 rounded-lg bg-orange-500 hover:bg-orange-600 text-white text-sm font-medium transition-colors flex-shrink-0"
            >
              前往审核
            </button>
          </div>
        </div>
      </ScrollReveal>

      <!-- 统计卡片 -->
      <ScrollReveal class="delay-100">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="card p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                <Icon icon="lucide:file-text" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
            <div class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-1">
              {{ stats.blog }}
            </div>
            <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
              博客文章
            </div>
          </div>

          <div class="card p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                <Icon icon="lucide:folder" class="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <div class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-1">
              {{ stats.projects }}
            </div>
            <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
              项目展示
            </div>
          </div>

          <div class="card p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                <Icon icon="lucide:calendar" class="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
            <div class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-1">
              {{ stats.life }}
            </div>
            <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
              生活记录
            </div>
          </div>

          <div class="card p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="w-12 h-12 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center">
                <Icon icon="lucide:star" class="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
            <div class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-1">
              {{ stats.featured }}
            </div>
            <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
              精选内容
            </div>
          </div>
        </div>
      </ScrollReveal>

      <!-- 快速操作 -->
      <ScrollReveal class="delay-200">
        <div>
          <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-4">
            快速操作
          </h2>
          <div :class="`grid grid-cols-1 ${pendingComments.length > 0 ? 'sm:grid-cols-4' : 'sm:grid-cols-3'} gap-4`">
            <button
              v-for="action in quickActions"
              :key="action.path"
              @click="router.push(action.path)"
              class="card p-6 text-left group hover:shadow-lg transition-all"
            >
              <div class="flex items-center gap-4">
                <div :class="`w-12 h-12 rounded-lg bg-gradient-to-br ${action.color} flex items-center justify-center text-white`">
                  <Icon :icon="action.icon" class="w-6 h-6" />
                </div>
                <div>
                  <div class="font-medium text-light-text-primary dark:text-dark-text-primary group-hover:text-primary-from transition-colors">
                    {{ action.label }}
                  </div>
                </div>
              </div>
            </button>
          </div>
        </div>
      </ScrollReveal>

      <!-- 最近内容 -->
      <ScrollReveal class="delay-300">
        <div class="space-y-6">
          <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary">
            最近内容
          </h2>

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- 最近文章 -->
            <div class="card p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="font-semibold text-light-text-primary dark:text-dark-text-primary flex items-center gap-2">
                  <Icon icon="lucide:file-text" class="w-5 h-5 text-blue-500" />
                  最近文章
                </h3>
                <button
                  @click="router.push('/admin/posts')"
                  class="text-sm text-primary-from hover:underline"
                >
                  查看全部
                </button>
              </div>
              <div v-if="recentPosts.blog.length > 0" class="space-y-3">
                <div
                  v-for="post in recentPosts.blog"
                  :key="post.slug"
                  class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
                  @click="router.push(`/admin/posts/${post.slug}`)"
                >
                  <div class="font-medium text-light-text-primary dark:text-dark-text-primary text-sm line-clamp-1 mb-1">
                    {{ post.title }}
                  </div>
                  <div class="text-xs text-light-text-muted dark:text-dark-text-muted">
                    {{ formatDate(post.date) }}
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4 text-sm text-light-text-muted dark:text-dark-text-muted">
                暂无文章
              </div>
            </div>

            <!-- 最近项目 -->
            <div class="card p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="font-semibold text-light-text-primary dark:text-dark-text-primary flex items-center gap-2">
                  <Icon icon="lucide:folder" class="w-5 h-5 text-purple-500" />
                  最近项目
                </h3>
                <button
                  @click="router.push('/admin/projects')"
                  class="text-sm text-primary-from hover:underline"
                >
                  查看全部
                </button>
              </div>
              <div v-if="recentPosts.projects.length > 0" class="space-y-3">
                <div
                  v-for="project in recentPosts.projects"
                  :key="project.slug"
                  class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
                  @click="router.push(`/admin/projects/${project.slug}`)"
                >
                  <div class="font-medium text-light-text-primary dark:text-dark-text-primary text-sm line-clamp-1 mb-1">
                    {{ project.title }}
                  </div>
                  <div class="flex items-center gap-2 text-xs text-light-text-muted dark:text-dark-text-muted">
                    <span>⭐ {{ (project as any).stars || 0 }}</span>
                    <span>🍴 {{ (project as any).forks || 0 }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4 text-sm text-light-text-muted dark:text-dark-text-muted">
                暂无项目
              </div>
            </div>

            <!-- 最近生活记录 -->
            <div class="card p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="font-semibold text-light-text-primary dark:text-dark-text-primary flex items-center gap-2">
                  <Icon icon="lucide:calendar" class="w-5 h-5 text-green-500" />
                  最近记录
                </h3>
                <button
                  @click="router.push('/admin/life')"
                  class="text-sm text-primary-from hover:underline"
                >
                  查看全部
                </button>
              </div>
              <div v-if="recentPosts.life.length > 0" class="space-y-3">
                <div
                  v-for="post in recentPosts.life"
                  :key="post.slug"
                  class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
                  @click="router.push(`/admin/life/${post.slug}`)"
                >
                  <div class="font-medium text-light-text-primary dark:text-dark-text-primary text-sm line-clamp-1 mb-1">
                    {{ post.title }}
                  </div>
                  <div class="text-xs text-light-text-muted dark:text-dark-text-muted">
                    {{ formatDate(post.date) }}
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4 text-sm text-light-text-muted dark:text-dark-text-muted">
                暂无记录
              </div>
            </div>
          </div>
        </div>
      </ScrollReveal>

      <!-- 系统信息 -->
      <ScrollReveal class="delay-300">
        <div class="card p-6">
          <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-4">
            系统信息
          </h2>
          <div class="space-y-3 text-sm">
            <div class="flex justify-between">
              <span class="text-light-text-secondary dark:text-dark-text-secondary">内容总数</span>
              <span class="font-medium text-light-text-primary dark:text-dark-text-primary">{{ stats.total }} 篇</span>
            </div>
            <div class="flex justify-between">
              <span class="text-light-text-secondary dark:text-dark-text-secondary">数据存储</span>
              <span class="font-medium text-light-text-primary dark:text-dark-text-primary">MySQL + Elasticsearch ✅</span>
            </div>
            <div class="flex justify-between">
              <span class="text-light-text-secondary dark:text-dark-text-secondary">版本</span>
              <span class="font-medium text-light-text-primary dark:text-dark-text-primary">v1.0.0</span>
            </div>
          </div>
        </div>
      </ScrollReveal>
    </div>
  </AdminLayout>
</template>
