<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { commentService } from '@/api/services'
import type { Comment } from '@/api/types'
import { notifyError, notifySuccess } from '@/utils/notification'
import CommentItem from './CommentItem.vue'

const props = defineProps<{
  articleId: number
}>()

// 本地存储键
const STORAGE_KEY = 'comment_user_info'

// 状态管理
const comments = ref<Comment[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

// 用户信息（从本地存储加载）
const userInfo = ref<{ name: string; email: string }>({
  name: '',
  email: ''
})

// 加载用户信息
onMounted(() => {
  const savedInfo = localStorage.getItem(STORAGE_KEY)
  if (savedInfo) {
    try {
      userInfo.value = JSON.parse(savedInfo)
    } catch (e) {
      // 忽略解析错误
    }
  }
  loadComments()
})

// 加载评论列表
const loadComments = async () => {
  loading.value = true
  error.value = null

  try {
    // 明确指定只加载已审核通过的评论
    const data = await commentService.getList({
      article: props.articleId,
      status: 'approved',  // 只显示已审核通过的评论
      page: 1,
      page_size: 100  // 获取更多评论以支持嵌套
    })

    // 获取所有评论（包括回复）
    const allComments = data.results || []

    // 缓存所有评论供 CommentItem 使用
    allCommentsCache.value = allComments

  } catch (e) {
    notifyError('加载评论失败，请稍后重试', '加载失败')
    error.value = e instanceof Error ? e.message : '加载评论失败'
  } finally {
    loading.value = false
  }
}

// 缓存所有评论（供递归组件使用）
const allCommentsCache = ref<Comment[]>([])

// 处理回复提交
const handleSubmitReply = async (commentId: number, content: string) => {
  // 检查是否有用户信息
  if (!userInfo.value.name || !userInfo.value.email) {
    notifyError('请先在上方评论框中填写您的姓名和邮箱', '需要完善信息')
    return
  }

  const payload = {
    article: props.articleId,
    parent: commentId,
    guest_name: userInfo.value.name,
    guest_email: userInfo.value.email,
    content
  }

  console.log('提交回复数据:', payload)

  loading.value = true
  try {
    const result = await commentService.create(payload)
    console.log('回复创建结果:', result)

    // 重新加载评论
    await loadComments()
    notifySuccess('回复成功，待审核！', '成功')
  } catch (e) {
    console.error('回复失败:', e)
    notifyError('回复失败，请稍后重试', '回复失败')
  } finally {
    loading.value = false
  }
}

// 获取顶级评论（用于模板循环）
const topLevelComments = computed(() => {
  return allCommentsCache.value.filter(c => !c.parent)
})
</script>

<template>
  <div class="space-y-6">
    <!-- 评论标题 -->
    <div class="flex items-center gap-2 mb-6">
      <Icon icon="lucide:message-square" class="w-6 h-6 text-primary-from" />
      <h2 class="text-2xl font-bold text-light-text-primary dark:text-dark-text-primary">
        评论 ({{ topLevelComments.length }})
      </h2>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <Icon icon="lucide:loader-2" class="w-6 h-6 animate-spin text-primary-from" />
      <span class="ml-2 text-light-text-secondary dark:text-dark-text-secondary">加载评论中...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="text-center py-8">
      <Icon icon="lucide:alert-circle" class="w-12 h-12 mx-auto mb-2 text-red-500" />
      <p class="text-light-text-secondary dark:text-dark-text-secondary">{{ error }}</p>
    </div>

    <!-- 评论列表（使用递归组件） -->
    <div v-else-if="topLevelComments.length > 0" class="space-y-6">
      <CommentItem
        v-for="comment in topLevelComments"
        :key="comment.id"
        :comment="comment"
        :level="0"
        :all-comments="allCommentsCache"
        :article-id="articleId"
        :user-info="userInfo"
        @submit-reply="handleSubmitReply"
      />
    </div>

    <!-- 空状态 -->
    <div v-else class="text-center py-12">
      <Icon icon="lucide:message-square" class="w-16 h-16 mx-auto mb-4 text-light-text-muted dark:text-dark-text-muted" />
      <p class="text-light-text-secondary dark:text-dark-text-secondary mb-2">
        还没有评论
      </p>
      <p class="text-sm text-light-text-muted dark:text-dark-text-muted">
        成为第一个发表评论的人吧！
      </p>
    </div>
  </div>
</template>

<style scoped>
/* 递归组件样式 */
</style>
