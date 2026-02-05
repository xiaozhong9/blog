import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Message } from '@/types/ai'
import { anthropicCall } from '@/utils/anthropic'

export const useAIChatStore = defineStore('aiChat', () => {
  const isOpen = ref(false)
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 系统提示词
  const systemPrompt = `你是一个友好的博客助手，帮助用户了解和探索 Nano Banana 博客的内容。

你的职责：
1. 回答关于博客内容的问题
2. 推荐相关文章
3. 总结文章要点
4. 提供技术建议和见解

博客信息：
- 博客名称：Nano Banana
- 主要内容：技术文章、Vue.js、TypeScript、前端开发
- 语言支持：中文和英文

请用友好、专业的方式回答，保持简洁。`

  // 切换开关
  const toggleOpen = () => {
    isOpen.value = !isOpen.value
  }

  // 发送消息
  const sendMessage = async (userMessage: string) => {
    // 添加用户消息
    messages.value.push({
      role: 'user',
      content: userMessage,
    })

    isLoading.value = true
    error.value = null

    try {
      // 调用 Anthropic API
      const response = await anthropicCall([
        ...messages.value,
      ], systemPrompt)

      // 添加 AI 回复
      messages.value.push({
        role: 'assistant',
        content: response,
      })
    } catch (err) {
      error.value = err instanceof Error ? err.message : '发送消息失败'
      console.error('AI Chat Error:', err)

      // 添加错误消息
      messages.value.push({
        role: 'assistant',
        content: '抱歉，我遇到了一些问题。请稍后再试。\n\n如果问题持续存在，请检查 API 密钥配置。',
      })
    } finally {
      isLoading.value = false
    }
  }

  // 清空消息
  const clearMessages = () => {
    messages.value = []
    error.value = null
  }

  // 获取消息历史（用于 API 调用）
  const messageHistory = computed(() => messages.value)

  return {
    isOpen,
    messages,
    isLoading,
    error,
    systemPrompt,
    toggleOpen,
    sendMessage,
    clearMessages,
    messageHistory,
  }
})
