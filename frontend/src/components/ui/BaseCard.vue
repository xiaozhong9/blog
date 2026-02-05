<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'default' | 'bordered' | 'elevated' | 'gradient'
    padding?: 'none' | 'sm' | 'md' | 'lg'
    hoverable?: boolean
  }>(),
  {
    variant: 'default',
    padding: 'md',
    hoverable: false,
  }
)

const classes = computed(() => {
  const variants = {
    default: 'bg-light-surface dark:bg-dark-surface',
    bordered: 'bg-light-surface dark:bg-dark-surface border border-light-border dark:border-dark-border',
    elevated: 'bg-light-surface dark:bg-dark-surface shadow-soft',
    gradient: 'bg-gradient-to-br from-primary-from/10 to-primary-to/10 border border-primary-from/20',
  }

  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }

  return [
    'rounded-2xl',
    'transition-all duration-300 cubic-bezier(0.22, 1, 0.36, 1)',
    variants[props.variant],
    paddings[props.padding],
    props.hoverable ? 'hover:-translate-y-1 hover:shadow-soft-lg cursor-pointer' : '',
  ]
})
</script>

<template>
  <div :class="classes">
    <slot />
  </div>
</template>
