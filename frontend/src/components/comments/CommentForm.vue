<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { commentService } from '@/api/services'

const props = defineProps<{
  articleId: number
}>()

const emit = defineEmits<{
  (event: 'submitted'): void
}>()

// 本地存储键
const STORAGE_KEY = 'comment_user_info'

// 表单数据
const form = ref({
  name: '',
  email: '',
  content: ''
})

// 提交状态
const isSubmitting = ref(false)
const submitSuccess = ref(false)
const submitError = ref('')

// 组件挂载时加载保存的用户信息
onMounted(() => {
  try {
    const savedInfo = localStorage.getItem(STORAGE_KEY)
    if (savedInfo) {
      const info = JSON.parse(savedInfo)
      form.value.name = info.name || ''
      form.value.email = info.email || ''
    }
  } catch (e) {
    // 忽略解析错误
  }
})

// 实时保存用户信息（姓名和邮箱）
watch(() => form.value.name, (newName) => {
  if (newName.trim()) {
    saveUserInfo()
  }
})

watch(() => form.value.email, (newEmail) => {
  if (newEmail.trim() && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmail)) {
    saveUserInfo()
  }
})

// 保存用户信息到 localStorage
const saveUserInfo = () => {
  try {
    const userInfo = {
      name: form.value.name,
      email: form.value.email
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(userInfo))
  } catch (e) {
    // 忽略保存错误
  }
}

// 表单验证
const validateForm = (): boolean => {
  if (!form.value.name.trim()) {
    submitError.value = '请输入您的名称'
    return false
  }
  if (!form.value.email.trim()) {
    submitError.value = '请输入您的邮箱'
    return false
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    submitError.value = '请输入有效的邮箱地址'
    return false
  }
  if (!form.value.content.trim()) {
    submitError.value = '请输入评论内容'
    return false
  }
  return true
}

// 提交评论
const handleSubmit = async () => {
  submitError.value = ''

  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    await commentService.create({
      article: props.articleId,
      guest_name: form.value.name,
      guest_email: form.value.email,
      content: form.value.content
    })

    submitSuccess.value = true

    // 保存用户信息（姓名和邮箱）以便下次使用
    saveUserInfo()

    // 只清空评论内容，保留用户信息
    form.value.content = ''

    // 3秒后隐藏成功消息
    setTimeout(() => {
      submitSuccess.value = false
    }, 3000)

    // 通知父组件
    emit('submitted')
  } catch (error: any) {
    submitError.value = error.message || '提交失败，请稍后重试'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="card p-6">
    <h3 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-4">
      发表评论
    </h3>

    <!-- 成功提示 -->
    <div v-if="submitSuccess" class="mb-4 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
      <div class="flex items-center gap-2 text-green-600 dark:text-green-400">
        <Icon icon="lucide:check-circle" class="w-5 h-5" />
        <span>评论提交成功！审核通过后将显示。</span>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="submitError" class="mb-4 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
      <div class="flex items-center gap-2 text-red-600 dark:text-red-400">
        <Icon icon="lucide:alert-circle" class="w-5 h-5" />
        <span>{{ submitError }}</span>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- 名称 -->
      <div>
        <label for="name" class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
          名称 <span class="text-red-500">*</span>
        </label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          placeholder="请输入您的名称"
          class="w-full px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                 bg-white dark:bg-gray-800
                 text-light-text-primary dark:text-dark-text-primary
                 placeholder-light-text-muted dark:placeholder-dark-text-muted
                 focus:outline-none focus:ring-2 focus:ring-primary-from
                 transition-colors"
          :disabled="isSubmitting"
        />
      </div>

      <!-- 邮箱 -->
      <div>
        <label for="email" class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
          电子邮箱 <span class="text-red-500">*</span>
        </label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          placeholder="your@email.com"
          class="w-full px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                 bg-white dark:bg-gray-800
                 text-light-text-primary dark:text-dark-text-primary
                 placeholder-light-text-muted dark:placeholder-dark-text-muted
                 focus:outline-none focus:ring-2 focus:ring-primary-from
                 transition-colors"
          :disabled="isSubmitting"
        />
      </div>

      <!-- 评论内容 -->
      <div>
        <label for="content" class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
          评论内容 <span class="text-red-500">*</span>
        </label>
        <textarea
          id="content"
          v-model="form.content"
          rows="5"
          placeholder="请输入您的评论..."
          class="w-full px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                 bg-white dark:bg-gray-800
                 text-light-text-primary dark:text-dark-text-primary
                 placeholder-light-text-muted dark:placeholder-dark-text-muted
                 focus:outline-none focus:ring-2 focus:ring-primary-from
                 resize-y
                 transition-colors"
          :disabled="isSubmitting"
        ></textarea>
      </div>

      <!-- 提交按钮 -->
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full sm:w-auto px-6 py-3 rounded-lg bg-gradient-to-r from-primary-from to-primary-to
               text-white font-medium hover:opacity-90 transition-opacity
               disabled:opacity-50 disabled:cursor-not-allowed
               flex items-center justify-center gap-2"
      >
        <Icon v-if="isSubmitting" icon="lucide:loader-2" class="w-5 h-5 animate-spin" />
        <Icon v-else icon="lucide:send" class="w-5 h-5" />
        <span>{{ isSubmitting ? '提交中...' : '提交评论' }}</span>
      </button>
    </form>

    <p class="mt-4 text-xs text-light-text-muted dark:text-dark-text-muted">
      <Icon icon="lucide:info" class="w-4 h-4 inline mr-1" />
      您的邮箱地址不会被公开，所有评论将在审核后显示。
    </p>
  </div>
</template>
