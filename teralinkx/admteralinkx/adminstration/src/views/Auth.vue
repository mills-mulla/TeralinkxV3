<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-end relative overflow-hidden">

    <!-- 3D Globe background -->
    <GlobeBackground class="absolute inset-0 w-full h-full" />

    <!-- Right side darkening behind card -->
    <div class="absolute inset-y-0 right-0 w-80 pointer-events-none" style="background: linear-gradient(to left, rgba(2,6,23,0.92) 60%, transparent 100%);"></div>


    <!-- Login card — pinned to right -->
    <div class="relative z-10 w-full max-w-sm mr-12 login-card">
      <div class="bg-slate-900/80 backdrop-blur-xl border border-slate-700/60 rounded-2xl shadow-2xl p-8">

        <!-- Logo + brand -->
        <div class="text-center mb-7">
          <img src="../assets/logo/teralinkx2.png" alt="TeralinkX" class="w-16 h-16 mx-auto mb-3 drop-shadow-[0_0_12px_rgba(59,130,246,0.6)]" />
          <h1 class="text-xl font-bold text-white tracking-wide">TeralinkX</h1>
          <p class="text-cyan-400 text-xs font-medium tracking-widest uppercase mt-0.5">Admin Console</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="relative">
            <UserIcon class="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input v-model="loginForm.username" type="text" required placeholder="Username"
              :class="['w-full pl-9 pr-3 py-2.5 text-sm bg-slate-800/80 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all', formErrors.username ? 'border-red-500' : 'border-slate-700']"
              @input="clearError('username')" />
          </div>
          <div class="relative">
            <LockClosedIcon class="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input v-model="loginForm.password" :type="showPassword ? 'text' : 'password'" required placeholder="Password"
              :class="['w-full pl-9 pr-9 py-2.5 text-sm bg-slate-800/80 border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all', formErrors.password ? 'border-red-500' : 'border-slate-700']"
              @input="clearError('password')" />
            <button type="button" @click="showPassword=!showPassword" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors">
              <EyeIcon v-if="showPassword" class="w-4 h-4" />
              <EyeSlashIcon v-else class="w-4 h-4" />
            </button>
          </div>

          <!-- Inline error -->
          <div v-if="showError" class="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">
            <ExclamationTriangleIcon class="w-4 h-4 text-red-400 shrink-0" />
            <p class="text-xs text-red-400">{{ errorMessage }}</p>
          </div>

          <button type="submit" :disabled="loading"
            class="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 mt-2">
            <div v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span>{{ loading ? 'Authenticating...' : 'Sign In' }}</span>
            <ArrowRightIcon v-if="!loading" class="w-4 h-4" />
          </button>
        </form>

        <p class="text-center text-[10px] text-slate-600 mt-6">Authorized personnel only &bull; All access is logged</p>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import GlobeBackground from '../components/GlobeBackground.vue'
import {
  ShieldCheckIcon,
  UserIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
  ArrowRightIcon,
  ExclamationCircleIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'

export default {
  name: 'Auth',
  components: {
    GlobeBackground,
    ShieldCheckIcon,
    UserIcon,
    LockClosedIcon,
    EyeIcon,
    EyeSlashIcon,
    ArrowRightIcon,
    ExclamationCircleIcon,
    ExclamationTriangleIcon,
    XMarkIcon,
  },
  emits: ['login-success'],
  setup(props, { emit }) {
    // Reactive data
    const loading = ref(false)
    const showPassword = ref(false)
    const showError = ref(false)
    const errorMessage = ref('')
    
    const loginForm = reactive({
      username: '',
      password: '',
    })
    
    const formErrors = reactive({
      username: '',
      password: ''
    })

    // Methods
    const clearError = (field) => {
      if (formErrors[field]) {
        formErrors[field] = ''
      }
    }

    const validateForm = () => {
      let valid = true
      formErrors.username = ''
      formErrors.password = ''

      if (!loginForm.username.trim()) {
        formErrors.username = 'Admin username is required'
        valid = false
      }

      if (!loginForm.password) {
        formErrors.password = 'Password is required'
        valid = false
      }

      return valid
    }

    // JWT Authentication with comprehensive fallback
    const handleLogin = async () => {
      if (!validateForm()) return

      loading.value = true
      showError.value = false

      try {
        console.log('🚀 Starting JWT authentication...')

        // Use dynamic fallback: try primary first, then fallback
        const PRIMARY_URL = 'https://srv.teralinkxwaves.uk'
        const FALLBACK_URL = 'https://accounts.teralinkxwaves.uk'
        
        let response
        let usedFallback = false
        let primaryError = null
        
        try {
          console.log('📡 Trying primary:', PRIMARY_URL)
          
          // Create abort controller for timeout
          const controller = new AbortController()
          const timeoutId = setTimeout(() => controller.abort(), 5000)
          
          response = await fetch(`${PRIMARY_URL}/suapi/auth/login/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: loginForm.username,
              password: loginForm.password,
            }),
            signal: controller.signal,
          })
          
          clearTimeout(timeoutId)
          
          // Trigger fallback on ANY error response (4xx, 5xx) or network issues
          if (!response.ok) {
            primaryError = `HTTP ${response.status}`
            throw new Error(primaryError)
          }
        } catch (error) {
          console.warn('⚠️ Primary failed:', error.message || error.name)
          console.log('🔄 Trying fallback:', FALLBACK_URL)
          usedFallback = true
          primaryError = error
          
          try {
            response = await fetch(`${FALLBACK_URL}/suapi/auth/login/`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                username: loginForm.username,
                password: loginForm.password,
              }),
            })
          } catch (fallbackError) {
            console.error('❌ Fallback also failed:', fallbackError.message)
            throw new Error('Both primary and fallback servers are unreachable')
          }
        }

        console.log(`📨 Login response status: ${response.status} (via ${usedFallback ? 'fallback' : 'primary'})`)
        
        const data = await response.json()
        console.log('📊 Login response data:', data)

        if (response.ok && data.success) {
          console.log('✅ JWT Login successful')
          
          // Extract tokens and user data
          const { tokens, user } = data
          
          if (tokens && tokens.access && tokens.refresh) {
            // Emit success event to App.vue with token data
            emit('login-success', {
              access: tokens.access,
              refresh: tokens.refresh,
              user: user
            })
            
            console.log('🎉 Login successful, tokens emitted to App.vue')
          } else {
            throw new Error('No tokens received from server')
          }
          
        } else {
          throw new Error(data.message || 'Authentication failed')
        }
        
      } catch (error) {
        console.error('❌ Authentication error:', error)
        
        // Enhanced error messages
        let userMessage = error.message
        if (error.name === 'AbortError') {
          userMessage = 'Connection timeout. Please check your network and try again.'
        } else if (error.message.includes('Network') || error.message.includes('Failed to fetch')) {
          userMessage = 'Network error. Please check your connection and try again.'
        } else if (error.message.includes('unreachable')) {
          userMessage = 'Unable to connect to authentication servers. Please try again later.'
        }
        
        showError.value = true
        errorMessage.value = userMessage
        
        setTimeout(() => {
          showError.value = false
        }, 5000)
      } finally {
        loading.value = false
      }
    }

    const features = [
      { icon: '📊', label: 'Real-time Analytics', desc: 'Live revenue, sessions and client metrics' },
      { icon: '👥', label: 'Client Management', desc: 'Full CRUD with voucher and device tracking' },
      { icon: '💰', label: 'Finance Intelligence', desc: 'MRR, churn, cash position and KPI trends' },
      { icon: '🛡️', label: 'HIDS Security', desc: 'Suricata + Zeek threat detection' },
    ]

    return {
      loading,
      showPassword,
      showError,
      errorMessage,
      loginForm,
      formErrors,
      features,
      clearError,
      handleLogin,
    }
  }
}
</script>

<style scoped>
.login-card {
  animation: cardIn 0.6s ease-out forwards;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-fade-in { animation: fade-in 0.3s ease-out; }
</style>