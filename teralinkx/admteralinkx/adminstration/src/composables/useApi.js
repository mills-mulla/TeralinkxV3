import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_SUAPI_HTTPS_URL || 'https://service.teralinkxwaves.uk'

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  withCredentials: true,
})

// Cache for GET requests
const cache = new Map()
const CACHE_DURATION = 60000 // 1 minute

http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const makeRequest = async (method, url, data = null, useCache = true) => {
    const cacheKey = `${method}:${url}:${JSON.stringify(data)}`
    
    // Check cache for GET requests
    if (method === 'get' && useCache) {
      const cached = cache.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return cached.data
      }
    }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await http({ method, url, data })
      
      // Cache GET responses
      if (method === 'get' && useCache) {
        cache.set(cacheKey, { data: response.data, timestamp: Date.now() })
        
        // Clean old cache entries
        if (cache.size > 100) {
          const firstKey = cache.keys().next().value
          cache.delete(firstKey)
        }
      }
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || err.response?.data?.message || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearCache = () => cache.clear()

  return { loading, error, makeRequest, clearCache }
}