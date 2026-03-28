<template>
  <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
  <div class="min-h-screen pt-20 flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 px-4">
    <!-- Modal Container -->
    <div class="w-full max-w-md bg-white dark:bg-gray-900 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <!-- Header -->
      <div class="bg-white dark:bg-gray-900 p-6 text-center">
        <div class="mb-4">
          <img src="@/assets/teralinkx2.png" alt="TeralinkX" class="h-60 w-auto mx-auto drop-shadow-lg" />
        </div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Enter Voucher Code</h1>
        <p class="text-gray-600 dark:text-gray-300 text-sm">Connect using your active package voucher</p>
      </div>

      <!-- Form Content -->
      <div class="p-6">
        <!-- Info Message -->
        <div v-if="!error" class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div class="flex items-start space-x-3">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div class="text-sm text-blue-700 dark:text-blue-300">
              <p class="font-medium mb-1">Manual Connection</p>
              <p>If not automatically connected, enter your voucher code from your active package list.</p>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div class="flex items-start space-x-3">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div class="text-sm text-red-700 dark:text-red-300">
              <p class="font-medium">Connection Error</p>
              <p>{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Voucher Form -->
        <form @submit.prevent="login" class="space-y-6">
          <!-- Voucher Input -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-900 dark:text-gray-100">
              <svg class="inline w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
              </svg>
              Voucher Code
            </label>
            <div class="relative">
              <input
                v-model="voucherCode"
                type="text"
                placeholder="Enter your voucher code"
                class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition disabled:opacity-50 disabled:cursor-not-allowed pl-12"
                :disabled="loading"
                required
              />
              <div class="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Find your voucher code in the active packages section
            </p>
          </div>

          <!-- Connect Button -->
          <button
            type="submit"
            :disabled="!voucherCode.trim() || loading"
            class="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl active:scale-[0.98] flex items-center justify-center"
          >
            <template v-if="loading">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Connecting...
            </template>
            <template v-else>
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              Connect Now
            </template>
          </button>
        </form>

        <!-- Help Section -->
        <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div class="text-center">
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Need help?</p>
            <button type="button" class="text-sm text-blue-600 dark:text-blue-400 hover:underline">
              View Active Packages
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '@/services/api'
import { useCsrfTokenStore } from '@/stores/useCsrf' 
import NavBar from '@/components/NavBar.vue'

const voucherCode = ref('')
const error = ref('')
const loading = ref(false)
const csrfStore = useCsrfTokenStore()

async function login() {
  if (!voucherCode.value.trim()) return
  
  loading.value = true
  error.value = ''
  
  try {
    const payload = {
      account: localStorage.getItem('account'),
      voucher_code: voucherCode.value,
      bound_mac: localStorage.getItem('mac_addr'),
    }

    const res = await api.post('/api/connect/', payload)

    if (res.status === 200) {
      window.location.href = '#/connected'
    } else {
      error.value = res.data.answer || res.data.error || 'Connection failed'
    }
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Connection failed'
  } finally {
    loading.value = false
  }
}
</script>


<style>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10%); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fadeIn {
  animation: fadeIn 0.8s ease-in-out forwards;
}
</style>
