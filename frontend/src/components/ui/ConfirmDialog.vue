<script setup lang="ts">
import { ref, watch } from 'vue'
import { Icon } from '@iconify/vue'

interface Props {
  show: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info'
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: '确定',
  cancelText: '取消',
  type: 'danger'
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const localShow = ref(props.show)

watch(() => props.show, (newVal) => {
  localShow.value = newVal
})

watch(localShow, (newVal) => {
  if (!newVal) {
    emit('cancel')
  }
})

const handleConfirm = () => {
  localShow.value = false
  emit('confirm')
}

const handleCancel = () => {
  localShow.value = false
  emit('cancel')
}

const iconMap = {
  danger: 'lucide:alert-triangle',
  warning: 'lucide:alert-circle',
  info: 'lucide:info'
}

const colorMap = {
  danger: 'text-red-600 dark:text-red-400',
  warning: 'text-yellow-600 dark:text-yellow-400',
  info: 'text-blue-600 dark:text-blue-400'
}

const bgMap = {
  danger: 'bg-red-100 dark:bg-red-900/20',
  warning: 'bg-yellow-100 dark:bg-yellow-900/20',
  info: 'bg-blue-100 dark:bg-blue-900/20'
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="localShow"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="handleCancel"
      >
        <!-- 背景遮罩 -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />

        <!-- 对话框 -->
        <Transition
          enter-active-class="transition-all duration-200"
          enter-from-class="scale-95 opacity-0"
          enter-to-class="scale-100 opacity-100"
          leave-active-class="transition-all duration-200"
          leave-from-class="scale-100 opacity-100"
          leave-to-class="scale-95 opacity-0"
        >
          <div
            v-if="localShow"
            class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6"
            @click.stop
          >
            <!-- 图标 -->
            <div class="flex justify-center mb-4">
              <div
                class="w-16 h-16 rounded-full flex items-center justify-center"
                :class="bgMap[type]"
              >
                <Icon
                  :icon="iconMap[type]"
                  class="w-8 h-8"
                  :class="colorMap[type]"
                />
              </div>
            </div>

            <!-- 标题 -->
            <h3 class="text-xl font-bold text-center text-light-text-primary dark:text-dark-text-primary mb-2">
              {{ title }}
            </h3>

            <!-- 消息 -->
            <p class="text-center text-light-text-secondary dark:text-dark-text-secondary mb-6">
              {{ message }}
            </p>

            <!-- 按钮 -->
            <div class="flex gap-3">
              <button
                @click="handleCancel"
                class="flex-1 px-4 py-2.5 rounded-xl border border-light-border dark:border-dark-border
                       text-light-text-primary dark:text-dark-text-primary
                       hover:bg-light-bg dark:hover:bg-gray-700
                       transition-colors duration-150 font-medium"
              >
                {{ cancelText }}
              </button>
              <button
                @click="handleConfirm"
                class="flex-1 px-4 py-2.5 rounded-xl
                       font-medium text-white transition-all duration-150"
                :class="type === 'danger'
                  ? 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 shadow-lg shadow-red-500/25'
                  : 'bg-gradient-to-r from-primary-from to-primary-to hover:opacity-90 shadow-lg shadow-primary-from/25'"
              >
                {{ confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
