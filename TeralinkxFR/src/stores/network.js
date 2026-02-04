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
    // Try multiple fallback methods
    try {
      // Method 1: Check local storage for previous IP
      const savedIP = localStorage.getItem('last_known_ip')
      if (savedIP && savedIP.startsWith('192.168.')) {
        return savedIP
      }

      // Method 2: Common local IP ranges
      const commonIPs = [
        '192.168.1.100',
        '192.168.0.100',
        '10.0.0.100',
        '172.16.0.100'
      ]

      // Try to ping each IP to see which one responds
      return commonIPs[0] // For now, return first common IP
    } catch (error) {
      return '192.168.1.100' // Ultimate fallback
    }
  }

  // Improved WebRTC IP detection with multiple fallbacks
  const getLocalIP = () => {
    return new Promise((resolve, reject) => {
      // Skip WebRTC if not in secure context (HTTPS/localhost)
      const isLocalhost = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1'
      const isSecure = window.location.protocol === 'https:' || isLocalhost
      
      if (!isSecure) {
        console.warn('WebRTC requires HTTPS. Using fallback IP.')
        resolve(getFallbackIP())
        return
      }

      try {
        const pc = new RTCPeerConnection({ 
          iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
          ] 
        })

        pc.createDataChannel('')
        
        pc.onicecandidate = (event) => {
          if (!event.candidate) {
            // ICE gathering complete
            setTimeout(() => {
              if (!ip.value) {
                // No IP found via WebRTC, use fallback
                pc.close()
                const fallbackIP = getFallbackIP()
                localStorage.setItem('last_known_ip', fallbackIP)
                resolve(fallbackIP)
              }
            }, 500)
            return
          }

          const candidate = event.candidate.candidate
          if (candidate) {
            // Match IPv4 addresses in local ranges
            const regex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/
            const match = candidate.match(regex)
            
            if (match) {
              const foundIP = match[1]
              // Filter for local/private IPs
              if (foundIP.startsWith('192.168.') || 
                  foundIP.startsWith('10.') || 
                  foundIP.startsWith('172.16.') ||
                  foundIP.startsWith('172.17.') ||
                  foundIP.startsWith('172.18.') ||
                  foundIP.startsWith('172.19.') ||
                  foundIP.startsWith('172.20.') ||
                  foundIP.startsWith('172.21.') ||
                  foundIP.startsWith('172.22.') ||
                  foundIP.startsWith('172.23.') ||
                  foundIP.startsWith('172.24.') ||
                  foundIP.startsWith('172.25.') ||
                  foundIP.startsWith('172.26.') ||
                  foundIP.startsWith('172.27.') ||
                  foundIP.startsWith('172.28.') ||
                  foundIP.startsWith('172.29.') ||
                  foundIP.startsWith('172.30.') ||
                  foundIP.startsWith('172.31.') ||
                  foundIP === '127.0.0.1') {
                
                pc.onicecandidate = null
                pc.close()
                localStorage.setItem('last_known_ip', foundIP)
                resolve(foundIP)
              }
            }
          }
        }

        pc.createOffer()
          .then(offer => {
            return pc.setLocalDescription(offer)
          })
          .catch(error => {
            console.warn('WebRTC offer error:', error)
            pc.close()
            resolve(getFallbackIP())
          })

        // Timeout after 2 seconds (reduced from 3)
        setTimeout(() => {
          if (pc.iceConnectionState !== 'closed') {
            pc.onicecandidate = null
            pc.close()
            const fallbackIP = getFallbackIP()
            localStorage.setItem('last_known_ip', fallbackIP)
            resolve(fallbackIP)
          }
        }, 2000)

      } catch (error) {
        console.error('WebRTC setup failed:', error)
        resolve(getFallbackIP())
      }
    })
  }

  // Actions
  const detectNetwork = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      // Try Mikrotik hotspot first
      if (window.$hotspot) {
        ip.value = window.$hotspot.ip || ''
        mac.value = window.$hotspot.mac || ''
        hasHotspotData.value = !!(window.$hotspot.ip && window.$hotspot.mac)
        source.value = 'mikrotik_hotspot'
        
        if (hasHotspotData.value) {
          console.log('✅ Mikrotik hotspot data detected')
          isLoading.value = false
          return true
        }
      }

      // Try direct URL parameters (common in captive portals)
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

      // Fallback to WebRTC with improved error handling
      const webRTCIP = await getLocalIP()
      ip.value = webRTCIP
      mac.value = generatePlaceholderMac()
      source.value = 'webrtc_fallback'
      hasHotspotData.value = false
      
      console.log(`📶 Network detected via ${source.value}: ${ip.value}, ${mac.value}`)
      
      isLoading.value = false
      return true
      
    } catch (error) {
      console.error('Network detection failed:', error)
      error.value = error.message
      source.value = 'detection_failed'
      
      // Set fallback values so app can continue
      ip.value = getFallbackIP()
      mac.value = generatePlaceholderMac()
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

  const simulateData = () => {
    const randomIP = `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255) + 1}`
    ip.value = randomIP
    mac.value = generateRandomMac()
    hasHotspotData.value = true
    source.value = 'simulated'
    error.value = null
  }

  const initialize = async () => {
    // Don't reinitialize if already has data
    if (ip.value && mac.value) {
      return
    }
    
    await detectNetwork()
    
    // Test backend connection in background (non-blocking)
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
    // State
    ip,
    mac,
    source,
    hasHotspotData,
    connectionTested,
    lastTest,
    isLoading,
    error,
    
    // Getters
    isConnected,
    connectionStatus,
    
    // Actions
    detectNetwork,
    testConnection,
    simulateData,
    initialize,
    reset
  }
})