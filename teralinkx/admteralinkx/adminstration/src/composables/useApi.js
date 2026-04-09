import { ref } from 'vue'
import axios from 'axios'

const PRIMARY_URL  = import.meta.env.VITE_SUAPI_PRIMARY_URL  || 'https://srv.teralinkxwaves.uk'
const FALLBACK_URL = import.meta.env.VITE_SUAPI_FALLBACK_URL || 'https://accounts.teralinkxwaves.uk'

// Track which base URL is currently active
let activeBaseURL = PRIMARY_URL
let primaryFailed = false

function createHttp(baseURL) {
  return axios.create({
    baseURL,
    timeout: 15000,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
    withCredentials: true,
  })
}

const http = createHttp(PRIMARY_URL)

// Test primary server on startup and switch to fallback if needed
const testPrimaryServer = async () => {
  try {
    await axios.get(`${PRIMARY_URL}/api/health/`, { timeout: 2000 })
    console.log('[API] Primary server is reachable:', PRIMARY_URL)
  } catch (error) {
    console.warn('[API] Primary server unreachable on startup, switching to fallback:', FALLBACK_URL)
    primaryFailed = true
    activeBaseURL = FALLBACK_URL
    http.defaults.baseURL = FALLBACK_URL
  }
}

// Run test on module load
testPrimaryServer()

// Request interceptor — inject auth token
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    const csrf = getCookie('csrftoken')
    if (csrf) config.headers['X-CSRFToken'] = csrf
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — handle 401 and fallback
http.interceptors.response.use(
  (response) => {
    // Primary responded — reset fallback flag
    if (primaryFailed) {
      primaryFailed = false
      activeBaseURL = PRIMARY_URL
      http.defaults.baseURL = PRIMARY_URL
      console.log('[API] Primary server restored:', PRIMARY_URL)
    }
    return response
  },
  async (error) => {
    // Network error or 5xx on primary — try fallback FIRST
    const isNetworkError = !error.response
    const isServerError  = error.response?.status >= 500
    const alreadyFallback = error.config?.baseURL === FALLBACK_URL

    if ((isNetworkError || isServerError) && !alreadyFallback && !primaryFailed) {
      console.warn(`[API] Primary ${PRIMARY_URL} unreachable, falling back to ${FALLBACK_URL}`)
      primaryFailed = true
      activeBaseURL = FALLBACK_URL
      http.defaults.baseURL = FALLBACK_URL

      // Retry the failed request on fallback
      const retryConfig = { ...error.config, baseURL: FALLBACK_URL }
      return axios(retryConfig)
    }

    // Handle 401 after fallback attempt
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/su/login'
      return Promise.reject(error)
    }

    return Promise.reject(error)
  }
)

// Cache for GET requests
const cache = new Map()
const CACHE_DURATION = 60000

function getCookie(name) {
  if (!document.cookie) return null
  const match = document.cookie.split(';')
    .map(c => c.trim())
    .find(c => c.startsWith(name + '='))
  return match ? decodeURIComponent(match.split('=')[1]) : null
}

export function useApi() {
  const loading = ref(false)
  const error   = ref(null)

  const makeRequest = async (method, url, data = null, useCache = true) => {
    const cacheKey = `${method}:${url}:${JSON.stringify(data)}`

    if (method === 'get' && useCache) {
      const cached = cache.get(cacheKey)
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return cached.data
      }
    }

    loading.value = true
    error.value   = null

    try {
      const response = await http({ method, url, data })

      if (method === 'get' && useCache) {
        cache.set(cacheKey, { data: response.data, timestamp: Date.now() })
        if (cache.size > 100) cache.delete(cache.keys().next().value)
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

  // Expose active URL for debugging
  const getActiveURL = () => activeBaseURL

  return { loading, error, makeRequest, clearCache, getActiveURL }
}

// Named export for components that use fetch() directly
export const API_BASE_URL = PRIMARY_URL
export const API_FALLBACK_URL = FALLBACK_URL

export async function fetchWithFallback(path, options = {}) {
  const token = localStorage.getItem('access_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  }
  try {
    const res = await fetch(`${PRIMARY_URL}/${path}`, { ...options, headers })
    if (res.ok || res.status < 500) return res
    throw new Error(`Primary returned ${res.status}`)
  } catch {
    console.warn(`[API] Falling back to ${FALLBACK_URL}`)
    return fetch(`${FALLBACK_URL}/${path}`, { ...options, headers })
  }
}
