<template>
  <!-- Modal Overlay -->
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Background Overlay -->
    <div 
      class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
      @click="closeModal"
    ></div>

    <!-- Modal Container -->
    <div class="flex min-h-full items-center justify-center p-4">
      <!-- Modal Content -->
      <div 
        class="relative w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-xl overflow-hidden transform transition-all"
        @click.stop
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-800 dark:to-blue-900 px-6 py-5">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-bold text-white">Reset Password</h2>
              <p class="text-blue-100 text-sm mt-1">Enter your phone number to reset password</p>
            </div>
            <button
              @click="closeModal"
              class="text-white hover:text-blue-200 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="px-6 py-6 space-y-6">
          <!-- Steps Indicator -->
          <div class="flex items-center justify-between mb-6">
            <div 
              class="flex flex-col items-center flex-1"
              :class="{ 'opacity-50': step > 1 }"
            >
              <div 
                class="w-8 h-8 rounded-full flex items-center justify-center mb-2"
                :class="{
                  'bg-blue-600 text-white': step === 1,
                  'bg-gray-200 dark:bg-gray-700 text-gray-500': step > 1
                }"
              >
                1
              </div>
              <span class="text-xs font-medium">Enter Phone</span>
            </div>
            
            <div class="flex-1 h-0.5 mx-2 bg-gray-200 dark:bg-gray-700"></div>
            
            <div 
              class="flex flex-col items-center flex-1"
              :class="{ 'opacity-50': step < 2 }"
            >
              <div 
                class="w-8 h-8 rounded-full flex items-center justify-center mb-2"
                :class="{
                  'bg-blue-600 text-white': step === 2,
                  'bg-gray-200 dark:bg-gray-700 text-gray-500': step < 2
                }"
              >
                2
              </div>
              <span class="text-xs font-medium">Verify OTP</span>
            </div>
            
            <div class="flex-1 h-0.5 mx-2 bg-gray-200 dark:bg-gray-700"></div>
            
            <div 
              class="flex flex-col items-center flex-1"
              :class="{ 'opacity-50': step < 3 }"
            >
              <div 
                class="w-8 h-8 rounded-full flex items-center justify-center mb-2"
                :class="{
                  'bg-blue-600 text-white': step === 3,
                  'bg-gray-200 dark:bg-gray-700 text-gray-500': step < 3
                }"
              >
                3
              </div>
              <span class="text-xs font-medium">New Password</span>
            </div>
          </div>

          <!-- Step 1: Phone Input -->
          <div v-if="step === 1" class="space-y-4">
            <div class="space-y-2">
              <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">
                Phone Number
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 dark:text-gray-400">+254</span>
                </div>
                <input
                  v-model="phone"
                  type="tel"
                  placeholder="712345678"
                  @input="validatePhone"
                  class="w-full pl-14 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  maxlength="9"
                />
                <div v-if="isValidPhone" class="absolute inset-y-0 right-3 flex items-center">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Enter your 9-digit phone number registered with Teralinkx
              </p>
            </div>

            <button
              @click="sendOTP"
              :disabled="!isValidPhone || sendingOTP"
              class="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl active:scale-[0.98]"
            >
              <span v-if="sendingOTP" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending OTP...
              </span>
              <span v-else>Send OTP</span>
            </button>
          </div>

          <!-- Step 2: OTP Verification -->
          <div v-if="step === 2" class="space-y-4">
            <div class="text-center">
              <p class="text-gray-600 dark:text-gray-300">
                Enter the 6-digit OTP sent to
                <span class="font-semibold">+254{{ phone }}</span>
              </p>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                OTP will expire in {{ formatTime(otpExpiry) }}
              </p>
            </div>

            <div class="space-y-2">
              <div class="flex justify-center space-x-2">
                <input
                  v-for="(digit, index) in otpDigits"
                  :key="index"
                  v-model="otpDigits[index]"
                  type="text"
                  maxlength="1"
                  @input="handleOtpInput(index, $event)"
                  @keydown.delete="handleOtpDelete(index, $event)"
                  @paste="handleOtpPaste($event)"
                  class="w-12 h-12 text-center text-xl font-bold border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:border-blue-500 focus:outline-none transition"
                  :class="{ 'border-blue-500': otpDigits[index] }"
                />
              </div>
            </div>

            <div class="flex justify-between items-center">
              <button
                @click="resendOTP"
                :disabled="canResendOTP === false"
                class="text-sm text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ resendText }}
              </button>
              
              <button
                @click="step = 1"
                class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Change phone number
              </button>
            </div>

            <button
              @click="verifyOTP"
              :disabled="!isOtpComplete || verifyingOTP"
              class="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl active:scale-[0.98]"
            >
              <span v-if="verifyingOTP" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Verifying...
              </span>
              <span v-else>Verify OTP</span>
            </button>
          </div>

          <!-- Step 3: New Password -->
          <div v-if="step === 3" class="space-y-4">
            <div class="text-center">
              <div class="w-16 h-16 mx-auto mb-4 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">OTP Verified</h3>
              <p class="text-gray-600 dark:text-gray-300 mt-1">
                Now set your new password
              </p>
            </div>

            <div class="space-y-4">
              <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">
                  New Password
                </label>
                <div class="relative">
                  <input
                    v-model="newPassword"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="Enter new password"
                    class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L6.59 6.59m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
                    </svg>
                    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                  </button>
                </div>
                <PasswordStrength :password="newPassword" />
              </div>

              <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">
                  Confirm Password
                </label>
                <input
                  v-model="confirmPassword"
                  type="password"
                  placeholder="Confirm new password"
                  class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  :class="{ 'border-red-300 dark:border-red-700': !passwordsMatch && confirmPassword }"
                />
                <p v-if="!passwordsMatch && confirmPassword" class="text-xs text-red-600 dark:text-red-400">
                  Passwords don't match
                </p>
              </div>
            </div>

            <div class="flex space-x-3">
              <button
                @click="step = 2"
                class="flex-1 py-3 px-4 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition"
              >
                Back
              </button>
              <button
                @click="resetPassword"
                :disabled="!canResetPassword || resettingPassword"
                class="flex-1 py-3 px-4 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
              >
                <span v-if="resettingPassword" class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Resetting...
                </span>
                <span v-else>Reset Password</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Success Message -->
        <div v-if="success" class="px-6 py-4 bg-green-50 dark:bg-green-900/20 border-t border-green-200 dark:border-green-800">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-green-800 dark:text-green-300">
                Password reset successful!
              </p>
              <p class="text-xs text-green-600 dark:text-green-400 mt-1">
                You can now sign in with your new password
              </p>
            </div>
            <button
              @click="closeModal"
              class="text-sm px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              Sign In
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from '@/composables/useToast'
import PasswordStrength from './PasswordStrength.vue'

const emit = defineEmits(['close'])

const { showSuccess, showError, showInfo } = useToast()

// State
const step = ref(1)
const phone = ref('')
const otpDigits = ref(Array(6).fill(''))
const newPassword = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const sendingOTP = ref(false)
const verifyingOTP = ref(false)
const resettingPassword = ref(false)
const success = ref(false)

// OTP expiry and rate-limit state
const otpExpiry = ref(null)
const canResendOTP = ref(true)
const resendCooldown = ref(0)
let resendInterval = null
let expiryInterval = null

// Client-side attempt tracking for additional protection (note: enforce server-side rate limiting too)
const sendAttempts = ref(0)
const maxSendAttempts = 5
const resendCooldownBase = 60 // base seconds
const resendCooldownMaxMultiplier = 8 // cap backoff multiplier

// Computed
const isValidPhone = computed(() => {
  const cleaned = phone.value.replace(/\D/g, '')
  return cleaned.length === 9
})

const isOtpComplete = computed(() => {
  return otpDigits.value.every(digit => digit !== '')
})

const passwordsMatch = computed(() => {
  return newPassword.value === confirmPassword.value
})

const canResetPassword = computed(() => {
  return (
    newPassword.value.length >= 6 &&
    passwordsMatch.value
  )
})

const resendText = computed(() => {
  if (sendAttempts.value >= maxSendAttempts) return 'Too many attempts'
  if (canResendOTP.value) return 'Resend OTP'
  return `Resend in ${resendCooldown.value}s`
})

// Methods
const validatePhone = () => {
  phone.value = phone.value.replace(/\D/g, '').slice(0, 9)
}

const formatTime = (seconds) => {
  if (!seconds || seconds <= 0) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleOtpInput = (index, event) => {
  const value = event.target.value
  
  if (/[0-9]/.test(value)) {
    otpDigits.value[index] = value
    
    // Move to next input
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

const handleOtpPaste = (event) => {
  event.preventDefault()
  const pasteData = event.clipboardData.getData('text').slice(0, 6)
  
  if (/^\d+$/.test(pasteData)) {
    const digits = pasteData.split('')
    digits.forEach((digit, index) => {
      if (index < 6) {
        otpDigits.value[index] = digit
      }
    })
  }
}

const computeBackoffSeconds = () => {
  // Exponential backoff based on attempts: base * 2^(attempts-1), capped
  const multiplier = Math.min(Math.pow(2, Math.max(0, sendAttempts.value - 1)), resendCooldownMaxMultiplier)
  return Math.round(resendCooldownBase * multiplier)
}

const clearExpiryInterval = () => {
  if (expiryInterval) {
    clearInterval(expiryInterval)
    expiryInterval = null
  }
}
const clearResendInterval = () => {
  if (resendInterval) {
    clearInterval(resendInterval)
    resendInterval = null
  }
}

const sendOTP = async () => {
  if (!isValidPhone.value) return

  if (sendAttempts.value >= maxSendAttempts) {
    showError('Too many OTP requests. Please try again later or contact support.')
    return
  }

  if (!canResendOTP.value) {
    showInfo(`Please wait ${resendCooldown.value}s before retrying.`)
    return
  }

  sendingOTP.value = true
  // Count the attempt immediately to avoid race conditions and brute-force looping
  sendAttempts.value++

  try {
    // TODO: Call your OTP sending API (server must enforce rate limiting)
    // await api.post('/api/password-reset/otp/', {
    //   phone: `254${phone.value}`
    // })

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))

    // Set OTP expiry (5 minutes)
    otpExpiry.value = 300

    // Clear any existing expiry timer then start a fresh one
    clearExpiryInterval()
    expiryInterval = setInterval(() => {
      if (otpExpiry.value > 0) {
        otpExpiry.value--
      } else {
        clearExpiryInterval()
        showError('OTP has expired. Please request a new one.')
        step.value = 1
      }
    }, 1000)

    // Move to OTP verification step
    step.value = 2
    showSuccess('OTP sent successfully')

    // Start resend cooldown with exponential backoff
    startResendCooldown()
  } catch (error) {
    showError('Failed to send OTP. Please try again.')
  } finally {
    sendingOTP.value = false
  }
}

const startResendCooldown = () => {
  // If attempts exceeded, block resend entirely
  if (sendAttempts.value >= maxSendAttempts) {
    canResendOTP.value = false
    resendCooldown.value = 0
    clearResendInterval()
    return
  }

  canResendOTP.value = false
  // Use exponential backoff based on number of attempts
  const cooldown = computeBackoffSeconds()
  resendCooldown.value = cooldown

  clearResendInterval()
  resendInterval = setInterval(() => {
    resendCooldown.value--

    if (resendCooldown.value <= 0) {
      canResendOTP.value = true
      clearResendInterval()
      // If attempts already exhausted, immediately lock again
      if (sendAttempts.value >= maxSendAttempts) {
        canResendOTP.value = false
      }
    }
  }, 1000)
}

const resendOTP = async () => {
  if (sendAttempts.value >= maxSendAttempts) {
    showError('Too many OTP requests. Please try again later.')
    return
  }

  if (!canResendOTP.value) {
    showInfo(`Please wait ${resendCooldown.value}s before retrying.`)
    return
  }

  await sendOTP()
  showInfo('New OTP sent')
}

const verifyOTP = async () => {
  if (!isOtpComplete.value) return
  
  verifyingOTP.value = true
  
  try {
    const otpCode = otpDigits.value.join('')
    
    // TODO: Call your OTP verification API
    // await api.post('/api/password-reset/verify/', {
    //   phone: `254${phone.value}`,
    //   otp: otpCode
    // })
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Move to password reset step
    step.value = 3
    showSuccess('OTP verified successfully')
    
  } catch (error) {
    showError('Invalid OTP. Please try again.')
  } finally {
    verifyingOTP.value = false
  }
}

const resetPassword = async () => {
  if (!canResetPassword.value) return
  
  resettingPassword.value = true
  
  try {
    // TODO: Call your password reset API
    // await api.post('/api/password-reset/confirm/', {
    //   phone: `254${phone.value}`,
    //   password: newPassword.value
    // })

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    success.value = true
    showSuccess('Password reset successful!')
    
    // Auto-close after 3 seconds
    setTimeout(() => {
      closeModal()
    }, 3000)
    
  } catch (error) {
    showError('Failed to reset password. Please try again.')
  } finally {
    resettingPassword.value = false
  }
}

const closeModal = () => {
  emit('close')
}

// Cleanup
onMounted(() => {
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.body.style.overflow = ''
  clearResendInterval()
  clearExpiryInterval()
})
</script>

<style scoped>
/* Custom focus styles for OTP inputs */
input:focus {
  outline: none;
  ring: 2px;
}
</style>