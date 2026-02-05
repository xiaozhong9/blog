/**
 * API 服务 - 提供所有 API 调用方法
 */

import { apiClient } from './client'
import { API_ENDPOINTS } from './config'
import type {
  ApiResponse,
  PaginatedResponse,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  Article,
  ArticleListItem,
  Category,
  Tag,
  Comment,
  CommentCreateRequest,
  OverviewStats,
  PopularArticle,
  SearchParams,
  SearchResponse,
  SearchSuggestResponse,
} from './types'

// ==================== 认证服务 ====================

export const authService = {
  /**
   * 用户登录
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const authData = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    )

    // 保存 tokens
    if (authData.access && authData.refresh) {
      apiClient.setTokens(authData.access, authData.refresh)
    }

    return authData
  },

  /**
   * 用户注册
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const authData = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      data
    )
    // 自动登录，保存 tokens
    if (authData.access && authData.refresh) {
      apiClient.setTokens(authData.access, authData.refresh)
    }
    return authData
  },

  /**
   * 用户登出
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT)
    } finally {
      apiClient.clearTokens()
    }
  },

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    return await apiClient.get<User>(API_ENDPOINTS.AUTH.ME)
  },

  /**
   * 检查是否已登录
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  },
}

// ==================== 文章服务 ====================

export const articleService = {
  /**
   * 获取文章列表
   * 注意：列表接口返回的是 ES 扁平化数据 (ArticleListItem)
   * 详情接口返回的是完整数据 (Article)
   */
  async getList(params?: {
    page?: number
    page_size?: number
    category?: string
    tag?: string
    locale?: string
    status?: string
    search?: string
    featured?: boolean
    author?: number
  }): Promise<PaginatedResponse<ArticleListItem>> {
    return await apiClient.get<PaginatedResponse<ArticleListItem>>(
      API_ENDPOINTS.ARTICLES.LIST,
      params
    )
  },

  /**
   * 获取文章详情
   */
  async getDetail(id: string | number): Promise<Article> {
    const endpoint = API_ENDPOINTS.ARTICLES.DETAIL(id)
    return await apiClient.get<Article>(endpoint)
  },

  /**
   * 获取精选文章
   */
  async getFeatured(): Promise<Article[]> {
    return await apiClient.get<Article[]>(API_ENDPOINTS.ARTICLES.FEATURED)
  },

  /**
   * 获取热门文章
   */
  async getPopular(params?: {
    period?: string
    limit?: number
  }): Promise<Article[]> {
    return await apiClient.get<Article[]>(
      API_ENDPOINTS.ARTICLES.POPULAR,
      params
    )
  },

  /**
   * 创建文章
   */
  async create(data: Partial<Article>): Promise<Article> {
    return await apiClient.post<Article>(API_ENDPOINTS.ARTICLES.LIST, data)
  },

  /**
   * 更新文章
   */
  async update(id: string | number, data: Partial<Article>): Promise<Article> {
    const endpoint = API_ENDPOINTS.ARTICLES.DETAIL(id)
    return await apiClient.put<Article>(endpoint, data)
  },

  /**
   * 删除文章
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.ARTICLES.DETAIL(id))
  },

  /**
   * 点赞文章
   */
  async like(id: string | number): Promise<{ like_count: number; liked: boolean }> {
    return await apiClient.post<{ like_count: number; liked: boolean }>(
      API_ENDPOINTS.ARTICLES.LIKE(id)
    )
  },

  /**
   * 取消点赞文章
   */
  async unlike(id: string | number): Promise<{ like_count: number; liked: boolean }> {
    return await apiClient.post<{ like_count: number; liked: boolean }>(
      API_ENDPOINTS.ARTICLES.UNLIKE(id)
    )
  },

  /**
   * 获取相关文章
   */
  async getRelated(id: string | number, limit?: number): Promise<Article[]> {
    return await apiClient.get<Article[]>(
      API_ENDPOINTS.ARTICLES.RELATED(id),
      limit ? { limit } : undefined
    )
  },
}

// ==================== 分类服务 ====================

export const categoryService = {
  /**
   * 获取所有分类
   */
  async getAll(params?: { type?: string }): Promise<Category[]> {
    return await apiClient.get<Category[]>(API_ENDPOINTS.CATEGORIES.LIST, params)
  },

  /**
   * 获取分类列表（别名）
   */
  async getList(params?: { type?: string }): Promise<Category[]> {
    return this.getAll(params)
  },

  /**
   * 获取分类详情
   */
  async getDetail(slug: string): Promise<Category> {
    return await apiClient.get<Category>(API_ENDPOINTS.CATEGORIES.DETAIL(slug))
  },
}

// ==================== 标签服务 ====================

export const tagService = {
  /**
   * 获取所有标签
   */
  async getAll(): Promise<Tag[]> {
    return await apiClient.get<Tag[]>(API_ENDPOINTS.TAGS.LIST)
  },

  /**
   * 获取标签列表（别名）
   */
  async getList(): Promise<Tag[]> {
    return this.getAll()
  },

  /**
   * 获取标签详情
   */
  async getDetail(slug: string): Promise<Tag> {
    return await apiClient.get<Tag>(API_ENDPOINTS.TAGS.DETAIL(slug))
  },
}

// ==================== 评论服务 ====================

export const commentService = {
  /**
   * 获取评论列表
   */
  async getList(params?: {
    article?: number
    author?: number
    status?: string
    top_level?: string
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<Comment>> {
    return await apiClient.get<PaginatedResponse<Comment>>(
      API_ENDPOINTS.COMMENTS.LIST,
      params
    )
  },

  /**
   * 创建评论
   */
  async create(data: CommentCreateRequest): Promise<Comment> {
    return await apiClient.post<Comment>(API_ENDPOINTS.COMMENTS.CREATE, data)
  },

  /**
   * 点赞评论
   */
  async like(id: string | number): Promise<void> {
    await apiClient.post(API_ENDPOINTS.COMMENTS.LIKE(id))
  },

  /**
   * 取消点赞
   */
  async unlike(id: string | number): Promise<void> {
    await apiClient.post(API_ENDPOINTS.COMMENTS.UNLIKE(id))
  },

  /**
   * 获取评论回复
   */
  async getReplies(id: string | number): Promise<Comment[]> {
    return await apiClient.get<Comment[]>(API_ENDPOINTS.COMMENTS.REPLIES(id)) || []
  },

  /**
   * 审核通过评论
   */
  async approve(id: string | number): Promise<Comment> {
    return await apiClient.post<Comment>(API_ENDPOINTS.COMMENTS.APPROVE(id))
  },

  /**
   * 拒绝评论
   */
  async reject(id: string | number): Promise<Comment> {
    return await apiClient.post<Comment>(API_ENDPOINTS.COMMENTS.REJECT(id))
  },

  /**
   * 标记为垃圾评论
   */
  async markSpam(id: string | number): Promise<Comment> {
    return await apiClient.post<Comment>(API_ENDPOINTS.COMMENTS.SPAM(id))
  },

  /**
   * 删除评论
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.COMMENTS.DETAIL(id))
  },

  /**
   * 获取评论详情
   */
  async getDetail(id: string | number): Promise<Comment> {
    return await apiClient.get<Comment>(API_ENDPOINTS.COMMENTS.DETAIL(id))
  },
}

// ==================== 统计服务 ====================

export const statsService = {
  /**
   * 获取总览统计
   */
  async getOverview(): Promise<OverviewStats> {
    return await apiClient.get<OverviewStats>(API_ENDPOINTS.STATS.OVERVIEW)
  },

  /**
   * 获取热门文章
   */
  async getPopularArticles(params?: {
    period?: string
    limit?: number
  }): Promise<PopularArticle[]> {
    return await apiClient.get<PopularArticle[]>(
      API_ENDPOINTS.STATS.POPULAR_ARTICLES,
      params
    )
  },
}

// ==================== 搜索服务 ====================

export const searchService = {
  /**
   * 全文搜索
   */
  async search(params: SearchParams): Promise<SearchResponse> {
    return await apiClient.get<SearchResponse>(
      API_ENDPOINTS.SEARCH.SEARCH,
      params
    )
  },

  /**
   * 搜索建议
   */
  async suggest(query: string): Promise<SearchSuggestResponse> {
    return await apiClient.get<SearchSuggestResponse>(
      API_ENDPOINTS.SEARCH.SUGGEST,
      { q: query }
    )
  },
}

// ==================== 用户服务 ====================

export const userService = {
  /**
   * 获取用户列表
   */
  async getList(params?: {
    page?: number
    page_size?: number
    search?: string
  }): Promise<PaginatedResponse<any>> {
    return await apiClient.get<PaginatedResponse<any>>(
      API_ENDPOINTS.USERS.LIST,
      params
    )
  },

  /**
   * 获取用户详情
   */
  async getDetail(id: string | number): Promise<any> {
    return await apiClient.get<any>(API_ENDPOINTS.USERS.DETAIL(id))
  },

  /**
   * 更新用户
   */
  async update(id: string | number, data: {
    username?: string
    nickname?: string
    email?: string
    avatar?: string
    bio?: string
    role?: string
  }): Promise<any> {
    return await apiClient.put<any>(API_ENDPOINTS.USERS.DETAIL(id), data)
  },

  /**
   * 删除用户
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.USERS.DETAIL(id))
  },

  /**
   * 获取公开的个人信息（用于 About 页面）
   */
  async getProfile(): Promise<any> {
    return await apiClient.get<any>(API_ENDPOINTS.USERS.PROFILE)
  },
}
