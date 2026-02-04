// services/api.js - ENHANCED WITH BETTER SESSION PERSISTENCE
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Token refresh state
let isRefreshing = false
let failedQueue = []
let refreshAttempts = 0
const MAX_REFRESH_ATTEMPTS = 3

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  
  failedQueue = []
}

// Helper functions for seamless re-auth
const generateFallbackMac = () => {
  const getRandomByte = () => {
    const array = new Uint8Array(1)
    crypto.getRandomValues(array)
    return array[0]
  }
  const bytes = Array.from({ length: 6 }, () => getRandomByte())
  bytes[0] = (bytes[0] & 0xFE) | 0x02
  return bytes.map(b => b.toString(16).padStart(2, '0')).join(':')
}

const generateFallbackIP = () => {
  const ranges = [
    { base: '10.0', range: 255 },
    { base: '172.16', range: 15 },
    { base: '192.168', range: 255 }
  ]
  const selectedRange = ranges[Math.floor(Math.random() * ranges.length)]
  const subnet = Math.floor(Math.random() * selectedRange.range)
  const host = Math.floor(Math.random() * 254) + 1
  return `${selectedRange.base}.${subnet}.${host}`
}

// Check if token is expired or expiring soon
const isTokenExpired = (token) => {
  if (!token) return true
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const now = Date.now() / 1000
    return payload.exp < now
  } catch {
    return true
  }
}

const isTokenExpiringSoon = (token) => {
  if (!token) return true
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const now = Date.now() / 1000
    const fiveMinutes = 5 * 60
    return (payload.exp - now) < fiveMinutes
  } catch {
    return true
  }
}

// Proactive token refresh
const proactiveRefresh = async () => {
  const token = localStorage.getItem('auth_token')
  const refreshToken = localStorage.getItem('refresh_token')
  
  if (token && refreshToken && isTokenExpiringSoon(token) && !isRefreshing) {
    try {
      await refreshTokens(refreshToken)
    } catch (error) {
      console.warn('Proactive refresh failed:', error)
    }
  }
}

// Refresh tokens function
const refreshTokens = async (refreshToken) => {
  const response = await axios.post(`${API_BASE_URL}/api/token/refresh/`, {
    refresh: refreshToken
  })
  
  const { access, refresh } = response.data
  
  // Update stored tokens
  localStorage.setItem('auth_token', access)
  if (refresh) {
    localStorage.setItem('refresh_token', refresh)
  }
  
  // Update axios default header
  api.defaults.headers.common['Authorization'] = `Bearer ${access}`
  
  return access
}

// Graceful logout with session cleanup
const gracefulLogout = (reason = 'Session expired') => {
  console.log(`Logging out user: ${reason}`)
  
  // Clear all auth data
  localStorage.removeItem('auth_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  sessionStorage.clear()
  
  // Show user-friendly message
  if (window.showToast) {
    window.showToast(`${reason}. Please sign in again.`, 'info')
  }
  
  // Redirect to signin with reason
  const currentPath = window.location.pathname
  if (currentPath !== '/' && currentPath !== '/signin') {
    window.location.href = `/?reason=${encodeURIComponent(reason)}&redirect=${encodeURIComponent(currentPath)}`
  }
}

// Request interceptor
api.interceptors.request.use(
  async (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('auth_token')
    if (token) {
      // Check if token is expired before making request
      if (isTokenExpired(token)) {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken && refreshAttempts < MAX_REFRESH_ATTEMPTS) {
          try {
            refreshAttempts++
            const newToken = await refreshTokens(refreshToken)
            config.headers['Authorization'] = `Bearer ${newToken}`
            refreshAttempts = 0 // Reset on success
          } catch (error) {
            gracefulLogout('Session expired')
            return Promise.reject(new Error('Session expired'))
          }
        } else {
          gracefulLogout('Session expired')
          return Promise.reject(new Error('Session expired'))
        }
      } else {
        config.headers['Authorization'] = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor with automatic device auth retry
api.interceptors.response.use(
  (response) => {
    refreshAttempts = 0
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      // Try device auto-auth first (fastest method)
      if (refreshAttempts < MAX_REFRESH_ATTEMPTS) {
        try {
          refreshAttempts++
          console.log('🔄 401 detected - attempting device auto-auth...')
          
          const deviceAuthResponse = await axios.post(`${API_BASE_URL}/api/users/auth/device-auto/`, {
            current_mac: generateFallbackMac(),
            current_ip: generateFallbackIP(),
            location_id: 1,
            device_info: {
              userAgent: navigator.userAgent,
              platform: navigator.platform,
              auto_refresh: true,
              timestamp: new Date().toISOString()
            }
          })
          
          if (deviceAuthResponse.data.success && deviceAuthResponse.data.auth) {
            const newToken = deviceAuthResponse.data.auth.access
            const newRefresh = deviceAuthResponse.data.auth.refresh
            
            // Update stored tokens
            localStorage.setItem('auth_token', newToken)
            localStorage.setItem('refresh_token', newRefresh)
            
            // Update user data
            if (deviceAuthResponse.data.user) {
              localStorage.setItem('user', JSON.stringify({
                id: deviceAuthResponse.data.user.id,
                username: deviceAuthResponse.data.user.username,
                email: deviceAuthResponse.data.user.email,
                phone: deviceAuthResponse.data.client?.phone_number,
                client: deviceAuthResponse.data.client,
                device: deviceAuthResponse.data.device,
                session: deviceAuthResponse.data.session
              }))
            }
            
            // Update axios header
            api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
            
            // Process queued requests
            processQueue(null, newToken)
            
            // Retry original request
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`
            refreshAttempts = 0
            console.log('✅ Device auto-auth successful - retrying request')
            return api(originalRequest)
          }
        } catch (deviceAuthError) {
          console.warn('❌ Device auto-auth failed:', deviceAuthError.message)
          
          // Fallback to token refresh if device auth fails
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            try {
              const newToken = await refreshTokens(refreshToken)
              processQueue(null, newToken)
              originalRequest.headers['Authorization'] = `Bearer ${newToken}`
              refreshAttempts = 0
              console.log('✅ Token refresh successful - retrying request')
              return api(originalRequest)
            } catch (refreshError) {
              console.error('❌ Token refresh also failed:', refreshError.message)
            }
          }
        } finally {
          isRefreshing = false
        }
      }
      
      // All auth methods failed
      processQueue(error, null)
      gracefulLogout('Session expired')
      return Promise.reject(error)
    }
    
    return Promise.reject(error)
  }
)

// Set up proactive refresh interval (every 2 minutes)
setInterval(proactiveRefresh, 2 * 60 * 1000)

// Error handling helper
export const handleError = (error) => {
  if (error.response) {
    return error.response.data?.error || error.response.data?.message || 'Server error'
  } else if (error.request) {
    return 'Network error. Please check your connection.'
  } else {
    return 'Request failed. Please try again.'
  }
}

// Export ONLY ONCE at the end
export { api }