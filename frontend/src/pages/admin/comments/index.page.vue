<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { Icon } from '@iconify/vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import { commentService } from '@/api/services'
import type { Comment } from '@/api/types'
import { notifySuccess, notifyError } from '@/utils/notification'

const router = useRouter()

// 状态管理
const comments = ref<Comment[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

// 删除确认对话框
const showDeleteDialog = ref(false)
const deletingId = ref<number>(0)
const deletingCount = ref<number>(0)  // 将要删除的评论总数（包括子评论）

// 过滤器
const statusFilter = ref<'all' | 'pending' | 'approved' | 'spam'>('pending')

// 父评论缓存（用于显示回复上下文）
const parentCommentsCache = ref<Record<number, Comment>>({})

// 加载评论
const loadComments = async () => {
  loading.value = true
  error.value = null

  try {
    const params: any = {
      page: 1,
      page_size: 100,
    }

    // 根据过滤器设置状态
    if (statusFilter.value !== 'all') {
      params.status = statusFilter.value
    }

    const data = await commentService.getList(params)
    comments.value = data.results || []

    // 更新统计（基于当前加载的数据）
    updateStats()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载评论失败'
  } finally {
    loading.value = false
  }
}

// 统计数据（从后端加载）
const stats = ref({
  all: 0,
  pending: 0,
  approved: 0,
  spam: 0,
})

// 加载统计数据
const updateStats = async () => {
  try {
    // 加载所有评论的统计
    const allData = await commentService.getList({ page: 1, page_size: 1000 })
    const allComments = allData.results || []

    stats.value = {
      all: allComments.length,
      pending: allComments.filter(c => c.status === 'pending').length,
      approved: allComments.filter(c => c.status === 'approved').length,
      spam: allComments.filter(c => c.status === 'spam').length,
    }
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

// 初始化
onMounted(() => {
  loadComments()
  updateStats()
})

// 过滤后的评论列表（虽然 loadComments 已经过滤了，但为了保持模板一致性）
const filteredComments = computed(() => {
  return comments.value
})

// 切换过滤器并重新加载
const setFilterAndReload = (filter: 'all' | 'pending' | 'approved' | 'spam') => {
  statusFilter.value = filter
  // 使用 nextTick 确保 statusFilter 更新后再加载
  loadComments()
}

// 审核操作
const handleApprove = async (id: number) => {
  try {
    await commentService.approve(id)
    await loadComments()
    notifySuccess('评论已通过审核', '审核成功')
  } catch (e) {
    notifyError('操作失败，请重试', '操作失败')
  }
}

const handleMarkSpam = async (id: number) => {
  try {
    await commentService.markSpam(id)
    await loadComments()
    notifySuccess('评论已标记为垃圾评论', '操作成功')
  } catch (e) {
    notifyError('操作失败，请重试', '操作失败')
  }
}

// 显示删除确认对话框
const showDeleteConfirm = (id: number) => {
  deletingId.value = id
  // 计算将要删除的评论总数（包括所有子评论）
  const countReplies = (commentId: number): number => {
    let count = 0
    const children = comments.value.filter(c => c.parent === commentId)
    for (const child of children) {
      count += 1 + countReplies(child.id)
    }
    return count
  }
  deletingCount.value = 1 + countReplies(id)
  showDeleteDialog.value = true
}

// 确认删除
const handleDeleteConfirm = async () => {
  showDeleteDialog.value = false

  try {
    await commentService.delete(deletingId.value)
    await loadComments()
    notifySuccess('评论已删除', '删除成功')
  } catch (e) {
    notifyError('删除失败，请重试', '操作失败')
  } finally {
    deletingId.value = 0
  }
}

// 取消删除
const handleDeleteCancel = () => {
  showDeleteDialog.value = false
  deletingId.value = 0
}

// 状态徽章
const getStatusBadge = (status: string) => {
  const badges = {
    pending: {
      text: '待审核',
      class: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
    },
    approved: {
      text: '已通过',
      class: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
    },
    spam: {
      text: '垃圾评论',
      class: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
    },
  }
  return badges[status as keyof typeof badges] || badges.pending
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// 获取文章链接
const getArticleLink = (comment: Comment) => {
  const category = (comment as any).article_category
  const slug = (comment as any).article_slug

  if (!category || !slug) {
    return null
  }

  // 根据分类生成不同的路由
  const categoryRoutes: Record<string, string> = {
    blog: '/blog',
    projects: '/projects',
    life: '/life',
    notes: '/notes',
  }

  const basePath = categoryRoutes[category] || '/blog'
  return `${basePath}/${slug}`
}

// 获取父评论（用于显示回复上下文）
const getParentComment = async (parentId: number) => {
  if (parentCommentsCache.value[parentId]) {
    return parentCommentsCache.value[parentId]
  }

  try {
    const parentComment = await commentService.getDetail(parentId)
    parentCommentsCache.value[parentId] = parentComment
    return parentComment
  } catch (e) {
    console.error('Failed to load parent comment:', e)
    return null
  }
}

// 显示父评论（带加载状态）
const showParentComment = ref<Record<number, boolean>>({})
const loadingParent = ref<Record<number, boolean>>({})

const toggleParentComment = async (comment: Comment) => {
  const parentId = comment.parent
  if (!parentId) return

  const commentId = comment.id

  // 如果已经显示，则隐藏
  if (showParentComment.value[commentId]) {
    showParentComment.value[commentId] = false
    return
  }

  // 显示加载状态
  loadingParent.value[commentId] = true
  showParentComment.value[commentId] = true

  // 加载父评论
  await getParentComment(parentId)

  loadingParent.value[commentId] = false
}

// 获取子评论数量
const getRepliesCount = (commentId: number) => {
  return comments.value.filter(c => c.parent === commentId).length
}

// 获取文章分类显示名称
const getCategoryName = (category: string) => {
  const names: Record<string, string> = {
    blog: '文章',
    projects: '项目',
    life: '生活记录',
    notes: '笔记',
  }
  return names[category] || category
}

// 获取文章标题
const getArticleTitle = (comment: Comment) => {
  return (comment as any).article_title || '未知文章'
}

// 跳转到文章编辑页面
const handleEditArticle = (comment: Comment) => {
  const slug = (comment as any).article_slug
  const category = (comment as any).article_category

  if (!slug) return

  const categoryRoutes: Record<string, string> = {
    blog: '/admin/posts',
    projects: '/admin/projects',
    life: '/admin/life',
    notes: '/admin/notes',
  }

  const basePath = categoryRoutes[category] || '/admin/posts'
  router.push(`${basePath}/${slug}`)
}

// 获取评论者显示名称
const getCommenterName = (comment: Comment) => {
  if (comment.author) {
    return comment.author.nickname || comment.author.username
  }
  return comment.guest_name || '访客'
}

// 获取评论者邮箱
const getCommenterEmail = (comment: Comment) => {
  if (comment.author) {
    return comment.author.email
  }
  return comment.guest_email
}

// 安全获取首字母（用于头像）
const getAvatarLetter = (name: string | undefined) => {
  if (!name || typeof name !== 'string') {
    return 'U'
  }
  const firstChar = name.charAt(0)
  return firstChar ? firstChar.toUpperCase() : 'U'
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- 标题和统计 -->
      <ScrollReveal>
        <div>
          <h1 class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-2">
            评论管理
          </h1>
          <p class="text-light-text-secondary dark:text-dark-text-secondary mb-6">
            管理和审核用户评论
          </p>

          <!-- 统计卡片 -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div
              @click="setFilterAndReload('all')"
              class="card p-4 cursor-pointer hover:shadow-lg transition-shadow"
              :class="statusFilter === 'all' ? 'ring-2 ring-primary-from' : ''"
            >
              <div class="text-2xl font-bold text-light-text-primary dark:text-dark-text-primary">
                {{ stats.all }}
              </div>
              <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
                全部
              </div>
            </div>

            <div
              @click="setFilterAndReload('pending')"
              class="card p-4 cursor-pointer hover:shadow-lg transition-shadow"
              :class="statusFilter === 'pending' ? 'ring-2 ring-yellow-500' : ''"
            >
              <div class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                {{ stats.pending }}
              </div>
              <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
                待审核
              </div>
            </div>

            <div
              @click="setFilterAndReload('approved')"
              class="card p-4 cursor-pointer hover:shadow-lg transition-shadow"
              :class="statusFilter === 'approved' ? 'ring-2 ring-green-500' : ''"
            >
              <div class="text-2xl font-bold text-green-600 dark:text-green-400">
                {{ stats.approved }}
              </div>
              <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
                已通过
              </div>
            </div>

            <div
              @click="setFilterAndReload('spam')"
              class="card p-4 cursor-pointer hover:shadow-lg transition-shadow"
              :class="statusFilter === 'spam' ? 'ring-2 ring-red-500' : ''"
            >
              <div class="text-2xl font-bold text-red-600 dark:text-red-400">
                {{ stats.spam }}
              </div>
              <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
                垃圾评论
              </div>
            </div>
          </div>
        </div>
      </ScrollReveal>

      <!-- 评论列表 -->
      <ScrollReveal class="delay-100">
        <div class="card">
          <!-- 加载状态 -->
          <div v-if="loading" class="p-12 text-center">
            <Icon icon="lucide:loader-2" class="w-8 h-8 animate-spin mx-auto mb-4 text-primary-from" />
            <p class="text-light-text-secondary dark:text-dark-text-secondary">加载中...</p>
          </div>

          <!-- 错误状态 -->
          <div v-else-if="error" class="p-12 text-center">
            <Icon icon="lucide:alert-circle" class="w-12 h-12 mx-auto mb-4 text-red-500" />
            <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-2">
              加载失败
            </h2>
            <p class="text-light-text-secondary dark:text-dark-text-secondary mb-6">
              {{ error }}
            </p>
            <button
              @click="loadComments"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90 transition-opacity"
            >
              <Icon icon="lucide:refresh-cw" class="w-4 h-4" />
              重试
            </button>
          </div>

          <!-- 评论列表 -->
          <div v-else-if="filteredComments.length > 0" class="divide-y divide-light-border dark:divide-dark-border">
            <div
              v-for="comment in filteredComments"
              :key="comment.id"
              class="p-6 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <div class="flex gap-4">
                <!-- 头像 -->
                <div class="flex-shrink-0">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-from to-primary-to flex items-center justify-center text-white font-bold">
                    {{ getAvatarLetter(getCommenterName(comment)) }}
                  </div>
                </div>

                <!-- 内容 -->
                <div class="flex-1 min-w-0">
                  <!-- 头部信息 -->
                  <div class="flex flex-wrap items-center gap-x-2 gap-y-1 mb-2">
                    <span class="font-medium text-light-text-primary dark:text-dark-text-primary">
                      {{ getCommenterName(comment) }}
                    </span>
                    <span v-if="getCommenterEmail(comment)" class="text-sm text-light-text-muted dark:text-dark-text-muted">
                      &lt;{{ getCommenterEmail(comment) }}&gt;
                    </span>
                    <span class="text-sm text-light-text-muted dark:text-dark-text-muted">
                      {{ formatDate(comment.created_at) }}
                    </span>
                    <span
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                      :class="getStatusBadge(comment.status).class"
                    >
                      {{ getStatusBadge(comment.status).text }}
                    </span>
                    <!-- 子评论数量 -->
                    <span
                      v-if="getRepliesCount(comment.id) > 0"
                      class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                    >
                      <Icon icon="lucide:message-square" class="w-3 h-3" />
                      {{ getRepliesCount(comment.id) }} 条回复
                    </span>
                  </div>

                  <!-- 评论内容 -->
                  <p class="text-light-text-secondary dark:text-dark-text-secondary mb-3 whitespace-pre-wrap">
                    {{ comment.content }}
                  </p>

                  <!-- 父评论上下文（如果是回复） -->
                  <div v-if="comment.parent" class="mb-3">
                    <button
                      @click="toggleParentComment(comment)"
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-900/20
                             hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors
                             text-sm text-blue-700 dark:text-blue-400 font-medium"
                    >
                      <Icon icon="lucide:corner-up-left" class="w-4 h-4" />
                      {{ showParentComment[comment.id] ? '隐藏' : '查看' }}被回复的评论
                    </button>

                    <!-- 父评论内容 -->
                    <div
                      v-if="showParentComment[comment.id]"
                      class="mt-2 p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50 border-l-4 border-blue-500"
                    >
                      <div v-if="loadingParent[comment.id]" class="flex items-center gap-2 text-sm text-light-text-muted">
                        <Icon icon="lucide:loader-2" class="w-4 h-4 animate-spin" />
                        加载中...
                      </div>
                      <div v-else-if="parentCommentsCache[comment.parent]">
                        <div class="flex items-center gap-2 mb-2">
                          <span class="font-medium text-light-text-primary dark:text-dark-text-primary text-sm">
                            {{ getCommenterName(parentCommentsCache[comment.parent]) }}
                          </span>
                          <span class="text-xs text-light-text-muted dark:text-dark-text-muted">
                            {{ formatDate(parentCommentsCache[comment.parent].created_at) }}
                          </span>
                        </div>
                        <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary whitespace-pre-wrap">
                          {{ parentCommentsCache[comment.parent].content }}
                        </p>
                      </div>
                      <div v-else class="text-sm text-red-600 dark:text-red-400">
                        无法加载父评论
                      </div>
                    </div>
                  </div>

                  <!-- 文章信息 -->
                  <div class="flex items-center gap-2 flex-wrap mb-3">
                    <!-- 查看原文按钮 -->
                    <a
                      v-if="getArticleLink(comment)"
                      :href="getArticleLink(comment)"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800
                             hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors
                             text-sm text-light-text-primary dark:text-dark-text-primary
                             hover:text-primary-from dark:hover:text-primary-to"
                    >
                      <Icon icon="lucide:external-link" class="w-4 h-4" />
                      查看原文
                    </a>
                  </div>

                  <!-- 文章编辑链接 -->
                  <div class="flex items-center gap-2 flex-wrap">
                    <button
                      @click="handleEditArticle(comment)"
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800
                             hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors
                             text-sm text-light-text-primary dark:text-dark-text-primary
                             hover:text-primary-from dark:hover:text-primary-to"
                    >
                      <Icon icon="lucide:edit" class="w-4 h-4" />
                      <span class="font-medium">{{ getArticleTitle(comment) }}</span>
                    </button>
                    <span
                      v-if="(comment as any).article_category"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
                             bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400"
                    >
                      {{ getCategoryName((comment as any).article_category) }}
                    </span>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="flex items-center gap-2 mt-4">
                    <!-- 待审核评论：通过、垃圾、删除 -->
                    <template v-if="comment.status === 'pending'">
                      <button
                        @click="handleApprove(comment.id)"
                        class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400 dark:hover:bg-green-900/50 transition-colors text-sm font-medium"
                      >
                        <Icon icon="lucide:check" class="w-4 h-4" />
                        通过
                      </button>
                      <button
                        @click="handleMarkSpam(comment.id)"
                        class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50 transition-colors text-sm font-medium"
                      >
                        <Icon icon="lucide:alert-triangle" class="w-4 h-4" />
                        垃圾
                      </button>
                      <button
                        @click="showDeleteConfirm(comment.id)"
                        class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/30 transition-colors text-sm font-medium"
                      >
                        <Icon icon="lucide:trash-2" class="w-4 h-4" />
                        删除
                      </button>
                    </template>

                    <!-- 已通过评论：垃圾、删除 -->
                    <template v-if="comment.status === 'approved'">
                      <button
                        @click="handleMarkSpam(comment.id)"
                        class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50 transition-colors text-sm font-medium"
                      >
                        <Icon icon="lucide:alert-triangle" class="w-4 h-4" />
                        垃圾
                      </button>
                      <button
                        @click="showDeleteConfirm(comment.id)"
                        class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/30 transition-colors text-sm font-medium"
                      >
                        <Icon icon="lucide:trash-2" class="w-4 h-4" />
                        删除
                      </button>
                    </template>

                    <!-- 垃圾评论：通过、删除 -->
                    <template v-if="comment.status === 'spam'">
                      <button
                        @click="handleApprove(comment.id)"
                        class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400 dark:hover:bg-green-900/50 transition-colors text-sm font-medium"
                      >
                        <Icon icon="lucide:check" class="w-4 h-4" />
                        通过
                      </button>
                      <button
                        @click="showDeleteConfirm(comment.id)"
                        class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/30 transition-colors text-sm font-medium"
                      >
                        <Icon icon="lucide:trash-2" class="w-4 h-4" />
                        删除
                      </button>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else class="p-12 text-center">
            <Icon icon="lucide:message-square" class="w-16 h-16 mx-auto mb-4 text-light-text-muted dark:text-dark-text-muted" />
            <h3 class="text-lg font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
              暂无评论
            </h3>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              当前筛选条件下没有评论
            </p>
          </div>
        </div>
      </ScrollReveal>
    </div>

    <!-- 删除确认对话框 -->
    <ConfirmDialog
      :show="showDeleteDialog"
      title="删除评论"
      :message="deletingCount > 1 ? `确定要删除这条评论吗？这将同时删除 ${deletingCount} 条评论（包括所有子回复），此操作无法撤销。` : '确定要删除这条评论吗？此操作无法撤销。'"
      confirm-text="删除"
      cancel-text="取消"
      type="danger"
      @confirm="handleDeleteConfirm"
      @cancel="handleDeleteCancel"
    />
  </AdminLayout>
</template>
