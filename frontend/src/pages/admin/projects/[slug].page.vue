<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { useAdminContentStore } from '@/stores/content.admin'
import { Icon } from '@iconify/vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import MarkdownEditor from '@/components/admin/MarkdownEditor.vue'

const router = useRouter()
const route = useRoute()
const adminContentStore = useAdminContentStore()

const isNew = computed(() => route.params.slug === 'new')
const slug = computed(() => route.params.slug as string)

// 表单数据
const formData = ref({
  title: '',
  description: '',
  content: '',
  techStack: [] as string[],
  stars: 0,
  forks: 0,
  repo: '',
  demo: '',
  status: 'active' as 'active' | 'maintenance',
  date: new Date().toISOString().split('T')[0],
})

const techInput = ref('')
const isSaving = ref(false)
const isLoading = ref(!isNew.value)

// 加载项目数据
onMounted(async () => {
  // 加载分类和标签（创建项目时需要）
  await adminContentStore.loadCategories()
  await adminContentStore.loadTags()

  if (!isNew.value) {
    try {
      const post = await adminContentStore.getPostBySlug(slug.value)
      if (post) {
        formData.value = {
          title: post.title,
          description: post.description,
          content: post.content || '', // 现在包含 content 字段
          techStack: (post as any).techStack || [],
          stars: (post as any).stars || 0,
          forks: (post as any).forks || 0,
          repo: (post as any).repo || '',
          demo: (post as any).demo || '',
          status: (post as any).status || 'active',
          date: post.date,
        }
      }
    } catch (error) {
      console.error('加载项目失败:', error)
    } finally {
      isLoading.value = false
    }
  }
})

// 添加技术栈
const addTech = () => {
  const tech = techInput.value.trim()
  if (tech && !formData.value.techStack.includes(tech)) {
    formData.value.techStack.push(tech)
    techInput.value = ''
  }
}

// 移除技术栈
const removeTech = (tech: string) => {
  const index = formData.value.techStack.indexOf(tech)
  if (index > -1) {
    formData.value.techStack.splice(index, 1)
  }
}

// 保存项目
const handleSave = async () => {
  isSaving.value = true

  try {
    const projectData = {
      title: formData.value.title,
      description: formData.value.description,
      content: formData.value.content,
      techStack: formData.value.techStack,
      stars: formData.value.stars,
      forks: formData.value.forks,
      repo: formData.value.repo,
      demo: formData.value.demo,
      status: formData.value.status,
      date: formData.value.date,
      category: 'projects' as const,
      locale: 'zh' as const,
    }

    if (isNew.value) {
      await adminContentStore.createPost(projectData)
      // 先重新加载列表数据，确保显示最新内容
      await adminContentStore.loadPostsByCategory('projects')
      // 使用时间戳强制路由刷新
      router.replace('/admin/projects?t=' + Date.now())
    } else {
      await adminContentStore.updatePost(slug.value, projectData)
      await adminContentStore.loadPostsByCategory('projects')
      router.replace('/admin/projects?t=' + Date.now())
    }
  } catch (error) {
    alert('保存失败：' + (error as Error).message)
  } finally {
    isSaving.value = false
  }
}

// 取消编辑
const handleCancel = () => {
  router.push('/admin/projects')
}
</script>

<template>
  <AdminLayout>
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- 标题 -->
      <ScrollReveal>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-2">
              {{ isNew ? '新建项目' : '编辑项目' }}
            </h1>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              {{ isNew ? '添加一个新项目' : '编辑项目信息' }}
            </p>
          </div>
          <button
            @click="handleCancel"
            class="flex items-center gap-2 px-4 py-2 rounded-lg
                   text-light-text-primary dark:text-dark-text-primary
                   hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <Icon icon="lucide:x" class="w-5 h-5" />
            取消
          </button>
        </div>
      </ScrollReveal>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="card p-12 text-center">
        <Icon icon="lucide:loader-2" class="w-8 h-8 animate-spin mx-auto mb-4 text-primary-from" />
        <p class="text-light-text-secondary dark:text-dark-text-secondary">加载中...</p>
      </div>

      <!-- 表单 -->
      <form v-else @submit.prevent="handleSave" class="space-y-6">
        <!-- 基本信息 -->
        <ScrollReveal class="delay-100">
          <div class="card p-6 space-y-6">
            <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary">
              基本信息
            </h2>

            <!-- 项目名称 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                项目名称 *
              </label>
              <input
                v-model="formData.title"
                type="text"
                required
                placeholder="请输入项目名称"
                class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from"
              />
            </div>

            <!-- 项目描述 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                项目描述 *
              </label>
              <textarea
                v-model="formData.description"
                required
                rows="3"
                placeholder="请输入项目描述"
                class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from
                       resize-none"
              />
            </div>

            <!-- 技术栈 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                技术栈
              </label>
              <div class="space-y-2">
                <div class="flex gap-2">
                  <input
                    v-model="techInput"
                    @keydown.enter.prevent="addTech"
                    type="text"
                    placeholder="Vue 3"
                    class="flex-1 px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           placeholder-light-text-muted dark:placeholder-dark-text-muted
                           focus:outline-none focus:ring-2 focus:ring-primary-from"
                  />
                  <button
                    type="button"
                    @click="addTech"
                    class="px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90 transition-opacity"
                  >
                    添加
                  </button>
                </div>
                <div v-if="formData.techStack.length > 0" class="flex flex-wrap gap-2">
                  <span
                    v-for="tech in formData.techStack"
                    :key="tech"
                    class="inline-flex items-center gap-1 px-3 py-1 rounded-full
                           bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-sm"
                  >
                    {{ tech }}
                    <button
                      type="button"
                      @click="removeTech(tech)"
                      class="hover:text-red-500 transition-colors"
                    >
                      <Icon icon="lucide:x" class="w-3 h-3" />
                    </button>
                  </span>
                </div>
              </div>
            </div>

            <!-- GitHub 链接 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                  GitHub 仓库
                </label>
                <input
                  v-model="formData.repo"
                  type="url"
                  placeholder="https://github.com/..."
                  class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                         bg-white dark:bg-gray-800
                         text-light-text-primary dark:text-dark-text-primary
                         placeholder-light-text-muted dark:placeholder-dark-text-muted
                         focus:outline-none focus:ring-2 focus:ring-primary-from"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                  演示地址
                </label>
                <input
                  v-model="formData.demo"
                  type="url"
                  placeholder="https://..."
                  class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                         bg-white dark:bg-gray-800
                         text-light-text-primary dark:text-dark-text-primary
                         placeholder-light-text-muted dark:placeholder-dark-text-muted
                         focus:outline-none focus:ring-2 focus:ring-primary-from"
                />
              </div>
            </div>

            <!-- Stars 和 Forks -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                  Stars
                </label>
                <input
                  v-model.number="formData.stars"
                  type="number"
                  min="0"
                  placeholder="0"
                  class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                         bg-white dark:bg-gray-800
                         text-light-text-primary dark:text-dark-text-primary
                         focus:outline-none focus:ring-2 focus:ring-primary-from"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                  Forks
                </label>
                <input
                  v-model.number="formData.forks"
                  type="number"
                  min="0"
                  placeholder="0"
                  class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                         bg-white dark:bg-gray-800
                         text-light-text-primary dark:text-dark-text-primary
                         focus:outline-none focus:ring-2 focus:ring-primary-from"
                />
              </div>
            </div>

            <!-- 状态 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                项目状态
              </label>
              <div class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="formData.status"
                    type="radio"
                    value="active"
                    class="w-4 h-4 text-primary-from focus:ring-primary-from"
                  />
                  <span class="text-sm text-light-text-primary dark:text-dark-text-primary">活跃开发</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="formData.status"
                    type="radio"
                    value="maintenance"
                    class="w-4 h-4 text-primary-from focus:ring-primary-from"
                  />
                  <span class="text-sm text-light-text-primary dark:text-dark-text-primary">维护模式</span>
                </label>
              </div>
            </div>
          </div>
        </ScrollReveal>

        <!-- 详细内容 -->
        <ScrollReveal class="delay-200">
          <div class="card p-6 space-y-6">
            <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary">
              详细内容
            </h2>

            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                Markdown 内容 *
              </label>
              <MarkdownEditor
                v-model="formData.content"
                placeholder="使用 Markdown 编写项目详情..."
                category="projects"
              />
            </div>
          </div>
        </ScrollReveal>

        <!-- 操作按钮 -->
        <ScrollReveal class="delay-300">
          <div class="flex items-center justify-end gap-4">
            <button
              type="button"
              @click="handleCancel"
              class="px-6 py-3 rounded-lg border border-light-border dark:border-dark-border
                     text-light-text-primary dark:text-dark-text-primary
                     hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="isSaving"
              class="flex items-center gap-2 px-6 py-3 rounded-lg
                     bg-gradient-to-r from-primary-from to-primary-to
                     text-white font-medium
                     hover:opacity-90 transition-opacity
                     disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Icon
                v-if="isSaving"
                icon="lucide:loader-2"
                class="w-5 h-5 animate-spin"
              />
              <Icon v-else icon="lucide:save" class="w-5 h-5" />
              {{ isSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </ScrollReveal>
      </form>
    </div>
  </AdminLayout>
</template>
