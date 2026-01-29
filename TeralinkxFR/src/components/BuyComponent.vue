<template>
  <div>
    <div class="fixed inset-0 bg-black bg-opacity-10 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-900 rounded-xl shadow-lg w-full max-w-xs sm:max-w-sm transition-all relative">
        <div class="flex justify-between items-center px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-base font-semibold text-gray-800 dark:text-white text-center w-full">Pay Via Mpesa</h3>
          <button
            @click="closeForm"
            class="absolute top-2 right-2 text-gray-500 hover:text-red-600 focus:outline-none text-sm"
          >
            ✕
          </button>
        </div>

        <form @submit.prevent="submitForm" class="px-4 py-3 space-y-3">
          <div>
            <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1" for="itemName">Package</label>
            <input
              id="itemName"
              v-model="itemName"
              readonly
              class="w-full px-3 py-2 text-sm font-medium rounded-md bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-white border border-gray-300 dark:border-gray-600"
            />
          </div>

          <div>
            <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1" for="itemAmount">Amount</label>
            <input
              id="itemAmount"
              v-model="itemAmount"
              readonly
              class="w-full px-3 py-2 text-sm font-medium rounded-md bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-white border border-gray-300 dark:border-gray-600"
            />
          </div>

          <div>
            <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1" for="phoneNumber">Phone Number</label>
            <input
              id="phoneNumber"
              type="text"
              v-model="phoneNumber"
              required
              class="w-full px-3 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-700 text-gray-800 dark:text-white border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring focus:ring-blue-300"
            />
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
              class="w-1/2 ml-2 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold py-2 rounded-md"
            >
              Buy
            </button>
          </div>
        </form>
      </div>
    </div>

    <Loader v-if="isLoading" @success="handlePaymentSuccess" @error="handlePaymentFailure" />
    <Loader1
      v-if="isLoading1"
      
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { toast } from 'vue3-toastify'
import Loader from './Loader.vue'
import  Loader1  from '@/views/Loader.vue'


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
const isLoading1 = ref(false)

onMounted(() => {
  const storedPhone = localStorage.getItem('account') || sessionStorage.getItem('account') || ''
  phoneNumber.value = storedPhone.startsWith('254') ? '0' + storedPhone.slice(3) : storedPhone

  itemName.value = `Buy ${props.packageDetails.package}`
  itemAmount.value = `@KES ${props.packageDetails.price}`
  itemDesc.value = props.packageDetails.package_code
  usedbalance.value = props.packageDetails.usedbalance
})

function closeForm() {
  emit('close')
}

function submitForm() {
  isLoading1.value = true
  getCSRFToken()
    .then(csrfToken => {
      const formattedPhoneNumber = phoneNumber.value.startsWith('254') ? phoneNumber.value : '254' + phoneNumber.value.slice(1)
      const extractPrice = itemAmount.value.match(/@KES\s*(\d+(\.\d+)?)/)
      const match = extractPrice ? parseFloat(extractPrice[1]) : null

      const payload = {
        ping: localStorage.getItem('ping') || sessionStorage.getItem('ping'),
        account: sessionStorage.getItem('account') || localStorage.getItem('account'),
        Amount: parseFloat(match),
        PhoneNumber: formattedPhoneNumber,
        UsedBalance: usedbalance.value,
        Items: [
          {
            package: itemName.value,
            price: match,
            package_code: itemDesc.value,
            phoneNumber: formattedPhoneNumber
          }
        ]
      }

      axios
        .post(`${import.meta.env.VITE_API_PROD_URL}/api/payment/`, payload, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            Authorization: `Token ${localStorage.getItem('authToken')}`
          }
        })
        .then(response => {
          checkoutId.value = response.data.checkout_id || ''
          if (checkoutId.value) {
            sessionStorage.setItem('checkoutId', checkoutId.value)
            isLoading1.value = false
            isLoading.value = true
            toast('🔄 Processing payment...')
            emit('submit', {
              checkoutId: checkoutId.value,
              phoneNumber: formattedPhoneNumber,
              amount: match
            })
          } else {
            toast.error('⚠️ No checkout ID received. Please try again.')
            isLoading1.value = false
          }
        })
        .catch(error => {
          console.error('Error sending payment payload:', error)
        })
    })
    .catch(error => {
      console.error('Failed to retrieve CSRF token:', error)
    })
}

function handlePaymentSuccess(data) {
  isLoading.value = false
  window.location.href = '/#/dashboard'
  emit('close')
}

function handlePaymentFailure(data) {
  isLoading.value = false
  toast(`❌ Payment failed: ${data.ResultDesc || 'Unknown error'}`)
  emit('close')
}

function getCSRFToken() {
  return new Promise((resolve, reject) => {
    axios
      .get(`${import.meta.env.VITE_API_PROD_URL}/api/get-csrf-token/`)
      .then(response => {
        const csrfToken = response.data.csrf_token
        csrfToken ? resolve(csrfToken) : reject('CSRF token not found in response')
      })
      .catch(error => reject('Failed to retrieve CSRF token', error))
  })
}
</script>

<style scoped>
</style>
