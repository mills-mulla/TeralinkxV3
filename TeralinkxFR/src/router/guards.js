// src/router/guards.js - Enhanced Route Guards with Auth Resilience
import { useAuthStore } from '@/stores/auth_resilient'
import { smartTokenManager } from '@/services/smartTokenManager'

/**
 * Enhanced authentication guard with resilience features
 */
export class AuthGuard {
  constructor() {
    this.maxAuthWaitTime = 10000 // 10 seconds max wait for auth
    this.retryAttempts = 3
    this.guardCache = new Map()
    this.lastGuardCheck = null
  }

  /**
   * Main authentication guard function
   */
  async checkAuth(to, from, next) {
    const authStore = useAuthStore()
    
    console.log(`🛡️ Route guard checking: ${to.path}`)
    
    try {
      // Phase 1: Quick cache check for recent successful auth
      if (this.isRecentlyAuthenticated()) {
        console.log('✅ Using cached auth status')
        return this.handleAuthenticatedUser(to, from, next)
      }

      // Phase 2: Check if auth store is initialized
      if (!authStore.token && !authStore.loading) {
        console.log('🔄 Initializing auth store...')
        await authStore.initialize()
      }

      // Phase 3: Wait for any ongoing authentication process
      await this.waitForAuthCompletion(authStore)

      // Phase 4: Validate current authentication status
      const authStatus = await this.validateAuthentication(authStore)
      
      if (authStatus.isValid) {
        console.log('✅ Authentication valid')
        this.cacheAuthSuccess()
        return this.handleAuthenticatedUser(to, from, next)
      }

      // Phase 5: Attempt recovery if authentication failed
      console.log('🔧 Authentication invalid, attempting recovery...')
      const recoveryResult = await this.attemptAuthRecovery(authStore)
      
      if (recoveryResult.success) {
        console.log('🎉 Auth recovery successful')
        this.cacheAuthSuccess()
        return this.handleAuthenticatedUser(to, from, next)
      }

      // Phase 6: All attempts failed, redirect to login
      console.log('❌ Authentication failed, redirecting to login')
      return this.handleUnauthenticatedUser(to, from, next, recoveryResult.reason)

    } catch (error) {
      console.error('💥 Route guard error:', error)
      return this.handleAuthError(to, from, next, error)
    }
  }

  /**
   * Check if user was recently authenticated (cache optimization)
   */
  isRecentlyAuthenticated() {
    const cacheTimeout = 30000 // 30 seconds
    const now = Date.now()
    
    if (this.lastGuardCheck && (now - this.lastGuardCheck) < cacheTimeout) {
      const authStore = useAuthStore()
      return authStore.isAuthenticated && authStore.token
    }
    
    return false
  }

  /**
   * Wait for authentication completion with timeout
   */
  async waitForAuthCompletion(authStore) {
    if (!authStore.loading) return

    console.log('⏳ Waiting for auth completion...')
    const startTime = Date.now()
    
    while (authStore.loading && (Date.now() - startTime) < this.maxAuthWaitTime) {
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    if (authStore.loading) {
      console.warn('⚠️ Auth initialization timeout')
    }
  }

  /**
   * Validate current authentication with multiple checks
   */
  async validateAuthentication(authStore) {
    const checks = []

    // Check 1: Basic token presence
    checks.push({
      name: 'token_presence',
      valid: !!authStore.token,
      reason: 'No access token'
    })

    // Check 2: Token structural validity
    if (authStore.token) {
      try {
        const isStructurallyValid = authStore.isAuthenticated
        checks.push({
          name: 'token_structure',
          valid: isStructurallyValid,
          reason: 'Token structurally invalid'
        })
      } catch (error) {
        checks.push({
          name: 'token_structure',
          valid: false,
          reason: `Token validation error: ${error.message}`
        })
      }
    }

    // Check 3: User data presence
    checks.push({
      name: 'user_data',
      valid: !!authStore.user,
      reason: 'No user data'
    })

    // Check 4: Token expiry check
    if (authStore.token) {
      const isExpiringSoon = authStore.isTokenExpiringSoon
      checks.push({
        name: 'token_expiry',
        valid: !isExpiringSoon,
        reason: 'Token expiring soon'
      })
    }

    // Evaluate all checks
    const failedChecks = checks.filter(check => !check.valid)
    const isValid = failedChecks.length === 0

    return {
      isValid,
      checks,
      failedChecks,
      reason: failedChecks.map(c => c.reason).join(', ')
    }
  }

  /**
   * Attempt authentication recovery using multiple strategies
   */
  async attemptAuthRecovery(authStore) {
    console.log('🔧 Starting auth recovery process...')
    
    const recoveryStrategies = [
      {
        name: 'token_refresh',
        handler: () => this.attemptTokenRefresh(authStore)
      },
      {
        name: 'smart_token_recovery',
        handler: () => this.attemptSmartTokenRecovery()
      },
      {
        name: 'device_auto_auth',
        handler: () => this.attemptDeviceAutoAuth()
      },
      {
        name: 'session_restoration',
        handler: () => this.attemptSessionRestoration(authStore)
      }
    ]

    for (const strategy of recoveryStrategies) {
      try {
        console.log(`🔄 Trying ${strategy.name}...`)
        const result = await Promise.race([
          strategy.handler(),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Timeout')), 5000)
          )
        ])

        if (result && result.success) {
          console.log(`✅ ${strategy.name} succeeded`)
          return { success: true, strategy: strategy.name }
        }
        
        console.log(`❌ ${strategy.name} failed:`, result?.error || 'Unknown error')
        
      } catch (error) {
        console.log(`⏰ ${strategy.name} timeout or error:`, error.message)
      }
    }

    return { 
      success: false, 
      reason: 'All recovery strategies failed',
      requiresManualAuth: true 
    }
  }

  /**
   * Strategy 1: Token refresh
   */
  async attemptTokenRefresh(authStore) {
    try {
      if (!authStore.refreshToken) {
        return { success: false, error: 'No refresh token' }
      }

      const success = await authStore.refreshAuth()
      return { success }
      
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Strategy 2: Smart token recovery
   */
  async attemptSmartTokenRecovery() {
    try {
      const storedTokens = smartTokenManager.getStoredTokens()
      if (!storedTokens) {
        return { success: false, error: 'No stored tokens' }
      }

      const recoveredTokens = await smartTokenManager.attemptTokenRecovery(storedTokens)
      
      if (recoveredTokens) {
        // Update auth store with recovered tokens
        const authStore = useAuthStore()
        authStore.token = recoveredTokens.access
        authStore.refreshToken = recoveredTokens.refresh
        
        return { success: true }
      }

      return { success: false, error: 'Token recovery failed' }
      
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Strategy 3: Device auto-auth
   */
  async attemptDeviceAutoAuth() {
    try {
      const authStore = useAuthStore()
      
      // Use the device auto-auth from auth store
      if (typeof authStore.deviceAutoAuth === 'function') {
        const result = await authStore.deviceAutoAuth()
        return result
      }

      return { success: false, error: 'Device auto-auth not available' }
      
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Strategy 4: Session restoration
   */
  async attemptSessionRestoration(authStore) {
    try {
      // Check for stored user data that might allow session restoration
      const storedUser = localStorage.getItem('user')
      if (!storedUser) {
        return { success: false, error: 'No stored user data' }
      }

      const userData = JSON.parse(storedUser)
      if (userData.phone && typeof authStore.attemptSeamlessReauth === 'function') {
        const success = await authStore.attemptSeamlessReauth(userData)
        return { success }
      }

      return { success: false, error: 'Session restoration not possible' }
      
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Handle authenticated user
   */
  handleAuthenticatedUser(to, from, next) {
    // Additional role-based checks could go here
    const authStore = useAuthStore()
    
    // Check if user account is active
    if (authStore.user?.client?.status !== 'active') {
      console.warn('⚠️ User account is not active')
      return this.handleInactiveAccount(to, from, next)
    }

    // Check for any route-specific permissions
    if (to.meta.permissions) {
      const hasPermission = this.checkRoutePermissions(to.meta.permissions, authStore.user)
      if (!hasPermission) {
        console.warn('⚠️ User lacks required permissions for route')
        return this.handleInsufficientPermissions(to, from, next)
      }
    }

    // All checks passed
    next()
  }

  /**
   * Handle unauthenticated user
   */
  handleUnauthenticatedUser(to, from, next, reason = 'Authentication required') {
    const redirectPath = this.buildRedirectPath(to, reason)
    
    // Clear any stale auth data
    const authStore = useAuthStore()
    authStore.clearAuth()
    
    // Redirect to login
    next(redirectPath)
  }

  /**
   * Handle authentication errors
   */
  handleAuthError(to, from, next, error) {
    console.error('💥 Authentication error:', error)
    
    const redirectPath = this.buildRedirectPath(to, `Authentication error: ${error.message}`)
    next(redirectPath)
  }

  /**
   * Handle inactive account
   */
  handleInactiveAccount(to, from, next) {
    const redirectPath = this.buildRedirectPath(to, 'Account is inactive. Please contact support.')
    next(redirectPath)
  }

  /**
   * Handle insufficient permissions
   */
  handleInsufficientPermissions(to, from, next) {
    // Redirect to dashboard or show error
    next({
      path: '/dashboard',
      query: { 
        error: 'Insufficient permissions',
        attempted: to.path 
      }
    })
  }

  /**
   * Check route-specific permissions
   */
  checkRoutePermissions(requiredPermissions, user) {
    if (!requiredPermissions || !Array.isArray(requiredPermissions)) {
      return true
    }

    // Example permission checking logic
    const userPermissions = user?.permissions || []
    const userRole = user?.role || 'user'

    // Admin has all permissions
    if (userRole === 'admin') return true

    // Check if user has all required permissions
    return requiredPermissions.every(permission => 
      userPermissions.includes(permission)
    )
  }

  /**
   * Build redirect path with context
   */
  buildRedirectPath(to, reason) {
    const params = new URLSearchParams()
    
    if (reason) params.set('reason', reason)
    if (to.path !== '/') params.set('redirect', to.fullPath)
    
    const queryString = params.toString()
    return queryString ? `/?${queryString}` : '/'
  }

  /**
   * Cache successful authentication
   */
  cacheAuthSuccess() {
    this.lastGuardCheck = Date.now()
  }

  /**
   * Clear authentication cache
   */
  clearCache() {
    this.lastGuardCheck = null
    this.guardCache.clear()
  }
}

// Export singleton instance
export const authGuard = new AuthGuard()

/**
 * Route-specific guards
 */
export const routeGuards = {
  /**
   * Standard authentication guard
   */
  requiresAuth: async (to, from, next) => {
    await authGuard.checkAuth(to, from, next)
  },

  /**
   * Admin-only guard
   */
  requiresAdmin: async (to, from, next) => {
    await authGuard.checkAuth(to, from, (result) => {
      if (typeof result === 'string' || typeof result === 'object') {
        // Authentication failed
        return next(result)
      }

      // Check admin role
      const authStore = useAuthStore()
      if (authStore.user?.role !== 'admin') {
        return next({
          path: '/dashboard',
          query: { error: 'Admin access required' }
        })
      }

      next()
    })
  },

  /**
   * Guest-only guard (for login page)
   */
  guestOnly: async (to, from, next) => {
    const authStore = useAuthStore()
    
    // Quick check for existing auth
    if (authStore.isAuthenticated && authStore.user) {
      console.log('✅ User already authenticated, redirecting to dashboard')
      return next('/dashboard')
    }

    // Allow access to guest pages
    next()
  },

  /**
   * Active account guard
   */
  requiresActiveAccount: async (to, from, next) => {
    await authGuard.checkAuth(to, from, (result) => {
      if (typeof result === 'string' || typeof result === 'object') {
        return next(result)
      }

      const authStore = useAuthStore()
      if (authStore.user?.client?.status !== 'active') {
        return next({
          path: '/',
          query: { 
            reason: 'Account is inactive. Please contact support.',
            redirect: to.fullPath 
          }
        })
      }

      next()
    })
  }
}