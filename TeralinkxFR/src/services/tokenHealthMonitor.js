// TeralinkxFR/src/services/tokenHealthMonitor.js - Real-time Token Health Monitoring
import { api } from './api'
import { smartTokenManager } from './smartTokenManager'

class TokenHealthMonitor {
  constructor(authStore) {
    this.authStore = authStore
    this.healthCheckInterval = 60000 // 1 minute
    this.isMonitoring = false
    this.healthCheckTimer = null
    this.consecutiveFailures = 0
    this.maxConsecutiveFailures = 3
    this.backoffMultiplier = 1
    this.maxBackoffMultiplier = 8
    this.isOffline = false
    this.lastSuccessfulCheck = null
  }

  /**
   * Start proactive token health monitoring
   */
  startMonitoring() {
    if (this.isMonitoring) {
      console.log('🔍 Token health monitoring already running')
      return
    }
    
    this.isMonitoring = true
    this.consecutiveFailures = 0
    this.backoffMultiplier = 1
    
    console.log('🔍 Starting token health monitoring')
    this.scheduleNextHealthCheck()
    
    // Listen for network status changes
    window.addEventListener('online', this.handleNetworkOnline.bind(this))
    window.addEventListener('offline', this.handleNetworkOffline.bind(this))
  }

  /**
   * Stop token health monitoring
   */
  stopMonitoring() {
    if (!this.isMonitoring) return
    
    this.isMonitoring = false
    
    if (this.healthCheckTimer) {
      clearTimeout(this.healthCheckTimer)
      this.healthCheckTimer = null
    }
    
    window.removeEventListener('online', this.handleNetworkOnline.bind(this))
    window.removeEventListener('offline', this.handleNetworkOffline.bind(this))
    
    console.log('🔍 Token health monitoring stopped')
  }

  /**
   * Schedule next health check with exponential backoff on failures
   */
  scheduleNextHealthCheck() {
    if (!this.isMonitoring) return
    
    const interval = this.healthCheckInterval * this.backoffMultiplier
    
    this.healthCheckTimer = setTimeout(async () => {
      await this.performHealthCheck()
      this.scheduleNextHealthCheck()
    }, interval)
  }

  /**
   * Perform comprehensive health check
   */
  async performHealthCheck() {
    if (!this.isMonitoring || this.isOffline) return
    
    try {
      console.log('🔍 Performing token health check...')
      
      // Check if we have tokens
      if (!this.authStore.token) {
        console.log('📭 No token available for health check')
        return
      }

      // Perform health check request
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/health-check/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.authStore.token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        await this.handleHealthCheckSuccess(response)
      } else {
        await this.handleHealthCheckFailure(response)
      }
      
    } catch (error) {
      await this.handleHealthCheckError(error)
    }
  }

  /**
   * Handle successful health check
   */
  async handleHealthCheckSuccess(response) {
    try {
      const data = await response.json()
      
      // Reset failure counters
      this.consecutiveFailures = 0
      this.backoffMultiplier = 1
      this.lastSuccessfulCheck = Date.now()
      
      // Check for backend version changes
      const backendVersion = response.headers.get('X-Backend-Version')
      const tokenVersion = response.headers.get('X-Token-Version')
      
      if (backendVersion && smartTokenManager.backendVersion && 
          backendVersion !== smartTokenManager.backendVersion) {
        console.log('🔄 Backend version change detected during health check')
        await this.handleBackendRestart()
        return
      }
      
      // Update stored versions
      if (backendVersion) smartTokenManager.backendVersion = backendVersion
      if (tokenVersion) smartTokenManager.tokenVersion = tokenVersion
      
      console.log('✅ Token health check passed')
      
      // Emit health check success event
      this.emitHealthEvent('healthy', {
        backend_version: backendVersion,
        token_version: tokenVersion,
        user_authenticated: data.user_authenticated,
        timestamp: data.timestamp
      })
      
    } catch (error) {
      console.error('❌ Error processing health check response:', error)
    }
  }

  /**
   * Handle failed health check
   */
  async handleHealthCheckFailure(response) {
    this.consecutiveFailures++
    
    console.log(`❌ Token health check failed (${this.consecutiveFailures}/${this.maxConsecutiveFailures}):`, 
                response.status, response.statusText)
    
    if (response.status === 401) {
      // Token is invalid - attempt recovery
      console.log('🔧 Token invalid, attempting recovery...')
      await this.attemptTokenRecovery('invalid_token')
      
    } else if (response.status === 503) {
      // Backend unavailable
      console.log('🚫 Backend unavailable, entering offline mode...')
      this.enterOfflineMode()
      
    } else if (response.status >= 500) {
      // Server error - increase backoff
      this.increaseBackoff()
      
    } else {
      // Other client errors
      console.log('⚠️ Unexpected health check failure:', response.status)
    }
    
    // Emit health check failure event
    this.emitHealthEvent('unhealthy', {
      status: response.status,
      consecutive_failures: this.consecutiveFailures,
      backoff_multiplier: this.backoffMultiplier
    })
    
    // If too many consecutive failures, attempt recovery
    if (this.consecutiveFailures >= this.maxConsecutiveFailures) {
      console.log('💥 Too many consecutive health check failures, attempting recovery...')
      await this.attemptTokenRecovery('consecutive_failures')
    }
  }

  /**
   * Handle health check network error
   */
  async handleHealthCheckError(error) {
    this.consecutiveFailures++
    
    console.log(`🌐 Token health check network error (${this.consecutiveFailures}/${this.maxConsecutiveFailures}):`, 
                error.message)
    
    // Check if it's a network connectivity issue
    if (!navigator.onLine) {
      this.handleNetworkOffline()
      return
    }
    
    // Increase backoff for network errors
    this.increaseBackoff()
    
    // Emit health check error event
    this.emitHealthEvent('error', {
      error: error.message,
      consecutive_failures: this.consecutiveFailures,
      backoff_multiplier: this.backoffMultiplier
    })
    
    // If too many consecutive failures, attempt recovery
    if (this.consecutiveFailures >= this.maxConsecutiveFailures) {
      console.log('💥 Too many consecutive health check errors, attempting recovery...')
      await this.attemptTokenRecovery('network_errors')
    }
  }

  /**
   * Attempt token recovery
   */
  async attemptTokenRecovery(reason) {
    try {
      console.log(`🔧 Attempting token recovery due to: ${reason}`)
      
      // Get stored tokens for recovery
      const storedTokens = smartTokenManager.getStoredTokens()
      
      // Attempt comprehensive recovery
      const recoveredTokens = await smartTokenManager.attemptTokenRecovery(storedTokens)
      
      if (recoveredTokens) {
        // Update auth store with recovered tokens
        this.authStore.token = recoveredTokens.access
        this.authStore.refreshToken = recoveredTokens.refresh
        
        // Reset failure counters
        this.consecutiveFailures = 0
        this.backoffMultiplier = 1
        
        console.log('🎉 Token recovery successful')
        
        // Emit recovery success event
        this.emitHealthEvent('recovered', {
          reason: reason,
          recovery_method: 'automatic'
        })
        
      } else {
        console.log('💥 Token recovery failed, user intervention required')
        
        // Emit recovery failure event
        this.emitHealthEvent('recovery_failed', {
          reason: reason,
          requires_manual_auth: true
        })
        
        // Clear auth and redirect to login
        this.authStore.clearAuth()
        this.showRecoveryFailedNotification()
      }
      
    } catch (error) {
      console.error('💥 Token recovery error:', error)
      
      // Emit recovery error event
      this.emitHealthEvent('recovery_error', {
        reason: reason,
        error: error.message
      })
    }
  }

  /**
   * Handle backend restart detection
   */
  async handleBackendRestart() {
    console.log('🔄 Backend restart detected, attempting seamless recovery...')
    
    // Emit backend restart event
    this.emitHealthEvent('backend_restart', {
      timestamp: Date.now()
    })
    
    // Attempt token recovery
    await this.attemptTokenRecovery('backend_restart')
  }

  /**
   * Enter offline mode
   */
  enterOfflineMode() {
    if (this.isOffline) return
    
    this.isOffline = true
    console.log('📴 Entering offline mode')
    
    // Cache user data for offline operation
    this.cacheUserDataForOffline()
    
    // Show offline indicator
    this.showOfflineNotification()
    
    // Emit offline event
    this.emitHealthEvent('offline', {
      timestamp: Date.now()
    })
  }

  /**
   * Exit offline mode
   */
  async exitOfflineMode() {
    if (!this.isOffline) return
    
    this.isOffline = false
    console.log('🌐 Exiting offline mode')
    
    // Reset failure counters
    this.consecutiveFailures = 0
    this.backoffMultiplier = 1
    
    // Attempt to sync any queued operations
    await this.syncQueuedOperations()
    
    // Refresh user data
    await this.authStore.refreshUserData()
    
    // Hide offline indicator
    this.hideOfflineNotification()
    
    // Emit online event
    this.emitHealthEvent('online', {
      timestamp: Date.now()
    })
  }

  /**
   * Handle network online event
   */
  handleNetworkOnline() {
    console.log('🌐 Network connection restored')
    this.exitOfflineMode()
  }

  /**
   * Handle network offline event
   */
  handleNetworkOffline() {
    console.log('📴 Network connection lost')
    this.enterOfflineMode()
  }

  /**
   * Increase backoff multiplier
   */
  increaseBackoff() {
    this.backoffMultiplier = Math.min(this.backoffMultiplier * 2, this.maxBackoffMultiplier)
    console.log(`⏰ Increased health check backoff to ${this.backoffMultiplier}x`)
  }

  /**
   * Cache user data for offline operation
   */
  cacheUserDataForOffline() {
    try {
      const userData = {
        user: this.authStore.user,
        balance: this.authStore.user?.client?.balance,
        lastSync: Date.now()
      }
      
      localStorage.setItem('offline_user_data', JSON.stringify(userData))
      console.log('💾 User data cached for offline mode')
      
    } catch (error) {
      console.error('❌ Failed to cache user data:', error)
    }
  }

  /**
   * Sync queued operations when coming back online
   */
  async syncQueuedOperations() {
    try {
      // Implementation for syncing queued operations
      console.log('🔄 Syncing queued operations...')
      
      // This would sync any operations that were queued while offline
      // For now, just log that sync would happen here
      
    } catch (error) {
      console.error('❌ Failed to sync queued operations:', error)
    }
  }

  /**
   * Show offline notification to user
   */
  showOfflineNotification() {
    // Emit event for UI to show offline indicator
    this.emitHealthEvent('show_offline_indicator', {
      message: 'You are currently offline. Some features may be limited.'
    })
  }

  /**
   * Hide offline notification
   */
  hideOfflineNotification() {
    // Emit event for UI to hide offline indicator
    this.emitHealthEvent('hide_offline_indicator', {})
  }

  /**
   * Show recovery failed notification
   */
  showRecoveryFailedNotification() {
    // Emit event for UI to show recovery failed message
    this.emitHealthEvent('show_recovery_failed', {
      message: 'Session expired. Please sign in again.',
      action: 'redirect_to_login'
    })
  }

  /**
   * Emit health monitoring events
   */
  emitHealthEvent(eventType, data) {
    const event = new CustomEvent('tokenHealthEvent', {
      detail: {
        type: eventType,
        data: data,
        timestamp: Date.now()
      }
    })
    
    window.dispatchEvent(event)
  }

  /**
   * Get monitoring status
   */
  getStatus() {
    return {
      isMonitoring: this.isMonitoring,
      isOffline: this.isOffline,
      consecutiveFailures: this.consecutiveFailures,
      backoffMultiplier: this.backoffMultiplier,
      lastSuccessfulCheck: this.lastSuccessfulCheck,
      nextCheckIn: this.healthCheckTimer ? 
        this.healthCheckInterval * this.backoffMultiplier : null
    }
  }
}

export { TokenHealthMonitor }