/**
 * API 客户端 - 封装 fetch 请求
 */

import type { ApiResponse, ApiError } from './types'
import { API_BASE_URL } from './config'

class ApiClient {
  private baseURL: string
  private accessToken: string | null = null
  private refreshToken: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.loadTokens()
  }

  /**
   * 获取认证头
   */
  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`
    }

    return headers
  }

  /**
   * 保存 tokens 到 localStorage
   */
  private saveTokens(access: string, refresh: string) {
    this.accessToken = access
    this.refreshToken = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  /**
   * 从 localStorage 加载 tokens
   */
  private loadTokens() {
    this.accessToken = localStorage.getItem('access_token')
    this.refreshToken = localStorage.getItem('refresh_token')
  }

  /**
   * 清除 tokens
   */
  clearTokens() {
    this.accessToken = null
    this.refreshToken = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  /**
   * 设置 tokens（用于登录后）
   */
  setTokens(access: string, refresh: string) {
    this.saveTokens(access, refresh)
  }

  /**
   * 通用请求方法
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`

    const config: RequestInit = {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()

      // 处理 401 未授权错误
      if (response.status === 401 && this.refreshToken) {
        // 尝试刷新 token
        const newTokens = await this.refreshAccessToken()
        if (newTokens) {
          // 重试原请求
          return this.request<T>(endpoint, options)
        }
      }

      // 检查响应状态
      if (!response.ok) {
        const error = {
          code: data.code || response.status,
          message: data.message || '请求失败',
          errors: data.errors || data.detail,
        } as ApiError
        throw error
      }

      return data
    } catch (error) {
      throw error
    }
  }

  /**
   * GET 请求
   */
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const url = params ? `${endpoint}?${new URLSearchParams(params)}` : endpoint
    const response = await this.request<T>(url, { method: 'GET' })
    return response.data
  }

  /**
   * POST 请求
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    const response = await this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return response.data
  }

  /**
   * PUT 请求
   */
  async put<T>(endpoint: string, data?: any): Promise<T> {
    const response = await this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
    return response.data
  }

  /**
   * PATCH 请求
   */
  async patch<T>(endpoint: string, data?: any): Promise<T> {
    const response = await this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
    return response.data
  }

  /**
   * DELETE 请求
   */
  async delete<T>(endpoint: string): Promise<T> {
    const response = await this.request<T>(endpoint, { method: 'DELETE' })
    // DELETE 请求可能没有 data 字段，返回整个响应
    return (response.data ?? response) as T
  }

  /**
   * 刷新 access token
   */
  private async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) {
      this.clearTokens()
      return false
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refreshToken }),
      })

      if (response.ok) {
        const data = await response.json()
        // 后端配置了 ROTATE_REFRESH_TOKENS=True，会返回新的 refresh_token
        const newAccess = data.data.access
        const newRefresh = data.data.refresh || this.refreshToken
        this.saveTokens(newAccess, newRefresh)
        return true
      } else {
        this.clearTokens()
        return false
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
      this.clearTokens()
      return false
    }
  }
}

// 创建全局 API 客户端实例
export const apiClient = new ApiClient(API_BASE_URL)
