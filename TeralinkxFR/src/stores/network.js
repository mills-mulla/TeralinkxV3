// stores/network.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../services/api'

export const useNetworkStore = defineStore('network', () => {
  // State
  const ip = ref('')
  const mac = ref('')
  const source = ref('unknown')
  const hasHotspotData = ref(false)
  const connectionTested = ref(false)
  const lastTest = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const isConnected = computed(() => !!ip.value && !!mac.value)
  const connectionStatus = computed(() => {
    if (!ip.value) return 'disconnected'
    if (!mac.value) return 'connecting'
    return 'connected'
  })

  // Helper functions
  const generatePlaceholderMac = () => {
    const sessionKey = sessionStorage.getItem('network_session_key') || 
                      Math.random().toString(36).substring(2, 11)
    sessionStorage.setItem('network_session_key', sessionKey)
    
    const hash = simpleHash(sessionKey)
    return `02:00:00:${hash.slice(0,2)}:${hash.slice(2,4)}:${hash.slice(4,6)}`.toUpperCase()
  }

  const simpleHash = (str) => {
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i)
      hash = hash & hash
    }
    return Math.abs(hash).toString(16).padStart(6, '0')
  }

  const generateRandomMac = () => {
    const hex = '0123456789ABCDEF'
    let mac = '02:00:00:'
    for (let i = 0; i < 6; i++) {
      mac += hex[Math.floor(Math.random() * 16)]
      if (i % 2 && i < 5) mac += ':'
    }
    return mac
  }

  const getFallbackIP = () => {
    try {
      const savedIP = localStorage.getItem('last_known_ip')
      if (savedIP && savedIP.startsWith('192.168.')) {
        return savedIP
      }
      return '192.168.1.100'
    } catch (error) {
      return '192.168.1.100'
    }
  }

  // Improved WebRTC IP detection with proper cleanup
  const getLocalIP = () => {
    return new Promise((resolve) => {
      const isLocalhost = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1'
      const isSecure = window.location.protocol === 'https:' || isLocalhost
      
      if (!isSecure) {
        resolve(getFallbackIP())
        return
      }

      let pc = null
      let timeoutId = null
      let resolved = false

      const cleanup = () => {
        if (timeoutId) {
          clearTimeout(timeoutId)
          timeoutId = null
        }
        if (pc) {
          pc.onicecandidate = null
          pc.close()
          pc = null
        }
      }

      const resolveOnce = (value) => {
        if (!resolved) {
          resolved = true
          cleanup()
          resolve(value)
        }
      }

      try {
        pc = new RTCPeerConnection({ 
          iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] 
        })

        pc.createDataChannel('')
        
        pc.onicecandidate = (event) => {
          if (!event.candidate) {
            setTimeout(() => {
              if (!resolved) {
                const fallbackIP = getFallbackIP()
                localStorage.setItem('last_known_ip', fallbackIP)
                resolveOnce(fallbackIP)
              }
            }, 500)
            return
          }

          const candidate = event.candidate.candidate
          if (candidate) {
            const regex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/
            const match = candidate.match(regex)
            
            if (match) {
              const foundIP = match[1]
              if (foundIP.startsWith('192.168.') || 
                  foundIP.startsWith('10.') || 
                  (foundIP.startsWith('172.') && 
                   parseInt(foundIP.split('.')[1]) >= 16 && 
                   parseInt(foundIP.split('.')[1]) <= 31)) {
                
                localStorage.setItem('last_known_ip', foundIP)
                resolveOnce(foundIP)
              }
            }
          }
        }

        pc.createOffer()
          .then(offer => pc.setLocalDescription(offer))
          .catch(() => resolveOnce(getFallbackIP()))

        timeoutId = setTimeout(() => {
          const fallbackIP = getFallbackIP()
          localStorage.setItem('last_known_ip', fallbackIP)
          resolveOnce(fallbackIP)
        }, 2000)

      } catch (error) {
        cleanup()
        resolve(getFallbackIP())
      }
    })
  }

  // Actions
  const detectNetwork = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      // Priority 1: URL parameters
      const urlParams = new URLSearchParams(window.location.search)
      const paramIP = urlParams.get('ip') || urlParams.get('client_ip')
      const paramMAC = urlParams.get('mac') || urlParams.get('client_mac')
      
      if (paramIP && paramMAC) {
        ip.value = paramIP
        mac.value = paramMAC.toUpperCase()
        source.value = 'url_parameters'
        hasHotspotData.value = true
        isLoading.value = false
        return true
      }

      // Priority 2: window.$hotspot (from hotspot plugin)
      if (window.$hotspot) {
        ip.value = window.$hotspot.ip || ''
        mac.value = window.$hotspot.mac || ''
        hasHotspotData.value = !!(window.$hotspot.ip && window.$hotspot.mac)
        source.value = 'mikrotik_hotspot'
        
        if (hasHotspotData.value) {
          isLoading.value = false
          return true
        }
      }

      // No valid hotspot data found
      error.value = 'No hotspot connection detected'
      source.value = 'detection_failed'
      hasHotspotData.value = false
      
      isLoading.value = false
      return false
      
    } catch (error) {
      error.value = error.message
      source.value = 'detection_failed'
      hasHotspotData.value = false
      
      isLoading.value = false
      return false
    }
  }

  const testConnection = async () => {
    try {
      const response = await api.get('/api/network-info/', { timeout: 5000 })
      connectionTested.value = true
      lastTest.value = new Date()
      return response.data
    } catch (error) {
      connectionTested.value = false
      throw error
    }
  }

  const initialize = async () => {
    if (ip.value && mac.value) {
      return
    }
    
    await detectNetwork()
    
    setTimeout(() => {
      testConnection().catch(() => {
        console.log('Backend test failed - running in offline mode')
      })
    }, 1000)
  }

  const reset = () => {
    ip.value = ''
    mac.value = ''
    source.value = 'unknown'
    hasHotspotData.value = false
    connectionTested.value = false
    lastTest.value = null
    isLoading.value = false
    error.value = null
  }

  return {
    ip, mac, source, hasHotspotData, connectionTested, lastTest, isLoading, error,
    isConnected, connectionStatus,
    detectNetwork, testConnection, initialize, reset
  }
})