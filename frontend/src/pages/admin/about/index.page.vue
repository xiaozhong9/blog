<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { Icon } from '@iconify/vue'
import ImageUpload from '@/components/admin/ImageUpload.vue'
import { userService } from '@/api/services'
import { notifySuccess, notifyError } from '@/utils/notification'

const router = useRouter()

// 用户信息
const userProfile = ref<any>(null)
const loading = ref(false)
const saving = ref(false)

// 编辑表单
const form = ref({
  nickname: '',
  bio: '',
  website: '',
  avatar: '',
  github_url: '',
  twitter_url: '',
  linkedin_url: '',
  story: '',
  skills: {} as Record<string, number>,
  timeline: [] as Array<{
    year: string
    title: string
    company?: string
    description: string
  }>
})

// 技能编辑状态
const skillName = ref('')
const skillLevel = ref(50)

// 时间线编辑状态
const timelineItem = ref({
  year: new Date().getFullYear(),
  title: '',
  company: '',
  description: ''
})

// 当前正在编辑的时间线索引（用于编辑模式）
const editingTimelineIndex = ref<number | null>(null)

// 预览数据（计算属性）
const previewSkills = computed(() => {
  return Object.entries(form.value.skills || {}).map(([name, level]) => ({
    name,
    level: level as number
  }))
})

// 时间线按年份排序（降序，最新的在前）
const previewTimeline = computed(() => {
  if (!form.value.timeline || form.value.timeline.length === 0) return []
  return [...form.value.timeline].sort((a, b) => {
    const yearA = parseInt(a.year) || 0
    const yearB = parseInt(b.year) || 0
    return yearB - yearA // 降序排序
  })
})

// 编辑区显示的时间线（同样按年份排序）
const sortedTimeline = computed(() => {
  if (!form.value.timeline || form.value.timeline.length === 0) return []
  return [...form.value.timeline].sort((a, b) => {
    const yearA = parseInt(a.year) || 0
    const yearB = parseInt(b.year) || 0
    return yearB - yearA // 降序排序
  })
})

// 加载用户信息
const loadUserProfile = async () => {
  loading.value = true
  try {
    const data = await userService.getProfile()
    userProfile.value = data

    // 确保时间线按年份排序
    let timeline = data.timeline || []
    if (timeline.length > 0) {
      timeline = [...timeline].sort((a: any, b: any) => {
        const yearA = parseInt(a.year) || 0
        const yearB = parseInt(b.year) || 0
        return yearB - yearA
      })
    }

    // 填充表单
    form.value = {
      nickname: data.nickname || '',
      bio: data.bio || '',
      website: data.website || '',
      avatar: data.avatar || '',
      github_url: data.github_url || '',
      twitter_url: data.twitter_url || '',
      linkedin_url: data.linkedin_url || '',
      story: data.story || '',
      skills: data.skills || {},
      timeline: timeline,
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    notifyError('加载用户信息失败', '加载失败')
  } finally {
    loading.value = false
  }
}

// 添加技能
const addSkill = () => {
  if (!skillName.value.trim()) return

  form.value.skills = {
    ...form.value.skills,
    [skillName.value]: skillLevel.value
  }

  skillName.value = ''
  skillLevel.value = 50
}

// 删除技能
const removeSkill = (name: string) => {
  const newSkills = { ...form.value.skills }
  delete newSkills[name]
  form.value.skills = newSkills
}

// 更新技能等级
const updateSkillLevel = (name: string, level: number) => {
  form.value.skills = {
    ...form.value.skills,
    [name]: level
  }
}

// 添加时间线
const addTimelineItem = () => {
  // 验证必填字段
  if (!timelineItem.value.title.trim()) {
    notifyError('请输入标题', '验证失败')
    return
  }

  // 年份可能是数字或字符串
  const yearStr = String(timelineItem.value.year).trim()
  if (!yearStr) {
    notifyError('请输入年份', '验证失败')
    return
  }

  // 验证年份格式
  const yearNum = parseInt(yearStr)
  if (isNaN(yearNum) || yearNum < 1900 || yearNum > 2100) {
    notifyError('请输入有效的年份（1900-2100）', '验证失败')
    return
  }

  // 添加新时间线项
  const newItem = {
    year: yearStr,
    title: timelineItem.value.title.trim(),
    company: timelineItem.value.company.trim(),
    description: timelineItem.value.description.trim()
  }

  form.value.timeline = [...form.value.timeline, newItem]

  // 重置表单
  timelineItem.value = {
    year: new Date().getFullYear(),
    title: '',
    company: '',
    description: ''
  }

  editingTimelineIndex.value = null
  notifySuccess('时间线已添加', '添加成功')
}

// 编辑时间线
const editTimelineItem = (index: number) => {
  const item = sortedTimeline.value[index]
  const originalIndex = form.value.timeline.indexOf(item)

  timelineItem.value = {
    year: parseInt(item.year) || new Date().getFullYear(),
    title: item.title,
    company: item.company || '',
    description: item.description || ''
  }
  editingTimelineIndex.value = originalIndex
}

// 更新时间线
const updateTimelineItem = () => {
  if (editingTimelineIndex.value === null) {
    addTimelineItem()
    return
  }

  // 验证必填字段
  if (!timelineItem.value.title.trim()) {
    notifyError('请输入标题', '验证失败')
    return
  }

  // 年份可能是数字或字符串
  const yearStr = String(timelineItem.value.year).trim()
  if (!yearStr) {
    notifyError('请输入年份', '验证失败')
    return
  }

  // 验证年份格式
  const yearNum = parseInt(yearStr)
  if (isNaN(yearNum) || yearNum < 1900 || yearNum > 2100) {
    notifyError('请输入有效的年份（1900-2100）', '验证失败')
    return
  }

  // 更新时间线项
  form.value.timeline[editingTimelineIndex.value] = {
    year: yearStr,
    title: timelineItem.value.title.trim(),
    company: timelineItem.value.company.trim(),
    description: timelineItem.value.description.trim()
  }

  // 重置表单
  timelineItem.value = {
    year: new Date().getFullYear(),
    title: '',
    company: '',
    description: ''
  }

  editingTimelineIndex.value = null
  notifySuccess('时间线已更新', '更新成功')
}

// 取消编辑
const cancelEdit = () => {
  timelineItem.value = {
    year: new Date().getFullYear(),
    title: '',
    company: '',
    description: ''
  }
  editingTimelineIndex.value = null
}

// 删除时间线
const removeTimelineItem = (index: number) => {
  form.value.timeline = form.value.timeline.filter((_, i) => i !== index)
  notifySuccess('时间线已删除', '删除成功')
}

// 保存用户信息
const handleSave = async () => {
  saving.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      notifyError('未登录', '保存失败')
      return
    }

    const payload = JSON.parse(atob(token.split('.')[1]))
    const userId = payload.user_id

    // 准备保存的数据，确保时间线按年份排序
    const saveData = {
      nickname: form.value.nickname?.trim() || '',
      bio: form.value.bio?.trim() || '',
      website: form.value.website?.trim() || '',
      avatar: form.value.avatar?.trim() || '',
      github_url: form.value.github_url?.trim() || '',
      twitter_url: form.value.twitter_url?.trim() || '',
      linkedin_url: form.value.linkedin_url?.trim() || '',
      story: form.value.story || '',
      skills: form.value.skills || {},
      timeline: previewTimeline.value, // 使用排序后的时间线
    }

    console.log('保存数据:', saveData)

    await userService.update(userId, saveData)

    await loadUserProfile()
    notifySuccess('关于页面内容已更新', '保存成功')
  } catch (error: any) {
    console.error('保存失败:', error)
    const errorMsg = error?.response?.data?.message || error?.message || '保存失败，请重试'
    notifyError(errorMsg, '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadUserProfile()
})
</script>

<template>
  <AdminLayout>
    <div class="h-[calc(100vh-4rem)] flex flex-col">
      <!-- 标题栏 -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-light-border dark:border-dark-border bg-white dark:bg-gray-800">
        <div>
          <h1 class="text-2xl font-bold text-light-text-primary dark:text-dark-text-primary">
            关于页面管理
          </h1>
          <p class="text-sm text-light-text-muted dark:text-dark-text-muted mt-1">
            编辑关于页面的个人信息、技能和时间线
          </p>
        </div>
        <div class="flex items-center gap-3">
          <a
            href="/about"
            target="_blank"
            class="inline-flex items-center gap-2 px-4 py-2 text-sm rounded-lg
                   border border-light-border dark:border-dark-border
                   text-light-text-primary dark:text-dark-text-primary
                   hover:bg-light-bg dark:hover:bg-gray-700
                   transition-colors"
          >
            <Icon icon="lucide:external-link" class="w-4 h-4" />
            查看前台
          </a>
          <button
            @click="handleSave"
            :disabled="saving"
            class="inline-flex items-center gap-2 px-6 py-2 rounded-lg
                   bg-gradient-to-r from-primary-from to-primary-to
                   text-white font-medium hover:opacity-90 transition-opacity
                   disabled:opacity-50"
          >
            <Icon v-if="saving" icon="lucide:loader-2" class="w-4 h-4 animate-spin" />
            <Icon v-else icon="lucide:save" class="w-4 h-4" />
            {{ saving ? '保存中...' : '保存更改' }}
          </button>
        </div>
      </div>

      <!-- 主内容区：左右分栏 -->
      <div class="flex-1 overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center h-full">
          <Icon icon="lucide:loader-2" class="w-8 h-8 animate-spin text-primary-from" />
          <span class="ml-3 text-light-text-secondary dark:text-dark-text-secondary">加载中...</span>
        </div>

        <div v-else class="flex h-full">
          <!-- 左侧：编辑表单 -->
          <div class="w-1/2 overflow-y-auto border-r border-light-border dark:border-dark-border p-6 space-y-6">
            <!-- 基本信息 -->
            <section>
              <h2 class="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary mb-4 flex items-center gap-2">
                <Icon icon="lucide:user" class="w-5 h-5" />
                基本信息
              </h2>

              <div class="space-y-4">
                <!-- 昵称 -->
                <div>
                  <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
                    昵称
                  </label>
                  <input
                    v-model="form.nickname"
                    type="text"
                    placeholder="输入您的昵称"
                    class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           placeholder-light-text-muted dark:placeholder-dark-text-muted
                           focus:outline-none focus:ring-2 focus:ring-primary-from text-sm"
                  />
                </div>

                <!-- 个人简介 -->
                <div>
                  <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
                    个人简介
                  </label>
                  <textarea
                    v-model="form.bio"
                    rows="3"
                    placeholder="介绍一下自己..."
                    class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           placeholder-light-text-muted dark:placeholder-dark-text-muted
                           focus:outline-none focus:ring-2 focus:ring-primary-from
                           resize-none text-sm"
                  />
                </div>

                <!-- 我的故事 -->
                <div>
                  <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
                    我的故事
                  </label>
                  <textarea
                    v-model="form.story"
                    rows="8"
                    placeholder="讲述你的个人经历、编程之旅、技术热情..."
                    class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           placeholder-light-text-muted dark:placeholder-dark-text-muted
                           focus:outline-none focus:ring-2 focus:ring-primary-from
                           resize-y text-sm"
                  />
                  <p class="mt-1 text-xs text-light-text-muted dark:text-dark-text-muted">
                    支持 Markdown 格式，将显示在关于页面的"我的故事"部分
                  </p>
                </div>

                <!-- 头像上传 -->
                <div>
                  <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
                    头像
                  </label>
                  <div class="flex items-center gap-4">
                    <!-- 头像预览 -->
                    <div
                      class="w-16 h-16 rounded-full bg-gradient-to-br from-primary-from to-primary-to
                            flex items-center justify-center text-white text-xl font-bold
                            overflow-hidden flex-shrink-0"
                    >
                      <img
                        v-if="form.avatar"
                        :src="form.avatar"
                        alt="Avatar"
                        class="w-full h-full object-cover"
                      />
                      <span v-else>{{ (form.nickname || 'U')[0] }}</span>
                    </div>
                    <!-- 上传组件 -->
                    <div class="flex-1">
                      <ImageUpload
                        v-model="form.avatar"
                        category="avatar"
                      />
                      <p class="mt-1 text-xs text-light-text-muted dark:text-dark-text-muted">
                        建议使用正方形头像，支持 JPG、PNG 格式，最大 5MB
                      </p>
                    </div>
                  </div>
                </div>

                <!-- 个人网站 -->
                <div>
                  <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
                    个人网站
                  </label>
                  <input
                    v-model="form.website"
                    type="url"
                    placeholder="https://example.com"
                    class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           placeholder-light-text-muted dark:placeholder-dark-text-muted
                           focus:outline-none focus:ring-2 focus:ring-primary-from text-sm"
                  />
                </div>
              </div>
            </section>

            <hr class="border-light-border dark:border-dark-border">

            <!-- 社交链接 -->
            <section>
              <h2 class="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary mb-4 flex items-center gap-2">
                <Icon icon="lucide:share-2" class="w-5 h-5" />
                社交链接
              </h2>

              <div class="space-y-3">
                <!-- GitHub -->
                <div>
                  <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
                    <Icon icon="lucide:github" class="w-4 h-4 inline mr-1" />
                    GitHub
                  </label>
                  <input
                    v-model="form.github_url"
                    type="url"
                    placeholder="https://github.com/username"
                    class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           placeholder-light-text-muted dark:placeholder-dark-text-muted
                           focus:outline-none focus:ring-2 focus:ring-primary-from text-sm"
                  />
                </div>

                <!-- Twitter -->
                <div>
                  <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
                    <Icon icon="lucide:twitter" class="w-4 h-4 inline mr-1" />
                    Twitter
                  </label>
                  <input
                    v-model="form.twitter_url"
                    type="url"
                    placeholder="https://twitter.com/username"
                    class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           placeholder-light-text-muted dark:placeholder-dark-text-muted
                           focus:outline-none focus:ring-2 focus:ring-primary-from text-sm"
                  />
                </div>

                <!-- LinkedIn -->
                <div>
                  <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
                    <Icon icon="lucide:linkedin" class="w-4 h-4 inline mr-1" />
                    LinkedIn
                  </label>
                  <input
                    v-model="form.linkedin_url"
                    type="url"
                    placeholder="https://linkedin.com/in/username"
                    class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           placeholder-light-text-muted dark:placeholder-dark-text-muted
                           focus:outline-none focus:ring-2 focus:ring-primary-from text-sm"
                  />
                </div>
              </div>
            </section>

            <hr class="border-light-border dark:border-dark-border">

            <!-- 技能栈 -->
            <section>
              <h2 class="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary mb-4 flex items-center gap-2">
                <Icon icon="lucide:zap" class="w-5 h-5" />
                技能栈
              </h2>

              <!-- 添加技能表单 -->
              <div class="flex items-center gap-2 mb-4">
                <input
                  v-model="skillName"
                  type="text"
                  placeholder="技能名称（如 Vue.js）"
                  @keydown.enter="addSkill"
                  class="flex-1 px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                         bg-white dark:bg-gray-800
                         text-light-text-primary dark:text-dark-text-primary
                         placeholder-light-text-muted dark:placeholder-dark-text-muted
                         focus:outline-none focus:ring-2 focus:ring-primary-from text-sm"
                />
                <input
                  v-model.number="skillLevel"
                  type="number"
                  min="0"
                  max="100"
                  class="w-20 px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                         bg-white dark:bg-gray-800
                         text-light-text-primary dark:text-dark-text-primary
                         focus:outline-none focus:ring-2 focus:ring-primary-from text-sm text-center"
                />
                <button
                  @click="addSkill"
                  class="px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90
                         transition-opacity text-sm font-medium"
                >
                  添加
                </button>
              </div>

              <!-- 技能列表 -->
              <div class="space-y-2">
                <div
                  v-for="(level, name) in form.skills"
                  :key="name"
                  class="flex items-center gap-3 p-3 rounded-lg border border-light-border dark:border-dark-border
                         bg-light-bg dark:bg-gray-800 group"
                >
                  <span class="flex-1 font-medium text-light-text-primary dark:text-dark-text-primary text-sm">
                    {{ name }}
                  </span>
                  <input
                    :value="level"
                    type="range"
                    min="0"
                    max="100"
                    @input="updateSkillLevel(name, Number(($event.target as HTMLInputElement).value))"
                    class="flex-1 h-2 accent-primary-from"
                  />
                  <span class="w-12 text-center text-sm text-light-text-muted dark:text-dark-text-muted">
                    {{ level }}%
                  </span>
                  <button
                    @click="removeSkill(name)"
                    class="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:bg-red-50
                           dark:hover:bg-red-900/20 rounded transition-all"
                  >
                    <Icon icon="lucide:x" class="w-4 h-4" />
                  </button>
                </div>

                <div v-if="Object.keys(form.skills).length === 0"
                     class="text-center py-6 text-light-text-muted dark:text-dark-text-muted text-sm">
                  暂无技能，请添加
                </div>
              </div>
            </section>

            <hr class="border-light-border dark:border-dark-border">

            <!-- 时间线 -->
            <section>
              <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary flex items-center gap-2">
                  <Icon icon="lucide:calendar" class="w-5 h-5" />
                  时间线
                </h2>
                <span class="text-xs text-light-text-muted dark:text-dark-text-muted bg-light-bg dark:bg-gray-800 px-2 py-1 rounded">
                  按年份自动排序
                </span>
              </div>

              <!-- 添加时间线表单 -->
              <div class="p-4 rounded-lg border border-light-border dark:border-dark-border
                      bg-light-bg dark:bg-gray-800 space-y-3 mb-4">
                <div class="grid grid-cols-3 gap-3">
                  <div>
                    <label class="block text-xs font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
                      年份 <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="timelineItem.year"
                      type="number"
                      min="1900"
                      max="2100"
                      step="1"
                      placeholder="2024"
                      class="w-full px-2 py-1.5 rounded border border-light-border dark:border-dark-border
                             bg-white dark:bg-gray-800
                             text-light-text-primary dark:text-dark-text-primary
                             focus:outline-none focus:ring-2 focus:ring-primary-from text-sm"
                    />
                  </div>
                  <div class="col-span-2">
                    <label class="block text-xs font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
                      标题 <span class="text-red-500">*</span>
                    </label>
                    <input
                      v-model="timelineItem.title"
                      type="text"
                      placeholder="Senior Developer"
                      class="w-full px-2 py-1.5 rounded border border-light-border dark:border-dark-border
                             bg-white dark:bg-gray-800
                             text-light-text-primary dark:text-dark-text-primary
                             focus:outline-none focus:ring-2 focus:ring-primary-from text-sm"
                    />
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
                    公司/组织（可选）
                  </label>
                  <input
                    v-model="timelineItem.company"
                    type="text"
                    placeholder="Tech Company"
                    class="w-full px-2 py-1.5 rounded border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           focus:outline-none focus:ring-2 focus:ring-primary-from text-sm"
                  />
                </div>
                <div>
                  <label class="block text-xs font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
                    描述
                  </label>
                  <textarea
                    v-model="timelineItem.description"
                    rows="2"
                    placeholder="描述这段经历..."
                    class="w-full px-2 py-1.5 rounded border border-light-border dark:border-dark-border
                           bg-white dark:bg-gray-800
                           text-light-text-primary dark:text-dark-text-primary
                           focus:outline-none focus:ring-2 focus:ring-primary-from
                           resize-none text-sm"
                  />
                </div>
                <div class="flex gap-2">
                  <button
                    v-if="editingTimelineIndex === null"
                    @click="addTimelineItem"
                    class="flex-1 px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90
                           transition-opacity text-sm font-medium"
                  >
                    添加到时间线
                  </button>
                  <template v-else>
                    <button
                      @click="updateTimelineItem"
                      class="flex-1 px-4 py-2 rounded-lg bg-green-500 text-white hover:opacity-90
                             transition-opacity text-sm font-medium"
                    >
                      更新
                    </button>
                    <button
                      @click="cancelEdit"
                      class="px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                             text-light-text-secondary dark:text-dark-text-secondary hover:bg-light-bg
                             dark:hover:bg-gray-700 transition-colors text-sm font-medium"
                    >
                      取消
                    </button>
                  </template>
                </div>
              </div>

              <!-- 时间线列表 -->
              <div class="space-y-3">
                <div
                  v-for="(item, index) in sortedTimeline"
                  :key="index"
                  class="relative pl-4 border-l-2 border-light-border dark:border-dark-border
                         hover:border-primary-from dark:hover:border-primary-from
                         transition-colors group"
                >
                  <div class="absolute left-0 top-0 w-3 h-3 -translate-x-[5px]
                              bg-gradient-to-br from-primary-from to-primary-to
                              rounded-full border-2 border-light-bg dark:border-dark-bg" />

                  <div class="mb-1">
                    <span class="text-xs font-semibold text-primary-from">{{ item.year }}</span>
                  </div>
                  <h3 class="text-sm font-bold text-light-text-primary dark:text-dark-text-primary">
                    {{ item.title }}
                  </h3>
                  <p v-if="item.company" class="text-xs text-light-text-secondary dark:text-dark-text-secondary">
                    @ {{ item.company }}
                  </p>
                  <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary mt-1">
                    {{ item.description }}
                  </p>

                  <!-- 操作按钮 -->
                  <div class="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100
                               transition-opacity">
                    <button
                      @click="editTimelineItem(form.timeline.indexOf(item))"
                      class="p-1 rounded hover:bg-blue-50 dark:hover:bg-blue-900/20
                             text-blue-500"
                      title="编辑"
                    >
                      <Icon icon="lucide:pencil" class="w-3 h-3" />
                    </button>
                    <button
                      @click="removeTimelineItem(form.timeline.indexOf(item))"
                      class="p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20
                             text-red-500"
                      title="删除"
                    >
                      <Icon icon="lucide:trash-2" class="w-3 h-3" />
                    </button>
                  </div>
                </div>

                <div v-if="form.timeline.length === 0"
                     class="text-center py-6 text-light-text-muted dark:text-dark-text-muted text-sm">
                  暂无时间线，请添加
                </div>
              </div>
            </section>
          </div>

          <!-- 右侧：实时预览 -->
          <div class="w-1/2 overflow-y-auto bg-light-bg dark:bg-gray-900 p-6">
            <div class="sticky top-0">
              <!-- 预览标签 -->
              <div class="flex items-center justify-between mb-6">
                <h2 class="text-lg font-semibold text-light-text-primary dark:text-dark-text-primary flex items-center gap-2">
                  <Icon icon="lucide:eye" class="w-5 h-5" />
                  实时预览
                </h2>
                <span class="text-xs px-2 py-1 rounded-full bg-green-100 dark:bg-green-900/30
                               text-green-700 dark:text-green-300 font-medium">
                  自动更新
                </span>
              </div>

              <!-- 预览内容 -->
              <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
                <!-- 头像和基本信息 -->
                <div class="text-center mb-8">
                  <div
                    class="w-20 h-20 mx-auto mb-4 rounded-full
                              bg-gradient-to-br from-primary-from to-primary-to
                              flex items-center justify-center text-white text-2xl font-bold"
                  >
                    <img
                      v-if="form.avatar"
                      :src="form.avatar"
                      :alt="form.nickname || 'U'"
                      class="w-full h-full rounded-full object-cover"
                    />
                    <span v-else>{{ (form.nickname || 'U')[0] }}</span>
                  </div>
                  <h3 class="text-2xl font-bold text-light-text-primary dark:text-dark-text-primary mb-2">
                    {{ form.nickname || '未设置昵称' }}
                  </h3>
                  <p v-if="form.bio" class="text-light-text-secondary dark:text-dark-text-secondary text-sm">
                    {{ form.bio }}
                  </p>
                  <p v-else class="text-light-text-muted dark:text-dark-text-muted text-sm italic">
                    暂无简介
                  </p>
                </div>

                <!-- 技能栈预览 -->
                <div class="mb-8">
                  <h4 class="text-sm font-semibold text-light-text-primary dark:text-dark-text-primary mb-3">
                    技能栈
                  </h4>
                  <div v-if="previewSkills.length > 0" class="space-y-2">
                    <div
                      v-for="skill in previewSkills"
                      :key="skill.name"
                      class="space-y-1"
                    >
                      <div class="flex justify-between text-xs">
                        <span class="font-medium text-light-text-primary dark:text-dark-text-primary">
                          {{ skill.name }}
                        </span>
                        <span class="text-light-text-muted dark:text-dark-text-muted">
                          {{ skill.level }}%
                        </span>
                      </div>
                      <div class="h-1.5 bg-light-bg dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          class="h-full bg-gradient-to-r from-primary-from to-primary-to
                                 transition-all duration-300"
                          :style="{ width: `${skill.level}%` }"
                        />
                      </div>
                    </div>
                  </div>
                  <p v-else class="text-xs text-light-text-muted dark:text-dark-text-muted italic py-2">
                    暂无技能
                  </p>
                </div>

                <!-- 时间线预览 -->
                <div class="mb-8">
                  <h4 class="text-sm font-semibold text-light-text-primary dark:text-dark-text-primary mb-3">
                    时间线
                  </h4>
                  <div v-if="previewTimeline.length > 0" class="space-y-4">
                    <div
                      v-for="(item, index) in previewTimeline"
                      :key="index"
                      class="relative pl-4 border-l-2 border-light-border dark:border-dark-border"
                    >
                      <div class="absolute left-0 top-0 w-2.5 h-2.5 -translate-x-[5px]
                                  bg-gradient-to-br from-primary-from to-primary-to
                                  rounded-full border-2 border-white dark:border-gray-800" />
                      <div class="mb-0.5">
                        <span class="text-xs font-semibold text-primary-from">{{ item.year }}</span>
                      </div>
                      <h5 class="text-sm font-bold text-light-text-primary dark:text-dark-text-primary">
                        {{ item.title }}
                      </h5>
                      <p v-if="item.company" class="text-xs text-light-text-secondary dark:text-dark-text-secondary">
                        @ {{ item.company }}
                      </p>
                      <p class="text-xs text-light-text-secondary dark:text-dark-text-secondary mt-0.5">
                        {{ item.description }}
                      </p>
                    </div>
                  </div>
                  <p v-else class="text-xs text-light-text-muted dark:text-dark-text-muted italic py-2">
                    暂无时间线
                  </p>
                </div>

                <!-- 社交链接预览 -->
                <div>
                  <h4 class="text-sm font-semibold text-light-text-primary dark:text-dark-text-primary mb-3">
                    联系方式
                  </h4>
                  <div class="flex flex-wrap gap-2">
                    <a
                      v-if="form.website"
                      :href="form.website"
                      target="_blank"
                      class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg
                             bg-light-bg dark:bg-gray-700
                             text-light-text-primary dark:text-dark-text-primary
                             hover:bg-light-border dark:hover:bg-gray-600
                             transition-colors text-xs border border-light-border dark:border-dark-border"
                    >
                      <Icon icon="lucide:globe" class="w-3 h-3" />
                      Website
                    </a>
                    <a
                      v-if="form.github_url"
                      :href="form.github_url"
                      target="_blank"
                      class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg
                             bg-light-bg dark:bg-gray-700
                             text-light-text-primary dark:text-dark-text-primary
                             hover:bg-light-border dark:hover:bg-gray-600
                             transition-colors text-xs border border-light-border dark:border-dark-border"
                    >
                      <Icon icon="lucide:github" class="w-3 h-3" />
                      GitHub
                    </a>
                    <a
                      v-if="form.twitter_url"
                      :href="form.twitter_url"
                      target="_blank"
                      class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg
                             bg-light-bg dark:bg-gray-700
                             text-light-text-primary dark:text-dark-text-primary
                             hover:bg-light-border dark:hover:bg-gray-600
                             transition-colors text-xs border border-light-border dark:border-dark-border"
                    >
                      <Icon icon="lucide:twitter" class="w-3 h-3" />
                      Twitter
                    </a>
                    <a
                      v-if="form.linkedin_url"
                      :href="form.linkedin_url"
                      target="_blank"
                      class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg
                             bg-light-bg dark:bg-gray-700
                             text-light-text-primary dark:text-dark-text-primary
                             hover:bg-light-border dark:hover:bg-gray-600
                             transition-colors text-xs border border-light-border dark:border-dark-border"
                    >
                      <Icon icon="lucide:linkedin" class="w-3 h-3" />
                      LinkedIn
                    </a>
                  </div>
                  <p v-if="!form.website && !form.github_url && !form.twitter_url && !form.linkedin_url"
                     class="text-xs text-light-text-muted dark:text-dark-text-muted italic py-2">
                    暂无社交链接
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
