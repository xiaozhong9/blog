/**
 * API 配置
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const API_ENDPOINTS = {
  // 认证
  AUTH: {
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    LOGOUT: '/auth/logout/',
    ME: '/auth/me/',
    REFRESH: '/auth/refresh/',
  },

  // 用户管理
  USERS: {
    LIST: '/auth/users/',
    DETAIL: (id: string | number) => `/auth/users/${id}/`,
    CHANGE_PASSWORD: '/auth/users/change-password/',
    PROFILE: '/auth/users/profile/',
  },

  // 文章
  ARTICLES: {
    LIST: '/articles/',
    DETAIL: (id: string | number) => `/articles/${id}/`,
    FEATURED: '/articles/featured/',
    POPULAR: '/articles/popular/',
    LIKE: (id: string | number) => `/articles/${id}/like/`,
    UNLIKE: (id: string | number) => `/articles/${id}/unlike/`,
    RELATED: (id: string | number) => `/articles/${id}/related/`,
  },

  // 分类
  CATEGORIES: {
    LIST: '/categories/',
    DETAIL: (slug: string) => `/categories/${slug}/`,
  },

  // 标签
  TAGS: {
    LIST: '/tags/',
    DETAIL: (slug: string) => `/tags/${slug}/`,
  },

  // 评论
  COMMENTS: {
    LIST: '/comments/',
    DETAIL: (id: string | number) => `/comments/${id}/`,
    CREATE: '/comments/',
    LIKE: (id: string | number) => `/comments/${id}/like/`,
    UNLIKE: (id: string | number) => `/comments/${id}/unlike/`,
    REPLIES: (id: string | number) => `/comments/${id}/replies/`,
    APPROVE: (id: string | number) => `/comments/${id}/approve/`,
    REJECT: (id: string | number) => `/comments/${id}/reject/`,
    SPAM: (id: string | number) => `/comments/${id}/spam/`,
  },

  // 统计
  STATS: {
    OVERVIEW: '/stats/overview/',
    POPULAR_ARTICLES: '/stats/popular_articles/',
  },

  // 搜索
  SEARCH: {
    SEARCH: '/search/',
    SUGGEST: '/search/suggest/',
  },
} as const
