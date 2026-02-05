<script setup lang="ts">
import { computed, onBeforeMount, ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { useAdminContentStore } from '@/stores/content.admin'
import { Icon } from '@iconify/vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import { notifySuccess, notifyError } from '@/utils/notification'

const router = useRouter()
const adminContentStore = useAdminContentStore()

// 状态切换追踪
const togglingStatus = ref<Record<string, boolean>>({})

// 删除确认对话框
const showDeleteDialog = ref(false)
const deletingSlug = ref<string>('')

// 每次进入页面时加载数据
onBeforeMount(async () => {
  await adminContentStore.loadPostsByCategory('projects')
})

// 获取所有项目
const projects = computed(() => {
  return adminContentStore.posts.filter(p => p.category === 'projects')
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
    await adminContentStore.loadPostsByCategory('projects')
    notifySuccess('项目已删除', '删除成功')
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
const handleToggleDraft = async (project: { slug: string; title: string; draft?: boolean }) => {
  const currentDraft = project.draft || false

  // 防止重复点击
  if (togglingStatus.value[project.slug]) {
    return
  }

  togglingStatus.value[project.slug] = true

  try {
    await adminContentStore.updatePost(project.slug, { draft: !currentDraft })

    // 更清晰的提示信息
    if (!currentDraft) {
      // 从已发布 → 草稿
      notifySuccess('项目已设置为草稿', '操作成功')
    } else {
      // 从草稿 → 已发布
      notifySuccess('项目已发布', '发布成功')
    }
  } catch (error) {
    notifyError('操作失败，请重试', '操作失败')
  } finally {
    togglingStatus.value[project.slug] = false
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
              项目管理
            </h1>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              管理你的项目展示
            </p>
          </div>
          <button
            @click="router.push('/admin/projects/new')"
            class="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary-from to-primary-to
                   text-white font-medium hover:opacity-90 transition-opacity"
          >
            <Icon icon="lucide:plus" class="w-5 h-5" />
            新建项目
          </button>
        </div>
      </ScrollReveal>

      <!-- 项目列表 -->
      <ScrollReveal class="delay-100">
        <div class="card overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    项目名称
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    Stars
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
                  v-for="project in projects"
                  :key="project.slug"
                  class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-from to-primary-to
                                    flex items-center justify-center text-white">
                        <Icon icon="lucide:folder" class="w-5 h-5" />
                      </div>
                      <div>
                        <div class="font-medium text-light-text-primary dark:text-dark-text-primary">
                          {{ project.title }}
                        </div>
                        <div class="text-sm text-light-text-muted dark:text-dark-text-muted line-clamp-1">
                          {{ project.description }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-1 text-yellow-600 dark:text-yellow-400">
                      <Icon icon="lucide:star" class="w-4 h-4" />
                      <span class="font-medium">{{ (project as any).stars || 0 }}</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-3">
                      <!-- 草稿/发布滑动开关 -->
                      <div class="flex items-center gap-2">
                        <button
                          @click="handleToggleDraft(project)"
                          :disabled="togglingStatus[project.slug]"
                          class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-from focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                          :class="project.draft ? 'bg-gray-200 dark:bg-gray-700' : 'bg-green-500'"
                        >
                          <span
                            class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                            :class="project.draft ? 'translate-x-1' : 'translate-x-6'"
                          />
                        </button>
                        <span class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
                          {{ project.draft ? '草稿' : '已发布' }}
                        </span>
                      </div>
                      <!-- 项目状态 -->
                      <span
                        v-if="!project.draft"
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="(project as any).status === 'active'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400'"
                        >
                        {{ (project as any).status === 'active' ? '活跃' : '维护中' }}
                      </span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <div class="flex items-center justify-end gap-2">
                      <button
                        @click="router.push(`/projects/${project.slug}`)"
                        class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="查看"
                      >
                        <Icon icon="lucide:eye" class="w-4 h-4 text-light-text-muted dark:text-dark-text-muted" />
                      </button>
                      <button
                        @click="router.push(`/admin/projects/${project.slug}`)"
                        class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="编辑"
                      >
                        <Icon icon="lucide:pencil" class="w-4 h-4 text-light-text-muted dark:text-dark-text-muted" />
                      </button>
                      <button
                        @click="showDeleteConfirm(project.slug)"
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
          <div v-if="projects.length === 0" class="p-12 text-center">
            <Icon icon="lucide:folder-open" class="w-16 h-16 mx-auto mb-4 text-light-text-muted dark:text-dark-text-muted" />
            <h3 class="text-lg font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
              还没有项目
            </h3>
            <p class="text-light-text-secondary dark:text-dark-text-secondary mb-4">
              开始添加你的项目展示吧
            </p>
            <button
              @click="router.push('/admin/projects/new')"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary-from to-primary-to
                     text-white font-medium hover:opacity-90 transition-opacity"
            >
              <Icon icon="lucide:plus" class="w-5 h-5" />
              添加项目
            </button>
          </div>
        </div>
      </ScrollReveal>
    </div>

    <!-- 删除确认对话框 -->
    <ConfirmDialog
      :show="showDeleteDialog"
      title="删除项目"
      message="确定要删除这个项目吗？此操作无法撤销。"
      confirm-text="删除"
      cancel-text="取消"
      type="danger"
      @confirm="handleDeleteConfirm"
      @cancel="handleDeleteCancel"
    />
  </AdminLayout>
</template>
