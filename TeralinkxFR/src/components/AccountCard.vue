<template>
  <div class="sm:max-w-md md:max-w-lg lg:max-w-xl mx-auto px-2 mt-1  text-text-light dark:bg-gray-900 dark:text-text-dark transition-colors duration-300">
    <AlertBanner />
    <!-- Greeting -->
    <div class="text-center mb-2 flex justify-center items-center space-x-2">
      <span class="text-2xl">{{ greetingIcon }}</span>
      <h1 class="text-cyan-600 text-md">{{ greeting }} {{ accountStore.client }}</h1>
    </div>

    <!-- Account Card -->
    <div class="w-full max-w-md mx-auto p-2 bg-card-light dark:bg-card-dark  dark:bg-gray-900  dark:shadow-gray-700 text-text-light dark:text-text-dark rounded-lg shadow space-y-2 transition-all duration-300">
      <!-- Header: Profile + Info -->
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <img
            :src="accountStore.userImage"
            alt="User"
            class="w-12 h-12 rounded-full object-cover"
          />
          
          <div>
            <p class="text-3xs text-gray-500 dark:text-gray-400 uppercase">Account</p>
            <p class="text-xs font-bold text-gray-800 dark:text-white">{{ accountStore.account }}</p>
            <p class="text-3xs text-gray-500 dark:text-gray-400 uppercase">Balance</p>
            <p class="text-xs font-semibold text-green-700 dark:text-green-400">KES {{ accountStore.balance }}</p>
          </div>
        </div>

        <!-- Logout Icon -->
        <button @click="logout()" title="Logout">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H6a2 2 0 01-2-2V7a2 2 0 012-2h5a2 2 0 012 2v1" />
          </svg>
        </button>
      </div>

      <!-- Divider -->
      <hr class="border-t border-gray-300 dark:border-gray-600" />

      <!-- Status -->
      <div class="flex items-center justify-start text-sm text-gray-600 dark:text-gray-300">
        <svg
          class="h-4 w-4 mr-1"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
          :class="isOnline ? 'text-green-500' : 'text-red-500'"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            v-if="isOnline"
            d="M8.53 16.11a6 6 0 016.94 0M5.1 12.69a10 10 0 0113.8 0M1.67 9.28a14 14 0 0120.66 0M12 20h.01"
          />
          <g v-else>
            <path d="M1 1l22 22" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M16.72 11.06a10 10 0 00-9.44 0" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M5.88 14.12a6 6 0 016.94 0" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M12 20h.01" stroke-linecap="round" stroke-linejoin="round" />
          </g>
        </svg>

        <span class="text-2xs">
          Internet status:
          <span :class="isOnline ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-500'" class="font-semibold text-2xs">
            {{ accountStore.status }}
          </span>
        </span>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAccountStore } from '@/stores/useAccountStore'
import { useCsrfTokenStore } from '@/stores/useCsrf'
import AlertBanner from './AlertBanner.vue';

const accountStore = useAccountStore()

const greeting = ref('')
const greetingIcon = ref('')

const isOnline = ref(false)

function checkInternetStatus() {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 3000) // 3s timeout

  fetch('https://www.google.com/favicon.ico', { signal: controller.signal, mode: 'no-cors' })
    .then(() => {
      isOnline.value = true
      accountStore.status = 'Online'
    })
    .catch(() => {
      isOnline.value = false
      accountStore.status = 'Offline'
    })
    .finally(() => clearTimeout(timeoutId))
}


function setGreeting() {
  const now = new Date()
  const hours = now.getHours()

  if (hours < 12) {
    greeting.value = 'Good morning'
    greetingIcon.value = '🌞'
  } else if (hours < 18) {
    greeting.value = 'Good afternoon'
    greetingIcon.value = '☀️'
  } else if (hours < 22) {
    greeting.value = 'Good evening'
    greetingIcon.value = '🌆'
  } else {
    greeting.value = 'Good night'
    greetingIcon.value = '🌙'
  }
}

const logout = async () => {
  const token = localStorage.getItem('authToken')
  const boundMac = sessionStorage.getItem('hs_mac') || localStorage.getItem('hs_mac')
  const boundIp = sessionStorage.getItem('hs_ip') || localStorage.getItem('hs_ip')

  if (!boundMac || !boundIp) {
    console.error('IP or MAC address not found')
    return
  }

  const csrfStore = useCsrfTokenStore()
  await csrfStore.fetchCsrf()

  const payload = {
    bound_mac: boundMac,
    bound_ip: boundIp
  }

  try {
    const disconnect = () =>
      axios.post(`${import.meta.env.VITE_API_PROD_URL}/api/disconnect/`, payload, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfStore.csrfToken,
          Authorization: `Token ${token}`
        }
      })

    const revokeToken = () =>
      axios.post(`${import.meta.env.VITE_API_PROD_URL}/api/logout/`, {}, {
        headers: {
          Authorization: `Token ${token}`
        }
      })

    await Promise.allSettled([disconnect(), revokeToken()])

    localStorage.clear()
    sessionStorage.clear()
    window.location.href = '/'
  } catch (error) {
    console.error('Logout error:', error)
    localStorage.clear()
    sessionStorage.clear()
    window.location.href = '/'
  }
}




onMounted(() => {
  setGreeting()
  accountStore.fetchAccountInfo()
  checkInternetStatus()
  setInterval(checkInternetStatus, 10000)
})
</script>

<style scoped>
/* Optional custom styles */
</style>
