<template>
  <div class="max-w-md mx-auto px-4 font-sans text-gray-900 dark:text-gray-100 transition-colors duration-300 rounded-md shadow-sm z-0">
    <!-- Title -->
    <h2 class="text-center text-sm font-bold text-gray-700 dark:text-gray-300 mb-4 px-3 py-2 bg-white/10 dark:bg-gray-800/10 backdrop-blur-md rounded-lg border border-white/20 dark:border-gray-600/20">MORE OFFERS</h2>

    <!-- Skeleton Loader -->
    <div v-if="dashboardStore.loading" class="grid grid-cols-2 gap-3 animate-pulse">
      <div v-for="n in 4" :key="n" class="bg-white/60 dark:bg-gray-700/60 backdrop-blur-sm rounded-lg h-28"></div>
    </div>

    <!-- No Packages -->
    <div v-else-if="regularPackages.length === 0" class="text-center text-sm text-gray-500 dark:text-gray-400 py-8">
      <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
      </svg>
      <p>No packages available</p>
    </div>

    <!-- Grid layout -->
    <div v-else class="grid grid-cols-2 gap-4 mb-4">
      <div
        v-for="(pkg, index) in regularPackages"
        :key="pkg.id"
        class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 backdrop-blur-sm p-2 rounded-lg shadow-lg border border-blue-100 dark:border-gray-600 flex flex-col justify-between transition-all duration-300 hover:shadow-xl hover:scale-[1.05] hover:-translate-y-1 transform animate-fade-in-card group"
        :style="{ animationDelay: `${index * 0.1}s` }"
      >
        <!-- Package Details -->
        <div class="mb-3">
          <!-- Package Name -->
          <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2 text-center transition-colors duration-300 group-hover:text-blue-600 dark:group-hover:text-blue-400">{{ pkg.name }}</h3>
          
          <!-- Duration and Data Limit -->
          <div class="flex items-center justify-around mb-2">
            <p class="text-xs text-gray-600 dark:text-gray-300 transition-all duration-300 group-hover:scale-105">⏰ {{ formatDuration(pkg) }}</p>
            <p class="text-xs text-gray-600 dark:text-gray-300 transition-all duration-300 group-hover:scale-105">{{ formatDataLimit(pkg) }}</p>
          </div>
          
          <!-- Device Limit and Price -->
          <div class="flex items-center justify-between">
            <p class="text-xs text-gray-600 dark:text-gray-300 transition-all duration-300 group-hover:scale-105">{{ getDeviceIcon(pkg.device_limit) }} {{ pkg.device_limit }} device{{ pkg.device_limit > 1 ? 's' : '' }}</p>
            <p class="text-sm text-black dark:text-white font-bold transition-all duration-300 group-hover:scale-110 group-hover:text-green-600 dark:group-hover:text-green-400">
              <span class="text-xs text-gray-700 dark:text-gray-400 font-semibold">KES</span> {{ pkg.price?.parsedValue || pkg.price }}
            </p>
          </div>
        </div>

        <!-- Buy Button -->
        <button
          class="w-full bg-green-600 text-white text-sm font-bold py-2 rounded hover:bg-green-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 hover:shadow-lg active:scale-95"
          :disabled="loadingId === pkg.id"
          @click="buy(pkg)"
        >
          <span v-if="loadingId === pkg.id" class="flex items-center justify-center space-x-2">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Processing...</span>
          </span>
          <span v-else>BUY</span>
        </button>
        <p v-if="errorMessage && loadingId === pkg.id" class="text-red-600 text-xs mt-1 animate-shake">{{ errorMessage }}</p>
      </div>
    </div>

    <!-- Buy Modal -->
    <BuyComponent
      v-if="showBuyComponent"
      @close="showBuyComponent = false"
      :packageDetails="selectedPackage"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import BuyComponent from './BuyComponent.vue'

const dashboardStore = useDashboardStore()
const authStore = useAuthStore()
const { showSuccess, showError } = useToast()

// Buy package state
const loadingId = ref(null)
const errorMessage = ref('')
const showBuyComponent = ref(false)
const selectedPackage = ref(null)

// Get only non-featured packages from dashboard data
const regularPackages = computed(() => {
  return dashboardStore.packages.filter(pkg => !pkg.is_featured)
})

const formatDuration = (pkg) => {
  const { duration_days, duration_hours, duration_minutes } = pkg
  
  if (duration_days > 0) {
    return `${duration_days} day${duration_days > 1 ? 's' : ''}`
  } else if (duration_hours > 0) {
    return `${duration_hours} hour${duration_hours > 1 ? 's' : ''}`
  } else if (duration_minutes > 0) {
    return `${duration_minutes} minute${duration_minutes > 1 ? 's' : ''}`
  }
  return 'Unlimited time'
}

const formatDataLimit = (pkg) => {
  if (pkg.is_unlimited) {
    return 'Unlimited data'
  } else if (pkg.data_limit_mb) {
    const mb = pkg.data_limit_mb
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(1)} GB`
    }
    return `${mb} MB`
  }
  return 'No data limit'
}

const getDeviceIcon = (deviceLimit) => {
  if (deviceLimit === 1) {
    // Single device - show current device type
    const deviceType = authStore.user?.device?.device_type || 'other'
    switch (deviceType) {
      case 'phone': return '📱'
      case 'tablet': return '📱'
      case 'laptop': return '💻'
      case 'desktop': return '🖥️'
      case 'tv': return '📺'
      default: return '💻'
    }
  } else if (deviceLimit === 2) {
    return '📱💻'  // Phone + PC for 2 devices
  } else {
    return '📺'  // Smart TV for multiple devices
  }
}

const buy = async (pkg) => {
  loadingId.value = pkg.id
  errorMessage.value = ''
  
  try {
    // Set selected package and show modal
    selectedPackage.value = pkg
    showBuyComponent.value = true
    
  } catch (error) {
    console.error('Purchase error:', error)
    errorMessage.value = error.message || 'Purchase failed'
    showError('Purchase failed. Please try again.')
  } finally {
    loadingId.value = null
  }
}
</script>
<style scoped>
@keyframes fade-in-card {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.animate-fade-in-card {
  animation: fade-in-card 0.6s ease-out;
  animation-fill-mode: both;
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}
</style>