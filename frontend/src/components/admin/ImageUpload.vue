<script setup lang="ts">
import { ref, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { uploadImage } from '@/utils/imageUpload'
import { notifySuccess, notifyError } from '@/utils/notification'

const props = defineProps<{
  modelValue: string
  category?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const imageUrl = ref(props.modelValue)
const isUploading = ref(false)
const fileInput = ref<HTMLInputElement>()

// 监听 modelValue 变化
watch(() => props.modelValue, (newVal) => {
  imageUrl.value = newVal
})

// 选择文件
const selectFile = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    notifyError('只能上传图片文件', '文件类型错误')
    return
  }

  // 验证文件大小（5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    notifyError('图片过大，最大支持 5MB', '文件过大')
    return
  }

  isUploading.value = true

  try {
    const result = await uploadImage(file, props.category || 'general')
    imageUrl.value = result.url
    emit('update:modelValue', result.url)
    notifySuccess('封面图上传成功', '上传成功')
  } catch (error) {
    console.error('上传失败:', error)
    notifyError('上传失败，请重试', '上传失败')
  } finally {
    isUploading.value = false
    // 清空 input，允许重复选择同一文件
    if (target) {
      target.value = ''
    }
  }
}

// 移除图片
const removeImage = () => {
  imageUrl.value = ''
  emit('update:modelValue', '')
}
</script>

<template>
  <div class="space-y-3">
    <!-- 图片预览 -->
    <div v-if="imageUrl" class="relative group">
      <div class="aspect-video w-full overflow-hidden rounded-lg bg-gray-100 dark:bg-gray-800">
        <img
          :src="imageUrl"
          alt="封面图预览"
          class="w-full h-full object-cover"
        />
      </div>
      <button
        type="button"
        @click="removeImage"
        class="absolute top-2 right-2 p-2 rounded-lg bg-red-500 text-white opacity-0 group-hover:opacity-100 transition-opacity"
        title="移除封面图"
      >
        <Icon icon="lucide:x" class="w-4 h-4" />
      </button>
    </div>

    <!-- 上传按钮 -->
    <div class="flex items-center gap-3">
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        class="hidden"
        @change="handleFileSelect"
      />
      <button
        type="button"
        @click="selectFile"
        :disabled="isUploading"
        class="flex items-center gap-2 px-4 py-2 rounded-lg border border-dashed border-gray-300 dark:border-gray-600
               hover:border-primary-from dark:hover:border-primary-from
               text-light-text-secondary dark:text-dark-text-secondary
               hover:text-primary-from dark:hover:text-primary-from
               transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Icon
          :icon="isUploading ? 'lucide:loader-2' : 'lucide:upload'"
          :class="{ 'animate-spin': isUploading }"
          class="w-5 h-5"
        />
        {{ isUploading ? '上传中...' : imageUrl ? '更换封面图' : '上传封面图' }}
      </button>

      <!-- URL 输入 -->
      <div class="flex-1 flex items-center gap-2">
        <span class="text-sm text-light-text-muted dark:text-dark-text-muted">或输入 URL:</span>
        <input
          :value="imageUrl"
          @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
          type="url"
          placeholder="https://..."
          class="flex-1 px-3 py-1.5 rounded-lg border border-light-border dark:border-dark-border
                 bg-white dark:bg-gray-800
                 text-light-text-primary dark:text-dark-text-primary text-sm
                 placeholder-light-text-muted dark:placeholder-dark-text-muted
                 focus:outline-none focus:ring-2 focus:ring-primary-from"
        />
      </div>
    </div>

    <!-- 提示信息 -->
    <p class="text-xs text-light-text-muted dark:text-dark-text-muted">
      支持 JPG、PNG、GIF、WebP 格式，最大 5MB。建议尺寸 16:9
    </p>
  </div>
</template>
