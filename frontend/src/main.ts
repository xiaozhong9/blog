import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from 'vue-router/auto-routes'
import { i18n } from './locales'
import App from './App.vue'
import './styles/main.css'

// 创建路由器
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：保护后台页面
router.beforeEach(async (to, from, next) => {
  // 检查是否是后台管理页面
  if (to.path.startsWith('/admin')) {
    // 登录页面不需要权限检查
    if (to.path === '/admin/login') {
      next()
      return
    }

    // 动态导入 auth store（避免循环依赖）
    const { useAuthStore } = await import('@/stores/auth.api')
    const authStore = useAuthStore()

    // 检查是否有 token
    const hasToken = localStorage.getItem('access_token')

    if (hasToken) {
      // 如果有 token 但没有用户信息，尝试获取
      if (!authStore.user) {
        try {
          await authStore.fetchCurrentUser()
        } catch (e) {
          // 获取用户信息失败，清除 token 并跳转登录页
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          next('/admin/login')
          return
        }
      }

      // 确认用户信息存在后才允许访问
      if (authStore.user) {
        next()
      } else {
        next('/admin/login')
      }
    } else {
      // 没有 token，跳转到登录页
      next('/admin/login')
    }
  } else {
    next()
  }
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
