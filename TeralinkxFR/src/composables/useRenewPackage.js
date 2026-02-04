import { ref } from 'vue'
import axios from 'axios'

export function useRenewPackage() {
  const loadingId = ref(null)
  const errorMessage = ref(null)
  const showRenewComponent = ref(false)
  const selectedVoucher = ref(null)
  const isLoading = ref(false)

  const renew = async (voucher, pingUserId) => {
    loadingId.value = voucher.dispatch_voucher_code
    isLoading.value = true
    errorMessage.value = null

    try {
        const response = await axios.post('/api/renew/', {
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${localStorage.getItem('authToken')}`
        },
        voucher_code: voucher.dispatch_voucher_code,
        ping: pingUserId,
      })

      // show confirmation modal
      selectedVoucher.value = voucher
      showRenewComponent.value = true
    } catch (err) {
      if (err.code === 'ECONNABORTED') {
        errorMessage.value = 'Request timeout. Please try again.'
      } else if (err.code === 'ERR_NETWORK') {
        errorMessage.value = 'Network error. Check your connection.'
      } else if (err.response?.status === 401) {
        errorMessage.value = 'Authentication failed. Please login again.'
      } else if (err.response?.status >= 500) {
        errorMessage.value = 'Server error. Please try again later.'
      } else {
        errorMessage.value = err.response?.data?.error || 'Renew failed'
      }
    } finally {
      isLoading.value = false
      loadingId.value = null
    }
  }

  return {
    renew,
    loadingId,
    errorMessage,
    showRenewComponent,
    selectedVoucher,
    isLoading,
  }
}
