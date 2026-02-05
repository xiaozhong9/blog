<script setup lang="ts">
import { ref, computed, onBeforeMount } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { useAdminContentStore } from '@/stores/content.admin'
import { Icon } from '@iconify/vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import { notifySuccess, notifyError } from '@/utils/notification'

const router = useRouter()
const adminContentStore = useAdminContentStore()

// 分页和搜索状态
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const statusFilter = ref<'all' | 'draft' | 'published' | 'featured'>('all')

// 存储每个文章的切换状态
const togglingStatus = ref<Record<string, boolean>>({})

// 删除确认对话框
const showDeleteDialog = ref(false)
const deletingSlug = ref<string>('')

// 加载数据函数
const loadPosts = async () => {
  await adminContentStore.loadPostsByCategory('blog')
}

// 每次进入页面时加载数据
onBeforeMount(loadPosts)

// 过滤后的文章
const filteredPosts = computed(() => {
  let posts = adminContentStore.posts

  // 状态过滤
  if (statusFilter.value === 'draft') {
    posts = posts.filter(p => p.draft)
  } else if (statusFilter.value === 'published') {
    posts = posts.filter(p => !p.draft)
  } else if (statusFilter.value === 'featured') {
    posts = posts.filter(p => p.featured && !p.draft)
  }

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    posts = posts.filter(p =>
      p.title.toLowerCase().includes(query) ||
      p.description.toLowerCase().includes(query)
    )
  }

  return posts
})

// 文章列表（分页）
const posts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPosts.value.slice(start, end)
})

// 分页信息
const total = computed(() => filteredPosts.value.length)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 显示删除确认对话框
const showDeleteConfirm = (slug: string) => {
  deletingSlug.value = slug
  showDeleteDialog.value = true
}

// 确认删除
const handleDeleteConfirm = async () => {
  const slugToDelete = deletingSlug.value
  showDeleteDialog.value = false

  try {
    // 调用删除 API
    await adminContentStore.deletePost(slugToDelete)
    // 删除成功后重新加载数据（确保从服务器获取最新状态）
    await loadPosts()
    // 如果当前页没有数据了，返回上一页
    if (posts.value.length === 0 && currentPage.value > 1) {
      currentPage.value--
    }
    notifySuccess('文章已删除', '删除成功')
  } catch (error: any) {
    // 显示详细错误信息
    const errorMessage = error?.message || error?.detail || '删除失败，请重试'
    notifyError(errorMessage, '操作失败')
  } finally {
    deletingSlug.value = ''
  }
}

// 取消删除
const handleDeleteCancel = () => {
  showDeleteDialog.value = false
  deletingSlug.value = ''
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1 // 搜索时重置到第一页
}

// 清空搜索
const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// 分页按钮点击
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 切换草稿/发布状态
const handleToggleDraft = async (post: { slug: string; title: string; draft?: boolean }) => {
  const currentDraft = post.draft || false

  // 防止重复点击
  if (togglingStatus.value[post.slug]) {
    return
  }

  togglingStatus.value[post.slug] = true

  try {
    await adminContentStore.updatePost(post.slug, { draft: !currentDraft })

    // 更清晰的提示信息
    if (!currentDraft) {
      // 从草稿 → 已发布
      notifySuccess('文章已设置为草稿', '发布成功')
    } else {
      // 从已发布 → 草稿
      notifySuccess('文章已发布', '操作成功')
    }
  } catch (error) {
    notifyError('操作失败，请重试', '操作失败')
  } finally {
    togglingStatus.value[post.slug] = false
  }
}

// 在当前页面打开查看文章
const handleViewPost = (slug: string) => {
  router.push(`/blog/${slug}`)
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- 标题和操作 -->
      <ScrollReveal>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-2">
              文章管理
            </h1>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              管理你的博客文章
            </p>
          </div>
          <button
            @click="router.push('/admin/posts/new')"
            class="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary-from to-primary-to
                   text-white font-medium hover:opacity-90 transition-opacity"
          >
            <Icon icon="lucide:plus" class="w-5 h-5" />
            新建文章
          </button>
        </div>
      </ScrollReveal>

      <!-- 搜索栏 -->
      <ScrollReveal class="delay-100">
        <div class="card p-4">
          <div class="flex items-center gap-4 mb-4">
            <div class="flex-1 relative">
              <Icon icon="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-light-text-muted dark:text-dark-text-muted" />
              <input
                v-model="searchQuery"
                @keydown.enter="handleSearch"
                type="text"
                placeholder="搜索文章标题、描述或标签..."
                class="w-full pl-10 pr-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from"
              />
            </div>
            <button
              @click="handleSearch"
              class="px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90 transition-opacity"
            >
              搜索
            </button>
            <button
              v-if="searchQuery"
              @click="clearSearch"
              class="px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                     text-light-text-primary dark:text-dark-text-primary
                     hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              清空
            </button>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-sm text-light-text-muted dark:text-dark-text-muted">筛选:</span>
              <button
                @click="statusFilter = 'all'"
                class="px-3 py-1 rounded text-sm transition-colors"
                :class="statusFilter === 'all'
                  ? 'bg-primary-from text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary hover:bg-gray-200 dark:hover:bg-gray-700'"
              >
                全部
              </button>
              <button
                @click="statusFilter = 'featured'"
                class="px-3 py-1 rounded text-sm transition-colors"
                :class="statusFilter === 'featured'
                  ? 'bg-yellow-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary hover:bg-gray-200 dark:hover:bg-gray-700'"
              >
                ⭐ 精选
              </button>
              <button
                @click="statusFilter = 'published'"
                class="px-3 py-1 rounded text-sm transition-colors"
                :class="statusFilter === 'published'
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary hover:bg-gray-200 dark:hover:bg-gray-700'"
              >
                已发布
              </button>
              <button
                @click="statusFilter = 'draft'"
                class="px-3 py-1 rounded text-sm transition-colors"
                :class="statusFilter === 'draft'
                  ? 'bg-gray-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary hover:bg-gray-200 dark:hover:bg-gray-700'"
              >
                草稿
              </button>
            </div>
            <div v-if="searchQuery || statusFilter !== 'all'" class="text-sm text-light-text-muted dark:text-dark-text-muted">
              找到 <span class="font-semibold text-light-text-primary dark:text-dark-text-primary">{{ total }}</span> 篇文章
            </div>
          </div>
        </div>
      </ScrollReveal>

      <!-- 文章列表 -->
      <ScrollReveal class="delay-200">
        <div class="card overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    标题
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    日期
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    标签
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    状态
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-light-border dark:divide-dark-border">
                <tr
                  v-for="post in posts"
                  :key="post.slug"
                  class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                      <Icon icon="lucide:file-text" class="w-5 h-5 text-light-text-muted dark:text-dark-text-muted" />
                      <div>
                        <div class="font-medium text-light-text-primary dark:text-dark-text-primary">
                          {{ post.title }}
                        </div>
                        <div class="text-sm text-light-text-muted dark:text-dark-text-muted line-clamp-1">
                          {{ post.description }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-light-text-secondary dark:text-dark-text-secondary">
                    {{ formatDate(post.date) }}
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex flex-wrap gap-1">
                      <BaseBadge
                        v-for="tag in post.tags.slice(0, 2)"
                        :key="tag"
                        variant="gray"
                        size="sm"
                      >
                        {{ tag }}
                      </BaseBadge>
                      <span v-if="post.tags.length > 2" class="text-xs text-light-text-muted dark:text-dark-text-muted">
                        +{{ post.tags.length - 2 }}
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-3">
                      <!-- 状态滑动开关 -->
                      <button
                        @click="handleToggleDraft(post)"
                        :disabled="togglingStatus[post.slug]"
                        class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-from focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        :class="post.draft ? 'bg-gray-200 dark:bg-gray-700' : 'bg-green-500'"
                      >
                        <span
                          class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                          :class="post.draft ? 'translate-x-1' : 'translate-x-6'"
                        />
                      </button>
                      <span class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
                        {{ post.draft ? '草稿' : '已发布' }}
                      </span>
                      <span v-if="post.featured" class="inline-flex items-center gap-1 text-xs text-yellow-600 dark:text-yellow-400">
                        <Icon icon="lucide:star" class="w-3 h-3" />
                        精选
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <div class="flex items-center justify-end gap-2">
                      <!-- 查看按钮 -->
                      <button
                        @click="handleViewPost(post.slug)"
                        class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="在新窗口查看"
                      >
                        <Icon icon="lucide:eye" class="w-4 h-4 text-light-text-muted dark:text-dark-text-muted" />
                      </button>
                      <!-- 编辑按钮 -->
                      <button
                        @click="router.push(`/admin/posts/${post.slug}`)"
                        class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="编辑"
                      >
                        <Icon icon="lucide:pencil" class="w-4 h-4 text-light-text-muted dark:text-dark-text-muted" />
                      </button>
                      <!-- 删除按钮 -->
                      <button
                        @click="showDeleteConfirm(post.slug)"
                        class="p-2 rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                        title="删除"
                      >
                        <Icon icon="lucide:trash-2" class="w-4 h-4 text-red-600 dark:text-red-400" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 空状态 -->
          <div v-if="posts.length === 0" class="p-12 text-center">
            <Icon icon="lucide:file-question" class="w-16 h-16 mx-auto mb-4 text-light-text-muted dark:text-dark-text-muted" />
            <h3 class="text-lg font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
              {{ searchQuery ? '未找到匹配的文章' : '还没有文章' }}
            </h3>
            <p class="text-light-text-secondary dark:text-dark-text-secondary mb-4">
              {{ searchQuery ? '试试其他搜索关键词' : '开始创建你的第一篇博客文章吧' }}
            </p>
            <button
              v-if="!searchQuery"
              @click="router.push('/admin/posts/new')"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary-from to-primary-to
                     text-white font-medium hover:opacity-90 transition-opacity"
            >
              <Icon icon="lucide:plus" class="w-5 h-5" />
              创建文章
            </button>
          </div>
        </div>
      </ScrollReveal>

      <!-- 分页 -->
      <ScrollReveal v-if="totalPages > 1" class="delay-300">
        <div class="flex items-center justify-between">
          <div class="text-sm text-light-text-muted dark:text-dark-text-muted">
            第 {{ currentPage }} / {{ totalPages }} 页，共 {{ total }} 篇
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                     text-light-text-primary dark:text-dark-text-primary
                     hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Icon icon="lucide:chevron-left" class="w-5 h-5" />
            </button>

            <div class="flex items-center gap-1">
              <button
                v-for="page in Math.min(totalPages, 5)"
                :key="page"
                @click="goToPage(page)"
                class="px-3 py-2 rounded-lg transition-colors"
                :class="currentPage === page
                  ? 'bg-primary-from text-white'
                  : 'border border-light-border dark:border-dark-border text-light-text-primary dark:text-dark-text-primary hover:bg-gray-50 dark:hover:bg-gray-800'"
              >
                {{ page }}
              </button>
              <span v-if="totalPages > 5" class="px-2 text-light-text-muted dark:text-dark-text-muted">...</span>
              <button
                v-if="totalPages > 5"
                @click="goToPage(totalPages)"
                class="px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                       text-light-text-primary dark:text-dark-text-primary
                       hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                {{ totalPages }}
              </button>
            </div>

            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                     text-light-text-primary dark:text-dark-text-primary
                     hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Icon icon="lucide:chevron-right" class="w-5 h-5" />
            </button>
          </div>
        </div>
      </ScrollReveal>
    </div>

    <!-- 删除确认对话框 -->
    <ConfirmDialog
      :show="showDeleteDialog"
      title="删除文章"
      message="确定要删除这篇文章吗？此操作无法撤销。"
      confirm-text="删除"
      cancel-text="取消"
      type="danger"
      @confirm="handleDeleteConfirm"
      @cancel="handleDeleteCancel"
    />
  </AdminLayout>
</template>
