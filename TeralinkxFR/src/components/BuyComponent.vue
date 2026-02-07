<template>
  <div>
    <div class="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 z-40 flex items-start justify-center pt-16">
      <div class="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-sm max-h-[calc(100vh-4rem)] overflow-y-auto mx-4">
        <div class="sticky top-0 bg-white dark:bg-gray-900 flex justify-between items-center px-4 py-3 border-b border-gray-200 dark:border-gray-700 rounded-t-xl">
          <h3 class="text-base font-semibold text-gray-800 dark:text-white text-center w-full flex items-center justify-center gap-2">
            <span>Pay Via</span>
            <img src="/src/assets/mpesa_no_bg.svg" alt="M-Pesa" class="w-16 h-8 object-contain">
          </h3>
          <button
            @click="closeForm"
            class="absolute top-2 right-2 text-gray-500 hover:text-red-600 focus:outline-none text-lg z-10"
          >
            ✕
          </button>
        </div>

        <form @submit.prevent="submitForm" class="px-4 py-3 space-y-3">
          <!-- Package Info -->
          <div class="bg-gray-50 dark:bg-gray-800 rounded-md p-3 mb-3">
            <p class="text-sm font-medium text-gray-800 dark:text-white">{{ props.packageDetails.name }}</p>
            <div class="flex items-center justify-between">
              <div>
                <p v-if="selectedCoupon" class="text-xs text-gray-500 line-through">KES {{ originalPrice.toFixed(2) }}</p>
                <p class="text-lg font-bold text-gray-900 dark:text-white">KES {{ packagePrice.toFixed(2) }}</p>
              </div>
              <div v-if="selectedCoupon" class="bg-purple-100 dark:bg-purple-900 px-2 py-1 rounded text-xs text-purple-800 dark:text-purple-200">
                {{ selectedCoupon.discount_value }}% OFF
              </div>
            </div>
          </div>

          <!-- Payment Breakdown (if mixed payment) -->
          <div v-if="props.packageDetails.paymentData" class="bg-gray-50 dark:bg-gray-800 rounded-md p-3 mb-3">
            <h4 class="text-sm font-medium text-gray-800 dark:text-white mb-2">Payment Breakdown</h4>
            <div class="text-xs space-y-1">
              <div class="flex justify-between">
                <span>Total Price:</span>
                <span>KES {{ props.packageDetails.paymentData.totalAmount.toFixed(2) }}</span>
              </div>
              <div v-if="props.packageDetails.paymentData.creditUsed > 0" class="flex justify-between text-green-600">
                <span>Credit Used:</span>
                <span>-KES {{ props.packageDetails.paymentData.creditUsed.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between font-bold border-t pt-1">
                <span>M-Pesa Payment:</span>
                <span>KES {{ props.packageDetails.paymentData.mpesaAmount.toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <!-- Available Coupons -->
          <div v-if="availableCouponsWithValidity.length > 0" class="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-md p-3 mb-3">
            <h4 class="text-sm font-medium text-purple-800 dark:text-purple-200 mb-2">Available Discount Coupons</h4>
            
            <div class="space-y-2">
              <div
                v-for="coupon in availableCouponsWithValidity"
                :key="coupon.code"
                @click="coupon.isUsable ? selectCoupon(coupon) : null"
                :class="[
                  'relative overflow-hidden rounded-lg transition-all duration-300',
                  coupon.isUsable 
                    ? 'cursor-pointer transform hover:scale-105' 
                    : 'cursor-not-allowed opacity-60',
                  selectedCoupon?.code === coupon.code && coupon.isUsable
                    ? 'ring-2 ring-purple-500 shadow-lg'
                    : coupon.isUsable ? 'hover:shadow-md' : ''
                ]"
              >
                <!-- Coupon Card -->
                <div :class="[
                  'p-2 text-white relative',
                  coupon.isUsable 
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500' 
                    : 'bg-gradient-to-r from-gray-400 to-gray-500'
                ]">
                  <!-- Decorative circles -->
                  <div class="absolute -top-1 -right-1 w-3 h-3 bg-white/20 rounded-full"></div>
                  <div class="absolute -bottom-1 -left-1 w-2 h-2 bg-white/10 rounded-full"></div>
                  
                  <!-- Coupon content -->
                  <div class="flex items-center justify-between relative z-10">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-1 mb-1">
                        <svg class="w-2 h-2" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M11,16.5L18,9.5L16.59,8.09L11,13.67L7.91,10.59L6.5,12L11,16.5Z"/>
                        </svg>
                        <span class="text-xs font-medium opacity-90 truncate">REWARD</span>
                      </div>
                      <h3 class="font-bold text-sm leading-tight">{{ coupon.discount_value }}% OFF</h3>
                      <p class="text-xs opacity-90">{{ coupon.savingsMessage }}</p>
                    </div>
                    
                    <!-- Discount badge -->
                    <div class="bg-white/20 backdrop-blur-sm rounded-full px-1.5 py-0.5 border border-white/30 ml-2">
                      <span class="text-xs font-bold">{{ coupon.discount_value }}%</span>
                    </div>
                  </div>
                  
                  <!-- Dotted line separator -->
                  <div class="absolute right-8 top-0 bottom-0 w-px border-l-2 border-dashed border-white/30"></div>
                  
                  <!-- Selection indicator -->
                  <div v-if="selectedCoupon?.code === coupon.code && coupon.isUsable" class="absolute top-0.5 left-0.5">
                    <div class="w-3 h-3 bg-white rounded-full flex items-center justify-center">
                      <svg class="w-1.5 h-1.5 text-purple-500" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z"/>
                      </svg>
                    </div>
                  </div>
                  
                  <!-- Unusable indicator -->
                  <div v-if="!coupon.isUsable" class="absolute top-0.5 right-0.5">
                    <div class="w-3 h-3 bg-red-500 rounded-full flex items-center justify-center">
                      <span class="text-xs text-white font-bold">!</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="selectedCoupon" class="mt-2 p-2 bg-green-100 dark:bg-green-900/20 rounded text-sm flex items-center justify-between">
              <span class="text-green-800 dark:text-green-200">✓ {{ selectedCoupon.name }} selected</span>
              <button @click="removeCoupon" class="text-green-600 hover:text-green-800 text-xs underline">Remove</button>
            </div>
          </div>

          <!-- Credit Usage Option -->
          <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-3 mb-3">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">Payment Options</h4>
            </div>
            <div class="space-y-2">
              <label class="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                <input type="checkbox" v-model="useCredit" class="rounded">
                <span>Use available credit (KES {{ Math.min(dashboardStore.balance, packagePrice).toFixed(2) }})</span>
              </label>
            </div>
            
            <!-- Payment Breakdown -->
            <div class="bg-white dark:bg-gray-800 rounded p-2 mt-3 text-xs">
              <div class="flex justify-between">
                <span>Original Price:</span>
                <span>KES {{ originalPrice.toFixed(2) }}</span>
              </div>
              <div v-if="selectedCoupon" class="flex justify-between text-purple-600">
                <span>Coupon Discount ({{ selectedCoupon.discount_value }}%):</span>
                <span>-KES {{ discountAmount.toFixed(2) }}</span>
              </div>
              <div v-if="useCredit" class="flex justify-between text-green-600">
                <span>Credit Used:</span>
                <span>-KES {{ creditToUse.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between font-bold border-t pt-1 mt-1">
                <span>M-Pesa Amount:</span>
                <span>KES {{ mpesaAmount.toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <!-- Account Balance Display -->
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-3 mb-3">
            <div class="flex justify-between items-center">
              <span class="text-xs text-blue-700 dark:text-blue-300 font-medium">Account Balance:</span>
              <span class="text-sm font-bold text-blue-800 dark:text-blue-200">KES {{ dashboardStore.balance.toFixed(2) }}</span>
            </div>
          </div>

          <div>
            <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1" for="phoneNumber">M-Pesa Phone Number</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span class="text-gray-500 text-sm">+254</span>
              </div>
              <input
                id="phoneNumber"
                type="tel"
                v-model="phoneNumber"
                @blur="formatPhoneNumber"
                required
                placeholder="712345678 or 112345678"
                maxlength="10"
                class="w-full pl-12 pr-3 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-700 text-gray-800 dark:text-white border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-1">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
              </svg>
              Enter 9-digit number (712345678, 112345678, or 0712345678)
            </p>
          </div>

          <div class="flex justify-between items-center pt-2">
            <button
              type="button"
              @click="closeForm"
              class="w-1/2 mr-2 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold py-2 rounded-md"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isProcessing"
              :class="[
                'w-1/2 ml-2 text-white text-sm font-semibold py-2 rounded-md transition flex items-center justify-center',
                isProcessing 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-green-600 hover:bg-green-700'
              ]"
            >
              <svg v-if="isProcessing" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isProcessing ? 'Processing...' : (mpesaAmount > 0 ? `Pay KES ${mpesaAmount.toFixed(2)} via M-Pesa` : 'Pay with Credit') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <PaymentLoader 
      v-if="isLoading" 
      :checkoutId="checkoutId"
      :amount="mpesaAmount"
      :phoneNumber="phoneNumber"
      @success="handlePaymentSuccess" 
      @error="handlePaymentFailure"
      @cancel="handlePaymentCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { toast } from '@/composables/useCustomToast'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import PaymentLoader from './PaymentLoader.vue'

const $router = useRouter()

const dashboardStore = useDashboardStore()
const authStore = useAuthStore()

const props = defineProps({
  packageDetails: Object
})

const emit = defineEmits(['close', 'submit'])

const phoneNumber = ref('')
const itemName = ref('')
const itemAmount = ref('')
const itemDesc = ref('')
const usedbalance = ref('')
const checkoutId = ref('')
const isLoading = ref(false)
const isProcessing = ref(false)
const processingTimeout = ref(null)

const useCredit = ref(props.packageDetails.defaultUseCredit ?? true) // Use default from payment selection

// Coupon state
const availableCoupons = ref([])
const selectedCoupon = ref(null)
const couponError = ref('')
const loading = ref(false)

// Computed properties for coupon validation
const availableCouponsWithValidity = computed(() => {
  return availableCoupons.value.map(coupon => {
    const baseDiscount = (originalPrice.value * coupon.discount_value) / 100
    
    // Apply dynamic rounding logic
    let effectiveDiscount
    if (originalPrice.value >= 50) {
      effectiveDiscount = Math.ceil(baseDiscount)
    } else {
      effectiveDiscount = Math.floor(baseDiscount)
    }
    
    // Calculate minimum package price for 3+ KES savings
    const minPriceFor3KES = Math.ceil(3 / (coupon.discount_value / 100))
    
    return {
      ...coupon,
      effectiveDiscount,
      isUsable: effectiveDiscount >= 3,
      minPriceFor3KES,
      savingsMessage: effectiveDiscount >= 3 
        ? `For ${effectiveDiscount}+ KES` 
        : `For ${minPriceFor3KES}+ KES packages`
    }
  })
})

// Computed properties for balance checking
const packagePrice = computed(() => {
  // Use original package price for calculations
  const basePrice = props.packageDetails.price?.parsedValue || props.packageDetails.price || 0
  
  // Apply coupon discount if selected
  if (selectedCoupon.value) {
    const discount = (basePrice * selectedCoupon.value.discount_value) / 100
    return Math.max(0, basePrice - discount)
  }
  
  return basePrice
})

const originalPrice = computed(() => {
  return props.packageDetails.price?.parsedValue || props.packageDetails.price || 0
})

const discountAmount = computed(() => {
  if (selectedCoupon.value) {
    const baseDiscount = (originalPrice.value * selectedCoupon.value.discount_value) / 100
    
    // 🔴 DYNAMIC M-PESA DISCOUNT ROUNDING SYSTEM
    // For expensive packages (≥50 KES): Round UP (ceiling) - more generous
    // For cheap packages (<50 KES): Round DOWN (floor) - conservative
    let roundedDiscount
    if (originalPrice.value >= 50) {
      // Expensive packages: Round UP for better customer experience
      roundedDiscount = Math.ceil(baseDiscount)
    } else {
      // Cheap packages: Round DOWN to maintain profitability
      roundedDiscount = Math.floor(baseDiscount)
    }
    
    return Math.min(roundedDiscount, originalPrice.value)
  }
  return 0
})

const creditToUse = computed(() => {
  if (!useCredit.value) return 0
  return Math.min(dashboardStore.balance, packagePrice.value)
})

const mpesaAmount = computed(() => {
  return Math.max(0, packagePrice.value - creditToUse.value)
})

onMounted(async () => {
  setPhoneNumber()
  await fetchAvailableCoupons()
  
  // Check if this is a mixed payment (credit + M-Pesa)
  if (props.packageDetails.paymentData) {
    const { paymentData } = props.packageDetails
    itemName.value = `Buy ${props.packageDetails.name}`
    itemAmount.value = `KES ${paymentData.mpesaAmount.toFixed(2)}`
    itemDesc.value = props.packageDetails.package_code
    usedbalance.value = paymentData.creditUsed || 0
  } else {
    itemName.value = `Buy ${props.packageDetails.name}`
    itemAmount.value = `KES ${props.packageDetails.price?.parsedValue || props.packageDetails.price}`
    itemDesc.value = props.packageDetails.package_code
    usedbalance.value = props.packageDetails.usedbalance || 0
  }
})

// Watch for dashboard data changes
watch(() => dashboardStore.phoneNumber, () => {
  if (dashboardStore.phoneNumber && !phoneNumber.value) {
    setPhoneNumber()
  }
})

function setPhoneNumber() {

  
  const dashboardPhone = dashboardStore.phoneNumber || ''
  const storedPhone = localStorage.getItem('account') || sessionStorage.getItem('account') || ''
  

  
  const phoneToUse = dashboardPhone || storedPhone

  
  if (phoneToUse) {
    phoneNumber.value = formatPhoneForDisplay(phoneToUse)

  }
}

function formatPhoneForDisplay(phone) {
  if (!phone) return ''
  
  // Remove all non-digits
  const cleaned = phone.replace(/\D/g, '')
  
  // Handle different formats
  if (cleaned.startsWith('254') && cleaned.length === 12) {
    // 254712345678 → 712345678
    return cleaned.substring(3)
  }
  if (cleaned.startsWith('0') && cleaned.length === 10) {
    // 0712345678 → 712345678
    return cleaned.substring(1)
  }
  if (cleaned.length === 9) {
    // 712345678 → 712345678 (already correct)
    return cleaned
  }
  
  return phone // Return original if can't format
}

function formatPhoneNumber() {
  if (!phoneNumber.value) return
  
  // Remove all non-digits
  const cleaned = phoneNumber.value.replace(/\D/g, '')
  
  // Format based on input
  if (cleaned.startsWith('0') && cleaned.length === 10) {
    // 0712345678 → 712345678
    phoneNumber.value = cleaned.substring(1)
  } else if (cleaned.startsWith('254') && cleaned.length === 12) {
    // 254712345678 → 712345678
    phoneNumber.value = cleaned.substring(3)
  } else if (cleaned.length === 9) {
    // 712345678 or 112345678 → keep as is
    phoneNumber.value = cleaned
  }
  // For other formats, keep original input
}

const fetchAvailableCoupons = async () => {
  try {
    loading.value = true
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/rewards/coupons/`, {
      headers: authStore.authHeaders
    })
    
    if (response.ok) {
      const data = await response.json()
      availableCoupons.value = data.coupons || []
    }
  } catch (error) {
  } finally {
    loading.value = false
  }
}

const selectCoupon = (coupon) => {
  selectedCoupon.value = coupon
  toast.success(`${coupon.name} selected (${coupon.discount_value}% off)`)
}

const removeCoupon = () => {
  selectedCoupon.value = null
  toast.info('Coupon removed')
}

function closeForm() {
  emit('close')
}

function clearProcessing() {
  isProcessing.value = false
  if (processingTimeout.value) {
    clearTimeout(processingTimeout.value)
    processingTimeout.value = null
  }
}

async function handleUnifiedPayment() {
  try {
    // Format phone number: add 254 prefix to the 9-digit number
    const formattedPhoneNumber = '254' + phoneNumber.value
    
    // Determine payment method based on amounts
    let paymentMethod
    if (mpesaAmount.value === 0) {
      paymentMethod = 'credit'
    } else if (creditToUse.value > 0) {
      paymentMethod = 'mixed'
    } else {
      paymentMethod = 'mpesa'
    }
    
    const paymentData = {
      package_id: props.packageDetails.id,
      payment_method: paymentMethod,
      phone_number: formattedPhoneNumber,
      use_credit: useCredit.value,
      auto_login: true
    }
    
    // Add coupon if selected
    if (selectedCoupon.value) {
      paymentData.coupon_code = selectedCoupon.value.code
    }
    
    // Log the payload being sent
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/payments/unified/`, {
      method: 'POST',
      headers: authStore.authHeaders,
      body: JSON.stringify(paymentData)
    })
    
    const data = await response.json()

    
    if (response.ok && data.success) {
      if (paymentMethod === 'credit') {
        // Pure credit payment - immediate success
        toast.success('Package purchased successfully with account credit!')
        await dashboardStore.fetchDashboardData()
        emit('close')
        $router.push('/connected')
      } else {
        // M-Pesa payment - start polling
        checkoutId.value = data.checkout_request_id
        sessionStorage.setItem('checkoutId', checkoutId.value)
        
        clearProcessing()
        isLoading.value = true
        
        toast.success('M-Pesa prompt sent! Please complete payment on your phone.')
      }
    } else if (response.status === 402 || data.error?.includes('insufficient')) {
      await dashboardStore.fetchDashboardData()
      toast.warning(data.error || 'Insufficient balance for this payment method.')
    } else {
      throw new Error(data.error || 'Payment failed')
    }
    
  } catch (error) {
    console.error('Unified payment error:', error)
    toast.error(`Payment failed: ${error.message}`)
    await dashboardStore.fetchDashboardData()
  } finally {
    if (isProcessing.value) {
      clearProcessing()
    }
  }
}

function submitForm() {
  if (isProcessing.value) return
  
  isProcessing.value = true
  
  // Set 60-second timeout
  processingTimeout.value = setTimeout(() => {
    if (isProcessing.value) {
      isProcessing.value = false
      toast.error('Payment processing timed out. Please try again.')
    }
  }, 60000)
  
  try {
    handleUnifiedPayment()
  } catch (error) {
    console.error('Payment submission error:', error)
    toast.error('Payment submission failed. Please try again.')
    clearProcessing()
  }
}

function handlePaymentCancel() {
  isLoading.value = false
  toast.info('Payment cancelled by user')
}

function handlePaymentSuccess(data) {
  isLoading.value = false
  toast.success('🎉 Payment successful! Your voucher has been activated.')
  // Force refresh dashboard data to show updated balance and voucher
  dashboardStore.fetchDashboardData()
  
  // Navigate to connected page instead of closing modal
  emit('close')
  $router.push('/connected')
}

function handlePaymentFailure(data) {
  isLoading.value = false
  toast.error('Payment failed. Please try again.')
}

const formatCouponDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}
</script>

<style scoped>
</style>