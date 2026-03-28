<template>
  <!-- Auth Loader - shown while checking existing credentials -->
  <AuthLoader v-if="isCheckingCredentials" />
  
  <!-- Main Signin Form - shown after credential check -->
  <div v-else class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 px-4">

    <!-- Main Auth Card -->
    <div class="w-full max-w-xs bg-white dark:bg-gray-900 shadow-xl rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700">
      <!-- Logo Header -->
      <div class="p-3 flex justify-center">
        <div class="text-center">
          <img src="../assets/teralinkx2.png" alt="Teralinkx Waves" class="h-32 mx-auto" />
          <h6 class="text-lg font-bold text-gray-900 dark:text-gray-100">Sign In</h6>
          <p class="text-black-100 text-xs mt-1">High-Speed Internet Access</p>
        </div>
      </div>

      <!-- Auth Form -->
      <form @submit.prevent="handleManualAuth" class="p-4 space-y-4">
        <!-- Connection Status -->
        <ConnectionStatus />

        <!-- Maintenance Announcements -->
        <MaintenanceAnnouncements />

        <!-- Error Display -->
        <AuthError 
          v-if="authStore.error"
          :error="authStore.error"
          @clear="authStore.clearError()"
        />

        <!-- Network Warning (shown when no hotspot data) -->
        <div v-if="!hotspot.ip || !hotspot.mac" class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
          <div class="flex items-start space-x-2">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.346 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            <div class="text-sm text-red-700 dark:text-red-300">
              <p class="font-medium">No Hotspot Connection</p>
              <p class="text-xs mt-1">Please connect to Teralinkx WiFi hotspot to continue.</p>
            </div>
          </div>
        </div>

        <!-- Step 1: Phone Number Input (Always shown first) -->
        <div class="space-y-4">
          <!-- Phone Input -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">
              Phone Number
            </label>
            <div class="relative">
              <input
                v-model="phone"
                type="tel"
                placeholder="0712345678 or 712345678"
                @input="validatePhone"
                @blur="handlePhoneBlur"
                :disabled="authStore.loading || isAutoProcessing"
                class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition disabled:opacity-50 disabled:cursor-not-allowed text-center"
                autocomplete="tel"
              />
              <div v-if="isValidPhone && !authStore.loading && !isAutoProcessing" class="absolute inset-y-0 right-3 flex items-center">
                <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <div v-if="isAutoProcessing" class="absolute inset-y-0 right-3 flex items-center">
                <svg class="animate-spin w-5 h-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Enter Kenyan number (0712345678, 712345678, or 254712345678)
            </p>
          </div>

          <!-- Password Input (Only shown if account requires password) -->
          <div v-if="showPasswordField" class="space-y-2 animate-fadeIn">
            <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">
              Account Password
              <span class="text-xs text-gray-500 dark:text-gray-400">(Required for your account)</span>
            </label>
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter your account password"
                :disabled="authStore.loading"
                class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition disabled:opacity-50 disabled:cursor-not-allowed"
                autocomplete="current-password"
                minlength="6"
                @keyup.enter="handleManualAuth"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                tabindex="-1"
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
          </div>
        </div>

        <!-- Account Status Info -->
        <div v-if="accountInfo" class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center space-x-2">
            <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span class="text-sm">
              <span v-if="accountInfo.exists && !accountInfo.requires_password">Existing account found</span>
              <span v-else-if="accountInfo.exists && accountInfo.requires_password">Password required</span>
              <span v-else>New account will be created</span>
            </span>
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ accountInfo.message }}
          </p>
          <p v-if="isAutoProcessing" class="text-xs text-blue-500 dark:text-blue-400 mt-1">
            <svg class="inline w-3 h-3 animate-spin mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing automatically...
          </p>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-3">
          <!-- Main Auth Button -->
          <button
            type="submit"
            :disabled="!canSubmit || authStore.loading || isAutoProcessing"
            class="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl active:scale-[0.98] flex items-center justify-center"
          >
            <template v-if="authStore.loading || isAutoProcessing">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="showPasswordField">Signing In...</span>
              <span v-else>Processing...</span>
            </template>
            <template v-else>
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
              </svg>
              <span v-if="showPasswordField">Sign In with Password</span>
              <span v-else>Sign In</span>
            </template>
          </button>

          <!-- Alternative Options -->
          <div v-if="showPasswordField" class="text-center">
            <button
              type="button"
              @click="forgotPassword"
              class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              Forgot Password?
            </button>
          </div>
        </div>


      </form>
    </div>

    <!-- Forgot Password Modal -->
    <ForgotPasswordModal 
      v-if="showForgotPasswordModal"
      @close="showForgotPasswordModal = false"
    />

    <!-- Connection Details Modal -->
    <ConnectionDetailsModal 
      v-if="showConnectionDetails"
      :network="networkStore"
      @close="showConnectionDetails = false"
    />


  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { api } from '@/services/api'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useNetworkStore } from '../stores/network'
import { useToast } from '../composables/useToast'
import { useHotspot } from '@/plugins/hotspot'
import { storage } from '../utils/storage'

// Components
import AuthLoader from '../components/AuthLoader.vue'
import ConnectionStatus from '../components/auth/ConnectionStatus.vue'
import AuthError from '../components/auth/AuthError.vue'
import ForgotPasswordModal from '../components/auth/ForgotPasswordModal.vue'
import ConnectionDetailsModal from '../components/network/ConnectionDetailsModal.vue'
import MaintenanceAnnouncements from '../components/auth/MaintenanceAnnouncements.vue'

// Store instances
const authStore = useAuthStore()
const networkStore = useNetworkStore()

const hotspot = useHotspot()

// Router and composables
const router = useRouter()
const { showSuccess, showError, showInfo } = useToast()

// Component state
const isCheckingCredentials = ref(true)
const phone = ref('')
const password = ref('')
const showPassword = ref(false)
const showPasswordField = ref(false)
const showForgotPasswordModal = ref(false)
const showConnectionDetails = ref(false)
const accountInfo = ref(null)
const isAutoProcessing = ref(false)
const hasCheckedAccount = ref(false)



// Computed properties
const isValidPhone = computed(() => {
  const normalized = normalizeKenyanPhone(phone.value)
  // Validate +254XXXXXXXXX format
  return /^\+254[0-9]{9}$/.test(normalized)
})

const canSubmit = computed(() => {
  if (!hotspot.ip || !hotspot.mac) return false
  if (!isValidPhone.value) return false
  if (showPasswordField.value && !password.value) return false
  return true
})

const showNetworkWarning = computed(() => {
  return false // Removed - we now block signin instead
})

// Debounced account check to prevent race conditions
let accountCheckTimeout = null

// Watch for phone changes - only check account, don't auto-submit
watch(phone, (newPhone) => {
  // Clear any pending account check
  if (accountCheckTimeout) {
    clearTimeout(accountCheckTimeout)
    accountCheckTimeout = null
  }
  
  // Check if normalized phone is valid length
  const normalized = normalizeKenyanPhone(newPhone)
  if (normalized && /^\+254[0-9]{9}$/.test(normalized)) {
    // Reset states when phone changes
    showPasswordField.value = false
    password.value = ''
    accountInfo.value = null
    hasCheckedAccount.value = false
    isAutoProcessing.value = false
    
    // Debounced account check to prevent race conditions
    accountCheckTimeout = setTimeout(() => {
      checkAccountStatus()
      accountCheckTimeout = null
    }, 500)
  } else {
    // Clear account info if phone is incomplete
    accountInfo.value = null
    showPasswordField.value = false
    hasCheckedAccount.value = false
  }
})

// Helper functions

const generateFallbackMac = () => {
  // Generate cryptographically secure random MAC with locally administered bit set
  const getRandomByte = () => {
    const array = new Uint8Array(1)
    crypto.getRandomValues(array)
    return array[0]
  }
  
  const bytes = Array.from({ length: 6 }, () => getRandomByte())
  bytes[0] = (bytes[0] & 0xFE) | 0x02 // Set locally administered bit, clear multicast bit
  
  return bytes.map(b => b.toString(16).padStart(2, '0')).join(':')
}

const generateFallbackIP = () => {
  // Generate random private IP in multiple ranges to avoid predictability
  const ranges = [
    { base: '10.0', range: 255 },
    { base: '172.16', range: 15 },
    { base: '192.168', range: 255 }
  ]
  
  const selectedRange = ranges[Math.floor(Math.random() * ranges.length)]
  const subnet = Math.floor(Math.random() * selectedRange.range)
  const host = Math.floor(Math.random() * 254) + 1
  
  return `${selectedRange.base}.${subnet}.${host}`
}

// Methods
const checkExistingCredentials = async () => {
  try {
    // Check if user has valid stored credentials
    const hasValidSession = await authStore.checkStoredSession()
    
    if (hasValidSession) {
      // Seamlessly redirect to dashboard
      router.push({ name: 'dashboard' })
      return
    }
  } catch (error) {
    console.warn('Session check failed:', error)
  } finally {
    // Always hide loader after check
    setTimeout(() => {
      isCheckingCredentials.value = false
    }, 1000) // Minimum 1 second for better UX
  }
}

const validatePhone = () => {
  // Just basic validation during typing, don't format yet
  const input = phone.value.trim()
  if (!input) return false
  
  const cleaned = input.replace(/\D/g, '')
  // Allow reasonable lengths while typing
  return cleaned.length >= 9 && cleaned.length <= 12
}

const normalizeKenyanPhone = (input) => {
  if (!input) return ''
  
  // Remove all non-digits
  const cleaned = input.replace(/\D/g, '')
  
  // Handle different input patterns
  if (cleaned.startsWith('0') && cleaned.length === 10) {
    // 0712345678 → +254712345678
    return '+254' + cleaned.substring(1)
  }
  if (cleaned.startsWith('254') && cleaned.length === 12) {
    // 254712345678 → +254712345678
    return '+' + cleaned
  }
  if (cleaned.length === 9) {
    // 712345678 → +254712345678
    return '+254' + cleaned
  }
  
  // Return original for validation to handle
  return input
}

const handlePhoneBlur = () => {
  // Normalize phone when user finishes entering (on blur)
  const normalized = normalizeKenyanPhone(phone.value)
  phone.value = normalized
  
  if (isValidPhone.value && !hasCheckedAccount.value) {
    checkAccountStatus()
  }
}

const checkAccountStatus = async () => {
  if (!isValidPhone.value) return
  
  // Block if no hotspot data
  if (!hotspot.ip || !hotspot.mac) {
    showError('Please connect to Teralinkx WiFi hotspot first')
    return
  }
  
  hasCheckedAccount.value = true
  
  try {
    const payload = {
      phone: normalizeKenyanPhone(phone.value),
      current_ip: hotspot.ip,
      current_mac: hotspot.mac
    }
    

    
    // Call backend to check account status with hotspot data
    const response = await authStore.checkAccountStatus(payload)
    
    // Update UI based on response
    accountInfo.value = {
      exists: response.exists,
      requires_password: response.requires_password,
      requires_otp: response.requires_otp,
      failed_attempts: response.failed_attempts || 0,
      account_locked: response.account_locked || false,
      message: response.message
    }
    
    // Handle account locked status
    if (response.account_locked) {
      showError('Account is temporarily locked due to too many failed login attempts. Please contact support.')
      return
    }
    
    // Only auto-signin for existing accounts WITHOUT password (desired behavior)
    if (response.exists && !response.requires_password && !response.requires_otp) {
      // Existing passwordless account - AUTO-SIGNIN
      showInfo('Welcome back! Signing you in...')
      isAutoProcessing.value = true
      
      // Delay slightly for better UX
      setTimeout(async () => {
        await performAuth(true) // Auto-signin
      }, 500)
      
    } else if (response.exists && response.requires_password) {
      // Existing account WITH password - show password field, WAIT for manual signin
      showPasswordField.value = true
      
      let message = 'Please enter your password to continue'
      if (response.failed_attempts > 0) {
        message += ` (${response.failed_attempts} failed attempts)`
      }
      showInfo(message)
      
    } else if (response.requires_otp) {
      // OTP required
      showInfo('OTP verification will be required')
      
    } else {
      // NEW ACCOUNT - show confirmation message with formatted phone
      const formattedPhone = normalizeKenyanPhone(phone.value)
      showInfo(`New account will be created for ${formattedPhone}. Click "Sign In" to continue.`)
    }
    
  } catch (error) {
    console.error('Account check error:', error)
    
    // Handle specific validation errors
    if (error.response && error.response.status === 400) {
      const errorData = error.response.data
      if (errorData.current_ip || errorData.current_mac) {
        showError('Network connection error. Please try again or contact support if issues persist.')
        return
      }
      // Show specific error message from API
      if (errorData.error) {
        showError(errorData.error)
        return
      }
    }
    
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      showError('Authentication failed. Please check your credentials.')
      return
    }
    
    // Handle server errors
    if (error.response && error.response.status >= 500) {
      showError('Server error. Please try again later.')
      return
    }
    
    accountInfo.value = {
      exists: false,
      requires_password: false,
      requires_otp: false,
      failed_attempts: 0,
      account_locked: false,
      message: `New account will be created for ${normalizeKenyanPhone(phone.value)}`
    }
    // Don't auto-signin on error
  }
}

const performAuth = async (isAuto = false) => {
  // Block if no hotspot data
  if (!hotspot.ip || !hotspot.mac) {
    showError('Please connect to Teralinkx WiFi hotspot first')
    return
  }
  
  const formattedPhone = normalizeKenyanPhone(phone.value)
  
  // Prepare authentication payload
  const payload = {
    phone: formattedPhone,
    current_mac: hotspot.mac,
    current_ip: hotspot.ip
  }
  

  
  // Only include password if required
  if (showPasswordField.value) {
    payload.password = password.value
  }
  
  try {
    // Call authentication
    authStore.loading = true
    const result = await authStore.passwordlessAuthenticate(payload)
    
    if (result.success) {
      if (result.requires_otp) {
        showSuccess('OTP sent! Please verify on dashboard')
        router.push({ 
          name: 'dashboard', 
          query: { 
            otp_required: 'true', 
            session_id: result.session_id,
            phone: formattedPhone 
          }
        })
      } else {
        const message = result.is_new_account 
          ? '🎉 Welcome to Teralinkx!' 
          : '👋 Welcome back!'
        showSuccess(message)
        
        // Check for post-login redirect
        const redirectPath = sessionStorage.getItem('postLoginRedirect')
        if (redirectPath) {
          sessionStorage.removeItem('postLoginRedirect')
          router.push(redirectPath)
        } else {
          router.push({ name: 'dashboard' })
        }
      }
    } else {
      // Handle specific error cases
      if (result.error_type === 'invalid_password') {
        // Clear password field for retry
        password.value = ''
        
        // Show specific error message with attempt count
        let errorMessage = 'Invalid password. Please try again.'
        if (result.failed_attempts && result.failed_attempts > 1) {
          errorMessage += ` (Attempt ${result.failed_attempts}/5)`
        }
        
        if (result.account_locked) {
          errorMessage = 'Account temporarily locked due to too many failed attempts. Please contact support.'
          showPasswordField.value = false // Hide password field if locked
        }
        
        showError(errorMessage)
        
        // Focus password field for retry (if not locked)
        if (!result.account_locked) {
          setTimeout(() => {
            const passwordInput = document.querySelector('input[type="password"]')
            if (passwordInput) passwordInput.focus()
          }, 100)
        }
        
      } else if (result.error_type === 'account_suspended') {
        showError(result.message || 'Account has been suspended. Please contact support.')
        showPasswordField.value = false // Hide password field
        
      } else if (result.requires_password && !showPasswordField.value) {
        showPasswordField.value = true
        showInfo('This account requires password authentication')
        
      } else {
        showError(result.message || 'Authentication failed. Please try again.')
      }
    }
    
  } catch (error) {
    console.error('Authentication error:', error)
    
    // Handle specific validation errors
    if (error.response && error.response.status === 400) {
      const errorData = error.response.data
      if (errorData.current_ip || errorData.current_mac) {
        showError('Network connection error. Please try again or contact support if issues persist.')
        return
      }
      // Show specific error message from API
      if (errorData.error) {
        showError(errorData.error)
        return
      }
    }
    
    // Handle authentication errors (401)
    if (error.response && error.response.status === 401) {
      const errorData = error.response.data
      if (errorData.code === 'AUTH_FAILED') {
        showError(errorData.error || 'Invalid credentials. Please check your phone number and password.')
      } else {
        showError('Authentication failed. Please try again.')
      }
      return
    }
    
    // Handle device conflicts (409)
    if (error.response && error.response.status === 409) {
      const errorData = error.response.data
      showError(errorData.error || 'Device conflict detected. Please contact support.')
      return
    }
    
    // Handle server errors (500+)
    if (error.response && error.response.status >= 500) {
      const errorData = error.response.data
      showError(errorData.error || 'Server error. Please try again later.')
      return
    }
    
    // Generic error
    showError(error.message || 'Authentication failed. Please try again.')
  } finally {
    authStore.loading = false
    isAutoProcessing.value = false
  }
}

const handleManualAuth = async () => {
  if (!hotspot.ip || !hotspot.mac) {
    showError('Please connect to Teralinkx WiFi hotspot first')
    return
  }
  
  if (!isValidPhone.value) {
    showError('Please enter a valid 9-digit Kenyan phone number')
    return
  }
  
  if (showPasswordField.value && !password.value) {
    showError('Password is required for this account')
    return
  }

  await performAuth(false)
}

const forgotPassword = () => {
  showForgotPasswordModal.value = true
}

const attemptAutoSignIn = async () => {
  try {
    
    const payload = {
      current_mac: hotspot.mac,
      current_ip: hotspot.ip,
      location_id: 1 // Default location must be available
    }
    
    const response = await api.post('/api/auth/device-auto/', payload)
    
    const data = response.data
    
    if (response.status === 200 && data.success) {
      
      // Store authentication data using the same format as passwordless auth
      if (data.auth) {
        // Use the same token storage as passwordless auth
        authStore.token = data.auth.access
        authStore.refreshToken = data.auth.refresh
        authStore.user = {
          id: data.user.id,
          username: data.user.username,
          email: data.user.email,
          phone: data.client.phone_number,
          client: data.client,
          device: data.device,
          session: data.session
        }
        
        // Persist to storage
        storage.set('auth_token', data.auth.access)
        storage.set('refresh_token', data.auth.refresh)
        storage.set('user', authStore.user)
        storage.set('last_activity', Date.now())
      } else {
        // Fallback for old format (backward compatibility)
        authStore.setAuthData({
          token: data.token,
          account: data.account,
          user_id: data.user_id
        })
      }
      
      showSuccess(`✨ ${data.message}`)
      
      // Navigate to dashboard
      const redirectPath = sessionStorage.getItem('postLoginRedirect')
      if (redirectPath) {
        sessionStorage.removeItem('postLoginRedirect')
        router.push(redirectPath)
      } else {
        router.push({ name: 'dashboard' })
      }
      
      return true // Auto sign-in successful
      
    } else {
      
      // Handle network validation errors
      if (response.status === 400 && (data.error?.includes('IP') || data.error?.includes('MAC'))) {
        showError('Network connection error. Please try again or contact support if issues persist.')
        return false
      }
      
      if (data.error_type === 'device_not_trusted' && data.suggested_phone) {
        // Pre-fill phone number for manual auth
        phone.value = data.suggested_phone
        showInfo('Please sign in manually to trust this device for future auto sign-in')
      }
      
      return false // Auto sign-in failed, continue with manual auth
    }
    
  } catch (error) {
    console.error('Auto sign-in error:', error)
    
    // Handle specific error responses
    if (error.response) {
      const errorData = error.response.data
      
      // Handle validation errors (400)
      if (error.response.status === 400) {
        if (errorData.error?.includes('IP') || errorData.error?.includes('MAC')) {
          console.warn('Network validation error during auto sign-in')
        } else if (errorData.code === 'BUSINESS_RULE_VIOLATION') {
          console.warn('Business rule violation:', errorData.error)
        }
        return false
      }
      
      // Handle authentication errors (401)
      if (error.response.status === 401) {
        console.warn('Auto sign-in authentication failed:', errorData.error)
        if (errorData.code === 'AUTH_FAILED') {
          // Device not trusted or credentials invalid
          return false
        }
      }
      
      // Handle device conflicts (409)
      if (error.response.status === 409) {
        console.warn('Device conflict during auto sign-in:', errorData.error)
        return false
      }
      
      // Handle server errors (500+)
      if (error.response.status >= 500) {
        console.error('Server error during auto sign-in:', errorData.error)
        return false
      }
    }
    
    return false // Auto sign-in failed, continue with manual auth
  }
}





// Lifecycle
onMounted(async () => {
  // CRITICAL: Check for valid hotspot credentials first
  if (!hotspot.ip || !hotspot.mac || 
      hotspot.ip === '192.168.88.100' || 
      hotspot.mac === '00:11:22:33:44:55') {
    console.warn('No valid hotspot credentials detected. Redirecting to login page...')
    // Clear any stored invalid credentials
    sessionStorage.removeItem('hotspotContext')
    localStorage.removeItem('hs_ip')
    localStorage.removeItem('hs_mac')
    // Redirect to login page to get fresh credentials
    window.location.href = '/login.html'
    return
  }
  
  // First check for existing credentials
  await checkExistingCredentials()
  
  // Initialize network detection (non-blocking)
  networkStore.initialize().catch(error => {
    // Continue anyway - fallback data will be used
  })
  
  // Try auto sign-in first (before manual auth)
  if (hotspot.mac && hotspot.ip) {
    const autoAuthResult = await attemptAutoSignIn()
    if (autoAuthResult) {
      // Auto sign-in successful, exit early
      return
    }
  }
  
  // Check existing session and handle redirect reasons
  if (authStore.isAuthenticated) {
    router.push({ name: 'dashboard' })
  } else {
    // Check for session expiry or logout reasons
    const urlParams = new URLSearchParams(window.location.search)
    const reason = urlParams.get('reason')
    const redirectPath = urlParams.get('redirect')
    
    if (reason) {
      // Show user-friendly message about why they need to sign in again
      setTimeout(() => {
        if (reason.includes('expired')) {
          showInfo('Your session has expired. Please sign in again to continue.')
        } else if (reason.includes('authentication')) {
          showError('Authentication error occurred. Please sign in again.')
        } else {
          showInfo(`${reason}. Please sign in to continue.`)
        }
        
        // Store redirect path for after successful login
        if (redirectPath && redirectPath !== '/') {
          sessionStorage.setItem('postLoginRedirect', redirectPath)
        }
      }, 500)
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }

})

onUnmounted(() => {
  // Clean up timeout if component unmounts
  if (accountCheckTimeout) {
    clearTimeout(accountCheckTimeout)
    accountCheckTimeout = null
  }

})
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}

/* Focus styles */
input:focus {
  outline: none;
  ring: 2px;
}
</style>