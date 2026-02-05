<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { useAdminContentStore } from '@/stores/content.admin'
import { Icon } from '@iconify/vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import MarkdownEditor from '@/components/admin/MarkdownEditor.vue'
import ImageUpload from '@/components/admin/ImageUpload.vue'
import { notifySuccess, notifyError } from '@/utils/notification'

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
  tags: [] as string[],
  image: '',
  date: new Date().toISOString().split('T')[0],
})

const tagInput = ref('')
const isSaving = ref(false)
const isLoading = ref(!isNew.value)

// 加载生活记录数据
onMounted(async () => {
  // 加载分类和标签（创建记录时需要）
  await adminContentStore.loadCategories()
  await adminContentStore.loadTags()

  if (!isNew.value) {
    try {
      const post = await adminContentStore.getPostBySlug(slug.value)

      if (post) {
        // 转换日期格式为 YYYY-MM-DD
        const dateStr = post.date ? new Date(post.date).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]

        formData.value = {
          title: post.title || '',
          description: post.description || '',
          content: post.content || '',
          tags: post.tags || [],
          image: post.image || '',
          date: dateStr,
        }
      }
    } catch (error) {
      // 加载失败
    } finally {
      isLoading.value = false
    }
  }
})

// 添加标签
const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !formData.value.tags.includes(tag)) {
    formData.value.tags.push(tag)
    tagInput.value = ''
  }
}

// 移除标签
const removeTag = (tag: string) => {
  const index = formData.value.tags.indexOf(tag)
  if (index > -1) {
    formData.value.tags.splice(index, 1)
  }
}

// 保存生活记录
const handleSave = async () => {
  // 验证必填字段
  if (!formData.value.title || !formData.value.description || !formData.value.content) {
    notifyError('请填写所有必填字段', '验证失败')
    return
  }

  isSaving.value = true

  try {
    const postData = {
      title: formData.value.title,
      description: formData.value.description,
      content: formData.value.content,
      tags: formData.value.tags,
      image: formData.value.image,
      date: formData.value.date,
      category: 'life' as const,
      locale: 'zh' as const,
      draft: false,  // 默认为已发布
    }

    if (isNew.value) {
      await adminContentStore.createPost(postData)
      // 先重新加载列表数据，确保显示最新内容
      await adminContentStore.loadPostsByCategory('life')
      // 使用时间戳强制路由刷新
      router.replace('/admin/life?t=' + Date.now())
    } else {
      await adminContentStore.updatePost(slug.value, postData)
      await adminContentStore.loadPostsByCategory('life')
      router.replace('/admin/life?t=' + Date.now())
    }
  } catch (error: any) {
    const errorMessage = error?.message || error?.errors || '未知错误'
    notifyError(`保存失败：${errorMessage}`, '操作失败')
  } finally {
    isSaving.value = false
  }
}

// 取消编辑
const handleCancel = () => {
  router.push('/admin/life')
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
              {{ isNew ? '新建生活记录' : '编辑生活记录' }}
            </h1>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              {{ isNew ? '记录生活点滴' : '编辑生活记录' }}
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

            <!-- 标题 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                标题 *
              </label>
              <input
                v-model="formData.title"
                type="text"
                required
                placeholder="请输入标题"
                class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from"
              />
            </div>

            <!-- 描述 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                描述 *
              </label>
              <textarea
                v-model="formData.description"
                required
                rows="2"
                placeholder="简短描述..."
                class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from
                       resize-none"
              />
            </div>

            <!-- 日期 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                日期 *
              </label>
              <input
                v-model="formData.date"
                type="date"
                required
                class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       focus:outline-none focus:ring-2 focus:ring-primary-from"
              />
            </div>

            <!-- 封面图 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                封面图
              </label>
              <ImageUpload
                v-model="formData.image"
                category="life"
              />
            </div>

            <!-- 标签 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                标签
              </label>
              <div class="space-y-2">
                <div class="flex gap-2">
                  <input
                    v-model="tagInput"
                    @keydown.enter.prevent="addTag"
                    type="text"
                    placeholder="输入标签后按回车"
                    class="flex-1 px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           placeholder-light-text-muted dark:placeholder-dark-text-muted
                           focus:outline-none focus:ring-2 focus:ring-primary-from"
                  />
                  <button
                    type="button"
                    @click="addTag"
                    class="px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90 transition-opacity"
                  >
                    添加
                  </button>
                </div>
                <div v-if="formData.tags.length > 0" class="flex flex-wrap gap-2">
                  <span
                    v-for="tag in formData.tags"
                    :key="tag"
                    class="inline-flex items-center gap-1 px-3 py-1 rounded-full
                           bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-sm"
                  >
                    #{{ tag }}
                    <button
                      type="button"
                      @click="removeTag(tag)"
                      class="hover:text-red-500 transition-colors"
                    >
                      <Icon icon="lucide:x" class="w-3 h-3" />
                    </button>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </ScrollReveal>

        <!-- 内容编辑 -->
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
                placeholder="记录生活点滴..."
                category="life"
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
