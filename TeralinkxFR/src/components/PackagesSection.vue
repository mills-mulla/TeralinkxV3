<template>
  <div class="max-w-md mx-auto px-4 text-text-light dark:text-text-dark transition-colors duration-300 z-0">
    <!-- Featured Packages Section -->
    <div v-if="featuredPackages.length > 0" class="mb-6">
      <h2 class="text-center text-sm font-bold text-gray-700 dark:text-gray-300 mb-4 px-3 py-2 bg-white/10 dark:bg-gray-800/10 backdrop-blur-md rounded-lg border border-white/20 dark:border-gray-600/20">FEATURED PACKAGES</h2>
      
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div
          v-for="pkg in featuredPackages"
          :key="pkg.id"
          class="relative bg-white/20 dark:bg-gray-800/20 backdrop-blur-md shadow-lg rounded-lg px-4 py-2 border border-white/30 dark:border-gray-600/30 hover:shadow-xl transition duration-300 overflow-hidden"
        >
          <!-- Featured Banner -->
          <div class="absolute top-0 left-0 w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white text-[10px] font-bold text-center py-0.5 z-10 flex items-center justify-center space-x-1">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a1 1 0 01.894.553l2.382 4.823 5.322.774a1 1 0 01.554 1.706l-3.85 3.754.909 5.304a1 1 0 01-1.451 1.054L10 17.347l-4.76 2.5a1 1 0 01-1.451-1.054l.909-5.304-3.85-3.754a1 1 0 01.554-1.706l5.322-.774 2.382-4.823A1 1 0 0110 2z" />
            </svg>
            <span>FEATURED</span>
          </div>

          <div class="mt-4 mb-3">
            <p class="font-semibold text-sm text-gray-800 dark:text-white mb-2 text-center">{{ pkg.name }}</p>
            <div class="flex items-center justify-around mb-2">
              <p class="text-xs text-gray-600 dark:text-gray-300">⏰ {{ formatDuration(pkg) }}</p>
              <p class="text-xs text-gray-600 dark:text-gray-300">{{ formatDataLimit(pkg) }}</p>
            </div>
            <div class="flex items-center justify-between">
              <p class="text-xs text-gray-600 dark:text-gray-300">{{ getDeviceIcon(pkg.device_limit) }} {{ pkg.device_limit }} device{{ pkg.device_limit > 1 ? 's' : '' }}</p>
              <p class="text-sm text-black dark:text-gray-200 font-bold">
                <span class="text-xs text-gray-700 dark:text-gray-400 font-semibold">KES</span> {{ pkg.price.parsedValue }}
              </p>
            </div>
          </div>

          <button
            @click="handleBuy(pkg)"
            :disabled="loading"
            class="relative w-full inline-flex items-center justify-center text-white bg-blue-700 hover:bg-blue-800 px-3 py-1 text-xs rounded shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading && selectedPackageId === pkg.id">Processing...</span>
            <span v-else>Buy Now</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Regular Packages Section -->
    <div v-if="regularPackages.length > 0">
      <h2 class="text-center text-sm font-bold text-gray-700 dark:text-gray-300 mb-4 px-3 py-2 bg-white/10 dark:bg-gray-800/10 backdrop-blur-md rounded-lg border border-white/20 dark:border-gray-600/20">MORE OFFERS</h2>
      
      <!-- Skeleton Loader -->
      <div v-if="dashboardStore.loading" class="grid grid-cols-2 gap-3 animate-pulse">
        <div v-for="n in 4" :key="n" class="bg-white/60 dark:bg-gray-700/60 backdrop-blur-sm rounded-lg h-28"></div>
      </div>

      <!-- Regular Package Cards -->
      <div v-else class="grid grid-cols-2 gap-4 mb-4">
        <div
          v-for="(pkg, index) in regularPackages"
          :key="pkg.id"
          class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 backdrop-blur-sm p-2 rounded-lg shadow-lg border border-blue-100 dark:border-gray-600 flex flex-col justify-between transition-all duration-300 hover:shadow-xl hover:scale-[1.05] hover:-translate-y-1 transform animate-fade-in-card group"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <div class="mb-3">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2 text-center transition-colors duration-300 group-hover:text-blue-600 dark:group-hover:text-blue-400">{{ pkg.name }}</h3>
            <div class="flex items-center justify-around mb-2">
              <p class="text-xs text-gray-600 dark:text-gray-300 transition-all duration-300 group-hover:scale-105">⏰ {{ formatDuration(pkg) }}</p>
              <p class="text-xs text-gray-600 dark:text-gray-300 transition-all duration-300 group-hover:scale-105">{{ formatDataLimit(pkg) }}</p>
            </div>
            <div class="flex items-center justify-between">
              <p class="text-xs text-gray-600 dark:text-gray-300 transition-all duration-300 group-hover:scale-105">{{ getDeviceIcon(pkg.device_limit) }} {{ pkg.device_limit }} device{{ pkg.device_limit > 1 ? 's' : '' }}</p>
              <p class="text-sm text-black dark:text-white font-bold transition-all duration-300 group-hover:scale-110 group-hover:text-green-600 dark:group-hover:text-green-400">
                <span class="text-xs text-gray-700 dark:text-gray-400 font-semibold">KES</span> {{ pkg.price?.parsedValue || pkg.price }}
              </p>
            </div>
          </div>

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
        </div>
      </div>
    </div>

    <!-- No Packages -->
    <div v-if="!dashboardStore.loading && featuredPackages.length === 0 && regularPackages.length === 0" class="text-center text-sm text-gray-500 dark:text-gray-400 py-8">
      <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
      </svg>
      <p>No packages available</p>
    </div>

    <Loader v-if="isloading" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import { useBuyOffer } from '@/composables/useBuyOffer'
import { useToast } from '@/composables/useToast'
import Loader from '@/views/Loader.vue'

const emit = defineEmits(['openPaymentModal', 'openBuyModal'])

const dashboardStore = useDashboardStore()
const authStore = useAuthStore()
const { showSuccess, showError } = useToast()
const { buyOffer, loading, error, isloading } = useBuyOffer()

const selectedPackageId = ref(null)
const loadingId = ref(null)

// Separate featured and regular packages
const featuredPackages = computed(() => {
  return dashboardStore.packages.filter(pkg => pkg.is_featured)
})

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
    return '📱💻'
  } else {
    return '📺'
  }
}

function handleBuy(pkg) {
  if (!loading.value) {
    selectedPackageId.value = pkg.id
    emit('openPaymentModal', pkg)
  }
}

const buy = async (pkg) => {
  loadingId.value = pkg.id
  
  try {
    emit('openBuyModal', pkg)
  } catch (error) {
    console.error('Purchase error:', error)
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

.animate-fade-in-card {
  animation: fade-in-card 0.6s ease-out;
  animation-fill-mode: both;
}
</style>