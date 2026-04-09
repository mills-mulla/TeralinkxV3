import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

export function useProfileApi() {
  const authStore = useAuthStore()

  const updateProfile = async (data) => {
    const response = await api.patch('/api/profile/update/', data)
    return response.data
  }

  const updateProfileImage = async (file) => {
    const formData = new FormData()
    formData.append('profile_image', file)

    const response = await api.post('/api/profile/image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  const getDevices = async () => {
    const response = await api.get('/api/devices/')
    return response.data
  }

  const updateDevice = async (deviceId, data) => {
    const response = await api.patch(`/api/devices/${deviceId}/update/`, data)
    return response.data
  }

  const blockDevice = async (deviceId) => {
    const response = await api.post(`/api/devices/${deviceId}/block/`)
    return response.data
  }

  const unblockDevice = async (deviceId) => {
    const response = await api.post(`/api/devices/${deviceId}/unblock/`)
    return response.data
  }

  const trustDevice = async (deviceId, trusted) => {
    const response = await api.post(`/api/devices/${deviceId}/trust/`, {
      is_trusted: trusted
    })
    return response.data
  }

  const removeDevice = async (deviceId) => {
    const response = await api.delete(`/api/devices/${deviceId}/remove/`)
    return response.data
  }

  const getAccountStats = async () => {
    const response = await api.get('/api/profile/stats/')
    return response.data
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