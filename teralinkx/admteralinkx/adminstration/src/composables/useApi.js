// src/composables/useApi.js
import { ref } from 'vue';
import axios from 'axios';

// Get the API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_SUAPI_HTTPS_URL || 'https://service.teralinkxwaves.uk';

// Create axios instance
const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
  withCredentials: true, // Important for Django sessions
});

// Request interceptor
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // For Django CSRF protection
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Helper function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export function useApi() {
  const loading = ref(false);
  const error = ref(null);

  const makeRequest = async (method, url, data = null) => {
    loading.value = true;
    error.value = null;
    
    try {
      console.log(`Making ${method.toUpperCase()} request to: ${API_BASE_URL}/${url}`);
      
      const response = await http({
        method,
        url,
        data
      });
      
      console.log('API Response:', response.data);
      return response.data;
    } catch (err) {
      console.error('API Error:', err);
      error.value = err.response?.data?.error || err.response?.data?.message || err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    error,
    makeRequest
  };
}
