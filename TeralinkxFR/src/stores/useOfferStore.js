import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useOfferStore = defineStore('offerStore', () => {
  const offers = ref([])
  const loading = ref(true)
  const error = ref(null)
  

  const fetchOffers = () => {
    loading.value = true
    fetch(`${import.meta.env.VITE_API_PROD_URL}/api/dailypass/`, {
      headers: {
        'Authorization': `Token ${localStorage.getItem('authToken')}`,
      },
    })
    .then((res) => {
      if (!res.ok) throw new Error('Failed to fetch daily passes')
      return res.json()
    })
    .then((data) => {
      offers.value = data.sort((a, b) => a.price - b.price)
      console.log(offers)
       

      loading.value = false
    })
    .catch((err) => {
      error.value = err.message || 'Failed to fetch offers'
      loading.value = false
    })
  }

  return {
    offers,
   
    loading,
    error,
    fetchOffers
  }
})
