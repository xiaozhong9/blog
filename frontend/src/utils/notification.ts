/**
 * 通知工具函数 - 快速发送通知
 */
import { useNotificationStore } from '@/stores/notification'

/**
 * 发送成功通知
 */
export const notifySuccess = (message: string, title?: string) => {
  const notificationStore = useNotificationStore()
  return notificationStore.success(message, title)
}

/**
 * 发送错误通知
 */
export const notifyError = (message: string, title?: string) => {
  const notificationStore = useNotificationStore()
  return notificationStore.error(message, title)
}

/**
 * 发送警告通知
 */
export const notifyWarning = (message: string, title?: string) => {
  const notificationStore = useNotificationStore()
  return notificationStore.warning(message, title)
}

/**
 * 发送信息通知
 */
export const notifyInfo = (message: string, title?: string) => {
  const notificationStore = useNotificationStore()
  return notificationStore.info(message, title)
}

/**
 * 从错误对象提取消息并发送错误通知
 */
export const notifyFromError = (error: unknown, fallbackMessage = '操作失败') => {
  let message = fallbackMessage

  if (error instanceof Error) {
    message = error.message
  } else if (typeof error === 'string') {
    message = error
  } else if (error && typeof error === 'object' && 'message' in error) {
    message = (error as any).message
  }

  return notifyError(message)
}
