<script setup lang="ts">
import { computed, onBeforeMount, ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { useAdminContentStore } from '@/stores/content.admin'
import { Icon } from '@iconify/vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import { notifySuccess, notifyError } from '@/utils/notification'
import { formatDate } from '@/utils/dateFormatter'

const router = useRouter()
const adminContentStore = useAdminContentStore()

// 状态切换追踪
const togglingStatus = ref<Record<string, boolean>>({})

// 删除确认对话框
const showDeleteDialog = ref(false)
const deletingSlug = ref<string>('')

// 加载数据函数
const loadPosts = async () => {
  await adminContentStore.loadPostsByCategory('life')
}

// 每次进入页面时加载数据
onBeforeMount(loadPosts)

// 获取所有生活记录
const lifePosts = computed(() => {
  return adminContentStore.posts.filter(p => p.category === 'life')
})

// 显示删除确认对话框
const showDeleteConfirm = (slug: string) => {
  deletingSlug.value = slug
  showDeleteDialog.value = true
}

// 确认删除
const handleDeleteConfirm = async () => {
  showDeleteDialog.value = false

  try {
    await adminContentStore.deletePost(deletingSlug.value)
    await adminContentStore.loadPostsByCategory('life')
    notifySuccess('记录已删除', '删除成功')
  } catch (error) {
    notifyError('删除失败，请重试', '操作失败')
  } finally {
    deletingSlug.value = ''
  }
}

// 取消删除
const handleDeleteCancel = () => {
  showDeleteDialog.value = false
  deletingSlug.value = ''
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
      // 从已发布 → 草稿
      notifySuccess('记录已设置为草稿', '操作成功')
    } else {
      // 从草稿 → 已发布
      notifySuccess('记录已发布', '发布成功')
    }
  } catch (error) {
    notifyError('操作失败，请重试', '操作失败')
  } finally {
    togglingStatus.value[post.slug] = false
  }
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
              生活记录管理
            </h1>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              管理你的生活点滴
            </p>
          </div>
          <button
            @click="router.push('/admin/life/new')"
            class="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary-from to-primary-to
                   text-white font-medium hover:opacity-90 transition-opacity"
          >
            <Icon icon="lucide:plus" class="w-5 h-5" />
            新建记录
          </button>
        </div>
      </ScrollReveal>

      <!-- 记录列表 -->
      <ScrollReveal class="delay-100">
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
                  v-for="post in lifePosts"
                  :key="post.slug"
                  class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-green-600
                                    flex items-center justify-center text-white text-lg font-bold">
                        {{ post.title[0] }}
                      </div>
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
                        v-for="tag in post.tags.slice(0, 3)"
                        :key="tag"
                        variant="gray"
                        size="sm"
                      >
                        #{{ tag }}
                      </BaseBadge>
                      <span v-if="post.tags.length > 3" class="text-xs text-light-text-muted dark:text-dark-text-muted">
                        +{{ post.tags.length - 3 }}
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-2">
                      <!-- 草稿/发布滑动开关 -->
                      <div class="flex items-center gap-2">
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
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <div class="flex items-center justify-end gap-2">
                      <button
                        @click="router.push(`/life/${post.slug}`)"
                        class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="查看"
                      >
                        <Icon icon="lucide:eye" class="w-4 h-4 text-light-text-muted dark:text-dark-text-muted" />
                      </button>
                      <button
                        @click="router.push(`/admin/life/${post.slug}`)"
                        class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="编辑"
                      >
                        <Icon icon="lucide:pencil" class="w-4 h-4 text-light-text-muted dark:text-dark-text-muted" />
                      </button>
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
          <div v-if="lifePosts.length === 0" class="p-12 text-center">
            <Icon icon="lucide:calendar-x" class="w-16 h-16 mx-auto mb-4 text-light-text-muted dark:text-dark-text-muted" />
            <h3 class="text-lg font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
              还没有生活记录
            </h3>
            <p class="text-light-text-secondary dark:text-dark-text-secondary mb-4">
              开始记录你的生活点滴吧
            </p>
            <button
              @click="router.push('/admin/life/new')"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary-from to-primary-to
                     text-white font-medium hover:opacity-90 transition-opacity"
            >
              <Icon icon="lucide:plus" class="w-5 h-5" />
              添加记录
            </button>
          </div>
        </div>
      </ScrollReveal>
    </div>

    <!-- 删除确认对话框 -->
    <ConfirmDialog
      :show="showDeleteDialog"
      title="删除记录"
      message="确定要删除这条记录吗？此操作无法撤销。"
      confirm-text="删除"
      cancel-text="取消"
      type="danger"
      @confirm="handleDeleteConfirm"
      @cancel="handleDeleteCancel"
    />
  </AdminLayout>
</template>
