<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { useAdminContentStore } from '@/stores/content.admin'
import { Icon } from '@iconify/vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import MarkdownEditor from '@/components/admin/MarkdownEditor.vue'
import ImageUpload from '@/components/admin/ImageUpload.vue'
import { useMarkdownReadingTime } from '@/composables/useReadingTime'

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
  featured: false,
  date: new Date().toISOString().split('T')[0],
  image: '',
})

// 自动计算阅读时间
const calculatedReadingTime = computed(() => {
  return useMarkdownReadingTime(formData.value.content || '')
})

const tagInput = ref('')
const isSaving = ref(false)
const isLoading = ref(!isNew.value)

// 加载文章数据
onMounted(async () => {
  // 加载分类和标签（创建文章时需要）
  await adminContentStore.loadCategories()
  await adminContentStore.loadTags()

  if (!isNew.value) {
    try {
      const post = await adminContentStore.getPostBySlug(slug.value)
      if (post) {
        // 转换日期格式从 ISO 到 yyyy-MM-dd
        const dateObj = new Date(post.date)
        const formattedDate = dateObj.toISOString().split('T')[0]

        formData.value = {
          title: post.title,
          description: post.description,
          content: post.content || '',
          tags: post.tags,
          featured: post.featured,
          date: formattedDate,
          image: post.image || '',
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

// 保存文章
const handleSave = async () => {
  isSaving.value = true

  try {
    const postData = {
      title: formData.value.title,
      description: formData.value.description,
      content: formData.value.content,
      tags: formData.value.tags,
      featured: formData.value.featured,
      readingTime: calculatedReadingTime.value, // 使用自动计算的阅读时间
      date: formData.value.date,
      image: formData.value.image,
      category: 'blog' as const,
      locale: 'zh' as const,
    }

    if (isNew.value) {
      await adminContentStore.createPost(postData)
      // 先重新加载列表数据，确保显示最新内容
      await adminContentStore.loadPostsByCategory('blog')
      // 使用时间戳强制路由刷新
      router.replace('/admin/posts?t=' + Date.now())
    } else {
      await adminContentStore.updatePost(slug.value, postData)
      await adminContentStore.loadPostsByCategory('blog')
      router.replace('/admin/posts?t=' + Date.now())
    }
  } catch (error) {
    alert('保存失败：' + (error as Error).message)
  } finally {
    isSaving.value = false
  }
}

// 取消编辑
const handleCancel = () => {
  router.push('/admin/posts')
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
              {{ isNew ? '新建文章' : '编辑文章' }}
            </h1>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              {{ isNew ? '创建一篇新的博客文章' : '编辑现有文章内容' }}
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
                placeholder="请输入文章标题"
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
                rows="3"
                placeholder="请输入文章描述"
                class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from
                       resize-none"
              />
            </div>

            <!-- 发布日期 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                发布日期
              </label>
              <input
                v-model="formData.date"
                type="date"
                class="w-full px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       focus:outline-none focus:ring-2 focus:ring-primary-from"
              />
            </div>

            <!-- 阅读时间（自动计算） -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                预计阅读时间
              </label>
              <div class="px-4 py-3 rounded-lg border border-light-border dark:border-dark-border
                          bg-gray-50 dark:bg-gray-800/50
                          text-light-text-primary dark:text-dark-text-primary">
                {{ calculatedReadingTime }} 分钟
              </div>
              <p class="mt-1 text-xs text-light-text-muted dark:text-dark-text-muted">
                根据文章内容自动计算
              </p>
            </div>

            <!-- 封面图 -->
            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                封面图
              </label>
              <ImageUpload
                v-model="formData.image"
                category="blog"
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
                           bg-primary-from/10 text-primary-from text-sm"
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

            <!-- 精选 -->
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                v-model="formData.featured"
                type="checkbox"
                class="w-4 h-4 rounded border-gray-300 text-primary-from focus:ring-primary-from"
              />
              <span class="text-sm text-light-text-primary dark:text-dark-text-primary">
                设为精选文章
              </span>
            </label>
          </div>
        </ScrollReveal>

        <!-- 内容编辑 -->
        <ScrollReveal class="delay-200">
          <div class="card p-6 space-y-6">
            <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary">
              文章内容
            </h2>

            <div>
              <label class="block text-sm font-medium text-light-text-secondary dark:text-dark-text-secondary mb-2">
                Markdown 内容 *
              </label>
              <MarkdownEditor
                v-model="formData.content"
                placeholder="开始编写你的文章内容... 支持拖拽或粘贴图片"
                category="blog"
              />
              <p class="mt-2 text-xs text-light-text-muted dark:text-dark-text-muted">
                支持图片上传和粘贴，可拖拽图片到编辑器或直接 Ctrl+V 粘贴
              </p>
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
