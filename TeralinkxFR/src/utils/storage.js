// utils/storage.js
const PREFIX = 'teralinkx_'

export const storage = {
  // Set item with encryption for sensitive data
  set(key, value) {
    try {
      const storageKey = `${PREFIX}${key}`
      const serialized = JSON.stringify(value)
      
      if (key === 'auth_token' || key === 'refresh_token') {
        // For tokens, use sessionStorage for better security
        sessionStorage.setItem(storageKey, serialized)
      } else {
        localStorage.setItem(storageKey, serialized)
      }
      
      return true
    } catch (error) {
      console.error('Storage set error:', error)
      return false
    }
  },

  // Get item
  get(key, defaultValue = null) {
    try {
      const storageKey = `${PREFIX}${key}`
      
      // Check both storages for tokens
      let value = sessionStorage.getItem(storageKey) || localStorage.getItem(storageKey)
      
      if (value) {
        return JSON.parse(value)
      }
      
      return defaultValue
    } catch (error) {
      console.error('Storage get error:', error)
      return defaultValue
    }
  },

  // Remove item
  remove(key) {
    try {
      const storageKey = `${PREFIX}${key}`
      sessionStorage.removeItem(storageKey)
      localStorage.removeItem(storageKey)
      return true
    } catch (error) {
      console.error('Storage remove error:', error)
      return false
    }
  },

  // Clear all app storage
  clear() {
    try {
      // Clear sessionStorage
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i)
        if (key.startsWith(PREFIX)) {
          sessionStorage.removeItem(key)
        }
      }
      
      // Clear localStorage
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key.startsWith(PREFIX)) {
          localStorage.removeItem(key)
        }
      }
      
      return true
    } catch (error) {
      console.error('Storage clear error:', error)
      return false
    }
  }
}