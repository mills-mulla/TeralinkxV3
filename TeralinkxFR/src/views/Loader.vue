<template>
  <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
    <div class="flex flex-col items-center space-y-4">
      <!-- Animated Loader -->
      <div class="relative w-12 h-12">
        <!-- Pulsing background -->
        <div class="absolute inset-0 bg-blue-400 opacity-30 rounded-full animate-ping"></div>
        <!-- Spinning loader ring -->
        <div class="relative w-12 h-12 border-8 border-gray-300 dark:border-gray-600 border-t-blue-500 dark:border-t-blue-400 rounded-full animate-spin"></div>
      </div>

      <p class="text-sm font-medium text-white dark:text-gray-200 animate-pulse">
        Processing...
      </p>
    </div>
  </div>
</template>

<script setup>
defineOptions({ name: 'Loader' })
</script>

<style scoped>
/* No custom styles needed — Tailwind handles all */
</style>
