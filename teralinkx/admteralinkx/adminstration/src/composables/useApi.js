import { ref } from 'vue'
import axios from 'axios'

const PRIMARY_URL  = import.meta.env.VITE_SUAPI_PRIMARY_URL  || 'https://srv.teralinkxwaves.uk'
const FALLBACK_URL = import.meta.env.VITE_SUAPI_FALLBACK_URL || 'https://accounts.teralinkxwaves.uk'

// If browser is already on the fallback domain, use it directly — no switching needed
const IS_ON_FALLBACK = window.location.origin === FALLBACK_URL
let activeBaseURL = IS_ON_FALLBACK ? FALLBACK_URL : PRIMARY_URL
let primaryFailed = IS_ON_FALLBACK

const http = axios.create({
  baseURL: activeBaseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Inject JWT token on every request
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

// Only fallback on true network failure (server down), not on CORS/auth errors
http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const isNetworkError = !error.response && error.code === 'ERR_NETWORK'
    const alreadyFallback = IS_ON_FALLBACK || error.config?.baseURL === FALLBACK_URL

    if (isNetworkError && !alreadyFallback && !primaryFailed) {
      console.warn('[API] Primary unreachable, switching to fallback')
      primaryFailed = true
      activeBaseURL = FALLBACK_URL
      http.defaults.baseURL = FALLBACK_URL
      return axios({ ...error.config, baseURL: FALLBACK_URL })
    }

    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/su/login'
    }

    return Promise.reject(error)
  }
)

// Cache for GET requests
const cache = new Map()
const CACHE_DURATION = 60000

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const makeRequest = async (method, url, data = null, useCache = true) => {
    const cacheKey = `${method}:${url}:${JSON.stringify(data)}`

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
  const invalidateCache = (urlPrefix = null) => {
    if (!urlPrefix) { cache.clear(); return }
    for (const key of cache.keys()) {
      if (key.includes(urlPrefix)) cache.delete(key)
    }
  }
  const getActiveURL = () => activeBaseURL

  return { loading, error, makeRequest, clearCache, invalidateCache, getActiveURL }
}

export const API_BASE_URL = PRIMARY_URL
export const API_FALLBACK_URL = FALLBACK_URL

export async function fetchWithFallback(path, options = {}) {
  const token = localStorage.getItem('access_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  }
  const base = IS_ON_FALLBACK ? FALLBACK_URL : PRIMARY_URL
  try {
    const res = await fetch(`${base}/${path}`, { ...options, headers })
    if (res.ok || res.status < 500) return res
    throw new Error(`Server returned ${res.status}`)
  } catch {
    if (!IS_ON_FALLBACK) {
      return fetch(`${FALLBACK_URL}/${path}`, { ...options, headers })
    }
    throw new Error('Request failed')
  }
}
