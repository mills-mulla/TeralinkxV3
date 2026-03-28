// services/api.js - ENHANCED WITH BETTER SESSION PERSISTENCE
import axios from 'axios'

// Multi-endpoint configuration like admin panel
const PRIMARY_URL = import.meta.env.VITE_API_PRIMARY_URL || 'https://srv.teralinkxwaves.uk'
const FALLBACK_URL = import.meta.env.VITE_API_FALLBACK_URL || 'https://service.teralinkxwaves.uk'
const LOCAL_URL = import.meta.env.VITE_API_BASE_URL || 'https://srv.teralinkxwaves.uk'

// Track which base URL is currently active
let activeBaseURL = PRIMARY_URL
let primaryFailed = false

// Create axios instance WITHOUT baseURL - we'll use full URLs
const api = axios.create({
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Helper function to get full API URL
const getApiUrl = (endpoint) => {
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
  return `${activeBaseURL}/${cleanEndpoint}`
}

// Custom API methods that use full URLs
const apiMethods = {
  get: (endpoint, config = {}) => {
    return api.get(getApiUrl(endpoint), config)
  },
  post: (endpoint, data = {}, config = {}) => {
    return api.post(getApiUrl(endpoint), data, config)
  },
  put: (endpoint, data = {}, config = {}) => {
    return api.put(getApiUrl(endpoint), data, config)
  },
  delete: (endpoint, config = {}) => {
    return api.delete(getApiUrl(endpoint), config)
  },
  patch: (endpoint, data = {}, config = {}) => {
    return api.patch(getApiUrl(endpoint), data, config)
  }
}

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

// Refresh tokens function with fallback support
const refreshTokens = async (refreshToken) => {
  const response = await axios.post(`${activeBaseURL}/api/token/refresh/`, {
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
    const sanitizedReason = String(reason).replace(/<[^>]*>/g, '').slice(0, 100);
    window.showToast(`${sanitizedReason}. Please sign in again.`, 'info')
  }
  
  // Redirect to signin with reason
  const currentPath = window.location.pathname
  if (currentPath !== '/' && currentPath !== '/signin') {
    // Sanitize reason to prevent XSS
    const sanitizedReason = reason.replace(/[<>"'&]/g, '')
    const sanitizedPath = currentPath.replace(/[<>"'&]/g, '')
    window.location.href = `/?reason=${encodeURIComponent(sanitizedReason)}&redirect=${encodeURIComponent(sanitizedPath)}`
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

// Response interceptor with automatic device auth retry and fallback support
api.interceptors.response.use(
  (response) => {
    // Primary responded successfully - reset fallback flag
    if (primaryFailed) {
      primaryFailed = false
      activeBaseURL = PRIMARY_URL
      console.log('✅ Primary server restored:', PRIMARY_URL)
    }
    refreshAttempts = 0
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Handle server failover first
    const isNetworkError = !error.response
    const isServerError = error.response?.status >= 500
    const isUsingFallback = originalRequest.url?.includes(FALLBACK_URL)
    
    if ((isNetworkError || isServerError) && !isUsingFallback && !primaryFailed) {
      console.warn(`🔄 Primary ${PRIMARY_URL} unreachable, falling back to ${FALLBACK_URL}`)
      primaryFailed = true
      activeBaseURL = FALLBACK_URL
      
      // Retry the failed request on fallback by reconstructing the URL
      const endpoint = originalRequest.url.replace(PRIMARY_URL, '')
      const fallbackUrl = `${FALLBACK_URL}${endpoint}`
      const retryConfig = { ...originalRequest, url: fallbackUrl }
      return axios(retryConfig)
    }
    
    // Handle 401 authentication errors
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
          
          const deviceAuthResponse = await axios.post(`${activeBaseURL}/api/users/auth/device-auto/`, {
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
            return apiMethods.get(originalRequest.url.replace(activeBaseURL, ''))
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

// Set up proactive refresh interval (every 2 minutes) - with cleanup
let refreshInterval = null

// Initialize interval only when needed
export const initializeProactiveRefresh = () => {
  if (!refreshInterval) {
    refreshInterval = setInterval(proactiveRefresh, 2 * 60 * 1000)
  }
}

// Cleanup function for memory management
export const cleanupProactiveRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

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

// Initialize axios with stored token
const initializeAuth = () => {
  const token = localStorage.getItem('auth_token')
  if (token && !isTokenExpired(token)) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    console.log('✅ API initialized with stored token')
  } else {
    console.log('⚠️ No valid token found in localStorage')
  }
}

// Call initialization immediately
initializeAuth()

// Function to manually set authorization token
const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    console.log('✅ Authorization token set manually')
  } else {
    delete api.defaults.headers.common['Authorization']
    console.log('❌ Authorization token removed')
  }
}

// Export API configuration and helper functions
export { apiMethods as api, setAuthToken }
export const getActiveURL = () => activeBaseURL
export const getPrimaryURL = () => PRIMARY_URL
export const getFallbackURL = () => FALLBACK_URL
export const getLocalURL = () => LOCAL_URL
export const isPrimaryFailed = () => primaryFailed