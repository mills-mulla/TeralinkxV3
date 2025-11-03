<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <!-- Background Decoration (keep your existing styles) -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
      <div class="absolute top-40 left-40 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
    </div>

    <!-- Main Login Card -->
    <div class="relative w-full max-w-md">
      <div class="bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 p-8">
        <!-- Header (keep your existing header) -->
        <div class="text-center mb-8">
          <div class="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <ShieldCheckIcon class="w-10 h-10 text-white" />
          </div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">
            Admin Access
          </h1>
          <p class="text-slate-600 font-light">Authorized personnel only</p>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username Field -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2 flex items-center">
              <UserIcon class="w-4 h-4 mr-2" />
              Admin Username
            </label>
            <div class="relative">
              <input
                v-model="loginForm.username"
                type="text"
                required
                placeholder="Enter admin username"
                :class="[
                  'w-full px-4 py-3 pl-11 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 bg-white/50 backdrop-blur-sm',
                  formErrors.username ? 'border-rose-500' : 'border-slate-300'
                ]"
                @input="clearError('username')"
              />
              <UserIcon class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            </div>
            <p v-if="formErrors.username" class="text-rose-600 text-xs mt-2 flex items-center">
              <ExclamationCircleIcon class="w-4 h-4 mr-1" />
              {{ formErrors.username }}
            </p>
          </div>

          <!-- Password Field -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2 flex items-center">
              <LockClosedIcon class="w-4 h-4 mr-2" />
              Password
            </label>
            <div class="relative">
              <input
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="Enter your password"
                :class="[
                  'w-full px-4 py-3 pl-11 pr-11 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 bg-white/50 backdrop-blur-sm',
                  formErrors.password ? 'border-rose-500' : 'border-slate-300'
                ]"
                @input="clearError('password')"
              />
              <LockClosedIcon class="w-5 h-5 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors duration-200"
              >
                <EyeIcon v-if="showPassword" class="w-5 h-5" />
                <EyeSlashIcon v-else class="w-5 h-5" />
              </button>
            </div>
            <p v-if="formErrors.password" class="text-rose-600 text-xs mt-2 flex items-center">
              <ExclamationCircleIcon class="w-4 h-4 mr-1" />
              {{ formErrors.password }}
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            :class="[
              'w-full py-4 px-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transform transition-all duration-300 flex items-center justify-center space-x-2',
              loading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'
            ]"
          >
            <div v-if="loading" class="flex items-center space-x-2">
              <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              <span>Authenticating...</span>
            </div>
            <div v-else class="flex items-center space-x-2">
              <ArrowRightIcon class="w-5 h-5" />
              <span>Access Dashboard</span>
            </div>
          </button>
        </form>
      </div>
    </div>

    <!-- Error Toast -->
    <div v-if="showError" class="fixed top-4 right-4 z-50">
      <div class="bg-rose-500 text-white px-6 py-4 rounded-xl shadow-lg flex items-center space-x-3 animate-fade-in">
        <ExclamationTriangleIcon class="w-5 h-5" />
        <div>
          <p class="font-medium">Authentication Failed</p>
          <p class="text-sm opacity-90">{{ errorMessage }}</p>
        </div>
        <button @click="showError = false" class="text-white/80 hover:text-white">
          <XMarkIcon class="w-5 h-5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
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

    // JWT Authentication
    const handleLogin = async () => {
      if (!validateForm()) return

      loading.value = true
      showError.value = false

      try {
        console.log('🚀 Starting JWT authentication...')

        const response = await fetch('https://service.teralinkxwaves.uk/suapi/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: loginForm.username,
            password: loginForm.password,
          }),
        })

        console.log('📨 Login response status:', response.status)
        
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
        if (error.message.includes('Network') || error.message.includes('Fetch')) {
          userMessage = 'Network error. Please check your connection and try again.'
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

    return {
      loading,
      showPassword,
      showError,
      errorMessage,
      loginForm,
      formErrors,
      clearError,
      handleLogin,
    }
  }
}
</script>

<style scoped>
/* Keep your existing styles */
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>