// src/stores/usePackageStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../services/api'

export const usePackageStore = defineStore('packageStore', () => {
  const packages = ref([])
  const loading = ref(true)
  const error = ref(null)

  const fetchPackages = async () => {
    loading.value = true
    try {
      const response = await api.get('/api/packages/')
      packages.value = response.data.sort((a, b) => a.price - b.price)
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  return { packages, loading, error, fetchPackages }
})
