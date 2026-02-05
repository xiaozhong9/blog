<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'

const isOpen = ref(false)
const shareData = ref({
  title: '',
  url: '',
  description: '',
})

const openShare = () => {
  if (navigator.share) {
    navigator.share({
      title: shareData.value.title,
      url: shareData.value.url,
      text: shareData.value.description,
    })
  } else {
    isOpen.value = !isOpen.value
  }
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(shareData.value.url)
    alert('链接已复制到剪贴板')
    isOpen.value = false
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const shareToTwitter = () => {
  const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareData.value.title)}&url=${encodeURIComponent(shareData.value.url)}`
  window.open(url, '_blank')
}

const shareToWeibo = () => {
  const url = `https://service.weibo.com/share/share.php?title=${encodeURIComponent(shareData.value.title)}&url=${encodeURIComponent(shareData.value.url)}`
  window.open(url, '_blank')
}

// 暴露方法供外部调用
defineExpose({
  setShareData: (data: { title: string; url: string; description: string }) => {
    shareData.value = data
  },
})
</script>

<template>
  <div class="share-container">
    <!-- 分享按钮 -->
    <button
      @click="openShare"
      class="share-button"
      title="分享"
    >
      <Icon icon="lucide:share-2" class="w-4 h-4" />
    </button>

    <!-- 分享弹窗 -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-150"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="isOpen"
          class="share-modal"
          @click="isOpen = false"
        >
          <div
            class="share-content"
            @click.stop
          >
            <h3 class="text-lg font-semibold mb-4 text-light-text-primary dark:text-dark-text-primary">
              分享到
            </h3>

            <!-- 分享选项 -->
            <div class="grid grid-cols-2 gap-3">
              <button
                @click="shareToTwitter"
                class="share-option twitter"
              >
                <Icon icon="lucide:twitter" class="w-5 h-5" />
                <span>Twitter</span>
              </button>

              <button
                @click="shareToWeibo"
                class="share-option weibo"
              >
                <Icon icon="lucide:rss" class="w-5 h-5" />
                <span>微博</span>
              </button>

              <button
                @click="copyLink"
                class="share-option copy"
              >
                <Icon icon="lucide:link" class="w-5 h-5" />
                <span>复制链接</span>
              </button>
            </div>

            <!-- 关闭按钮 -->
            <button
              @click="isOpen = false"
              class="mt-4 w-full py-2 text-sm text-light-text-muted dark:text-dark-text-muted hover:text-light-text-primary dark:hover:text-dark-text-primary transition-colors"
            >
              取消
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.share-button {
  padding: 0.5rem;
  border-radius: 0.5rem;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  transition: all 0.2s;
}

.share-button:hover {
  background: rgba(96, 165, 250, 0.9);
}

.share-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.share-content {
  background: white;
  dark:bg: dark-bg;
  border-radius: 1rem;
  padding: 1.5rem;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.share-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.share-option.twitter {
  background: #1DA1F2;
  color: white;
}

.share-option.weibo {
  background: #E6162D;
  color: white;
}

.share-option.copy {
  background: #6366f1;
  color: white;
}

.share-option:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}
</style>
