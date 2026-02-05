export interface Message {
  role: 'user' | 'assistant'
  content: string
}

export interface AIChatState {
  isOpen: boolean
  messages: Message[]
  isLoading: boolean
  error: string | null
}
