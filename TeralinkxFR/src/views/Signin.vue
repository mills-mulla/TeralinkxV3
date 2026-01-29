<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-white to-blue-50 dark:from-gray-900 dark:to-gray-800 px-4">
    <!-- Developer Tools Toggle -->
    <div class="absolute top-4 right-4">
      <button
        @click="toggleDevTools"
        class="p-2 bg-gray-800 dark:bg-gray-700 text-white rounded-lg text-xs font-mono hover:bg-gray-900 transition-all shadow-md"
        title="Toggle Developer Tools (Shift+D)"
      >
        <span v-if="!devStore.showDevTools">DEV</span>
        <span v-else class="text-green-400">● DEV</span>
      </button>
    </div>

    <!-- Main Auth Card -->
    <div class="w-full max-w-md bg-white dark:bg-gray-900 shadow-2xl rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700">
      <!-- Logo Header -->
      <div class=" dark:from-blue-800 dark:to-blue-900 p-2 flex justify-center">
        <div class="text-center">
          <img src="../assets/teralinkx2.png" alt="Teralinkx Waves" class="h-60 " />
          <h6 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Sign In</h6>
          <p class="text-black-100 text-sm mt-2">High-Speed Internet Access</p>
        </div>
      </div>

      <!-- Auth Form -->
      <form @submit.prevent="handleManualAuth" class="p-6 space-y-6">
        <!-- Connection Status -->
        <ConnectionStatus 
          :ip="networkStore.ip"
          :mac="networkStore.mac"
          :source="networkStore.source"
          :isConnected="networkStore.isConnected"
          @simulate="simulateNetworkData"
          @test="testBackend"
        />

        <!-- Error Display -->
        <AuthError 
          v-if="authStore.error"
          :error="authStore.error"
          @clear="authStore.clearError()"
        />

        <!-- Network Warning (shown when using fallback data) -->
        <div v-if="showNetworkWarning" class="p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
          <div class="flex items-start space-x-2">
            <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.346 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            <div class="text-sm text-yellow-700 dark:text-yellow-300">
              <p class="font-medium">Using fallback network data</p>
              <p class="text-xs mt-1">You can still proceed with authentication.</p>
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
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span class="text-gray-500 dark:text-gray-400">+254</span>
              </div>
              <input
                v-model="phone"
                type="tel"
                placeholder="712345678"
                @input="validatePhone"
                @blur="handlePhoneBlur"
                :disabled="authStore.loading || isAutoProcessing"
                class="w-full pl-14 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition disabled:opacity-50 disabled:cursor-not-allowed"
                maxlength="9"
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
              Enter your 9-digit Kenyan number
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

        <!-- Test Authentication (Dev Only) -->
        <DevAuthTools v-if="devStore.showDevTools" @test="handleTestAuth" />
      </form>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50">
        <p class="text-center text-xs text-gray-500 dark:text-gray-400">
          © {{ new Date().getFullYear() }} Teralinkx Waves. All rights reserved.
        </p>
        <p v-if="devStore.showDevTools" class="text-center text-xs text-gray-500 dark:text-gray-400 mt-1">
          v{{ appVersion }} | Env: {{ envName }}
        </p>
      </div>
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

    <!-- Developer Console -->
    <DevConsole v-if="devStore.showConsole" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useNetworkStore } from '../stores/network'
import { useDevStore } from '../stores/dev'
import { useToast } from '../composables/useToast'

// Components
import ConnectionStatus from '../components/auth/ConnectionStatus.vue'
import AuthError from '../components/auth/AuthError.vue'
import DevAuthTools from '../components/dev/DevAuthTools.vue'
import ForgotPasswordModal from '../components/auth/ForgotPasswordModal.vue'
import ConnectionDetailsModal from '../components/network/ConnectionDetailsModal.vue'
import DevConsole from '../components/dev/DevConsole.vue'

// Store instances
const authStore = useAuthStore()
const networkStore = useNetworkStore()
const devStore = useDevStore()

// Router and composables
const router = useRouter()
const { showSuccess, showError, showInfo } = useToast()

// Component state
const phone = ref('')
const password = ref('')
const showPassword = ref(false)
const showPasswordField = ref(false)
const showForgotPasswordModal = ref(false)
const showConnectionDetails = ref(false)
const accountInfo = ref(null)
const isAutoProcessing = ref(false)
const hasCheckedAccount = ref(false)

const appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0'
const envName = import.meta.env.VITE_ENV_NAME || 'development'
const isDevelopment = import.meta.env.DEV || envName === 'development'

// Computed properties
const isValidPhone = computed(() => {
  const cleaned = phone.value.replace(/\D/g, '')
  return cleaned.length === 9
})

const canSubmit = computed(() => {
  if (!isValidPhone.value) return false
  if (showPasswordField.value && !password.value) return false
  return true
})

const showNetworkWarning = computed(() => {
  return networkStore.source === 'detection_failed' || 
         networkStore.source === 'fallback' ||
         (!networkStore.ip && !networkStore.mac)
})

// Watch for phone changes - only check account, don't auto-submit
watch(phone, (newPhone) => {
  if (newPhone.length === 9) {
    // Reset states when phone changes
    showPasswordField.value = false
    password.value = ''
    accountInfo.value = null
    hasCheckedAccount.value = false
    isAutoProcessing.value = false
    
    // Auto-check account after brief delay
    setTimeout(() => {
      checkAccountStatus()
    }, 300)
  } else {
    // Clear account info if phone is incomplete
    accountInfo.value = null
    showPasswordField.value = false
    hasCheckedAccount.value = false
  }
})

// Helper functions
const generateFallbackMac = () => {
  const randomHex = () => Math.floor(Math.random() * 256).toString(16).padStart(2, '0')
  return `02:00:00:${randomHex()}:${randomHex()}:${randomHex()}`
}

const generateFallbackIP = () => {
  return `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255) + 1}`
}

// Methods
const validatePhone = () => {
  phone.value = phone.value.replace(/\D/g, '').slice(0, 9)
}

const handlePhoneBlur = () => {
  if (isValidPhone.value && !hasCheckedAccount.value) {
    checkAccountStatus()
  }
}

const toggleDevTools = () => {
  devStore.toggleDevTools()
  if (devStore.showDevTools) {
    showSuccess('Developer tools enabled')
  }
}

const simulateNetworkData = () => {
  networkStore.simulateData()
  showSuccess('Network data simulated')
}

const testBackend = async () => {
  try {
    await networkStore.testConnection()
    showSuccess('Backend connection successful')
  } catch (error) {
    showError('Backend connection failed')
  }
}

const checkAccountStatus = async () => {
  if (!isValidPhone.value) return
  
  hasCheckedAccount.value = true
  
  try {
    // Call backend to check account status with fallback data
    const response = await authStore.checkAccountStatus({
      phone: `254${phone.value}`,
      current_ip: networkStore.ip || generateFallbackIP(),
      current_mac: networkStore.mac || generateFallbackMac()
    })
    
    // Update UI based on response
    accountInfo.value = {
      exists: response.exists,
      requires_password: response.requires_password,
      requires_otp: response.requires_otp,
      message: response.message
    }
    
    console.log('Account check result:', response)
    
    // If account exists and doesn't require password, auto-signin
    if (response.exists && !response.requires_password && !response.requires_otp) {
      // Auto-signin for passwordless accounts
      console.log('Auto-signin for passwordless account')
      isAutoProcessing.value = true
      await performAuth() // This will auto-signin
    } else if (response.exists && response.requires_password) {
      // Show password field for accounts with passwords
      showPasswordField.value = true
      showInfo('This account requires password authentication')
    } else if (response.requires_otp) {
      // Handle OTP accounts
      showInfo('OTP verification required')
    }
    // For new accounts (response.exists === false), user must click Sign In
    
  } catch (error) {
    console.log('Account check failed:', error.message)
    accountInfo.value = {
      exists: false,
      requires_password: false,
      requires_otp: false,
      message: 'New account will be created'
    }
  }
}

const performAuth = async (isAuto = false) => {
  const formattedPhone = `254${phone.value}`
  
  // Prepare authentication payload with fallback data
  const payload = {
    phone: formattedPhone,
    current_mac: networkStore.mac || generateFallbackMac(),
    current_ip: networkStore.ip || generateFallbackIP(),
    device_info: navigator.userAgent,
    timestamp: new Date().toISOString()
  }
  
  // Only include password if required
  if (showPasswordField.value) {
    payload.password = password.value
  }
  
  console.log('🔐 Auth payload:', payload)
  
  try {
    // Call authentication
    authStore.loading = true
    const result = await authStore.passwordlessAuthenticate(payload)
    console.log('📊 Auth result:', result)
    
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
        // Ensure we actually navigate to dashboard
        console.log('Redirecting to dashboard...')
        router.push({ name: 'dashboard' })
      }
    } else {
      // Handle specific error cases
      if (result.requires_password && !showPasswordField.value) {
        showPasswordField.value = true
        showInfo('This account requires password authentication')
      } else {
        showError(result.message || 'Authentication failed')
      }
    }
    
  } catch (error) {
    console.error('❌ Auth error:', error)
    showError(error.message || 'Authentication failed. Please try again.')
  } finally {
    authStore.loading = false
    isAutoProcessing.value = false
  }
}

const handleManualAuth = async () => {
  console.log('✅ Manual sign in clicked - Phone:', phone.value)
  
  if (!isValidPhone.value) {
    showError('Please enter a valid 9-digit Kenyan phone number')
    return
  }
  
  if (showPasswordField.value && !password.value) {
    showError('Password is required for this account')
    return
  }

  // Development mode: bypass network check
  const shouldCheckNetwork = !isDevelopment
  
  if (shouldCheckNetwork && !networkStore.isConnected) {
    showError('Please connect to Teralinkx WiFi first')
    console.log('Not connected to WiFi')
    return
  }

  await performAuth(false)
}

const forgotPassword = () => {
  showForgotPasswordModal.value = true
}

const handleTestAuth = (type) => {
  if (type === 'success') {
    phone.value = '712345678'
    showSuccess('Test phone loaded')
    
    // Simulate account check
    setTimeout(() => {
      accountInfo.value = {
        exists: true,
        requires_password: false,
        requires_otp: false,
        message: 'Test account ready for passwordless login'
      }
      // Auto-signin for test
      isAutoProcessing.value = true
      setTimeout(() => {
        performAuth(true)
      }, 500)
    }, 500)
  } else {
    authStore.setError('Test authentication error')
  }
}

// Setup dev shortcuts handler
let devKeyHandler = null

// Lifecycle
onMounted(() => {
  // Initialize network detection (non-blocking)
  networkStore.initialize().catch(error => {
    console.warn('Network initialization warning:', error.message)
    // Continue anyway - fallback data will be used
  })
  
  // Check existing session
  if (authStore.isAuthenticated) {
    console.log('User already authenticated, redirecting to dashboard')
    router.push({ name: 'dashboard' })
  }
  
  // Setup dev shortcuts
  devKeyHandler = (e) => {
    if (e.shiftKey && e.key === 'D') {
      toggleDevTools()
    }
    if (e.shiftKey && e.key === 'C' && devStore.showDevTools) {
      showConnectionDetails.value = !showConnectionDetails.value
    }
  }
  
  window.addEventListener('keydown', devKeyHandler)
})

onUnmounted(() => {
  if (devKeyHandler) {
    window.removeEventListener('keydown', devKeyHandler)
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