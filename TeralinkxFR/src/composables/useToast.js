// composables/useToast.js
import { ref } from 'vue'

export const useToast = () => {
  const toasts = ref([])

  const showToast = (message, type = 'info', duration = 5000) => {
    const id = Date.now()
    const toast = { id, message, type }
    
    toasts.value.push(toast)
    
    // Auto remove
    setTimeout(() => {
      removeToast(id)
    }, duration)
    
    return id
  }

  const showSuccess = (message, duration = 3000) => {
    return showToast(message, 'success', duration)
  }

  const showError = (message, duration = 5000) => {
    return showToast(message, 'error', duration)
  }

  const showWarning = (message, duration = 4000) => {
    return showToast(message, 'warning', duration)
  }

  const showInfo = (message, duration = 4000) => {
    return showToast(message, 'info', duration)
  }

  const removeToast = (id) => {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  return {
    toasts,
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeToast
  }
}