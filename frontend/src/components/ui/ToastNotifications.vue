<script setup lang="ts">
import { TransitionGroup } from 'vue'
import { Icon } from '@iconify/vue'
import { useNotificationStore } from '@/stores/notification'
import type { NotificationType } from '@/stores/notification'

const notificationStore = useNotificationStore()

const typeConfig: Record<NotificationType, { icon: string; gradient: string; border: string }> = {
  success: {
    icon: 'lucide:check-circle',
    gradient: 'from-green-400 to-emerald-500',
    border: 'border-green-500 dark:border-green-400',
  },
  error: {
    icon: 'lucide:x-circle',
    gradient: 'from-red-400 to-rose-500',
    border: 'border-red-500 dark:border-red-400',
  },
  warning: {
    icon: 'lucide:alert-triangle',
    gradient: 'from-yellow-400 to-amber-500',
    border: 'border-yellow-500 dark:border-yellow-400',
  },
  info: {
    icon: 'lucide:info',
    gradient: 'from-blue-400 to-indigo-500',
    border: 'border-blue-500 dark:border-blue-400',
  },
}

const getIcon = (type: NotificationType) => typeConfig[type].icon
const getGradient = (type: NotificationType) => typeConfig[type].gradient
const getBorder = (type: NotificationType) => typeConfig[type].border
</script>

<template>
  <!-- 固定在右上角 -->
  <div class="fixed top-20 right-4 z-50 flex flex-col gap-2 pointer-events-none">
    <TransitionGroup
      name="toast"
      tag="div"
      class="flex flex-col gap-2"
    >
      <div
        v-for="notification in notificationStore.notifications"
        :key="notification.id"
        class="pointer-events-auto min-w-[320px] max-w-md bg-white dark:bg-gray-800 rounded-lg shadow-lg border-l-4 overflow-hidden"
        :class="getBorder(notification.type)"
      >
        <div class="flex items-start gap-3 p-4">
          <!-- 图标 -->
          <div
            class="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br flex items-center justify-center"
            :class="getGradient(notification.type)"
          >
            <Icon
              :icon="getIcon(notification.type)"
              class="w-4 h-4 text-white"
            />
          </div>

          <!-- 内容 -->
          <div class="flex-1 min-w-0">
            <h4
              v-if="notification.title"
              class="text-sm font-semibold text-light-text-primary dark:text-dark-text-primary mb-1"
            >
              {{ notification.title }}
            </h4>
            <p class="text-sm text-light-text-secondary dark:text-dark-text-secondary break-words">
              {{ notification.message }}
            </p>
          </div>

          <!-- 关闭按钮 -->
          <button
            @click="notificationStore.removeNotification(notification.id)"
            class="flex-shrink-0 text-light-text-muted dark:text-dark-text-muted hover:text-light-text-primary dark:hover:text-dark-text-primary transition-colors"
          >
            <Icon icon="lucide:x" class="w-4 h-4" />
          </button>
        </div>

        <!-- 进度条 -->
        <div
          v-if="notification.duration && notification.duration > 0"
          class="h-1 bg-gradient-to-r animate-progress"
          :class="getGradient(notification.type)"
          :style="{ animationDuration: `${notification.duration}ms` }"
        />
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
/* 进入动画 */
.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-enter-to {
  opacity: 1;
  transform: translateX(0);
}

.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

/* 离开动画 */
.toast-leave-from {
  opacity: 1;
  transform: translateX(0);
  max-height: 200px;
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
  max-height: 0;
  margin: 0;
  padding: 0;
}

.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

/* 进度条动画 */
@keyframes progress {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

.animate-progress {
  animation: progress linear forwards;
}
</style>
