import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useContentStore } from './content.api'
import type { SearchResult, SearchHistoryItem, SearchOptions } from '@/types/search'

const SEARCH_HISTORY_KEY = 'search_history'
const MAX_HISTORY_ITEMS = 10

export const useSearchStore = defineStore('search', () => {
  const contentStore = useContentStore()

  // Search state
  const query = ref('')
  const isOpen = ref(false)
  const selectedIndex = ref(0)
  const searchHistory = ref<SearchHistoryItem[]>([])
  const isSearching = ref(false)

  // Search results (now loaded from Elasticsearch)
  const results = ref<SearchResult[]>([])

  // Watch for query changes and trigger search
  watch(query, async (newQuery) => {
    if (newQuery.trim()) {
      await performSearch(newQuery)
    } else {
      results.value = []
    }
  })

  // Perform search using Elasticsearch
  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      results.value = []
      return
    }

    isSearching.value = true
    try {
      const { results: searchResults } = await contentStore.searchPosts({
        search: searchQuery,
        draft: false,
      })

      results.value = searchResults.map(post => ({
        id: post.slug,
        title: post.title,
        description: post.description,
        category: post.category,
        tags: post.tags,
        slug: post.slug,
      }))
    } catch (e) {
      // Fallback to client-side filtering if ES fails
      const filtered = contentStore.filterPosts({
        search: searchQuery,
        draft: false,
      })
      results.value = filtered.map(post => ({
        id: post.slug,
        title: post.title,
        description: post.description,
        category: post.category,
        tags: post.tags,
        slug: post.slug,
      }))
    } finally {
      isSearching.value = false
    }
  }

  // Load search history from localStorage
  const loadHistory = () => {
    try {
      const saved = localStorage.getItem(SEARCH_HISTORY_KEY)
      if (saved) {
        searchHistory.value = JSON.parse(saved)
      }
    } catch (e) {
      console.error('Failed to load search history:', e)
    }
  }

  // Save search history to localStorage
  const saveHistory = () => {
    try {
      localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(searchHistory.value))
    } catch (e) {
      console.error('Failed to save search history:', e)
    }
  }

  // Add query to search history
  const addToHistory = (q: string) => {
    if (!q.trim()) return

    // Remove existing entry if present
    searchHistory.value = searchHistory.value.filter(item => item.query !== q)

    // Add new entry at the beginning
    searchHistory.value.unshift({
      query: q,
      timestamp: Date.now(),
    })

    // Keep only MAX_HISTORY_ITEMS
    searchHistory.value = searchHistory.value.slice(0, MAX_HISTORY_ITEMS)

    saveHistory()
  }

  // Clear search history
  const clearHistory = () => {
    searchHistory.value = []
    saveHistory()
  }

  // Open search modal
  const open = () => {
    isOpen.value = true
    selectedIndex.value = 0
  }

  // Close search modal
  const close = () => {
    isOpen.value = false
    query.value = ''
    results.value = []
    selectedIndex.value = 0
  }

  // Set search query
  const setQuery = (q: string) => {
    query.value = q
    selectedIndex.value = 0
  }

  // Navigate results with keyboard
  const navigate = (direction: 'up' | 'down') => {
    const maxIndex = results.value.length - 1
    if (direction === 'up') {
      selectedIndex.value = selectedIndex.value > 0 ? selectedIndex.value - 1 : maxIndex
    } else {
      selectedIndex.value = selectedIndex.value < maxIndex ? selectedIndex.value + 1 : 0
    }
  }

  // Select result
  const selectResult = () => {
    if (results.value[selectedIndex.value]) {
      const result = results.value[selectedIndex.value]
      addToHistory(query.value)
      close()
      // Navigate to post
      return result.slug
    }
    return null
  }

  // Get recent searches (from history)
  const recentSearches = computed(() => {
    return searchHistory.value.slice(0, 5)
  })

  // Get popular searches from real tags and article data
  const popularSearches = computed(() => {
    // 1. 从所有文章的标签中提取热门标签
    const allTags = new Set<string>()
    contentStore.posts.forEach(post => {
      if (!post.draft) {
        post.tags.forEach(tag => allTags.add(tag))
      }
    })

    // 2. 按浏览量排序文章，提取标题中的关键词
    const popularPosts = [...contentStore.posts]
      .filter(p => !p.draft)
      .sort((a, b) => (b.views || 0) - (a.views || 0))
      .slice(0, 10)

    // 3. 组合标签和文章标题关键词
    const suggestions = [
      ...Array.from(allTags).slice(0, 5),
      ...popularPosts.map(p => p.title.split(' ').slice(0, 3).join(' ')).slice(0, 3)
    ]

    // 4. 去重并限制数量
    return Array.from(new Set(suggestions)).slice(0, 8)
  })

  return {
    query,
    isOpen,
    selectedIndex,
    searchHistory,
    results,
    isSearching,
    recentSearches,
    popularSearches,
    loadHistory,
    addToHistory,
    clearHistory,
    open,
    close,
    setQuery,
    navigate,
    selectResult,
  }
})
