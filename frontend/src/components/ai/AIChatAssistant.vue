<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import { useAIChatStore } from '@/stores/aiChat'

const { t } = useI18n()
const aiChatStore = useAIChatStore()

const { isOpen, messages, isLoading } = storeToRefs(aiChatStore)
const inputMessage = ref('')
const chatContainer = ref<HTMLElement>()
const inputRef = ref<HTMLInputElement>()

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return

  inputMessage.value = ''
  await aiChatStore.sendMessage(message)

  // 滚动到底部
  await nextTick()
  scrollToBottom()
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 处理快捷键
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 清空聊天
const clearChat = () => {
  aiChatStore.clearMessages()
}

// 打开时聚焦输入框
const onOpen = () => {
  nextTick(() => {
    inputRef.value?.focus()
  })
}

// 格式化消息
const formatMessage = (content: string) => {
  // 简单的 Markdown 格式化
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="px-1 py-0.5 bg-light-bg dark:bg-dark-bg rounded text-sm">$1</code>')
    .replace(/\n/g, '<br>')
}

// 切换开关时聚焦
watch(() => isOpen.value, (isOpen) => {
  if (isOpen) {
    onOpen()
  }
})
</script>

<template>
  <!-- 悬浮按钮 -->
  <Transition
    enter-active-class="transition-all duration-300"
    enter-from-class="opacity-0 scale-75"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition-all duration-200"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-75"
  >
    <button
      v-if="!isOpen"
      @click="aiChatStore.toggleOpen()"
      class="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full
             bg-gradient-to-r from-primary-from to-primary-to
             text-white shadow-lg hover:shadow-xl
             flex items-center justify-center
             transition-all duration-300 hover:scale-110"
      title="AI 助手"
    >
      <Icon icon="lucide:message-circle" class="w-7 h-7" />
    </button>
  </Transition>

  <!-- 聊天窗口 -->
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0 translate-y-4 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition-all duration-200"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-4 scale-95"
    >
      <div
        v-if="isOpen"
        class="fixed bottom-6 right-6 z-50 w-96 max-w-[calc(100vw-3rem)]
               bg-light-surface dark:bg-dark-surface
               rounded-2xl shadow-2xl
               border border-light-border dark:border-dark-border
               flex flex-col max-h-[600px]"
        style="height: 500px;"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3
                    border-b border-light-border dark:border-dark-border">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-gradient-to-r from-primary-from to-primary-to
                        flex items-center justify-center">
              <Icon icon="lucide:bot" class="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 class="font-semibold text-sm text-light-text-primary dark:text-dark-text-primary">
                AI 助手
              </h3>
              <p class="text-xs text-light-text-muted dark:text-dark-text-muted">
                由 Claude 驱动
              </p>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <button
              @click="clearChat"
              class="p-2 rounded-lg text-light-text-muted dark:text-dark-text-muted
                     hover:bg-light-bg dark:hover:bg-dark-bg
                     transition-colors duration-150"
              title="清空聊天"
            >
              <Icon icon="lucide:trash-2" class="w-4 h-4" />
            </button>
            <button
              @click="aiChatStore.toggleOpen()"
              class="p-2 rounded-lg text-light-text-muted dark:text-dark-text-muted
                     hover:bg-light-bg dark:hover:bg-dark-bg
                     transition-colors duration-150"
              title="关闭"
            >
              <Icon icon="lucide:x" class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          ref="chatContainer"
          class="flex-1 overflow-y-auto px-4 py-4 space-y-4"
        >
          <!-- 欢迎消息 -->
          <div
            v-if="messages.length === 0"
            class="text-center py-8"
          >
            <Icon icon="lucide:sparkles" class="w-12 h-12 mx-auto mb-4 text-primary-from opacity-50" />
            <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary">
              你好！我是 AI 助手，可以帮你：
            </p>
            <ul class="text-sm text-light-text-muted dark:text-dark-text-muted mt-3 space-y-1 text-left inline-block">
              <li>• 解答博客内容相关问题</li>
              <li>• 推荐相关文章</li>
              <li>• 总结文章要点</li>
            </ul>
          </div>

          <!-- 消息 -->
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="flex gap-3"
            :class="{ 'flex-row-reverse': message.role === 'user' }"
          >
            <!-- Avatar -->
            <div
              class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center"
              :class="message.role === 'user'
                ? 'bg-gradient-to-r from-primary-from to-primary-to'
                : 'bg-light-bg dark:bg-dark-bg'"
            >
              <Icon
                :icon="message.role === 'user' ? 'lucide:user' : 'lucide:bot'"
                class="w-4 h-4"
                :class="message.role === 'user' ? 'text-white' : 'text-primary-from'"
              />
            </div>

            <!-- Message Content -->
            <div
              class="max-w-[75%] px-4 py-2.5 rounded-2xl text-sm"
              :class="message.role === 'user'
                ? 'bg-gradient-to-r from-primary-from to-primary-to text-white rounded-br-sm'
                : 'bg-light-bg dark:bg-dark-bg text-light-text-primary dark:text-dark-text-primary rounded-bl-sm'"
            >
              <div v-html="formatMessage(message.content)" />
            </div>
          </div>

          <!-- Loading -->
          <div
            v-if="isLoading"
            class="flex gap-3"
          >
            <div class="w-8 h-8 rounded-full bg-light-bg dark:bg-dark-bg
                        flex items-center justify-center">
              <Icon icon="lucide:bot" class="w-4 h-4 text-primary-from" />
            </div>
            <div class="px-4 py-2.5 rounded-2xl rounded-bl-sm
                        bg-light-bg dark:bg-dark-bg">
              <div class="flex gap-1">
                <div class="w-2 h-2 rounded-full bg-primary-from animate-bounce" style="animation-delay: 0ms;"></div>
                <div class="w-2 h-2 rounded-full bg-primary-from animate-bounce" style="animation-delay: 150ms;"></div>
                <div class="w-2 h-2 rounded-full bg-primary-from animate-bounce" style="animation-delay: 300ms;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="p-4 border-t border-light-border dark:border-dark-border">
          <div class="flex items-center gap-2">
            <input
              ref="inputRef"
              v-model="inputMessage"
              type="text"
              placeholder="问我任何关于博客的问题..."
              class="flex-1 px-4 py-2.5 rounded-xl
                     bg-light-bg dark:bg-dark-bg
                     text-light-text-primary dark:text-dark-text-primary
                     placeholder:text-light-text-muted dark:placeholder:text-dark-text-muted
                     border border-light-border dark:border-dark-border
                     focus:outline-none focus:border-primary-from
                     transition-colors duration-150"
              :disabled="isLoading"
              @keydown="handleKeydown"
            />
            <button
              @click="sendMessage"
              :disabled="!inputMessage.trim() || isLoading"
              class="p-2.5 rounded-xl
                     bg-gradient-to-r from-primary-from to-primary-to
                     text-white
                     disabled:opacity-50 disabled:cursor-not-allowed
                     hover:opacity-90 transition-opacity duration-150"
            >
              <Icon
                :icon="isLoading ? 'lucide:loader-2' : 'lucide:send'"
                class="w-5 h-5"
                :class="{ 'animate-spin': isLoading }"
              />
            </button>
          </div>
          <p class="text-xs text-light-text-muted dark:text-dark-text-muted mt-2 text-center">
            AI 可能会犯错，请核实重要信息
          </p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.animate-bounce {
  animation: bounce 1.4s infinite ease-in-out both;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
