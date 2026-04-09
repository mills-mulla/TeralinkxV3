<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-50 space-y-3 pointer-events-none max-w-md w-full">
      <TransitionGroup name="toast" tag="div" class="space-y-3">
        <div
          v-for="toast in globalToast.toasts.value"
          :key="toast.id"
          :class="[
            'pointer-events-auto w-full bg-white dark:bg-gray-800 shadow-xl rounded-lg overflow-hidden border-l-4 transform transition-all duration-300 ease-out',
            getToastStyles(toast.type)
          ]"
        >
          <div class="p-4">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <div :class="getIconStyles(toast.type)">
                  <!-- Success Icon -->
                  <svg v-if="toast.type === 'success'" class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <!-- Error Icon -->
                  <svg v-else-if="toast.type === 'error'" class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                  <!-- Warning Icon -->
                  <svg v-else-if="toast.type === 'warning'" class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                  <!-- Info Icon -->
                  <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
              <div class="ml-3 w-0 flex-1">
                <p v-if="toast.title" class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ toast.title }}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-300" :class="{ 'mt-1': toast.title }">
                  {{ toast.message }}
                </p>
              </div>
              <div class="ml-4 flex-shrink-0">
                <button
                  @click="globalToast.remove(toast.id)"
                  class="inline-flex text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 focus:outline-none transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Progress bar -->
          <div
            v-if="toast.duration > 0"
            class="h-1 bg-gray-200 dark:bg-gray-700 overflow-hidden"
          >
            <div
              :class="[
                'h-full transition-all ease-linear',
                getProgressBarStyles(toast.type)
              ]"
              :style="{ 
                width: `${toast.progress}%`,
                transitionDuration: `${toast.duration}ms`
              }"
            ></div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import globalToast from '@/composables/useCustomToast'

const getToastStyles = (type) => {
  const styles = {
    success: 'border-green-500 bg-green-50 dark:bg-green-900/10',
    error: 'border-red-500 bg-red-50 dark:bg-red-900/10',
    warning: 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/10',
    info: 'border-blue-500 bg-blue-50 dark:bg-blue-900/10'
  }
  return styles[type] || styles.info
}

const getIconStyles = (type) => {
  const styles = {
    success: 'text-green-500',
    error: 'text-red-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500'
  }
  return styles[type] || styles.info
}

const getProgressBarStyles = (type) => {
  const styles = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500'
  }
  return styles[type] || styles.info
}
</script>

<style scoped>
.toast-enter-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-leave-active {
  transition: all 0.3s ease-in;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>