// composables/useBuyOffer.js
import { ref,getCurrentInstance } from 'vue'
import axios from 'axios'
import { useAccountStore } from '@/stores/useAccountStore'
import { useCsrfTokenStore } from '@/stores/useCsrf'
import { useOfferStore } from '@/stores/useOfferStore'
import { useVoucherStore } from '@/stores/useVoucherStore'
import { toast } from 'vue3-toastify'


export function useBuyOffer() {
  const loading = ref(false)
  const error = ref(null)
  const isloading = ref(false) 
  const { proxy } = getCurrentInstance()
  const hotspotIP = proxy.$hotspot.ip

  const csrfStore = useCsrfTokenStore()
  const accountStore = useAccountStore()
  const offerStore = useOfferStore()
  const voucherStore = useVoucherStore()

  const buyOffer = async (offer, onSuccessModal) => {
    isloading.value = true
    loading.value = true
    error.value = null

    try {
      await csrfStore.fetchCsrf()
      const account = localStorage.getItem('account') || sessionStorage.getItem('account')
      const ping = localStorage.getItem('ping') || sessionStorage.getItem('ping')

      const payload = {
        client_id: account,
        pass_id: offer.id,
        ping: ping,
        hotspotIP: hotspotIP,

      }

      const response = await axios.post(`${import.meta.env.VITE_API_PROD_URL}/api/purchase/`, payload, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfStore.csrfToken,
          Authorization: `Token ${localStorage.getItem('authToken')}`
        }
      })

      if (response.status === 200) {
        isloading.value = false
        await accountStore.fetchAccountInfo()
        await voucherStore.fetchActiveVouchers()
        toast.success('Offer purchased successfully!')
        
      } else if (response.status === 201) {
        isloading.value = false 
        offer.price = response.data.new_price
        offer.usedbalance = response.data.used_balance
        
        if (onSuccessModal) onSuccessModal(offer) // onSuccessModal is the openBuycomponent argument callback
      } else {
        throw new Error('Unexpected response status')
      }
    } catch (err) {
      console.error('Offer purchase error:', err)
      error.value = err.response?.data?.message || err.message || 'Failed to process offer purchase'
      toast.error(error.value)
    } finally {
      loading.value = false
    }
  }

  return {
    buyOffer,
    loading,
    error
  }
}