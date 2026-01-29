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
  const authHeaders = computed(() => ({
    Authorization: `Bearer ${token.value}`,
    'Content-Type': 'application/json'
  }))

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
        message: response.data.message || ''
      }
      
    } catch (err) {
      // If account doesn't exist, return appropriate status
      if (err.response?.status === 404) {
        return {
          exists: false,
          requires_password: false,
          requires_otp: false,
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
        
        // Store user data
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
        
        // Persist to storage
        storage.set('auth_token', token.value)
        storage.set('refresh_token', refreshToken.value)
        storage.set('user', user.value)
        
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
      
      // Return structured error response
      if (err.response?.data?.code === 'AUTH_FAILED') {
        return {
          success: false,
          requires_password: true, // Account requires password
          message: err.response.data.error || 'Password required'
        }
      }
      
      return {
        success: false,
        message: error.value || 'Authentication failed'
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
      
      token.value = response.data.access
      refreshToken.value = response.data.refresh
      
      storage.set('auth_token', token.value)
      storage.set('refresh_token', refreshToken.value)
      
      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      clearAuth()
      return false
    }
  }

  const setupTokenRefresh = () => {
    const expiry = jwtService.getExpiry(token.value)
    const refreshTime = expiry - 5 * 60 * 1000
    
    if (refreshTime > 0) {
      setTimeout(async () => {
        await refreshAuth()
      }, refreshTime - Date.now())
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
  }

  // Initialize from storage
  const initialize = () => {
    const storedToken = storage.get('auth_token')
    const storedRefresh = storage.get('refresh_token')
    const storedUser = storage.get('user')
    
    if (storedToken && jwtService.isValid(storedToken)) {
      token.value = storedToken
      refreshToken.value = storedRefresh
      user.value = storedUser
      setupTokenRefresh()
    } else {
      clearAuth()
    }
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
    
    // Passwordless Authentication Actions
    checkAccountStatus,
    passwordlessAuthenticate,
    setupPassword,
    verifyOTP,
    authenticate, // For regular auth
    
    // Existing Actions
    logout,
    refreshAuth,
    clearError,
    setError,
    initialize,
    clearAuth
  }
})