/**
 * Notification Store - 管理应用通知
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: number
  type: NotificationType
  title?: string
  message: string
  duration?: number
  timestamp: number
}

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  let nextId = 1

  /**
   * 添加通知
   */
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const id = nextId++
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: Date.now(),
      duration: notification.duration ?? (notification.type === 'error' ? 5000 : 3000),
    }

    notifications.value.push(newNotification)

    // 自动移除
    if (newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }

    return id
  }

  /**
   * 移除通知
   */
  const removeNotification = (id: number) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  /**
   * 清空所有通知
   */
  const clearAll = () => {
    notifications.value = []
  }

  // 便捷方法
  const success = (message: string, title?: string) => {
    return addNotification({ type: 'success', message, title })
  }

  const error = (message: string, title?: string) => {
    return addNotification({ type: 'error', message, title })
  }

  const warning = (message: string, title?: string) => {
    return addNotification({ type: 'warning', message, title })
  }

  const info = (message: string, title?: string) => {
    return addNotification({ type: 'info', message, title })
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info,
  }
})
