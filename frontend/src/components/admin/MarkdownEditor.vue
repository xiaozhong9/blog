<script setup lang="ts">
import { ref, watch } from 'vue'
import { MdEditor, type ToolbarNames } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { uploadImage } from '@/utils/imageUpload'
import { notifySuccess, notifyError } from '@/utils/notification'

// Props
const props = defineProps<{
  modelValue: string
  placeholder?: string
  readonly?: boolean
  category?: string  // 图片分类（blog、projects、life 等）
}>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// 编辑器引用
const editorRef = ref<InstanceType<typeof MdEditor>>()

// 当前内容
const content = ref(props.modelValue)

// 监听 modelValue 变化
watch(() => props.modelValue, (newVal) => {
  content.value = newVal
})

// 监听内容变化
watch(content, (newVal) => {
  emit('update:modelValue', newVal)
})

// 工具栏配置
const toolbars: ToolbarNames[] = [
  'bold',
  'underline',
  'italic',
  'strikeThrough',
  '-',
  'title',
  'sub',
  'sup',
  'quote',
  'unorderedList',
  'orderedList',
  'task',
  '-',
  'codeRow',
  'code',
  'link',
  'image',
  'table',
  '-',
  'revoke',
  'next',
  'save',
  '=',
  'pageFullscreen',
  'fullscreen',
  'preview',
  'htmlPreview',
  'catalog',
]

/**
 * 自定义图片上传
 * 支持拖拽、粘贴、选择文件
 * md-editor-v3 会自动处理所有图片上传操作（包括粘贴）
 */
const handleUpload = async (
  files: File[],
  callback: (urls: string[]) => void
) => {
  try {
    const urls: string[] = []

    for (const file of files) {
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        notifyError(`不支持的文件类型: ${file.type}`, '上传失败')
        continue
      }

      // 验证文件大小（10MB）
      const maxSize = 10 * 1024 * 1024
      if (file.size > maxSize) {
        notifyError('文件过大，最大支持 10MB', '上传失败')
        continue
      }

      // 上传图片（传递 category 参数）
      const result = await uploadImage(file, props.category || 'general')
      urls.push(result.url)

      notifySuccess(`图片 ${file.name} 上传成功`, '上传成功')
    }

    callback(urls)
  } catch (error) {
    console.error('图片上传失败:', error)
    notifyError('图片上传失败，请重试', '上传失败')
    callback([])
  }
}

// 暴露编辑器实例供父组件使用
defineExpose({
  editorRef,
})
</script>

<template>
  <MdEditor
    ref="editorRef"
    v-model="content"
    :placeholder="placeholder || '开始编写你的文章...'"
    :readonly="readonly"
    :toolbars="toolbars"
    @onUploadImg="handleUpload"
    style="height: 600px;"
  />
</template>

<style scoped>
/* 编辑器样式优化 */
:deep(.md-editor) {
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

:deep(.dark .md-editor) {
  border-color: #1e293b;
}

:deep(.md-editor .md-editor-toolbar) {
  border-radius: 0.5rem 0.5rem 0 0;
}

:deep(.md-editor-preview) {
  background-color: #ffffff;
}

:deep(.dark .md-editor-preview) {
  background-color: #1e293b;
}

/* 预览区域样式 */
:deep(.md-editor-preview) {
  padding: 1rem;
}

:deep(.md-editor-preview h1) {
  font-size: 2em;
  font-weight: 700;
  margin-top: 0.67em;
  margin-bottom: 0.67em;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.3em;
}

:deep(.md-editor-preview h2) {
  font-size: 1.5em;
  font-weight: 600;
  margin-top: 0.83em;
  margin-bottom: 0.83em;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.3em;
}

:deep(.md-editor-preview img) {
  max-width: 100%;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

:deep(.md-editor-preview code) {
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25rem;
  font-size: 0.9em;
}

:deep(.md-editor-preview pre) {
  background-color: #282c34;
  color: #abb2bf;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

:deep(.md-editor-preview pre code) {
  background-color: transparent;
  padding: 0;
}
</style>
