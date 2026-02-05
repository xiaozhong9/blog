<script setup lang="ts">
import { computed } from 'vue'
import type { HTMLAttributes } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'ghost' | 'text'
    size?: 'sm' | 'md' | 'lg'
    disabled?: boolean
    loading?: boolean
    type?: HTMLAttributes['type']
  }>(),
  {
    variant: 'primary',
    size: 'md',
    disabled: false,
    loading: false,
    type: 'button',
  }
)

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const classes = computed(() => {
  const variants = {
    primary: 'bg-gradient-to-r from-primary-from to-primary-to text-white hover:opacity-90 shadow-soft',
    secondary: 'bg-light-bg dark:bg-dark-bg text-light-text-primary dark:text-dark-text-primary hover:bg-light-border dark:hover:bg-dark-border',
    ghost: 'bg-transparent text-light-text-secondary dark:text-dark-text-secondary hover:bg-light-bg dark:hover:bg-dark-bg',
    text: 'bg-transparent text-primary-from hover:underline p-0',
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  }

  return [
    'inline-flex items-center justify-center gap-2 font-medium rounded-xl',
    'transition-all duration-150',
    'focus:outline-none focus:ring-2 focus:ring-primary-from focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    variants[props.variant],
    props.variant !== 'text' ? sizes[props.size] : '',
  ]
})

const handleClick = (e: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', e)
  }
}
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="classes"
    @click="handleClick"
  >
    <span
      v-if="loading"
      class="i-lucide:loader-2 animate-spin w-4 h-4"
    />
    <slot />
  </button>
</template>
