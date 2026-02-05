import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const ADMIN_PASSWORD_KEY = 'nano_banana_admin_logged_in'
const ADMIN_PASSWORD = 'admin' // 简单密码，生产环境应该使用更安全的方式

export const useAdminStore = defineStore('admin', () => {
  // 登录状态
  const isLoggedIn = ref(false)

  // 检查登录状态
  const checkLoginStatus = () => {
    const stored = localStorage.getItem(ADMIN_PASSWORD_KEY)
    isLoggedIn.value = stored === 'true'
  }

  // 登录
  const login = (password: string): boolean => {
    if (password === ADMIN_PASSWORD) {
      isLoggedIn.value = true
      localStorage.setItem(ADMIN_PASSWORD_KEY, 'true')
      return true
    }
    return false
  }

  // 登出
  const logout = () => {
    isLoggedIn.value = false
    localStorage.removeItem(ADMIN_PASSWORD_KEY)
  }

  // 初始化时检查登录状态
  checkLoginStatus()

  return {
    isLoggedIn,
    login,
    logout,
    checkLoginStatus,
  }
})
