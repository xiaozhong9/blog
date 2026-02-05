<script setup lang="ts">
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()

const handleLogout = () => {
  // 清除 JWT tokens
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/admin/login')
}

// 导航菜单
const navItems = [
  { path: '/admin', icon: 'lucide:home', label: '首页' },
  { path: '/admin/posts', icon: 'lucide:file-text', label: '文章管理' },
  { path: '/admin/projects', icon: 'lucide:folder', label: '项目管理' },
  { path: '/admin/life', icon: 'lucide:calendar', label: '生活记录' },
  { path: '/admin/comments', icon: 'lucide:message-square', label: '评论管理' },
  { path: '/admin/about', icon: 'lucide:user', label: '关于我' },
]

// 当前激活的菜单项
const activePath = computed(() => route.path)
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 顶部导航栏 -->
    <header class="bg-white dark:bg-gray-800 border-b border-light-border dark:border-dark-border">
      <div class="px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center gap-8">
            <RouterLink to="/admin" class="flex items-center gap-2">
              <Icon icon="lucide:layout-dashboard" class="w-6 h-6 text-primary-from" />
              <span class="text-xl font-bold text-light-text-primary dark:text-dark-text-primary">
                Nano Banana Admin
              </span>
            </RouterLink>

            <!-- 导航菜单 -->
            <nav class="hidden md:flex items-center gap-1">
              <RouterLink
                v-for="item in navItems"
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                :class="activePath.startsWith(item.path)
                  ? 'bg-primary-from/10 text-primary-from'
                  : 'text-light-text-secondary dark:text-dark-text-secondary hover:bg-gray-100 dark:hover:bg-gray-700'"
              >
                <Icon :icon="item.icon" class="w-4 h-4" />
                {{ item.label }}
              </RouterLink>
            </nav>
          </div>

          <!-- 右侧操作 -->
          <div class="flex items-center gap-4">
            <!-- 前台链接 -->
            <RouterLink
              to="/"
              class="hidden sm:flex items-center gap-2 text-sm text-light-text-secondary dark:text-dark-text-secondary
                     hover:text-light-text-primary dark:hover:text-dark-text-primary transition-colors"
            >
              <Icon icon="lucide:external-link" class="w-4 h-4" />
              前台
            </RouterLink>

            <!-- 登出按钮 -->
            <button
              @click="handleLogout"
              class="flex items-center gap-2 px-3 py-2 text-sm rounded-lg
                     text-red-600 dark:text-red-400
                     hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            >
              <Icon icon="lucide:log-out" class="w-4 h-4" />
              <span class="hidden sm:inline">登出</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="p-4 sm:p-6 lg:p-8">
      <slot />
    </main>
  </div>
</template>
