// TeralinkxFR/src/services/smartTokenManager.js - Smart Token Management with Recovery
import { api } from './api'
import { jwtService } from './jwt'
import { storage } from '../utils/storage'

class SmartTokenManager {
  constructor() {
    this.tokenValidationInterval = null
    this.maxRetries = 3
    this.retryDelay = 1000
    this.healthCheckInterval = 60000 // 1 minute
    this.isMonitoring = false
    this.backendVersion = null
    this.tokenVersion = null
  }

  /**
   * Store tokens with metadata for validation
   */
  async storeTokens(tokens) {
    try {
      // Get backend version for restart detection
      const backendVersion = await this.getBackendVersion()
      const deviceFingerprint = await this.getDeviceFingerprint()
      
      const tokenData = {
        ...tokens,
        stored_at: Date.now(),
        backend_version: backendVersion,
        token_version: this.tokenVersion,
        device_fingerprint: deviceFingerprint,
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString()
      }
      
      // Use both storage types for redundancy
      storage.set('auth_tokens', tokenData)
      sessionStorage.setItem('auth_tokens_backup', JSON.stringify(tokenData))
      
      console.log('🔐 Tokens stored with metadata:', {
        backend_version: backendVersion,
        token_version: this.tokenVersion,
        stored_at: new Date(tokenData.stored_at).toISOString()
      })
      
      return true
    } catch (error) {
      console.error('❌ Token storage failed:', error)
      return false
    }
  }

  /**
   * Validate stored tokens and detect backend restarts
   */
  async validateStoredTokens() {
    try {
      const stored = this.getStoredTokens()
      if (!stored) {
        console.log('📭 No stored tokens found')
        return null
      }

      // Check token structural validity
      if (!stored.access || !jwtService.isValid(stored.access)) {
        console.log('🔓 Stored access token is invalid')
        return await this.attemptTokenRecovery(stored)
      }

      // Check if backend version changed (indicates restart)
      const currentBackendVersion = await this.getBackendVersion()
      if (stored.backend_version && stored.backend_version !== currentBackendVersion) {
        console.log('🔄 Backend restart detected:', {
          stored: stored.backend_version,
          current: currentBackendVersion
        })
        return await this.attemptTokenRecovery(stored)
      }

      // Tokens appear valid
      console.log('✅ Stored tokens validated successfully')
      return stored
      
    } catch (error) {
      console.error('❌ Token validation error:', error)
      return await this.attemptTokenRecovery(this.getStoredTokens())
    }
  }

  /**
   * Attempt comprehensive token recovery using multiple strategies
   */
  async attemptTokenRecovery(oldTokens) {
    console.log('🔧 Starting comprehensive token recovery...')
    
    const recoveryStrategies = [
      {
        name: 'refresh_token',
        priority: 1,
        timeout: 3000,
        handler: () => this.refreshTokenStrategy(oldTokens)
      },
      {
        name: 'device_auto_auth',
        priority: 2,
        timeout: 5000,
        handler: () => this.deviceAutoAuthStrategy(oldTokens)
      },
      {
        name: 'enhanced_device_auth',
        priority: 3,
        timeout: 7000,
        handler: () => this.enhancedDeviceAuthStrategy(oldTokens)
      },
      {
        name: 'session_recovery',
        priority: 4,
        timeout: 4000,
        handler: () => this.sessionRecoveryStrategy(oldTokens)
      }
    ]

    // Try strategies in parallel with timeouts
    const promises = recoveryStrategies.map(async (strategy) => {
      try {
        console.log(`🔄 Trying ${strategy.name} strategy...`)
        
        const result = await Promise.race([
          strategy.handler(),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Timeout')), strategy.timeout)
          )
        ])
        
        if (result && result.success) {
          console.log(`✅ ${strategy.name} strategy succeeded`)
          return { ...result, strategy: strategy.name, priority: strategy.priority }
        }
        
        console.log(`❌ ${strategy.name} strategy failed:`, result?.error || 'Unknown error')
        return { success: false, strategy: strategy.name, error: result?.error || 'Failed' }
        
      } catch (error) {
        console.log(`⏰ ${strategy.name} strategy timeout or error:`, error.message)
        return { success: false, strategy: strategy.name, error: error.message }
      }
    })

    const results = await Promise.allSettled(promises)
    
    // Find first successful result by priority
    const successful = results
      .filter(r => r.status === 'fulfilled' && r.value.success)
      .map(r => r.value)
      .sort((a, b) => a.priority - b.priority)

    if (successful.length > 0) {
      const winner = successful[0]
      console.log(`🎉 Token recovery successful using ${winner.strategy}`)
      
      // Store recovered tokens
      if (winner.tokens) {
        await this.storeTokens(winner.tokens)
      }
      
      return winner.tokens
    }

    console.log('💥 All token recovery strategies failed')
    return null
  }

  /**
   * Strategy 1: Refresh token
   */
  async refreshTokenStrategy(oldTokens) {
    try {
      if (!oldTokens?.refresh) {
        return { success: false, error: 'No refresh token available' }
      }

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          refresh: oldTokens.refresh
        })
      })

      if (response.ok) {
        const data = await response.json()
        return {
          success: true,
          tokens: {
            access: data.access,
            refresh: data.refresh || oldTokens.refresh
          }
        }
      }

      return { success: false, error: `HTTP ${response.status}` }
      
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Strategy 2: Device auto-auth
   */
  async deviceAutoAuthStrategy(oldTokens) {
    try {
      const deviceMac = await this.getDeviceMac()
      const deviceIP = await this.getDeviceIP()
      
      const payload = {
        current_mac: deviceMac,
        current_ip: deviceIP,
        location_id: 1,
        device_info: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language,
          seamless_reauth: true,
          stored_user_data: oldTokens?.user_data,
          timestamp: new Date().toISOString()
        }
      }

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/users/auth/device-auto/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.auth) {
          return {
            success: true,
            tokens: data.auth,
            user_data: {
              user: data.user,
              client: data.client,
              device: data.device
            }
          }
        }
      }

      return { success: false, error: 'Device auto-auth failed' }
      
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Strategy 3: Enhanced device auth with multiple fallbacks
   */
  async enhancedDeviceAuthStrategy(oldTokens) {
    try {
      const deviceMac = await this.getDeviceMac()
      const deviceIP = await this.getDeviceIP()
      
      const payload = {
        current_mac: deviceMac,
        current_ip: deviceIP,
        location_id: 1,
        device_info: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language,
          seamless_reauth: true,
          stored_user_data: oldTokens?.user_data,
          timestamp: new Date().toISOString()
        }
      }

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/enhanced-device/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.auth) {
          return {
            success: true,
            tokens: data.auth,
            user_data: {
              user: data.user,
              client: data.client,
              device: data.device
            }
          }
        }
      }

      return { success: false, error: 'Enhanced device auth failed' }
      
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Strategy 4: Session recovery
   */
  async sessionRecoveryStrategy(oldTokens) {
    try {
      // This would attempt to recover from session backup
      // Implementation depends on backend session backup system
      return { success: false, error: 'Session recovery not implemented' }
      
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * Get stored tokens from storage
   */
  getStoredTokens() {
    try {
      const stored = storage.get('auth_tokens')
      if (stored) return stored

      // Fallback to session storage
      const backup = sessionStorage.getItem('auth_tokens_backup')
      if (backup) {
        return JSON.parse(backup)
      }

      return null
    } catch (error) {
      console.error('Error getting stored tokens:', error)
      return null
    }
  }

  /**
   * Get backend version for restart detection
   */
  async getBackendVersion() {
    try {
      if (this.backendVersion) return this.backendVersion

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/status/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        this.backendVersion = data.backend_version || 'unknown'
        this.tokenVersion = data.jwt_version || 'v1'
        return this.backendVersion
      }

      return 'unknown'
    } catch (error) {
      console.warn('Could not get backend version:', error)
      return 'unknown'
    }
  }

  /**
   * Generate device fingerprint
   */
  async getDeviceFingerprint() {
    try {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      ctx.textBaseline = 'top'
      ctx.font = '14px Arial'
      ctx.fillText('Device fingerprint', 2, 2)
      
      const fingerprint = [
        navigator.userAgent,
        navigator.language,
        screen.width + 'x' + screen.height,
        new Date().getTimezoneOffset(),
        canvas.toDataURL()
      ].join('|')
      
      // Simple hash
      let hash = 0
      for (let i = 0; i < fingerprint.length; i++) {
        const char = fingerprint.charCodeAt(i)
        hash = ((hash << 5) - hash) + char
        hash = hash & hash // Convert to 32-bit integer
      }
      
      return Math.abs(hash).toString(16)
    } catch (error) {
      return 'unknown'
    }
  }

  /**
   * Get device MAC address (fallback generation)
   */
  async getDeviceMac() {
    // In browser, we can't get real MAC, so generate consistent fallback
    const stored = localStorage.getItem('device_mac_fallback')
    if (stored) return stored

    const fingerprint = await this.getDeviceFingerprint()
    const bytes = []
    for (let i = 0; i < 6; i++) {
      const byte = parseInt(fingerprint.substr(i * 2, 2), 16) || Math.floor(Math.random() * 256)
      bytes.push(byte.toString(16).padStart(2, '0'))
    }
    
    // Ensure it's a locally administered MAC
    bytes[0] = (parseInt(bytes[0], 16) | 0x02).toString(16).padStart(2, '0')
    
    const mac = bytes.join(':')
    localStorage.setItem('device_mac_fallback', mac)
    return mac
  }

  /**
   * Get device IP address (fallback generation)
   */
  async getDeviceIP() {
    // Generate consistent private IP fallback
    const stored = localStorage.getItem('device_ip_fallback')
    if (stored) return stored

    const ranges = [
      { base: '10.0', range: 255 },
      { base: '172.16', range: 15 },
      { base: '192.168', range: 255 }
    ]
    
    const fingerprint = await this.getDeviceFingerprint()
    const rangeIndex = parseInt(fingerprint.substr(0, 1), 16) % ranges.length
    const selectedRange = ranges[rangeIndex]
    
    const subnet = parseInt(fingerprint.substr(1, 2), 16) % selectedRange.range
    const host = (parseInt(fingerprint.substr(3, 2), 16) % 254) + 1
    
    const ip = `${selectedRange.base}.${subnet}.${host}`
    localStorage.setItem('device_ip_fallback', ip)
    return ip
  }

  /**
   * Clear all stored tokens and metadata
   */
  clearTokens() {
    storage.remove('auth_tokens')
    sessionStorage.removeItem('auth_tokens_backup')
    localStorage.removeItem('device_mac_fallback')
    localStorage.removeItem('device_ip_fallback')
    this.backendVersion = null
    this.tokenVersion = null
  }
}

// Export singleton instance
export const smartTokenManager = new SmartTokenManager()