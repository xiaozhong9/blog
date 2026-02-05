/**
 * API 类型定义（匹配后端 Django API）
 */

// ==================== 通用类型 ====================

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface ApiError {
  code: number
  message: string
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  count: number
  page: number
  page_size: number
  results: T[]
}

// ==================== 用户/认证 ====================

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  password_confirm: string
  email?: string
  nickname?: string
}

export interface AuthResponse {
  refresh: string
  access: string
  user: User
}

export interface User {
  id: number
  username: string
  email?: string
  nickname: string
  avatar: string
  bio: string
  website: string
  role: 'admin' | 'editor' | 'user'
  is_verified: boolean
  articles_count: number
  comments_count: number
  created_at: string
}

// ==================== 文章 ====================

/**
 * Elasticsearch 返回的扁平化文章数据（列表接口使用）
 * ES 文档结构定义在 backend/search/models.py 的 ArticleDocument
 */
export interface ArticleListItem {
  id: number
  slug: string
  title: string
  description: string
  content: string
  author_username: string
  author_nickname: string
  category_name: string
  category_slug: string
  tags_names: string[]
  locale: 'zh' | 'en'
  status: 'draft' | 'published' | 'archived'
  featured: boolean
  reading_time: number
  cover_image: string
  created_at: string
  updated_at: string
  published_at: string
  view_count: number
  like_count: number
  comment_count: number
  // 项目专属字段
  stars?: number
  forks?: number
  repo?: string
  demo?: string
  tech_stack?: string[]
}

/**
 * 完整的文章数据（详情接口使用，来自 MySQL）
 */
export interface Article {
  id: number
  slug: string
  title: string
  description: string
  content: string
  author: Author
  category: Category
  category_type: string
  tags: Tag[]
  locale: 'zh' | 'en'
  reading_time: number
  status: 'draft' | 'published' | 'archived'
  featured: boolean
  cover_image: string
  keywords: string
  view_count: number
  like_count: number
  comment_count: number
  // 项目专属字段
  stars?: number
  forks?: number
  repo?: string
  demo?: string
  tech_stack?: string[]
  project_status?: string
  created_at: string
  updated_at: string
  published_at: string
}

export interface Author {
  id: number
  username: string
  nickname: string
  avatar: string
}

export interface Category {
  id: number
  slug: string
  name: string
  category_type: 'blog' | 'projects' | 'life' | 'notes'
  icon?: string
  description?: string
  keywords?: string
  sort_order: number
  articles_count: number
  created_at: string
  updated_at: string
}

export interface Tag {
  id: number
  slug: string
  name: string
  color?: string
  description?: string
  keywords?: string
  articles_count: number
  created_at: string
  updated_at: string
}

// ==================== 评论 ====================

export interface Comment {
  id: number
  article: number
  article_title?: string
  article_slug?: string
  article_category?: string
  author?: CommentAuthor
  guest_name: string
  parent?: number | null
  content: string
  is_markdown: boolean
  status: 'pending' | 'approved' | 'spam' | 'deleted'
  like_count: number
  created_at: string
  updated_at: string
  approved_at?: string | null
  replies?: Comment[]
}

export interface CommentAuthor {
  id: number
  username: string
  nickname: string
  avatar: string
  email: string
}

export interface CommentCreateRequest {
  article: number
  parent?: number
  content: string
  guest_name?: string
  guest_email?: string
  guest_url?: string
}

// ==================== 统计 ====================

export interface OverviewStats {
  total_articles: number
  total_users: number
  total_comments: number
  total_views: number
  articles_published: number
  articles_draft: number
  today_articles: number
  today_users: number
  today_comments: number
  today_views: number
  popular_categories: PopularCategory[]
  popular_tags: PopularTag[]
}

export interface PopularCategory {
  slug: string
  name: string
  article_count: number
}

export interface PopularTag {
  slug: string
  name: string
  color: string
  article_count: number
}

export interface PopularArticle {
  id: number
  slug: string
  title: string
  description: string
  cover_image: string
  view_count: number
  like_count: number
  comment_count: number
  created_at: string
  author: Author
  category: {
    slug: string
    name: string
  }
}

// ==================== 搜索 ====================

export interface SearchResult {
  id: number
  title: string
  description: string
  slug?: string
  category?: {
    id: number
    name: string
    slug: string
  }
  tags?: Array<{
    id: number
    name: string
    slug: string
  }>
  locale: 'zh' | 'en'
  reading_time: number
  featured: boolean
  view_count: number
  published_at: string
  highlight?: {
    title?: string[]
    description?: string[]
    content?: string[]
  }
}

export interface SearchResponse {
  items: SearchResult[]
  total: number
  page: number
  page_size: number
  query: string
}

export interface SearchSuggestResponse {
  suggestions: string[]
}

export interface SearchParams {
  q: string  // 搜索关键词
  category?: string  // 分类过滤
  tags?: string  // 标签过滤 (逗号分隔)
  locale?: 'zh' | 'en'  // 语言过滤
  page?: number  // 页码
  page_size?: number  // 每页数量
}
