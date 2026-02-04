// composables/useCustomToast.js
import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

export const useCustomToast = () => {
  const addToast = (message, type = 'info', title = null, duration = 5000) => {
    const id = ++toastId
    const toast = {
      id,
      message,
      type,
      title,
      duration,
      progress: 0,
      createdAt: Date.now()
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

  const success = (message, title = null, duration = 5000) => {
    return addToast(message, 'success', title, duration)
  }

  const error = (message, title = null, duration = 7000) => {
    return addToast(message, 'error', title, duration)
  }

  const warning = (message, title = null, duration = 6000) => {
    return addToast(message, 'warning', title, duration)
  }

  const info = (message, title = null, duration = 5000) => {
    return addToast(message, 'info', title, duration)
  }

  return {
    toasts,
    success,
    error,
    warning,
    info,
    remove: removeToast,
    clear: clearAll
  }
}

// Global instance for easy access
const globalToast = useCustomToast()

// Export individual methods for convenience
export const toast = {
  success: globalToast.success,
  error: globalToast.error,
  warning: globalToast.warning,
  info: globalToast.info,
  remove: globalToast.remove,
  clear: globalToast.clear
}

export default globalToast