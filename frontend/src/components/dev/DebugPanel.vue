<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useContentStore } from '@/stores/content.api'
import { useAuthStore } from '@/stores/auth.api'
import { useNotificationStore } from '@/stores/notification'
import { useThemeStore } from '@/stores/theme'

const isDev = import.meta.env.DEV
const isExpanded = ref(false)
const activeTab = ref<'state' | 'actions' | 'logs'>('state')

const contentStore = useContentStore()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const themeStore = useThemeStore()

// 调试日志
const debugLogs = ref<Array<{ timestamp: number; message: string; type: 'info' | 'warn' | 'error' }>>([])

const addLog = (message: string, type: 'info' | 'warn' | 'error' = 'info') => {
  debugLogs.value.push({
    timestamp: Date.now(),
    message,
    type,
  })
  // 限制日志数量
  if (debugLogs.value.length > 100) {
    debugLogs.value.shift()
  }
}

// 拦截 console
onMounted(() => {
  if (isDev) {
    const originalLog = console.log
    const originalWarn = console.warn
    const originalError = console.error

    console.log = (...args) => {
      originalLog(...args)
      addLog(args.join(' '), 'info')
    }

    console.warn = (...args) => {
      originalWarn(...args)
      addLog(args.join(' '), 'warn')
    }

    console.error = (...args) => {
      originalError(...args)
      addLog(args.join(' '), 'error')
    }
  }
})

// 测试通知
const testNotifications = () => {
  notificationStore.success('这是一个成功通知', '成功')
  setTimeout(() => {
    notificationStore.error('这是一个错误通知', '错误')
  }, 1000)
  setTimeout(() => {
    notificationStore.warning('这是一个警告通知', '警告')
  }, 2000)
  setTimeout(() => {
    notificationStore.info('这是一个信息通知', '信息')
  }, 3000)
}

// 清空日志
const clearLogs = () => {
  debugLogs.value = []
}

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour12: false })
}

// 日志类型颜色
const logTypeColor = (type: string) => {
  const colors = {
    info: 'text-blue-500',
    warn: 'text-yellow-500',
    error: 'text-red-500',
  }
  return colors[type as keyof typeof colors] || 'text-gray-500'
}
</script>

<template>
  <div v-if="isDev" class="fixed bottom-4 right-4 z-40">
    <!-- 折叠状态 -->
    <div
      v-if="!isExpanded"
      @click="isExpanded = true"
      class="bg-primary-from text-white px-4 py-2 rounded-lg shadow-lg cursor-pointer hover:opacity-90 transition-opacity flex items-center gap-2"
    >
      <Icon icon="lucide:bug" class="w-4 h-4" />
      <span class="text-sm font-medium">调试面板</span>
    </div>

    <!-- 展开状态 -->
    <div
      v-else
      class="bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-light-border dark:border-dark-border w-96 max-h-[600px] flex flex-col"
    >
      <!-- 头部 -->
      <div class="flex items-center justify-between p-3 border-b border-light-border dark:border-dark-border">
        <div class="flex items-center gap-2">
          <Icon icon="lucide:bug" class="w-4 h-4 text-primary-from" />
          <span class="text-sm font-semibold text-light-text-primary dark:text-dark-text-primary">
            调试面板
          </span>
        </div>
        <div class="flex items-center gap-1">
          <button
            @click="testNotifications"
            class="px-2 py-1 text-xs text-primary-from hover:bg-primary-from/10 rounded transition-colors"
          >
            测试通知
          </button>
          <button
            @click="isExpanded = false"
            class="p-1 text-light-text-muted dark:text-dark-text-muted hover:text-light-text-primary dark:hover:text-dark-text-primary transition-colors"
          >
            <Icon icon="lucide:x" class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- 标签页 -->
      <div class="flex border-b border-light-border dark:border-dark-border">
        <button
          v-for="tab in ['state', 'actions', 'logs'] as const"
          :key="tab"
          @click="activeTab = tab"
          class="flex-1 px-3 py-2 text-xs font-medium capitalize transition-colors"
          :class="activeTab === tab
            ? 'text-primary-from border-b-2 border-primary-from'
            : 'text-light-text-muted dark:text-dark-text-muted hover:text-light-text-primary dark:hover:text-dark-text-primary'"
        >
          {{ tab === 'state' ? '状态' : tab === 'actions' ? '操作' : '日志' }}
        </button>
      </div>

      <!-- 内容区 -->
      <div class="flex-1 overflow-auto p-3 text-xs">
        <!-- 状态标签 -->
        <div v-if="activeTab === 'state'" class="space-y-3">
          <!-- 内容状态 -->
          <div class="space-y-1">
            <h3 class="font-semibold text-light-text-primary dark:text-dark-text-primary">内容</h3>
            <div class="grid grid-cols-2 gap-2 text-light-text-secondary dark:text-dark-text-secondary">
              <div>文章数: {{ contentStore.posts.length }}</div>
              <div>精选: {{ contentStore.featuredPosts.length }}</div>
              <div>加载中: {{ contentStore.loading }}</div>
              <div>错误: {{ contentStore.error || '无' }}</div>
            </div>
          </div>

          <!-- 认证状态 -->
          <div class="space-y-1">
            <h3 class="font-semibold text-light-text-primary dark:text-dark-text-primary">认证</h3>
            <div class="grid grid-cols-2 gap-2 text-light-text-secondary dark:text-dark-text-secondary">
              <div>已登录: {{ authStore.isLoggedIn }}</div>
              <div v-if="authStore.user">用户: {{ authStore.user.username }}</div>
              <div v-else>用户: 未登录</div>
            </div>
          </div>

          <!-- 主题状态 -->
          <div class="space-y-1">
            <h3 class="font-semibold text-light-text-primary dark:text-dark-text-primary">主题</h3>
            <div class="text-light-text-secondary dark:text-dark-text-secondary">
              当前: {{ themeStore.currentTheme }}
            </div>
          </div>

          <!-- 通知状态 -->
          <div class="space-y-1">
            <h3 class="font-semibold text-light-text-primary dark:text-dark-text-primary">通知</h3>
            <div class="text-light-text-secondary dark:text-dark-text-secondary">
              数量: {{ notificationStore.notifications.length }}
            </div>
          </div>
        </div>

        <!-- 操作标签 -->
        <div v-if="activeTab === 'actions'" class="space-y-2">
          <button
            @click="contentStore.loadAllContent()"
            class="w-full px-3 py-2 text-left rounded bg-light-surface dark:bg-dark-surface hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            重新加载内容
          </button>
          <button
            @click="authStore.fetchCurrentUser()"
            class="w-full px-3 py-2 text-left rounded bg-light-surface dark:bg-dark-surface hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            刷新用户信息
          </button>
          <button
            @click="themeStore.toggleTheme()"
            class="w-full px-3 py-2 text-left rounded bg-light-surface dark:bg-dark-surface hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            切换主题
          </button>
          <button
            @click="notificationStore.clearAll()"
            class="w-full px-3 py-2 text-left rounded bg-light-surface dark:bg-dark-surface hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            清空通知
          </button>
        </div>

        <!-- 日志标签 -->
        <div v-if="activeTab === 'logs'" class="space-y-1">
          <div class="flex items-center justify-between mb-2">
            <span class="text-light-text-secondary dark:text-dark-text-secondary">
              共 {{ debugLogs.length }} 条
            </span>
            <button
              @click="clearLogs"
              class="text-xs text-primary-from hover:underline"
            >
              清空
            </button>
          </div>
          <div class="space-y-1 max-h-[300px] overflow-auto">
            <div
              v-for="log in debugLogs.slice().reverse()"
              :key="log.timestamp"
              class="flex gap-2 text-xs font-mono"
            >
              <span class="text-light-text-muted dark:text-dark-text-muted flex-shrink-0">
                {{ formatTime(log.timestamp) }}
              </span>
              <span :class="logTypeColor(log.type)" class="flex-shrink-0">
                {{ log.type.toUpperCase() }}
              </span>
              <span class="text-light-text-secondary dark:text-dark-text-secondary break-all">
                {{ log.message }}
              </span>
            </div>
            <div v-if="debugLogs.length === 0" class="text-center text-light-text-muted dark:text-dark-text-muted py-4">
              暂无日志
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
