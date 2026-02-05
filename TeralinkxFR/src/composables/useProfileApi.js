import { useAuthStore } from '@/stores/auth'

export function useProfileApi() {
  const authStore = useAuthStore()

  const apiRequest = async (url, options = {}) => {
    // Validate URL to prevent SSRF attacks
    if (!url.startsWith('/api/')) {
      throw new Error('Invalid API endpoint')
    }
    
    const response = await fetch(url, {
      headers: {
        ...authStore.authHeaders,
        ...options.headers
      },
      ...options
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`)
    }

    return response.json()
  }

  const updateProfile = async (data) => {
    return apiRequest(`${import.meta.env.VITE_API_BASE_URL}/api/profile/update/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
  }

  const updateProfileImage = async (file) => {
    const formData = new FormData()
    formData.append('profile_image', file)

    const headers = { ...authStore.authHeaders }
    delete headers['Content-Type'] // Let browser set multipart boundary

    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/profile/image/`, {
      method: 'POST',
      headers,
      body: formData
    })

    if (!response.ok) {
      throw new Error(`Image upload failed: ${response.status}`)
    }

    return response.json()
  }

  const getDevices = async () => {
    return apiRequest(`${import.meta.env.VITE_API_BASE_URL}/api/devices/`)
  }

  const updateDevice = async (deviceId, data) => {
    return apiRequest(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${deviceId}/update/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
  }

  const blockDevice = async (deviceId) => {
    return apiRequest(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${deviceId}/block/`, {
      method: 'POST'
    })
  }

  const unblockDevice = async (deviceId) => {
    return apiRequest(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${deviceId}/unblock/`, {
      method: 'POST'
    })
  }

  const trustDevice = async (deviceId, trusted) => {
    return apiRequest(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${deviceId}/trust/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ is_trusted: trusted })
    })
  }

  const removeDevice = async (deviceId) => {
    return apiRequest(`${import.meta.env.VITE_API_BASE_URL}/api/devices/${deviceId}/remove/`, {
      method: 'DELETE'
    })
  }

  const getAccountStats = async () => {
    return apiRequest(`${import.meta.env.VITE_API_BASE_URL}/api/profile/stats/`)
  }

  return {
    updateProfile,
    updateProfileImage,
    getDevices,
    updateDevice,
    blockDevice,
    unblockDevice,
    trustDevice,
    removeDevice,
    getAccountStats
  }
}