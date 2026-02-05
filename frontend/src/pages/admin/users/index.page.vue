<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { Icon } from '@iconify/vue'
import ScrollReveal from '@/components/effects/ScrollReveal.vue'
import ConfirmDialog from '@/components/ui/ConfirmDialog.vue'
import { userService } from '@/api/services'
import { notifySuccess, notifyError } from '@/utils/notification'

const router = useRouter()

// 用户列表状态
const users = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

// 搜索和筛选
const searchQuery = ref('')
const roleFilter = ref<'all' | 'admin' | 'editor' | 'user'>('all')

// 编辑对话框
const editingUser = ref<any | null>(null)
const showEditDialog = ref(false)
const editForm = ref({
  username: '',
  nickname: '',
  email: '',
  role: 'user',
})

// 删除确认对话框
const showDeleteDialog = ref(false)
const deletingUser = ref<any | null>(null)

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  error.value = null

  try {
    const params: any = {
      page: 1,
      page_size: 100,
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    const data = await userService.getList(params)
    users.value = data.results || []
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载用户失败'
    notifyError('加载用户失败', '加载失败')
  } finally {
    loading.value = false
  }
}

// 过滤后的用户
const filteredUsers = ref<any[]>([])

// 更新过滤
const updateFilters = () => {
  let result = users.value

  if (roleFilter.value !== 'all') {
    result = result.filter(u => u.role === roleFilter.value)
  }

  filteredUsers.value = result
}

// 搜索处理
const handleSearch = () => {
  loadUsers()
}

// 清空搜索
const clearSearch = () => {
  searchQuery.value = ''
  loadUsers()
}

// 打开编辑对话框
const openEditDialog = (user: any) => {
  editingUser.value = user
  editForm.value = {
    username: user.username,
    nickname: user.nickname || '',
    email: user.email,
    role: user.role || 'user',
  }
  showEditDialog.value = true
}

// 关闭编辑对话框
const closeEditDialog = () => {
  editingUser.value = null
  showEditDialog.value = false
}

// 保存用户
const saveUser = async () => {
  if (!editingUser.value) return

  try {
    await userService.update(editingUser.value.id, {
      username: editForm.value.username,
      nickname: editForm.value.nickname,
      email: editForm.value.email,
      role: editForm.value.role,
    })

    notifySuccess('用户信息已更新', '更新成功')
    closeEditDialog()
    await loadUsers()
  } catch (e) {
    notifyError('更新失败，请重试', '更新失败')
  }
}

// 显示删除确认对话框
const showDeleteConfirm = (user: any) => {
  deletingUser.value = user
  showDeleteDialog.value = true
}

// 确认删除
const handleDeleteConfirm = async () => {
  showDeleteDialog.value = false

  try {
    await userService.delete(deletingUser.value.id)
    notifySuccess('用户已删除', '删除成功')
    await loadUsers()
  } catch (e) {
    notifyError('删除失败，请重试', '删除失败')
  } finally {
    deletingUser.value = null
  }
}

// 取消删除
const handleDeleteCancel = () => {
  showDeleteDialog.value = false
  deletingUser.value = null
}

// 获取角色显示名称
const getRoleName = (role: string) => {
  const roles: Record<string, string> = {
    admin: '管理员',
    editor: '编辑',
    user: '用户',
  }
  return roles[role] || role
}

// 获取角色样式
const getRoleClass = (role: string) => {
  const classes: Record<string, string> = {
    admin: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    editor: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    user: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
  }
  return classes[role] || classes.user
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// 初始化
onMounted(() => {
  loadUsers()
})
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- 标题和操作 -->
      <ScrollReveal>
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-light-text-primary dark:text-dark-text-primary mb-2">
              用户管理
            </h1>
            <p class="text-light-text-secondary dark:text-dark-text-secondary">
              管理系统用户和权限
            </p>
          </div>
        </div>
      </ScrollReveal>

      <!-- 搜索栏 -->
      <ScrollReveal class="delay-100">
        <div class="card p-4">
          <div class="flex items-center gap-4 mb-4">
            <div class="flex-1 relative">
              <Icon icon="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-light-text-muted dark:text-dark-text-muted" />
              <input
                v-model="searchQuery"
                @keydown.enter="handleSearch"
                type="text"
                placeholder="搜索用户名、邮箱或昵称..."
                class="w-full pl-10 pr-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                       bg-white dark:bg-gray-800
                       text-light-text-primary dark:text-dark-text-primary
                       placeholder-light-text-muted dark:placeholder-dark-text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary-from"
              />
            </div>
            <button
              @click="handleSearch"
              class="px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90 transition-opacity"
            >
              搜索
            </button>
            <button
              v-if="searchQuery"
              @click="clearSearch"
              class="px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                     text-light-text-primary dark:text-dark-text-primary
                     hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              清空
            </button>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-sm text-light-text-muted dark:text-dark-text-muted">角色筛选:</span>
            <button
              @click="roleFilter = 'all'; updateFilters()"
              class="px-3 py-1 rounded text-sm transition-colors"
              :class="roleFilter === 'all'
                ? 'bg-primary-from text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary hover:bg-gray-200 dark:hover:bg-gray-700'"
            >
              全部
            </button>
            <button
              @click="roleFilter = 'admin'; updateFilters()"
              class="px-3 py-1 rounded text-sm transition-colors"
              :class="roleFilter === 'admin'
                ? 'bg-red-500 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary hover:bg-gray-200 dark:hover:bg-gray-700'"
            >
              管理员
            </button>
            <button
              @click="roleFilter = 'editor'; updateFilters()"
              class="px-3 py-1 rounded text-sm transition-colors"
              :class="roleFilter === 'editor'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary hover:bg-gray-200 dark:hover:bg-gray-700'"
            >
              编辑
            </button>
            <button
              @click="roleFilter = 'user'; updateFilters()"
              class="px-3 py-1 rounded text-sm transition-colors"
              :class="roleFilter === 'user'
                ? 'bg-gray-500 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-light-text-primary dark:text-dark-text-primary hover:bg-gray-200 dark:hover:bg-gray-700'"
            >
              用户
            </button>
          </div>
        </div>
      </ScrollReveal>

      <!-- 用户列表 -->
      <ScrollReveal class="delay-200">
        <div class="card overflow-hidden">
          <!-- 加载状态 -->
          <div v-if="loading" class="p-12 text-center">
            <Icon icon="lucide:loader-2" class="w-8 h-8 animate-spin mx-auto mb-4 text-primary-from" />
            <p class="text-light-text-secondary dark:text-dark-text-secondary">加载中...</p>
          </div>

          <!-- 错误状态 -->
          <div v-else-if="error" class="p-12 text-center">
            <Icon icon="lucide:alert-circle" class="w-12 h-12 mx-auto mb-4 text-red-500" />
            <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-2">
              加载失败
            </h2>
            <p class="text-light-text-secondary dark:text-dark-text-secondary mb-6">
              {{ error }}
            </p>
            <button
              @click="loadUsers"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90 transition-opacity"
            >
              <Icon icon="lucide:refresh-cw" class="w-4 h-4" />
              重试
            </button>
          </div>

          <!-- 用户列表 -->
          <div v-else class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    用户
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    邮箱
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    角色
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    注册时间
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-light-text-muted dark:text-dark-text-muted uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-light-border dark:divide-dark-border">
                <tr
                  v-for="user in filteredUsers"
                  :key="user.id"
                  class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-from to-primary-to flex items-center justify-center text-white font-bold">
                        {{ (user.nickname || user.username)[0]?.toUpperCase() || 'U' }}
                      </div>
                      <div>
                        <div class="font-medium text-light-text-primary dark:text-dark-text-primary">
                          {{ user.nickname || user.username }}
                        </div>
                        <div class="text-sm text-light-text-muted dark:text-dark-text-muted">
                          @{{ user.username }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 text-sm text-light-text-secondary dark:text-dark-text-secondary">
                    {{ user.email }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getRoleClass(user.role)"
                    >
                      {{ getRoleName(user.role) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-light-text-secondary dark:text-dark-text-secondary">
                    {{ formatDate(user.date_joined || user.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <div class="flex items-center justify-end gap-2">
                      <button
                        @click="openEditDialog(user)"
                        class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title="编辑"
                      >
                        <Icon icon="lucide:pencil" class="w-4 h-4 text-light-text-muted dark:text-dark-text-muted" />
                      </button>
                      <button
                        v-if="user.role !== 'admin'"
                        @click="showDeleteConfirm(user)"
                        class="p-2 rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                        title="删除"
                      >
                        <Icon icon="lucide:trash-2" class="w-4 h-4 text-red-600 dark:text-red-400" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- 空状态 -->
            <div v-if="filteredUsers.length === 0" class="p-12 text-center">
              <Icon icon="lucide:users" class="w-16 h-16 mx-auto mb-4 text-light-text-muted dark:text-dark-text-muted" />
              <h3 class="text-lg font-medium text-light-text-primary dark:text-dark-text-primary mb-2">
                {{ searchQuery ? '未找到匹配的用户' : '还没有用户' }}
              </h3>
              <p class="text-light-text-secondary dark:text-dark-text-secondary">
                {{ searchQuery ? '试试其他搜索关键词' : '用户注册后将显示在这里' }}
              </p>
            </div>
          </div>
        </div>
      </ScrollReveal>
    </div>

    <!-- 编辑对话框 -->
    <div v-if="showEditDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="card max-w-md w-full p-6">
        <h2 class="text-xl font-semibold text-light-text-primary dark:text-dark-text-primary mb-4">
          编辑用户
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
              用户名
            </label>
            <input
              v-model="editForm.username"
              type="text"
              class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                     bg-white dark:bg-gray-800
                     text-light-text-primary dark:text-dark-text-primary
                     focus:outline-none focus:ring-2 focus:ring-primary-from"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
              昵称
            </label>
            <input
              v-model="editForm.nickname"
              type="text"
              class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                     bg-white dark:bg-gray-800
                     text-light-text-primary dark:text-dark-text-primary
                     focus:outline-none focus:ring-2 focus:ring-primary-from"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
              邮箱
            </label>
            <input
              v-model="editForm.email"
              type="email"
              class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                     bg-white dark:bg-gray-800
                     text-light-text-primary dark:text-dark-text-primary
                     focus:outline-none focus:ring-2 focus:ring-primary-from"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-light-text-primary dark:text-dark-text-primary mb-1">
              角色
            </label>
            <select
              v-model="editForm.role"
              class="w-full px-3 py-2 rounded-lg border border-light-border dark:border-dark-border
                     bg-white dark:bg-gray-800
                     text-light-text-primary dark:text-dark-text-primary
                     focus:outline-none focus:ring-2 focus:ring-primary-from"
            >
              <option value="user">普通用户</option>
              <option value="editor">编辑</option>
              <option value="admin">管理员</option>
            </select>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 mt-6">
          <button
            @click="closeEditDialog"
            class="px-4 py-2 rounded-lg border border-light-border dark:border-dark-border
                   text-light-text-primary dark:text-dark-text-primary
                   hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            取消
          </button>
          <button
            @click="saveUser"
            class="px-4 py-2 rounded-lg bg-primary-from text-white hover:opacity-90 transition-opacity"
          >
            保存
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <ConfirmDialog
      :show="showDeleteDialog"
      :title="`删除用户`"
      :message="`确定要删除用户 \"${deletingUser?.username}\" 吗？此操作无法撤销。`"
      confirm-text="删除"
      cancel-text="取消"
      type="danger"
      @confirm="handleDeleteConfirm"
      @cancel="handleDeleteCancel"
    />
  </AdminLayout>
</template>
