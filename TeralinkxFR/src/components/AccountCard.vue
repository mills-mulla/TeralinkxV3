<template>
  <div class="sm:max-w-md md:max-w-lg lg:max-w-xl mx-auto px-2 mt-1 text-text-light dark:text-text-dark transition-colors duration-300">
    <AlertBanner />
    
    <!-- Greeting Section -->
    <div class="text-center mb-4">
      <div class="inline-flex items-center space-x-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 px-6 py-3 rounded-md border border-blue-100 dark:border-gray-600">
        <div class="text-3xl animate-pulse">{{ greetingIcon }}</div>
        <div>
          <h1 class="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
            {{ greeting }}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-300 font-medium">{{ dashboardStore.clientName || dashboardStore.account }}</p>
        </div>
      </div>
    </div>

    <!-- Account Card -->
    <div class="w-full max-w-md mx-auto p-2 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 backdrop-blur-sm shadow-lg text-text-light dark:text-text-dark rounded-lg space-y-2 transition-all duration-300 border border-blue-100 dark:border-gray-600 transform hover:scale-[1.02] hover:shadow-xl">
      <!-- Loading State -->
      <div v-if="dashboardStore.loading" class="animate-pulse">
        <div class="flex items-center space-x-3">
          <div class="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-full animate-pulse"></div>
          <div class="space-y-2">
            <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-24 animate-pulse"></div>
            <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-32 animate-pulse"></div>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div v-else class="animate-fade-in-content">
        <!-- Header: Profile + Info -->
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <img
              :src="userImage"
              alt="User"
              class="w-12 h-12 rounded-full object-cover transition-transform duration-300 hover:scale-110 hover:rotate-3"
            />
            
            <div class="space-y-1">
              <p class="text-3xs text-gray-500 dark:text-gray-400 uppercase transition-colors duration-300">Account</p>
              <p class="text-xs font-bold text-gray-800 dark:text-white transition-all duration-300 hover:text-blue-600 dark:hover:text-blue-400">
                {{ dashboardStore.account }}
                <span v-if="dashboardStore.phoneNumber" class="text-2xs text-gray-500 dark:text-gray-400">
                  [{{ dashboardStore.phoneNumber }}]
                </span>
              </p>
              <p class="text-3xs text-gray-500 dark:text-gray-400 uppercase transition-colors duration-300">Balance</p>
              <p class="text-xs font-semibold transition-all duration-300 hover:scale-105" :class="balanceColorClass">KES {{ dashboardStore.balance.toFixed(2) }}</p>
            </div>
          </div>

          <!-- Logout Icon -->
          <button @click="logout" title="Logout" class="group transition-all duration-300 hover:scale-110 hover:rotate-12">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-600 transition-all duration-300 group-hover:drop-shadow-lg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H6a2 2 0 01-2-2V7a2 2 0 012-2h5a2 2 0 012 2v1" />
            </svg>
          </button>
        </div>

        <!-- Divider -->
        <hr class="border-t border-gray-300 dark:border-gray-600 transition-colors duration-300" />

        <!-- Status Section -->
        <div class="flex items-center justify-center space-x-4">
          <!-- Internet Status -->
          <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 group transition-all duration-300 hover:scale-105">
            <svg
              class="h-4 w-4 mr-1 transition-all duration-300 group-hover:scale-110"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
              :class="internetStatusColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                v-if="dashboardStore.isOnline"
                d="M8.53 16.11a6 6 0 016.94 0M5.1 12.69a10 10 0 0113.8 0M1.67 9.28a14 14 0 0120.66 0M12 20h.01"
              />
              <g v-else>
                <path d="M1 1l22 22" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M16.72 11.06a10 10 0 00-9.44 0" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M5.88 14.12a6 6 0 016.94 0" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M12 20h.01" stroke-linecap="round" stroke-linejoin="round" />
              </g>
            </svg>
            <span class="text-2xs transition-colors duration-300">
              Internet:
              <span :class="dashboardStore.isOnline ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-500'" class="font-semibold text-2xs transition-all duration-300">
                {{ dashboardStore.isOnline ? 'Online' : 'Offline' }}
              </span>
            </span>
          </div>

          <!-- Account Status -->
          <div class="flex items-center text-sm text-gray-600 dark:text-gray-300 group transition-all duration-300 hover:scale-105">
            <svg
              class="h-4 w-4 mr-1 transition-all duration-300 group-hover:scale-110"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
              :class="accountStatusColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                v-if="dashboardStore.status === 'active'"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span class="text-2xs transition-colors duration-300">
              Account:
              <span :class="accountStatusTextColor" class="font-semibold text-2xs capitalize transition-all duration-300">
                {{ dashboardStore.status }}
              </span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import AlertBanner from './AlertBanner.vue'
import defaultAvatar from '@/assets/avatar2.png'

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()

const greeting = ref('')
const greetingIcon = ref('')

const userImage = computed(() => {
  // Check for profile image from multiple sources
  const profileImage = dashboardStore.userImage || 
                      authStore.user?.client?.profile_image || 
                      authStore.user?.profile_image
  
  return profileImage || defaultAvatar
})

const balanceColorClass = computed(() => {
  const status = dashboardStore.balanceStatus
  switch (status) {
    case 'low':
      return 'text-red-600 dark:text-red-400'
    case 'medium':
      return 'text-orange-500 dark:text-orange-400'
    case 'good':
      return 'text-green-700 dark:text-green-400'
    default:
      return 'text-gray-600 dark:text-gray-400'
  }
})

const internetStatusColor = computed(() => {
  return dashboardStore.isOnline ? 'text-green-500' : 'text-red-500'
})

const accountStatusColor = computed(() => {
  switch (dashboardStore.status) {
    case 'active':
      return 'text-green-500'
    case 'suspended':
      return 'text-orange-500'
    case 'inactive':
      return 'text-gray-500'
    case 'banned':
      return 'text-red-500'
    default:
      return 'text-gray-500'
  }
})

const accountStatusTextColor = computed(() => {
  switch (dashboardStore.status) {
    case 'active':
      return 'text-green-600 dark:text-green-400'
    case 'suspended':
      return 'text-orange-600 dark:text-orange-400'
    case 'inactive':
      return 'text-gray-600 dark:text-gray-400'
    case 'banned':
      return 'text-red-600 dark:text-red-400'
    default:
      return 'text-gray-600 dark:text-gray-400'
  }
})

const logout = async () => {
  try {
    await authStore.logout()
  } catch (error) {
    console.error('Logout error:', error)
    // Force logout even if API fails
    authStore.clearAuth()
    window.location.href = '/'
  }
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

onMounted(() => {
  setGreeting()
})
</script>
<style scoped>
@keyframes fade-in-content {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-content {
  animation: fade-in-content 0.5s ease-out;
}
</style>