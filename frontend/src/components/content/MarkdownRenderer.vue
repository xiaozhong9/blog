<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps<{
  content: string
}>()

const markdownHtml = ref('')
const codeBlocks = ref<Array<{ id: string; code: string; language: string }>>([])
const copiedStates = ref<Record<string, boolean>>({})

// Parse markdown and convert to HTML
const renderMarkdown = (md: string) => {
  let html = md
  let blockIndex = 0

  // Code blocks with language - must be processed first!
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const id = `code-block-${blockIndex++}`
    const language = lang || 'text'
    codeBlocks.value.push({ id, code, language })
    return `<div class="code-block-container" data-block-id="${id}"></div>`
  })

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3 id="$1">$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2 id="$1">$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1 id="$1">$1</h1>')

  // Bold and italic
  html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>')

  // Code blocks (inline)
  html = html.replace(/`([^`]+)`/gim, '<code class="inline-code">$1</code>')

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" class="text-primary-from hover:underline">$1</a>')

  // Images - convert ![alt](url) to <img> tags
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/gim, (match, alt, url) => {
    // Convert relative /media/ paths to full backend URLs
    const imageUrl = url.startsWith('/media/')
      ? `${import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'}${url}`
      : url
    return `<img src="${imageUrl}" alt="${alt}" class="rounded-lg my-4 max-w-full" loading="lazy" />`
  })

  // Paragraphs
  html = html.split('\n\n').map(para => {
    if (!para.startsWith('<') && !para.startsWith('div')) {
      return `<p>${para}</p>`
    }
    return para
  }).join('\n')

  // Lists
  html = html.replace(/^\* (.*$)/gim, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul class="list-disc list-inside">$1</ul>')

  return html
}

onMounted(() => {
  markdownHtml.value = renderMarkdown(props.content)

  // After rendering, inject code blocks into their containers
  setTimeout(() => {
    codeBlocks.value.forEach(block => {
      const container = document.querySelector(`[data-block-id="${block.id}"]`)
      if (container) {
        container.innerHTML = `
          <div class="relative group rounded-lg overflow-hidden my-6" style="background-color: #282c34;">
            <!-- 复制按钮和语言标签 -->
            <div class="flex items-center justify-between px-4 py-2" style="background-color: #21252b; border-bottom: 1px solid #3e4451;">
              <span class="text-xs font-medium" style="color: #abb2bf;">${block.language}</span>
              <button
                onclick="window.copyCodeBlock('${block.id}')"
                class="flex items-center gap-1.5 px-2 py-1 text-xs rounded
                       hover:bg-gray-700
                       text-gray-200 hover:text-white
                       transition-colors"
                title="复制代码"
              >
                <span class="copy-icon-${block.id}">复制</span>
              </button>
            </div>
            <pre class="p-4 overflow-x-auto !bg-transparent !m-0" style="color: #abb2bf;"><code class="text-sm font-mono leading-relaxed" style="color: #abb2bf;">${escapeHtml(block.code)}</code></pre>
          </div>
        `
      }
    })
  }, 0)
})

const escapeHtml = (text: string) => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// Copy code functionality
const copyCode = async (blockId: string) => {
  const block = codeBlocks.value.find(b => b.id === blockId)
  if (!block) return

  try {
    await navigator.clipboard.writeText(block.code)
    copiedStates.value[blockId] = true

    // Update button text
    const btnIcon = document.querySelector(`.copy-icon-${blockId}`)
    if (btnIcon) {
      btnIcon.textContent = '已复制！'
    }

    // Reset after 2 seconds
    setTimeout(() => {
      copiedStates.value[blockId] = false
      const newBtnIcon = document.querySelector(`.copy-icon-${blockId}`)
      if (newBtnIcon) {
        newBtnIcon.textContent = '复制'
      }
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// Expose to window for onclick handler
declare global {
  interface Window {
    copyCodeBlock: (id: string) => Promise<void>
  }
}

if (typeof window !== 'undefined') {
  window.copyCodeBlock = copyCode
}
</script>

<template>
  <div class="markdown-renderer">
    <div v-html="markdownHtml" />
  </div>
</template>

<style>
/* Base prose styles */
.markdown-renderer {
  @apply text-light-text-primary dark:text-dark-text-primary;
  line-height: 1.75;
}

.markdown-renderer h2 {
  @apply text-2xl font-bold mt-12 mb-6 text-light-text-primary dark:text-dark-text-primary;
  scroll-margin-top: 100px;
}

.markdown-renderer h3 {
  @apply text-xl font-bold mt-8 mb-4 text-light-text-primary dark:text-dark-text-primary;
  scroll-margin-top: 100px;
}

.markdown-renderer p {
  @apply mb-6 leading-relaxed;
}

.markdown-renderer ul {
  @apply mb-6 ml-6;
}

.markdown-renderer a {
  @apply text-primary-from hover:text-primary-to transition-colors;
}

.markdown-renderer :deep(.inline-code) {
  @apply px-1 py-0.5 rounded font-mono text-sm;
  background-color: #f3f4f6;
  color: #d73a49;
}

.dark .markdown-renderer :deep(.inline-code) {
  background-color: #3e4451;
  color: #e06c75;
}

.markdown-renderer :deep(.code-block-container) {
  @apply my-6;
}
</style>
