import { ref } from 'vue'
import axios from 'axios'

export function useRenewPackage() {
  const loadingId = ref(null)
  const errorMessage = ref(null)
  const showRenewComponent = ref(false)
  const selectedVoucher = ref(null)
  const isloading = ref(false)

  const renew = async (voucher, pingUserId) => {
    loadingId.value = voucher.dispatch_voucher_code
    isloading.value = true
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
      errorMessage.value = err.response?.data?.error || 'Renew failed'
    } finally {
      isloading.value = false
    }
  }

  return {
    renew,
    loadingId,
    errorMessage,
    showRenewComponent,
    selectedVoucher,
    isloading,
  }
}
