<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'default' | 'primary' | 'success' | 'warning' | 'gray'
    size?: 'sm' | 'md'
  }>(),
  {
    variant: 'default',
    size: 'md',
  }
)

const classes = computed(() => {
  const variants = {
    default: 'bg-light-bg dark:bg-dark-bg text-light-text-secondary dark:text-dark-text-secondary',
    primary: 'bg-primary-from/10 text-primary-from',
    success: 'bg-green-500/10 text-green-500',
    warning: 'bg-yellow-500/10 text-yellow-500',
    gray: 'bg-gray-500/10 text-gray-500',
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  }

  return [
    'inline-flex items-center rounded-lg font-medium',
    variants[props.variant],
    sizes[props.size],
  ]
})
</script>

<template>
  <span :class="classes">
    <slot />
  </span>
</template>
