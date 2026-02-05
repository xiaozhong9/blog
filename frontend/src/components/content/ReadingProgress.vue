<script setup lang="ts">
defineProps<{
  progress: number
}>()
</script>

<template>
  <div class="fixed top-16 left-0 right-0 z-40 h-1 bg-light-bg dark:bg-dark-bg">
    <div
      class="h-full bg-gradient-to-r from-primary-from to-primary-to
             transition-all duration-150 ease-out"
      :style="{ width: `${Math.min(progress, 100)}%` }"
    />
  </div>
</template>
