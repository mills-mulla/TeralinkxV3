import { ref , getCurrentInstance} from 'vue'
import axios from 'axios'
import { useCsrfTokenStore } from '@/stores/useCsrf'
import { usePackageStore } from '@/stores/usePackageStore'
import { useAccountStore } from '@/stores/useAccountStore'
import { toast} from 'vue3-toastify'
import { useVoucherStore } from '@/stores/useVoucherStore'

export function useBuyPackage() {
  const loadingId = ref(null) // ID of package being processed
  const errorMessage = ref(null)
  const showBuyComponent = ref(false)
  const selectedPackage = ref(null)
  const isloading = ref(false) // Loading state for the package card
  const { proxy } = getCurrentInstance()
  const hotspotIP = proxy.$hotspot.ip

  const csrfStore = useCsrfTokenStore()
  const voucherStore = useVoucherStore()
  const accountStore = useAccountStore()


  async function buy(pkg) {
    loadingId.value = pkg.id
    errorMessage.value = null
    try {
      await csrfStore.fetchCsrf()
      const account = localStorage.getItem('account') || sessionStorage.getItem('account')
      const ping = localStorage.getItem('ping') || sessionStorage.getItem('ping')
      isloading.value = true 

      const payload = {
        client_id: account,
        package_id: pkg.id,
        ping,
        hotspot_ip: hotspotIP,
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
        toast.success('Package successfully purchased!')
        window.location = 'https://login.teralinkxwaves.uk/htm.html#/connected'

      } else if (response.status === 201) {
        isloading.value = false
        const { new_price, used_credit } = response.data
        pkg.price = new_price
        pkg.usedbalance = used_credit
        selectedPackage.value = pkg
        showBuyComponent.value = true
      } else {
        throw new Error('Unexpected server response')
      }
    } catch (error) {
      if (error.code === 'ECONNABORTED') {
        errorMessage.value = 'Request timeout. Please try again.'
      } else if (error.code === 'ERR_NETWORK') {
        errorMessage.value = 'Network error. Check your connection.'
      } else if (error.response?.status === 401) {
        errorMessage.value = 'Authentication failed. Please login again.'
      } else if (error.response?.status === 402) {
        errorMessage.value = 'Insufficient balance for this package.'
      } else if (error.response?.status === 404) {
        errorMessage.value = 'Package not found or no longer available.'
      } else if (error.response?.status >= 500) {
        errorMessage.value = 'Server error. Please try again later.'
      } else {
        errorMessage.value = error?.response?.data?.message || error.message || 'Purchase failed'
      }
      toast.error(errorMessage.value)
    } finally {
      loadingId.value = null
      isloading.value = false
    }
  }

  return {
    buy,
    loadingId,
    errorMessage,
    showBuyComponent,
    selectedPackage,
  }
}
