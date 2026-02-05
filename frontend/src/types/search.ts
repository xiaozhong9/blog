export interface SearchResult {
  id: string
  title: string
  description: string
  category: string
  tags: string[]
  slug: string
}

export interface SearchHistoryItem {
  query: string
  timestamp: number
}

export interface SearchOptions {
  limit?: number
  category?: string
  tags?: string[]
}
