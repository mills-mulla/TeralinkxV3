// services/api.js - CORRECTED VERSION
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

// Error handling helper
export const handleError = (error) => {
  if (error.response) {
    return error.response.data?.message || 'Server error'
  } else if (error.request) {
    return 'Network error. Please check your connection.'
  } else {
    return 'Request failed. Please try again.'
  }
}

// Export ONLY ONCE at the end
export { api }