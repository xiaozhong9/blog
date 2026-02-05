/**
 * Authentication Store - 使用真实 API
 * 从硬编码密码迁移到 JWT 认证
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/api/services'
import { apiClient } from '@/api/client'
import type { User } from '@/api/types'
import { notifySuccess, notifyError } from '@/utils/notification'
import { logger } from '@/utils/logger'

const TOKEN_STORAGE_KEY = 'access_token'
const REFRESH_TOKEN_STORAGE_KEY = 'refresh_token'

export const useAuthStore = defineStore('auth', () => {
  // 当前用户
  const user = ref<User | null>(null)

  // 登录状态
  const isLoggedIn = computed(() => user.value !== null)

  // 加载状态
  const loading = ref(false)

  // 错误信息
  const error = ref<string | null>(null)

  /**
   * 初始化认证状态
   * 检查 localStorage 中是否有 token
   */
  const initializeAuth = async () => {
    const accessToken = localStorage.getItem(TOKEN_STORAGE_KEY)
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)

    if (accessToken && refreshToken) {
      // 设置 tokens 到 api client
      apiClient.setTokens(accessToken, refreshToken)

      // 尝试获取用户信息
      await fetchCurrentUser()
    }
  }

  /**
   * 登录
   */
  const login = async (username: string, password: string): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await authService.login({ username, password })
      // 保存用户信息
      user.value = response.user
      // tokens 已在 authService 中保存到 localStorage 和 apiClient
      notifySuccess(`欢迎回来，${user.value?.nickname || user.value?.username}！`, '登录成功')
      return true
    } catch (e: any) {
      logger.error('登录失败', e)
      notifyError(e.message || '登录失败，请检查用户名和密码', '登录失败')
      error.value = e.message || '登录失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 注册
   */
  const register = async (userData: {
    username: string
    email: string
    password: string
    nickname?: string
  }): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await authService.register(userData)

      // 保存用户信息
      user.value = response.user

      notifySuccess('注册成功！欢迎加入 Nano Banana', '注册成功')
      return true
    } catch (e: any) {
      logger.error('注册失败', e)
      notifyError(e.message || '注册失败', '注册失败')
      error.value = e.message || '注册失败'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 登出
   */
  const logout = async () => {
    loading.value = true
    error.value = null

    try {
      // 调用登出 API
      await authService.logout()
    } catch (e) {
      logger.error('登出 API 调用失败', e)
    } finally {
      // 无论 API 是否成功，都清除本地状态
      user.value = null
      apiClient.clearTokens()
      loading.value = false
    }
  }

  /**
   * 获取当前用户信息
   */
  const fetchCurrentUser = async () => {
    loading.value = true
    error.value = null

    try {
      const userData = await authService.getCurrentUser()
      user.value = userData
    } catch (e: any) {
      logger.error('获取用户信息失败', e)

      // 如果获取用户信息失败，可能是 token 过期
      // 清除本地认证状态
      if (e.response?.status === 401) {
        user.value = null
        apiClient.clearTokens()
      }

      error.value = e.message || '获取用户信息失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 检查是否已登录（兼容旧接口）
   * @deprecated 使用 isLoggedIn computed 属性代替
   */
  const checkLoginStatus = () => {
    // 不需要做任何事，isLoggedIn computed 会自动计算
    return isLoggedIn.value
  }

  /**
   * 更新用户信息
   */
  const updateUser = (updates: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...updates }
    }
  }

  return {
    user,
    isLoggedIn,
    loading,
    error,

    // 方法
    initializeAuth,
    login,
    register,
    logout,
    fetchCurrentUser,
    checkLoginStatus,
    updateUser,
  }
})
