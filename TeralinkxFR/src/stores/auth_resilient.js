// stores/auth.js - ENHANCED VERSION WITH RESILIENCE FEATURES
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, setAuthToken } from '../services/api'
import { jwtService } from '../services/jwt'
import { storage } from '../utils/storage'
import { smartTokenManager } from '../services/smartTokenManager'
import { TokenHealthMonitor } from '../services/tokenHealthMonitor'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref('')
  const refreshToken = ref('')
  const loading = ref(false)
  const error = ref('')
  const session = ref(null)
  const isOfflineMode = ref(false)
  
  // Health monitoring
  let tokenHealthMonitor = null

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

  // Initialize from storage with resilience features
  const initialize = async () => {
    console.log('🚀 Initializing auth store with resilience features...')
    
    try {
      // Validate stored tokens with smart token manager
      const validatedTokens = await smartTokenManager.validateStoredTokens()
      
      if (validatedTokens) {
        // Tokens are valid or were successfully recovered
        token.value = validatedTokens.access
        refreshToken.value = validatedTokens.refresh
        
        // Get user data from storage or API
        const storedUser = storage.get('user')
        if (storedUser) {
          user.value = storedUser
        } else {
          // Fetch fresh user data
          await fetchUserData()
        }
        
        // Set authorization header
        setAuthToken(token.value)
        
        // Start health monitoring
        startHealthMonitoring()
        
        // Setup token refresh
        setupTokenRefresh()
        setupPeriodicRefresh()
        setupSessionTracking()
        
        console.log('✅ Auth initialization successful')
        
      } else {
        // No valid tokens found, clear everything
        console.log('📭 No valid tokens found during initialization')
        clearAuth()
      }
      
    } catch (error) {
      console.error('💥 Auth initialization error:', error)
      clearAuth()
    }
  }
  
  // Start token health monitoring
  const startHealthMonitoring = () => {
    if (!tokenHealthMonitor) {
      tokenHealthMonitor = new TokenHealthMonitor({
        token: token.value,
        user: user.value,
        clearAuth: clearAuth,
        refreshUserData: fetchUserData
      })
      
      // Listen for health monitoring events
      window.addEventListener('tokenHealthEvent', handleHealthEvent)
    }
    
    tokenHealthMonitor.startMonitoring()
  }
  
  // Stop token health monitoring
  const stopHealthMonitoring = () => {
    if (tokenHealthMonitor) {
      tokenHealthMonitor.stopMonitoring()
      window.removeEventListener('tokenHealthEvent', handleHealthEvent)
    }
  }
  
  // Handle health monitoring events
  const handleHealthEvent = (event) => {
    const { type, data } = event.detail
    
    switch (type) {
      case 'backend_restart':
        console.log('🔄 Backend restart detected by health monitor')
        break
        
      case 'recovered':
        console.log('🎉 Token recovery successful')
        // Tokens should already be updated by the monitor
        break
        
      case 'recovery_failed':
        console.log('💥 Token recovery failed, clearing auth')
        clearAuth()
        break
        
      case 'offline':
        console.log('📴 Entering offline mode')
        isOfflineMode.value = true
        break
        
      case 'online':
        console.log('🌐 Exiting offline mode')
        isOfflineMode.value = false
        break
        
      case 'show_recovery_failed':
        setError('Session expired. Please sign in again.')
        setTimeout(() => {
          window.location.href = '/'
        }, 2000)
        break
    }
  }
  
  // Fetch user data from API
  const fetchUserData = async () => {
    try {
      if (!token.value) return
      
      const response = await api.get('/api/me/')
      if (response.data) {
        user.value = {
          id: response.data.user_id,
          username: response.data.username,
          email: response.data.email,
          phone: response.data.client?.phone_number,
          client: response.data.client
        }
        
        storage.set('user', user.value)
        return true
      }
      
      return false
      
    } catch (error) {
      console.error('Failed to fetch user data:', error)
      return false
    }
  }

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
        // Store tokens with smart token manager
        token.value = response.data.auth.access
        refreshToken.value = response.data.auth.refresh
        
        await smartTokenManager.storeTokens({
          access: token.value,
          refresh: refreshToken.value,
          user_data: response.data.user
        })
        
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
        storage.set('user', user.value)
        storage.set('last_activity', Date.now())
        
        // Set authorization header
        setAuthToken(token.value)
        
        // Start health monitoring
        startHealthMonitoring()
        
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
        
        await smartTokenManager.storeTokens({
          access: token.value,
          refresh: refreshToken.value,
          user_data: user.value
        })
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

  // Enhanced logout with health monitoring cleanup
  const logout = async () => {
    try {
      // Stop health monitoring
      stopHealthMonitoring()
      
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

  // Enhanced refresh with smart token manager
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
      
      // Store tokens with smart token manager
      await smartTokenManager.storeTokens({
        access: token.value,
        refresh: refreshToken.value,
        user_data: user.value
      })
      
      // Setup next refresh
      setupTokenRefresh()
      
      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      
      // Attempt recovery using smart token manager
      const recoveredTokens = await smartTokenManager.attemptTokenRecovery({
        access: token.value,
        refresh: refreshToken.value,
        user_data: user.value
      })
      
      if (recoveredTokens) {
        token.value = recoveredTokens.access
        refreshToken.value = recoveredTokens.refresh
        setupTokenRefresh()
        return true
      }
      
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

  // Enhanced clear auth with monitoring cleanup
  const clearAuth = () => {
    // Stop health monitoring
    stopHealthMonitoring()
    
    // Clear state
    user.value = null
    token.value = ''
    refreshToken.value = ''
    session.value = null
    isOfflineMode.value = false
    
    // Clear storage
    storage.remove('auth_token')
    storage.remove('refresh_token')
    storage.remove('user')
    storage.remove('last_activity')
    
    // Clear smart token manager
    smartTokenManager.clearTokens()
    
    // Clear authorization header
    setAuthToken(null)
  }

  // Set offline mode
  const setOfflineMode = (offline) => {
    isOfflineMode.value = offline
  }
  
  // Get health monitoring status
  const getHealthStatus = () => {
    return tokenHealthMonitor ? tokenHealthMonitor.getStatus() : null
  }

  // Setup periodic refresh check
  const setupPeriodicRefresh = () => {
    setInterval(() => {
      if (isTokenExpiringSoon.value && refreshToken.value) {
        refreshAuth()
      }
    }, 2 * 60 * 1000) // 2 minutes
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
    isOfflineMode,
    
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
    
    // Auth methods
    logout,
    refreshAuth,
    clearError,
    setError,
    initialize,
    clearAuth,
    
    // Health monitoring
    startHealthMonitoring,
    stopHealthMonitoring,
    setOfflineMode,
    getHealthStatus,
    fetchUserData,
  }
})