// stores/useCsrf.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCsrfTokenStore = defineStore('csrfStore', () => {
  const csrfToken = ref('')
  const error = ref(null)

  const fetchCsrf = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_PROD_URL}/api/get-csrf-token/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem('authToken')}`,
        },
      })
      if (!res.ok) throw new Error('Failed to fetch CSRF token')

      const data = await res.json()
      csrfToken.value = data.csrf_token
    } catch (err) {
      error.value = err.message
    }
  }

  return {
    csrfToken,
    error,
    fetchCsrf,
  }
})
