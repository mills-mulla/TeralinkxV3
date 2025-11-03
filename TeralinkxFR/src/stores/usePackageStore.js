// src/stores/usePackageStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePackageStore = defineStore('packageStore', () => {
  const packages = ref([])
  const loading = ref(true)
  const error = ref(null)

  const fetchPackages = async () => {
    loading.value = true
    try {
      const res = await fetch(`${import.meta.env.VITE_API_PROD_URL}/api/packages/`, {
        headers: {
          Authorization: `Token ${localStorage.getItem('authToken')}`,
        },
      })
      if (!res.ok) throw new Error('Failed to fetch packages')
      const data = await res.json()
      
      packages.value = data.sort((a, b) => a.price - b.price)
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  return { packages, loading, error, fetchPackages }
})
