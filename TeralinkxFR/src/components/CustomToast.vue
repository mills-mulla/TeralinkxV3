<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-30 space-y-2 pointer-events-none">
      <TransitionGroup
        name="toast"
        tag="div"
        class="space-y-2"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'pointer-events-auto max-w-sm w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg overflow-hidden border-l-4 transform transition-all duration-300 ease-in-out',
            getToastStyles(toast.type)
          ]"
        >
          <div class="p-4">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <component :is="getIcon(toast.type)" :class="getIconStyles(toast.type)" />
              </div>
              <div class="ml-3 w-0 flex-1">
                <p v-if="toast.title" class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ toast.title }}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-300" :class="{ 'mt-1': toast.title }">
                  {{ toast.message }}
                </p>
              </div>
              <div class="ml-4 flex-shrink-0 flex">
                <button
                  @click="removeToast(toast.id)"
                  class="bg-white dark:bg-gray-800 rounded-md inline-flex text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                >
                  <XMarkIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
          
          <!-- Progress bar -->
          <div
            v-if="toast.duration > 0"
            class="h-1 bg-gray-200 dark:bg-gray-700"
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
import { ref, onMounted, onUnmounted } from 'vue'

// Icons
const CheckCircleIcon = {
  template: `
    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
    </svg>
  `
}

const ExclamationTriangleIcon = {
  template: `
    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
    </svg>
  `
}

const XCircleIcon = {
  template: `
    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
    </svg>
  `
}

const InformationCircleIcon = {
  template: `
    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
    </svg>
  `
}

const XMarkIcon = {
  template: `
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
    </svg>
  `
}

const toasts = ref([])
let toastId = 0

const getIcon = (type) => {
  const icons = {
    success: CheckCircleIcon,
    error: XCircleIcon,
    warning: ExclamationTriangleIcon,
    info: InformationCircleIcon
  }
  return icons[type] || InformationCircleIcon
}

const getToastStyles = (type) => {
  const styles = {
    success: 'border-green-400 bg-green-50 dark:bg-green-900/20',
    error: 'border-red-400 bg-red-50 dark:bg-red-900/20',
    warning: 'border-yellow-400 bg-yellow-50 dark:bg-yellow-900/20',
    info: 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
  }
  return styles[type] || styles.info
}

const getIconStyles = (type) => {
  const styles = {
    success: 'text-green-400',
    error: 'text-red-400',
    warning: 'text-yellow-400',
    info: 'text-blue-400'
  }
  return `w-6 h-6 ${styles[type] || styles.info}`
}

const getProgressBarStyles = (type) => {
  const styles = {
    success: 'bg-green-400',
    error: 'bg-red-400',
    warning: 'bg-yellow-400',
    info: 'bg-blue-400'
  }
  return styles[type] || styles.info
}

const addToast = (message, type = 'info', title = null, duration = 5000) => {
  const id = ++toastId
  const toast = {
    id,
    message,
    type,
    title,
    duration,
    progress: 0
  }
  
  toasts.value.push(toast)
  
  if (duration > 0) {
    // Start progress animation
    setTimeout(() => {
      const toastElement = toasts.value.find(t => t.id === id)
      if (toastElement) {
        toastElement.progress = 100
      }
    }, 100)
    
    // Auto remove
    setTimeout(() => {
      removeToast(id)
    }, duration + 100)
  }
  
  return id
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

const clearAll = () => {
  toasts.value = []
}

// Expose methods globally
const useToast = () => ({
  success: (message, title = null, duration = 5000) => addToast(message, 'success', title, duration),
  error: (message, title = null, duration = 7000) => addToast(message, 'error', title, duration),
  warning: (message, title = null, duration = 6000) => addToast(message, 'warning', title, duration),
  info: (message, title = null, duration = 5000) => addToast(message, 'info', title, duration),
  remove: removeToast,
  clear: clearAll
})

// Make it available globally
if (typeof window !== 'undefined') {
  window.toast = useToast()
}

defineExpose({
  addToast,
  removeToast,
  clearAll,
  useToast
})
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>