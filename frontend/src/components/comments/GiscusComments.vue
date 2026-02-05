<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

interface GiscusProps {
  repo?: string
  repoId?: string
  category?: string
  categoryId?: string
  mapping?: string
  term?: string
  theme?: string
  lang?: string
}

const props = withDefaults(defineProps<GiscusProps>(), {
  repo: 'your-username/your-repo', // 替换为你的 GitHub 仓库
  repoId: '', // 从 https://giscus.app 获取
  category: 'Announcements',
  categoryId: '', // 从 https://giscus.app 获取
  mapping: 'pathname',
  term: '',
  theme: 'preferred_color_scheme',
  lang: 'zh-CN',
})

const container = ref<HTMLElement>()
let scriptElement: HTMLScriptElement | null = null

const loadGiscus = () => {
  if (!container.value) return

  // 清除旧的评论
  if (scriptElement) {
    scriptElement.remove()
  }

  // 清空容器
  container.value.innerHTML = ''

  // 创建 Giscus 脚本
  scriptElement = document.createElement('script')
  scriptElement.src = 'https://giscus.app/client.js'
  scriptElement.async = true
  scriptElement.crossOrigin = 'anonymous'

  // 设置 Giscus 配置
  const giscusConfig: Record<string, string> = {
    'data-repo': props.repo,
    'data-repo-id': props.repoId,
    'data-category': props.category,
    'data-category-id': props.categoryId,
    'data-mapping': props.mapping,
    'data-strict': '0',
    'data-reactions-enabled': '1',
    'data-emit-metadata': '0',
    'data-input-position': 'bottom',
    'data-theme': props.theme,
    'data-lang': props.lang,
    'data-loading': 'lazy',
  }

  if (props.term) {
    giscusConfig['data-term'] = props.term
  }

  // 应用配置
  Object.entries(giscusConfig).forEach(([key, value]) => {
    scriptElement?.setAttribute(key, value)
  })

  container.value.appendChild(scriptElement)
}

onMounted(() => {
  loadGiscus()
})

// 监听主题变化
watch(() => props.theme, () => {
  loadGiscus()
})
</script>

<template>
  <div class="giscus-container mt-12 pt-8 border-t border-light-border dark:border-dark-border">
    <h2 class="text-2xl font-bold mb-6 text-light-text-primary dark:text-dark-text-primary">
      {{ $t('post.comments') || '评论' }}
    </h2>
    <div ref="container" class="giscus"></div>
  </div>
</template>

<style>
.giscus {
  margin-top: 1rem;
}

.giscus-frame {
  border-radius: 0.75rem;
}
</style>
