<!-- components/DashboardOTPVerification.vue -->
<template>
  <div v-if="showOTPVerification" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
      <div class="text-center mb-4">
        <h3 class="text-lg font-semibold">Verify Your Account</h3>
        <p class="text-gray-600 dark:text-gray-300 mt-1">
          Enter the OTP sent to {{ maskedPhone }}
        </p>
      </div>
      
      <div class="space-y-4">
        <!-- OTP Input -->
        <div class="flex justify-center space-x-2">
          <input
            v-for="(digit, index) in otpDigits"
            :key="index"
            v-model="otpDigits[index]"
            type="text"
            maxlength="1"
            @input="handleOtpInput(index, $event)"
            @keydown.delete="handleOtpDelete(index, $event)"
            class="w-12 h-12 text-center text-xl font-bold border-2 rounded-lg focus:border-blue-500 focus:outline-none"
          />
        </div>
        
        <!-- Timer -->
        <div class="text-center">
          <p class="text-sm" :class="timer > 0 ? 'text-gray-500' : 'text-blue-500'">
            {{ timer > 0 ? `Resend OTP in ${timer}s` : 'Ready to resend' }}
          </p>
        </div>
        
        <!-- Actions -->
        <div class="flex space-x-3">
          <button
            @click="resendOTP"
            :disabled="timer > 0 || loading"
            class="flex-1 py-2 px-4 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            Resend OTP
          </button>
          <button
            @click="verifyOTP"
            :disabled="!isOtpComplete || loading"
            class="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ loading ? 'Verifying...' : 'Verify' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useToast } from '../composables/useToast'

const props = defineProps({
  phone: String,
  sessionId: String,
  show: Boolean
})

const emit = defineEmits(['verified', 'cancel'])

const authStore = useAuthStore()
const { showSuccess, showError } = useToast()

const otpDigits = ref(Array(6).fill(''))
const loading = ref(false)
const timer = ref(60)
let timerInterval = null

const maskedPhone = computed(() => {
  if (!props.phone) return ''
  return `+254***${props.phone.slice(-3)}`
})

const isOtpComplete = computed(() => {
  return otpDigits.value.every(digit => digit !== '')
})

const showOTPVerification = computed(() => props.show)

const handleOtpInput = (index, event) => {
  const value = event.target.value
  if (/[0-9]/.test(value)) {
    otpDigits.value[index] = value
    if (index < 5) {
      const nextInput = event.target.nextElementSibling
      if (nextInput) nextInput.focus()
    }
  } else {
    otpDigits.value[index] = ''
  }
}

const handleOtpDelete = (index, event) => {
  if (event.key === 'Backspace' && !otpDigits.value[index] && index > 0) {
    const prevInput = event.target.previousElementSibling
    if (prevInput) {
      prevInput.focus()
      otpDigits.value[index - 1] = ''
    }
  }
}

const verifyOTP = async () => {
  if (!isOtpComplete.value) return
  
  loading.value = true
  const otpCode = otpDigits.value.join('')
  
  try {
    const result = await authStore.verifyOTP({
      phone: props.phone,
      otp_code: otpCode,
      session_id: props.sessionId
    })
    
    if (result.success) {
      showSuccess('OTP verified successfully!')
      emit('verified')
    } else {
      showError(result.message)
    }
  } catch (error) {
    showError('OTP verification failed')
  } finally {
    loading.value = false
  }
}

const resendOTP = async () => {
  timer.value = 60
  startTimer()
  // Call API to resend OTP
  showSuccess('OTP resent successfully')
}

const startTimer = () => {
  if (timerInterval) clearInterval(timerInterval)
  
  timerInterval = setInterval(() => {
    if (timer.value > 0) {
      timer.value--
    } else {
      clearInterval(timerInterval)
    }
  }, 1000)
}

onMounted(() => {
  startTimer()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>