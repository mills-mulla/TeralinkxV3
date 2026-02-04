// stores/auth.js - UPDATED VERSION
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../services/api'
import { jwtService } from '../services/jwt'
import { storage } from '../utils/storage'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref('')
  const refreshToken = ref('')
  const loading = ref(false)
  const error = ref('')
  const session = ref(null)

  // Getters
  const isAuthenticated = computed(() => {
    if (!token.value) return false
    return jwtService.isValid(token.value)
  })

  const currentUser = computed(() => user.value)
  const authHeaders = computed(() => {
    if (!token.value) {
      return { 'Content-Type': 'application/json' }
    }
    return {
      Authorization: `Bearer ${token.value}`,
      'Content-Type': 'application/json'
    }
  })

  const isTokenExpiringSoon = computed(() => {
    if (!token.value) return false
    try {
      const expiry = jwtService.getExpiry(token.value)
      const now = Date.now()
      const fiveMinutes = 5 * 60 * 1000
      return (expiry - now) < fiveMinutes
    } catch {
      return true
    }
  })

  const tokenExpiresAt = computed(() => {
    if (!token.value) return null
    try {
      return new Date(jwtService.getExpiry(token.value))
    } catch {
      return null
    }
  })

  // Passwordless Authentication Actions
  const checkAccountStatus = async (payload) => {
    try {
      loading.value = true
      error.value = ''
      
      // Check if account exists and its authentication requirements
      const response = await api.post('/api/account/check/', payload)
      
      return {
        exists: response.data.exists,
        requires_password: response.data.requires_password || false,
        requires_otp: response.data.requires_otp || false,
        failed_attempts: response.data.failed_attempts || 0,
        account_locked: response.data.account_locked || false,
        message: response.data.message || ''
      }
      
    } catch (err) {
      // If account doesn't exist, return appropriate status
      if (err.response?.status === 404) {
        return {
          exists: false,
          requires_password: false,
          requires_otp: false,
          failed_attempts: 0,
          account_locked: false,
          message: 'New account will be created'
        }
      }
      
      error.value = api.handleError(err)
      throw new Error(error.value)
    } finally {
      loading.value = false
    }
  }

  const passwordlessAuthenticate = async (payload) => {
    try {
      loading.value = true
      error.value = ''
      
      // Passwordless authentication endpoint
      const response = await api.post('/api/auth/passwordless/', payload)
      
      if (response.data.auth) {
        // Store tokens
        token.value = response.data.auth.access
        refreshToken.value = response.data.auth.refresh
        
        // Store user data with activity timestamp
        user.value = {
          id: response.data.user.id,
          username: response.data.user.username,
          email: response.data.user.email,
          phone: response.data.user.phone || response.data.client?.phone_number,
          client: response.data.client,
          device: response.data.device,
          session: response.data.session
        }
        
        // Store session data for OTP if needed
        session.value = response.data.session
        
        // Persist to storage with activity tracking
        storage.set('auth_token', token.value)
        storage.set('refresh_token', refreshToken.value)
        storage.set('user', user.value)
        storage.set('last_activity', Date.now())
        
        // Setup auto-refresh
        setupTokenRefresh()
      }
      
      return {
        success: true,
        requires_otp: response.data.metadata?.requires_otp || false,
        requires_password: response.data.metadata?.requires_password || false,
        is_new_account: response.data.metadata?.is_new_user || false,
        session_id: response.data.session?.session_id,
        message: response.data.metadata?.message || 'Authentication successful'
      }
      
    } catch (err) {
      error.value = api.handleError(err)
      
      // Handle specific authentication errors
      if (err.response?.status === 401) {
        const errorData = err.response.data
        
        // Check for invalid password error
        if (errorData?.error?.includes('Invalid password') || errorData?.code === 'AUTH_FAILED') {
          return {
            success: false,
            error_type: 'invalid_password',
            requires_password: true,
            failed_attempts: errorData?.failed_attempts || null,
            account_locked: errorData?.account_locked || false,
            message: errorData?.error || 'Invalid password. Please try again.'
          }
        }
        
        // Check for account suspended error
        if (errorData?.error?.includes('suspended') || errorData?.error?.includes('banned')) {
          return {
            success: false,
            error_type: 'account_suspended',
            message: errorData?.error || 'Account has been suspended. Please contact support.'
          }
        }
        
        // Generic authentication failure
        return {
          success: false,
          error_type: 'auth_failed',
          requires_password: errorData?.requires_password || true,
          message: errorData?.error || 'Authentication failed. Please check your credentials.'
        }
      }
      
      // Handle device conflict errors
      if (err.response?.status === 409) {
        return {
          success: false,
          error_type: 'device_conflict',
          message: err.response.data?.error || 'Device conflict detected'
        }
      }
      
      // Handle validation errors
      if (err.response?.status === 400) {
        return {
          success: false,
          error_type: 'validation_error',
          message: err.response.data?.error || error.value
        }
      }
      
      // Generic error
      return {
        success: false,
        error_type: 'system_error',
        message: error.value || 'Authentication failed. Please try again.'
      }
    } finally {
      loading.value = false
    }
  }

  const setupPassword = async (payload) => {
    try {
      loading.value = true
      error.value = ''
      
      const response = await api.post('/api/account/setup-password/', payload)
      
      return {
        success: true,
        message: response.data.message || 'Password set up successfully'
      }
      
    } catch (err) {
      error.value = api.handleError(err)
      throw new Error(error.value)
    } finally {
      loading.value = false
    }
  }

  const verifyOTP = async (payload) => {
    try {
      loading.value = true
      error.value = ''
      
      const response = await api.post('/api/auth/verify-otp/', payload)
      
      if (response.data.auth) {
        // Update tokens after OTP verification
        token.value = response.data.auth.access
        refreshToken.value = response.data.auth.refresh
        
        storage.set('auth_token', token.value)
        storage.set('refresh_token', refreshToken.value)
      }
      
      return {
        success: true,
        message: response.data.message || 'OTP verified successfully'
      }
      
    } catch (err) {
      error.value = api.handleError(err)
      return {
        success: false,
        message: error.value
      }
    } finally {
      loading.value = false
    }
  }

  // Optional: Regular authentication for backwards compatibility
  const authenticate = async (payload) => {
    try {
      loading.value = true
      error.value = ''
      
      const response = await api.post('/api/client/', payload)
      
      if (response.data.auth) {
        // Store tokens
        token.value = response.data.auth.access
        refreshToken.value = response.data.auth.refresh
        
        // Store user data
        user.value = {
          id: response.data.user.id,
          username: response.data.user.username,
          email: response.data.user.email,
          phone: response.data.client?.phone_number,
          client: response.data.client,
          device: response.data.device,
          session: response.data.session
        }
        
        // Persist to storage
        storage.set('auth_token', token.value)
        storage.set('refresh_token', refreshToken.value)
        storage.set('user', user.value)
        
        // Setup auto-refresh
        setupTokenRefresh()
      }
      
      return {
        success: true,
        requires_otp: false,
        requires_password: false,
        is_new_account: response.data.metadata?.is_new_user || false,
        session_id: response.data.session?.session_id,
        message: 'Authentication successful'
      }
      
    } catch (err) {
      error.value = api.handleError(err)
      return {
        success: false,
        message: error.value
      }
    } finally {
      loading.value = false
    }
  }

  // Existing methods
  const logout = async () => {
    try {
      if (refreshToken.value) {
        await api.post('/api/logout/', { refresh: refreshToken.value })
      }
    } catch (error) {
      console.warn('Logout API call failed:', error)
    } finally {
      clearAuth()
      window.location.href = '/'
    }
  }

  const refreshAuth = async () => {
    try {
      if (!refreshToken.value) throw new Error('No refresh token')
      
      const response = await api.post('/api/token/refresh/', {
        refresh: refreshToken.value,
        device_mac: user.value?.device?.mac_address
      })
      
      // Update tokens
      token.value = response.data.access
      if (response.data.refresh) {
        refreshToken.value = response.data.refresh
      }
      
      // Update storage
      storage.set('auth_token', token.value)
      storage.set('refresh_token', refreshToken.value)
      
      // Setup next refresh
      setupTokenRefresh()
      
      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      clearAuth()
      return false
    }
  }

  const setupTokenRefresh = () => {
    if (!token.value) return
    
    try {
      const expiry = jwtService.getExpiry(token.value)
      const now = Date.now()
      const refreshTime = expiry - 5 * 60 * 1000 // 5 minutes before expiry
      
      if (refreshTime > now) {
        setTimeout(async () => {
          if (token.value && refreshToken.value) {
            await refreshAuth()
          }
        }, refreshTime - now)
      }
    } catch (error) {
      console.warn('Failed to setup token refresh:', error)
    }
  }

  const clearError = () => {
    error.value = ''
  }

  const setError = (message) => {
    error.value = message
  }

  const clearAuth = () => {
    user.value = null
    token.value = ''
    refreshToken.value = ''
    session.value = null
    storage.remove('auth_token')
    storage.remove('refresh_token')
    storage.remove('user')
    storage.remove('last_activity')
  }

  // Check for existing valid session
  const checkStoredSession = async () => {
    const storedToken = storage.get('auth_token')
    const storedRefresh = storage.get('refresh_token')
    const storedUser = storage.get('user')
    
    // Check if we have valid tokens
    if (storedToken && jwtService.isValid(storedToken)) {
      token.value = storedToken
      refreshToken.value = storedRefresh
      user.value = storedUser
      
      setupTokenRefresh()
      setupPeriodicRefresh()
      setupSessionTracking()
      
      return true
    }
    
    // Check if we can do seamless re-auth
    if (storedUser?.phone) {
      const success = await attemptSeamlessReauth(storedUser)
      if (success) {
        setupPeriodicRefresh()
        setupSessionTracking()
        return true
      }
    }
    
    // No valid session found
    clearAuth()
    return false
  }

  // Device Auto-Authentication for seamless token refresh
  const deviceAutoAuth = async (deviceMac = null, deviceIP = null) => {
    try {
      // Generate fallback network data if not provided
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
      
      const payload = {
        current_mac: deviceMac || user.value?.device?.mac_address || generateFallbackMac(),
        current_ip: deviceIP || generateFallbackIP(),
        location_id: 1,
        device_info: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language,
          seamless_reauth: true,
          timestamp: new Date().toISOString()
        }
      }
      
      const response = await api.post('/api/users/auth/device-auto/', payload)
      
      if (response.data.success) {
        // Update tokens
        token.value = response.data.token
        
        // Update user data
        if (response.data.user_id) {
          user.value = {
            ...user.value,
            id: response.data.user_id,
            account: response.data.account
          }
        }
        
        // Persist to storage
        storage.set('auth_token', token.value)
        storage.set('user', user.value)
        storage.set('last_activity', Date.now())
        
        return {
          success: true,
          token: response.data.token,
          message: response.data.message
        }
      }
      
      return {
        success: false,
        error: response.data.error || 'Device auto-auth failed'
      }
      
    } catch (error) {
      console.error('Device auto-auth error:', error)
      return {
        success: false,
        error: error.message || 'Device auto-auth failed'
      }
    }
  }

  // Set authentication data (used by device auto-auth)
  const setAuthData = (authData) => {
    if (authData.token) {
      token.value = authData.token
      storage.set('auth_token', authData.token)
    }
    
    if (authData.account) {
      if (!user.value) user.value = {}
      user.value.account = authData.account
    }
    
    if (authData.user_id) {
      if (!user.value) user.value = {}
      user.value.id = authData.user_id
    }
    
    if (user.value) {
      storage.set('user', user.value)
    }
    
    storage.set('last_activity', Date.now())
    setupTokenRefresh()
  }
  const attemptSeamlessReauth = async (storedUser) => {
    try {
      loading.value = true
      
      // Generate fallback network data if needed
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
      
      // Prepare seamless auth payload
      const payload = {
        phone: storedUser.phone,
        current_mac: storedUser.device?.mac_address || generateFallbackMac(),
        current_ip: generateFallbackIP(),
        device_info: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          seamless_reauth: true
        },
        timestamp: new Date().toISOString()
      }
      
      // Attempt passwordless authentication
      const response = await api.post('/api/auth/passwordless/', payload)
      
      if (response.data.auth) {
        // Store new tokens
        token.value = response.data.auth.access
        refreshToken.value = response.data.auth.refresh
        
        // Update user data
        user.value = {
          id: response.data.user.id,
          username: response.data.user.username,
          email: response.data.user.email,
          phone: response.data.user.phone || response.data.client?.phone_number,
          client: response.data.client,
          device: response.data.device,
          session: response.data.session
        }
        
        // Persist to storage with activity tracking
        storage.set('auth_token', token.value)
        storage.set('refresh_token', refreshToken.value)
        storage.set('user', user.value)
        storage.set('last_activity', Date.now())
        
        // Setup auto-refresh
        setupTokenRefresh()
        
        return true
      }
      
      return false
      
    } catch (error) {
      console.warn('Seamless re-auth failed:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // Setup periodic refresh check
  const setupPeriodicRefresh = () => {
    setInterval(() => {
      if (isTokenExpiringSoon.value && refreshToken.value) {
        refreshAuth()
      }
    }, 2 * 60 * 1000) // 2 minutes
  }

  // Initialize from storage with seamless re-authentication
  const initialize = async () => {
    const storedToken = storage.get('auth_token')
    const storedRefresh = storage.get('refresh_token')
    const storedUser = storage.get('user')
    const lastActivity = storage.get('last_activity')
    
    // Check if tokens exist and are structurally valid
    if (storedToken && storedRefresh && jwtService.isValid(storedToken)) {
      token.value = storedToken
      refreshToken.value = storedRefresh
      user.value = storedUser
      
      // Update last activity
      storage.set('last_activity', Date.now())
      
      setupTokenRefresh()
      setupPeriodicRefresh()
      setupSessionTracking()
      
    } else if (storedUser?.phone) {
      // Tokens expired but we have user data - attempt seamless re-auth
      console.log('Tokens expired, attempting seamless re-authentication...')
      
      try {
        const success = await attemptSeamlessReauth(storedUser)
        if (success) {
          console.log('Seamless re-authentication successful')
          setupPeriodicRefresh()
          setupSessionTracking()
        } else {
          console.log('Seamless re-authentication failed, clearing session')
          clearAuth()
        }
      } catch (error) {
        console.warn('Seamless re-authentication error:', error)
        clearAuth()
      }
    } else {
      // No valid tokens or user data found
      clearAuth()
    }
  }

  // Session activity tracking to extend session on user activity
  const setupSessionTracking = () => {
    let activityTimer = null
    const ACTIVITY_THRESHOLD = 30 * 60 * 1000 // 30 minutes
    
    const resetActivityTimer = () => {
      if (activityTimer) clearTimeout(activityTimer)
      
      // Update last activity timestamp
      storage.set('last_activity', Date.now())
      
      activityTimer = setTimeout(() => {
        // User inactive for 30 minutes - proactively refresh if needed
        if (isTokenExpiringSoon.value && refreshToken.value) {
          refreshAuth()
        }
      }, ACTIVITY_THRESHOLD)
    }
    
    // Single throttled event handler for all activity events
    let throttleTimer = null
    const throttledHandler = () => {
      if (!throttleTimer) {
        throttleTimer = setTimeout(() => {
          resetActivityTimer()
          throttleTimer = null
        }, 1000) // Throttle to once per second
      }
    }
    
    // Track user activity with single handler
    const events = ['mousedown', 'keypress', 'scroll', 'touchstart']
    events.forEach(event => {
      document.addEventListener(event, throttledHandler, { passive: true, once: false })
    })
    
    // Initial timer
    resetActivityTimer()
  }

  return {
    // State
    user,
    token,
    refreshToken,
    loading,
    error,
    session,
    
    // Getters
    isAuthenticated,
    currentUser,
    authHeaders,
    isTokenExpiringSoon,
    tokenExpiresAt,
    
    // Passwordless Authentication Actions
    checkAccountStatus,
    passwordlessAuthenticate,
    setupPassword,
    verifyOTP,
    authenticate, // For regular auth
    attemptSeamlessReauth, // For seamless re-auth
    
    // Backward compatibility
    setAuthData,
    
    // Existing methods
    logout,
    refreshAuth,
    clearError,
    setError,
    initialize,
    clearAuth,
    checkStoredSession
  }
})