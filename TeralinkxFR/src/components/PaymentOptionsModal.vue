<template>
  <div class="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 z-40 flex items-start justify-center pt-16">
    <div class="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-sm max-h-[calc(100vh-4rem)] overflow-y-auto mx-4">
      <!-- Header -->
      <div class="sticky top-0 bg-white dark:bg-gray-900 flex justify-between items-center px-4 py-3 border-b border-gray-200 dark:border-gray-700 rounded-t-xl">
        <h3 class="text-base font-semibold text-gray-800 dark:text-white text-center w-full">Choose Payment Method</h3>
        <button @click="closeModal" class="absolute top-2 right-2 text-gray-500 hover:text-red-600 focus:outline-none text-lg">✕</button>
      </div>

      <div class="px-4 py-3 space-y-4">
        <!-- Package Info -->
        <div class="bg-gray-50 dark:bg-gray-800 rounded-md p-3">
          <p class="text-sm font-medium text-gray-800 dark:text-white">{{ packageDetails.name }}</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white">KES {{ packagePrice.toFixed(2) }}</p>
        </div>

        <!-- Account Balance -->
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-3">
          <div class="flex justify-between items-center">
            <span class="text-xs text-blue-700 dark:text-blue-300 font-medium">Account Balance:</span>
            <span class="text-sm font-bold text-blue-800 dark:text-blue-200">KES {{ dashboardStore.balance.toFixed(2) }}</span>
          </div>
        </div>

        <!-- Payment Options -->
        <div class="space-y-3">
          <!-- Credit Payment Option -->
          <div v-if="paymentFlow.canPayWithCredit" class="border border-green-200 dark:border-green-800 rounded-md p-3 bg-green-50 dark:bg-green-900/20">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-medium text-green-800 dark:text-green-200">Pay with Account Credit</h4>
              <span class="text-xs bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200 px-2 py-1 rounded">Recommended</span>
            </div>
            <p class="text-xs text-green-700 dark:text-green-300 mb-3">Instant activation using your account balance</p>
            <button @click="payWithCredit" :disabled="loading" class="w-full bg-green-600 hover:bg-green-700 text-white text-sm font-semibold py-2 rounded-md transition">
              {{ loading ? 'Processing...' : `Pay KES ${packagePrice.toFixed(2)} with Credit` }}
            </button>
          </div>

          <!-- Mixed Payment Option -->
          <div v-if="paymentFlow.canPayWithMixed && !paymentFlow.canPayWithCredit" class="border border-orange-200 dark:border-orange-800 rounded-md p-3 bg-orange-50 dark:bg-orange-900/20">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-medium text-orange-800 dark:text-orange-200">Mixed Payment</h4>
              <span class="text-xs bg-orange-100 dark:bg-orange-800 text-orange-800 dark:text-orange-200 px-2 py-1 rounded">Smart Option</span>
            </div>
            
            <!-- Payment Breakdown -->
            <div class="bg-white dark:bg-gray-800 rounded p-2 mb-3 text-xs">
              <div class="flex justify-between text-green-600">
                <span>Credit Used:</span>
                <span>KES {{ paymentFlow.creditAmount.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between text-blue-600">
                <span>M-Pesa Payment:</span>
                <span>KES {{ paymentFlow.mpesaAmount.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between font-bold border-t pt-1 mt-1">
                <span>Total:</span>
                <span>KES {{ packagePrice.toFixed(2) }}</span>
              </div>
            </div>

            <button @click="payWithMixed" :disabled="loading" class="w-full bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold py-2 rounded-md transition">
              {{ loading ? 'Processing...' : `Pay Credit + M-Pesa` }}
            </button>
          </div>

          <!-- M-Pesa Payment Option -->
          <div class="border border-blue-200 dark:border-blue-800 rounded-md p-3 bg-blue-50 dark:bg-blue-900/20">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-medium text-blue-800 dark:text-blue-200 flex items-center gap-2">
                <img src="/src/assets/mpesa_no_bg.svg" alt="M-Pesa" class="w-12 h-12">
                Pay with M-Pesa
              </h4>
            </div>
            <p class="text-xs text-blue-700 dark:text-blue-300 mb-3">Pay the full amount via M-Pesa</p>
            <button @click="payWithMpesa" :disabled="loading" class="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold py-2 rounded-md transition">
              {{ loading ? 'Processing...' : `Pay KES ${packagePrice.toFixed(2)} via M-Pesa` }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { api } from '@/services/api'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import { toast } from 'vue3-toastify'

const props = defineProps({
  packageDetails: Object
})

const emit = defineEmits(['close', 'paymentSelected'])

const router = useRouter()
const dashboardStore = useDashboardStore()
const authStore = useAuthStore()
const loading = ref(false)

// Computed properties for smart payment flow
const packagePrice = computed(() => {
  return props.packageDetails.price?.parsedValue || props.packageDetails.price || 0
})

const paymentFlow = computed(() => {
  const userBalance = dashboardStore.balance
  const price = packagePrice.value
  
  if (userBalance >= price) {
    return {
      canPayWithCredit: true,
      canPayWithMixed: false,
      recommendedMethod: 'credit',
      creditAmount: price,
      mpesaAmount: 0
    }
  } else if (userBalance > 0) {
    return {
      canPayWithCredit: false,
      canPayWithMixed: true,
      recommendedMethod: 'mixed',
      creditAmount: userBalance,
      mpesaAmount: price - userBalance
    }
  } else {
    return {
      canPayWithCredit: false,
      canPayWithMixed: false,
      recommendedMethod: 'mpesa',
      creditAmount: 0,
      mpesaAmount: price
    }
  }
})

// Methods
function closeModal() {
  emit('close')
}

async function payWithCredit() {
  if (!paymentFlow.value.canPayWithCredit) {
    toast.error('Insufficient balance for credit payment')
    return
  }
  
  loading.value = true
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/payments/unified/`, {
      method: 'POST',
      headers: authStore.authHeaders,
      body: JSON.stringify({
        payment_method: 'credit',
        package_id: props.packageDetails.id
      })
    })
    
    const data = response.data
    
    if (response.status === 200 && data.success) {
      toast.success('Package purchased successfully with account credit!')
      await dashboardStore.fetchDashboardData()
      emit('close')
      router.push('/connected')
    } else {
      throw new Error(data.error || 'Credit payment failed')
    }
    
  } catch (error) {
    console.error('Credit payment error:', error)
    toast.error(`Credit payment failed: ${error.message}`)
  } finally {
    loading.value = false
  }
}

async function payWithMixed() {
  // Open BuyComponent for mixed payment with use_credit = true
  emit('paymentSelected', {
    method: 'mixed',
    useCredit: true,
    packageDetails: props.packageDetails,
    paymentData: {
      totalAmount: packagePrice.value,
      creditUsed: paymentFlow.value.creditAmount,
      mpesaAmount: paymentFlow.value.mpesaAmount
    }
  })
}

async function payWithMpesa() {
  // Open BuyComponent for M-Pesa payment with use_credit = false
  emit('paymentSelected', {
    method: 'mpesa',
    useCredit: false,
    packageDetails: props.packageDetails
  })
}

// Add payment status polling
async function pollPaymentStatus(checkoutRequestId) {
  const maxAttempts = 60 // Poll for 2 minutes
  let attempts = 0
  
  const poll = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/payment-status/${checkoutRequestId}/`, {
        headers: authStore.authHeaders
      })
      
      const data = response.data
      
      if (data.payment_status === 'completed' && data.voucher_created) {
        toast.success('🎉 Payment successful! Your voucher has been activated.')
        await dashboardStore.fetchDashboardData()
        emit('close')
        router.push('/connected')
        return
      }
      
      if (data.queue_status === 'failed') {
        toast.error('Payment failed. Please try again.')
        return
      }
      
      // Continue polling if still pending
      attempts++
      if (attempts < maxAttempts) {
        setTimeout(poll, 2000) // Poll every 2 seconds
      } else {
        toast.warning('Payment status check timed out. Please check your vouchers.')
      }
      
    } catch (error) {
      console.error('Payment status check error:', error)
      attempts++
      if (attempts < maxAttempts) {
        setTimeout(poll, 2000)
      }
    }
  }
  
  // Start polling after 5 seconds
  setTimeout(poll, 5000)
}
</script>