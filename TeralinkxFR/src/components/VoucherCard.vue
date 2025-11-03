<template>
  <div class=" sm:max-w-md md:max-w-lg lg:max-w-xl w-full max-w-xs mx-auto space-y-3 mb-2  text-text-light dark:bg-gray-900 dark:text-text-dark">
    <!-- Loading Skeleton -->
    <div v-if="voucherStore.loading" class="space-y-3">
      <div v-for="n in 2" :key="n" class="bg-gray-200 dark:bg-gray-700 rounded-lg h-28 animate-pulse"></div>
    </div>

    <!-- No Vouchers Message -->
    <div
      v-else-if="voucherStore.vouchers.length === 0"
      class="text-center text-sm text-text-light dark:text-text-dark mt-4 shadow-lg rounded-lg p-4 bg-white dark:bg-gray-800"
    >
      <div class="flex justify-center items-center space-x-2">
        <svg
          class="w-5 h-5 text-gray-400 dark:text-gray-500"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span>You don't have an active voucher.</span>
      </div>
    </div>

    <!-- Active Vouchers -->
    <div
      v-else
      v-for="voucher in voucherStore.vouchers"
      :key="voucher.dispatch_voucher_code"
      :class="[
        'flex items-center justify-between bg-white dark:bg-card-dark shadow-md rounded-lg px-4 py-2 relative transition-all duration-300',
        voucher.is_expired
          ? 'border-2 border-red-500 dark:border-red-600 opacity-60'
          : 'border-2 border-green-500 dark:border-green-600 opacity-100'
      ]"
    >

      <div>
        <p class="font-semibold text-sm text-gray-800 dark:text-white flex items-center space-x-1">
          <svg class="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
          <span>{{ voucher.dispatch_voucher_code }}</span>
        </p>
        <p class="text-2xs text-gray-600 dark:text-gray-300">{{ voucher.dispatch_devices }} {{ voucher.dispatch_package }}</p>
        <p class="text-2xs text-gray-700 dark:text-gray-400">
          <span class="text-3xs text-blue-600">USAGE: </span>
          <span class="font-semibold " v-if="voucher.usage_limit !== null">
            {{ formatUsage(totalUsage(voucher)) }} of <span class="text-red-600"> {{ formatUsage(voucher.usage_limit) }} </span>
          </span>
          <span v-else>
            {{ formatUsage(totalUsage(voucher)) }} <span class="text-green-600">(Unlimited)</span>
          </span>
        </p>

        <p class="text-2xs text-gray-700 dark:text-gray-400">
          <span class="text-3xs text-red-600">EXPIRY:</span> {{ voucher.dispatch_expiry }}
        </p>
      </div>

      <!-- Action Button -->
      <button
        v-if="voucher.dispatch_status === 'active' && !voucher.is_expired"
        @click="() => reconnect(voucher.dispatch_voucher_code)"
        class="text-white bg-green-600 hover:bg-green-700 px-3 py-1 text-xs rounded"
      >
        RECONNECT
      </button>

      <button
        v-else
        :disabled="isloading && loadingId === voucher.dispatch_voucher_code"
        @click="() => renewVoucher(voucher)"
        class="text-white bg-blue-500 hover:bg-blue-600 px-3 py-1 text-xs rounded"
      >
        <span v-if="isloading && loadingId === voucher.dispatch_voucher_code">
          ⏳ RENEWING...
        </span>
        <span v-else>
          RENEW
        </span>
      </button>

      <!-- Expired Stamp -->
      <span
        v-if="voucher.is_expired"
        class="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 rotate-[-20deg] text-red-600 font-bold text-xl  pointer-events-none"
      >
        EXPIRED
      </span>
    </div>
  </div>
</template>


<script setup>
import { getCurrentInstance, onMounted } from 'vue'
import { useVoucherStore } from '@/stores/useVoucherStore'
import { useRenewPackage } from '@/composables/useRenewPackage'
import { toast } from 'vue3-toastify'
import axios from 'axios'

const voucherStore = useVoucherStore()
const formatUsage = (mb) => {
  const num = Number(mb) || 0  
  if (num < 1024) return num.toFixed(2) + ' MB'
  const gb = num / 1024
  if (gb < 1024) return gb.toFixed(2) + ' GB'
  const tb = gb / 1024
  return tb.toFixed(2) + ' TB'
}


const totalUsage = (voucher) => Number(voucher.total_download || 0) + Number(voucher.total_upload || 0)

const { proxy } = getCurrentInstance() // to access global properties
const hotspotIP = proxy.$hotspot.ip

onMounted(() => {
  voucherStore.fetchActiveVouchers()
})

const getCSRFToken = async () => {
  const response = await axios.get(`${import.meta.env.VITE_API_PROD_URL}/api/get-csrf-token/`)
  return response.data.csrf_token
}

const reconnect = async (voucherCode) => {
  try {
    const csrfToken = await getCSRFToken()

    const payload = {
      account: sessionStorage.getItem('account') || localStorage.getItem('account'),
      voucher_code: voucherCode,
      bound_ip: hotspotIP
    }

    const response = await axios.post(`${import.meta.env.VITE_API_PROD_URL}/api/reconnect/`, payload, {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'Authorization': `Token ${localStorage.getItem('authToken')}`
      }
    })

    if (response.status === 200) {
      toast.success('Reconnected successfully!')
      window.location = 'https://login.teralinkxwaves.uk/index.html#/connected'
    } else {
      toast.error('Reconnect failed. Please try again.')
    }
  } catch (error) {
    console.error('Reconnect error:', error)
    toast.error('Reconnect failed. Try again later.')
  }
}

const { renew, isloading, loadingId } = useRenewPackage()

const renewVoucher = async (voucher) => {
  try {
    await renew(voucher, voucher.dispatch_account) // send voucher + client_id
    toast.success(`Renewed voucher: ${voucher.dispatch_voucher_code}`)
  } catch (err) {
    toast.error(`Renew failed: ${err.message || 'try again later'}`)
  }
}
</script>

<style scoped>

</style>
