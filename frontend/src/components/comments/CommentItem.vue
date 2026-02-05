<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import type { Comment } from '@/api/types'

const props = defineProps<{
  comment: Comment
  level?: number  // 层级深度，用于限制嵌套和样式
  allComments?: Comment[]  // 所有评论（用于查找嵌套回复）
  articleId?: number  // 文章ID，用于提交回复
  showReplyBox?: boolean  // 是否显示回复框
  userInfo?: { name: string; email: string }  // 用户信息
}>()

const emit = defineEmits<{
  reply: [commentId: number, authorName: string]
  submitReply: [commentId: number, content: string]
}>()

// 层级深度限制（超过这个层级会折叠）
const MAX_NESTED_LEVEL = 5
const COLLAPSE_LEVEL = 3  // 超过3层自动折叠

// 是否折叠深层回复
const collapseDeep = ref(props.level || 0 >= COLLAPSE_LEVEL)

// 回复输入框状态
const replyContent = ref('')
const showReplyInput = ref(false)

// 计算属性：获取该评论的所有直接回复
const directReplies = computed(() => {
  if (!props.allComments) return []

  return props.allComments.filter(c => c.parent === props.comment.id)
})

// 计算属性：是否有深层回复（用于显示"查看更多"）
const hasDeepReplies = computed(() => {
  return directReplies.value.length > 0 ||
         (props.level || 0) < MAX_NESTED_LEVEL
})

// 切换折叠状态
const toggleCollapse = () => {
  collapseDeep.value = !collapseDeep.value
}

// 格式化时间
const formatTime = (dateStr: string | undefined) => {
  if (!dateStr) return '未知时间'

  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '未知时间'

  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`

  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// 获取作者名称
const getAuthorName = (comment: Comment) => {
  if (!comment) return '访客'

  const guestName = (comment as any).guest_name
  if (guestName && typeof guestName === 'string' && guestName.trim()) {
    return guestName
  }

  const author = (comment as any).author
  if (author && author.id) {
    const name = author.nickname || author.username || '访客'
    return name && typeof name === 'string' ? name : '访客'
  }

  return '访客'
}

// 获取首字母（头像）
const getAvatarLetter = (name: string | undefined) => {
  if (!name || typeof name !== 'string') {
    return 'V'
  }
  const firstChar = name.charAt(0)
  return firstChar ? firstChar.toUpperCase() : 'V'
}

// 处理回复点击
const handleReply = () => {
  showReplyInput.value = !showReplyInput.value
  if (showReplyInput.value) {
    // 聚焦到输入框
    setTimeout(() => {
      const textarea = document.getElementById(`reply-input-${props.comment.id}`)
      textarea?.focus()
    }, 100)
  }
}

// 提交回复
const handleSubmitReply = () => {
  if (!replyContent.value.trim()) return

  if (!props.userInfo?.name || !props.userInfo?.email) {
    alert('请先在上方评论框中填写您的姓名和邮箱')
    return
  }

  emit('submitReply', props.comment.id, replyContent.value)
  replyContent.value = ''
  showReplyInput.value = false
}

// 取消回复
const cancelReply = () => {
  replyContent.value = ''
  showReplyInput.value = false
}

// 动态缩进样式
const indentStyle = computed(() => {
  const level = props.level || 0
  if (level === 0) return ''

  // 每层缩进
  const indent = level * 16
  return `margin-left: ${indent}px;`
})
</script>

<template>
  <div class="comment-item" :style="indentStyle">
    <!-- 主评论 -->
    <div :class="['card p-4 transition-all', level > 0 ? 'bg-gray-50 dark:bg-gray-800/50' : '']">
      <div class="flex gap-3">
        <!-- 头像 -->
        <div class="flex-shrink-0">
          <div
            :class="[
              'rounded-full flex items-center justify-center text-white font-bold',
              level === 0 ? 'w-10 h-10 bg-gradient-to-br from-primary-from to-primary-to' : 'w-8 h-8 bg-gradient-to-br from-gray-400 to-gray-500'
            ]"
          >
            {{ getAvatarLetter(getAuthorName(comment)) }}
          </div>
        </div>

        <!-- 内容 -->
        <div class="flex-1 min-w-0">
          <!-- 头部信息 -->
          <div class="flex items-center gap-2 mb-2 flex-wrap">
            <span :class="['font-medium text-light-text-primary dark:text-dark-text-primary', level === 0 ? '' : 'text-sm']">
              {{ getAuthorName(comment) }}
            </span>
            <span :class="['text-light-text-muted dark:text-dark-text-muted', level === 0 ? 'text-sm' : 'text-xs']">
              {{ formatTime(comment.created_at) }}
            </span>
            <!-- 层级指示器 -->
            <BaseBadge
              v-if="level > 0"
              variant="gray"
              size="sm"
            >
              {{ level + 1 }}级
            </BaseBadge>
          </div>

          <!-- 评论内容 -->
          <div
            :class="['text-light-text-secondary dark:text-dark-text-secondary whitespace-pre-wrap', level === 0 ? 'mb-3' : 'mb-2 text-sm']"
          >
            {{ comment.content }}
          </div>

          <!-- 操作按钮 -->
          <div :class="['flex items-center gap-3', level === 0 ? 'text-sm' : 'text-xs']">
            <button
              @click="handleReply"
              class="flex items-center gap-1 text-light-text-muted dark:text-dark-text-muted
                     hover:text-primary-from dark:hover:text-primary-to transition-colors"
            >
              <Icon icon="lucide:corner-up-left" :class="level === 0 ? 'w-4 h-4' : 'w-3 h-3'" />
              {{ showReplyInput ? '取消' : '回复' }}
            </button>
            <!-- 显示回复数 -->
            <span
              v-if="directReplies.length > 0"
              class="text-light-text-muted dark:text-dark-text-muted"
            >
              {{ directReplies.length }} 条回复
            </span>
          </div>

          <!-- 回复输入框（直接在评论下方） -->
          <div v-if="showReplyInput" class="mt-3">
            <div class="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 space-y-3">
              <!-- 回复目标提示 -->
              <div class="flex items-center justify-between text-sm">
                <span class="text-light-text-secondary dark:text-dark-text-secondary">
                  回复 <span class="font-medium text-primary-from">@{{ getAuthorName(comment) }}</span>
                </span>
              </div>
              <textarea
                :id="`reply-input-${comment.id}`"
                v-model="replyContent"
                rows="3"
                :placeholder="`写下你对 @${getAuthorName(comment)} 的回复...`"
                class="w-full px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from
                       resize-y"
              />
              <div class="flex gap-2">
                <button
                  @click="handleSubmitReply"
                  :disabled="!replyContent?.trim()"
                  class="px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90
                         disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  发送
                </button>
                <button
                  @click="cancelReply"
                  class="px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                         text-light-text-primary dark:text-dark-text-primary
                         hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 子回复（递归渲染） -->
    <div v-if="directReplies.length > 0" class="mt-2">
      <!-- 深层折叠提示 -->
      <div
        v-if="collapseDeep && level < MAX_NESTED_LEVEL"
        class="mt-2"
      >
        <button
          @click="toggleCollapse"
          class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
                 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400
                 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors
                 text-sm font-medium"
        >
          <Icon icon="lucide:chevron-down" class="w-4 h-4" />
          查看更多回复 ({{ directReplies.length }})
        </button>
      </div>

      <!-- 显示子回复 -->
      <template v-if="!collapseDeep || level >= MAX_NESTED_LEVEL">
        <CommentItem
          v-for="reply in directReplies"
          :key="reply.id"
          :comment="reply"
          :level="(level || 0) + 1"
          :all-comments="allComments"
          :article-id="articleId"
          :user-info="userInfo"
          @submit-reply="(id, content) => emit('submitReply', id, content)"
        />
      </template>

      <!-- 折叠时显示"收起"按钮 -->
      <div
        v-if="!collapseDeep && level < COLLAPSE_LEVEL && directReplies.length > 0"
        class="mt-2"
      >
        <button
          @click="toggleCollapse"
          class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
                 text-light-text-muted dark:text-dark-text-muted
                 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors
                 text-sm"
        >
          <Icon icon="lucide:chevron-up" class="w-4 h-4" />
          收起回复
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comment-item {
  border-left: 2px solid transparent;
}

.comment-item:hover {
  border-left-color: rgb(96 165 250 / 0.3);
}
</style>
