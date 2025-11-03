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
        window.location = 'https://login.teralinkxwaves.uk/index.html#/connected'

      } else if (response.status === 201) {
        isloading.value = false
        const { new_price, used_balance } = response.data
        pkg.price = new_price
        pkg.usedbalance = used_balance
        selectedPackage.value = pkg
        showBuyComponent.value = true
      } else {
        throw new Error('Unexpected server response')
      }
    } catch (error) {
      errorMessage.value = error?.response?.data?.message || error.message || 'Purchase failed'
      toast.error(errorMessage.value)
    } finally {
      loadingId.value = null
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
