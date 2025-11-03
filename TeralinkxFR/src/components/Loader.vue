<template>
  <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
    <div class="flex flex-col items-center justify-center space-y-4">
      <!-- Spinner with Pulse Animation -->
      <div class="relative w-12 h-12">
        <div class="absolute inset-0 rounded-full bg-blue-400 opacity-30 animate-ping"></div>
        <div class="relative w-12 h-12 border-8 border-gray-300 dark:border-gray-600 border-t-blue-600 dark:border-t-blue-400 rounded-full animate-spin"></div>
      </div>

      <!-- Loading Text -->
      <p class="text-sm font-medium text-white dark:text-gray-200 animate-pulse">
        {{ statusMessage }}
      </p>
    </div>
  </div>
</template>

<script setup>

import { ref, onMounted, onBeforeUnmount ,getCurrentInstance} from 'vue'
import { toast } from 'vue3-toastify'

const props = defineProps({
  interval: { type: Number, default: 5000 }, // polling interval
  timeout: { type: Number, default: 60000 }, // max wait time
  onSuccess: Function,
  onError: Function
})

const emit = defineEmits(['success', 'error'])
const polling = ref(null)
const requestId = ref(null)
const statusMessage = ref('Processing...')
const abortController = ref(null)
const { proxy } = getCurrentInstance()
const hotspotIP = proxy.$hotspot.ip

onMounted(() => {
  requestId.value = sessionStorage.getItem('checkoutId')
  if (requestId.value) {
    startPolling()
  } else {
    console.warn('⚠️ No requestId found in sessionStorage!')
    statusMessage.value = 'No payment request found.'
  }
})

onBeforeUnmount(() => {
  stopPolling()
})

function stopPolling() {
  clearInterval(polling.value)
  abortController.value?.abort()
}

function startPolling() {
  const startTime = Date.now()

  polling.value = setInterval(async () => {
    if (Date.now() - startTime >= props.timeout) {
      stopPolling()
      sessionStorage.removeItem('checkoutId')
      toast('❌ Payment timed out.', { type: 'error', autoClose: 5000, position: 'top-right' })
      statusMessage.value = 'Payment timed out.'
      emitError({ ResultDesc: 'Timeout' })
      return
    }

    abortController.value = new AbortController()

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/checkoutstatus/?request_id=${requestId.value}&ping=${sessionStorage.getItem('ping') || localStorage.getItem('ping')}&hotspot_ip=${hotspotIP}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': sessionStorage.getItem('csrfToken') || ''
          },
          signal: abortController.value.signal
        }
      )

      if (!response.ok) throw new Error(`HTTP error ${response.status}`)

      const data = await response.json()

      if (Number(data.ResultCode) === 0) {
        console.log('✅ Payment successful:', data)
        stopPolling()
        sessionStorage.removeItem('checkoutId')
        toast('✅ Payment successful!', { type: 'success', autoClose: 5000, position: 'top-right' })
        statusMessage.value = 'Payment successful!'
        emitSuccess(data)
        window.location = 'https://login.teralinkxwaves.uk/index.html#/connected'
      } else if (data.ResultDesc?.toLowerCase().includes('failed')) {
        stopPolling()
        sessionStorage.removeItem('checkoutId')
        statusMessage.value = 'Payment failed.'
        emitError(data)
      } else {
        statusMessage.value = 'Processing payment...'
      }
    } catch (err) {
      console.error('❌ Polling error:', err)
      statusMessage.value = 'Network error, retrying...'
    }
  }, props.interval)
}

function emitSuccess(data) {
  emit('success', data)
}


function emitError(data) {
    emit('error', data)
}
</script>
