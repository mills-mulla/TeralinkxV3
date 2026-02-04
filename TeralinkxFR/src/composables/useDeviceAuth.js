// composables/useDeviceAuth.js
import { useAuthStore } from '@/stores/auth'
import { useHotspot } from '@/plugins/hotspot'

export const useDeviceAuth = () => {
  const authStore = useAuthStore()
  const hotspot = useHotspot()

  // Generate fallback network data
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

  // Fast device auto-auth
  const attemptDeviceAuth = async () => {
    try {
      
      const payload = {
        current_mac: hotspot.mac || generateFallbackMac(),
        current_ip: hotspot.ip || generateFallbackIP(),
        location_id: 1,
        device_info: {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          language: navigator.language,
          manual_trigger: true,
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
      
      const data = await response.json()
      
      if (response.ok && data.success && data.auth) {
        // Update auth store with new tokens
        authStore.token = data.auth.access
        authStore.refreshToken = data.auth.refresh
        authStore.user = {
          id: data.user.id,
          username: data.user.username,
          email: data.user.email,
          phone: data.client.phone_number,
          client: data.client,
          device: data.device,
          session: data.session
        }
        
        // Persist to storage
        localStorage.setItem('auth_token', data.auth.access)
        localStorage.setItem('refresh_token', data.auth.refresh)
        localStorage.setItem('user', JSON.stringify(authStore.user))
        localStorage.setItem('last_activity', Date.now())
        
        return { success: true, message: data.message }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  return {
    attemptDeviceAuth
  }
}