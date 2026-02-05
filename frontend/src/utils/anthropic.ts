import type { Message } from '@/types/ai'

const API_URL = 'https://api.anthropic.com/v1/messages'
const API_VERSION = '2023-06-01'

/**
 * 调用 Anthropic Claude API
 */
export async function anthropicCall(
  messages: Message[],
  systemPrompt?: string,
  model = 'claude-3-haiku-20240307'
): Promise<string> {
  // 从环境变量获取 API key
  const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY

  if (!apiKey) {
    throw new Error(
      'Anthropic API key is missing. ' +
      'Please set VITE_ANTHROPIC_API_KEY in your .env file.'
    )
  }

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': API_VERSION,
        'dangerously-allow-browser': 'true', // 仅用于开发环境
      },
      body: JSON.stringify({
        model,
        max_tokens: 1024,
        system: systemPrompt,
        messages: messages.map(m => ({
          role: m.role,
          content: m.content,
        })),
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(
        `API Error (${response.status}): ${errorData.error?.message || response.statusText}`
      )
    }

    const data = await response.json()
    return data.content[0]?.text || ''
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Unknown error occurred')
  }
}

/**
 * 获取可用模型列表
 */
export const AVAILABLE_MODELS = {
  haiku: 'claude-3-haiku-20240307',
  sonnet: 'claude-3-sonnet-20240229',
  opus: 'claude-3-opus-20240229',
} as const

export type ModelName = keyof typeof AVAILABLE_MODELS
