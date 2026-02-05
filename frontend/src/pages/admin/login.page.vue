<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.api'
import { Icon } from '@iconify/vue'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('admin')
const password = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

const handleLogin = async () => {
  errorMessage.value = ''
  isSubmitting.value = true

  try {
    const success = await authStore.login(username.value, password.value)

    if (success) {
      await router.push('/admin')
    } else {
      errorMessage.value = authStore.error || '登录失败，请检查用户名和密码'
      isSubmitting.value = false
    }
  } catch (error) {
    console.error('登录错误:', error)
    errorMessage.value = '登录过程中发生错误: ' + (error as Error).message
    isSubmitting.value = false
  }

  // 确保无论如何都重置 loading 状态
  setTimeout(() => {
    if (isSubmitting.value) {
      isSubmitting.value = false
    }
  }, 5000)
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-from/10 to-primary-to/10
              dark:from-gray-900 dark:to-gray-800 px-4">
    <div class="max-w-md w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-2">
          Nano Banana
        </h1>
        <p class="text-light-text-secondary dark:text-dark-text-secondary">
          后台管理系统
        </p>
      </div>

      <!-- 登录卡片 -->
      <div class="card p-8">
        <h2 class="text-2xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-6">
          管理员登录
        </h2>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- 用户名输入 -->
          <div>
            <label for="username" class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
              用户名
            </label>
            <div class="relative">
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="请输入用户名"
                class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from"
                :disabled="isSubmitting"
                required
              />
              <Icon
                icon="lucide:user"
                class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-light-text-muted dark:text-dark-text-muted"
              />
            </div>
          </div>

          <!-- 密码输入 -->
          <div>
            <label for="password" class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
              密码
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                type="password"
                placeholder="请输入密码"
                class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from"
                :disabled="isSubmitting"
                required
              />
              <Icon
                icon="lucide:lock"
                class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-light-text-muted dark:text-dark-text-muted"
              />
            </div>
            <p class="mt-2 text-xs text-light-text-muted dark:text-dark-text-muted">
              默认凭据: admin / admin123
            </p>
          </div>

          <!-- 错误提示 -->
          <div v-if="errorMessage" class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
            {{ errorMessage }}
          </div>

          <!-- 提交按钮 -->
          <button
            type="submit"
            :disabled="isSubmitting || !username || !password"
            class="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-primary-from to-primary-to
                   text-white font-medium
                   hover:opacity-90 transition-opacity
                   disabled:opacity-50 disabled:cursor-not-allowed
                   flex items-center justify-center gap-2"
          >
            <Icon
              v-if="isSubmitting"
              icon="lucide:loader-2"
              class="w-5 h-5 animate-spin"
            />
            <Icon v-else icon="lucide:log-in" class="w-5 h-5" />
            {{ isSubmitting ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- 提示信息 -->
        <div class="mt-6 pt-6 border-t border-light-border dark:border-dark-border">
          <p class="text-sm text-light-text-muted dark:text-dark-text-muted text-center">
            使用 JWT 认证访问后端 API
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
