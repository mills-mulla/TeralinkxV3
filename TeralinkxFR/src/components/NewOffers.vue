<template>
  <div class="max-w-md mx-auto px-4 text-text-light dark:text-text-dark transition-colors duration-300 z-0">
    <h2 class="text-center text-sm font-bold text-gray-700 dark:text-gray-300 mb-4 px-3 py-2 bg-white/10 dark:bg-gray-800/10 backdrop-blur-md rounded-lg border border-white/20 dark:border-gray-600/20">FEATURED PACKAGES</h2>

    <!-- Skeleton Loader -->
    <div v-if="dashboardStore.loading" class="grid grid-cols-2 gap-3 animate-pulse">
      <div v-for="n in 4" :key="n" class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg h-28"></div>
    </div>

    <!-- No Featured Packages -->
    <div v-else-if="featuredPackages.length === 0" class="text-center text-sm text-gray-500 dark:text-gray-400 py-8">
      <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
      </svg>
      <p>No featured packages available</p>
    </div>

    <!-- Featured Package Cards -->
    <div v-else class="grid grid-cols-2 gap-4">
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

        <!-- Package Details -->
        <div class="mt-4 mb-3">
          <!-- Package Name -->
          <p class="font-semibold text-sm text-gray-800 dark:text-white mb-2 text-center">{{ pkg.name }}</p>
          
          <!-- Duration and Data Limit -->
          <div class="flex items-center justify-around mb-2">
            <p class="text-xs text-gray-600 dark:text-gray-300">⏰ {{ formatDuration(pkg) }}</p>
            <p class="text-xs text-gray-600 dark:text-gray-300">{{ formatDataLimit(pkg) }}</p>
          </div>
          
          <!-- Device Limit and Price -->
          <div class="flex items-center justify-between">
            <p class="text-xs text-gray-600 dark:text-gray-300">{{ getDeviceIcon(pkg.device_limit) }} {{ pkg.device_limit }} device{{ pkg.device_limit > 1 ? 's' : '' }}</p>
            <p class="text-sm text-black dark:text-gray-200 font-bold">
              <span class="text-xs text-gray-700 dark:text-gray-400 font-semibold">KES</span> {{ pkg.price.parsedValue }}
            </p>
          </div>
        </div>

        <!-- Buy Button -->
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

    <!-- Payment Options Modal -->
    <PaymentOptionsModal
      v-if="showPaymentModal"
      @close="showPaymentModal = false"
      @paymentSelected="handlePaymentSelected"
      :packageDetails="selectedPackage"
    />
    
    <!-- M-Pesa Payment Modal -->
    <BuyComponent
      v-if="showBuyComponent"
      @close="showBuyComponent = false"
      :packageDetails="selectedPackage"
    />
    <Loader v-if="isloading" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import { useBuyOffer } from '@/composables/useBuyOffer'
import PaymentOptionsModal from './PaymentOptionsModal.vue'
import BuyComponent from './BuyComponent.vue'
import Loader from '@/views/Loader.vue'

const dashboardStore = useDashboardStore()
const authStore = useAuthStore()
const showPaymentModal = ref(false)
const showBuyComponent = ref(false)
const selectedPackage = ref(null)
const selectedPackageId = ref(null)

const { buyOffer, loading, error, isloading } = useBuyOffer()

// Get only featured packages from dashboard data
const featuredPackages = computed(() => {
  return dashboardStore.packages.filter(pkg => pkg.is_featured)
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

function handleBuy(pkg) {
  if (!loading.value) {
    selectedPackage.value = pkg
    selectedPackageId.value = pkg.id
    showPaymentModal.value = true
  }
}

function handlePaymentSelected(paymentInfo) {
  showPaymentModal.value = false
  
  if (paymentInfo.method === 'credit') {
    // Handle credit payment directly
    buyOffer(paymentInfo.packageDetails)
  } else if (paymentInfo.method === 'mpesa') {
    // Show M-Pesa modal with payment breakdown
    selectedPackage.value = {
      ...paymentInfo.packageDetails,
      paymentData: paymentInfo.paymentData
    }
    showBuyComponent.value = true
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Wallpoet&display=swap');

@keyframes stampPop {
  0% {
    transform: scale(0.5) rotate(-30deg);
    opacity: 0;
  }
  100% {
    transform: scale(1) rotate(-30deg);
    opacity: 0.7;
  }
}

.sold-out-stamp {
  font-family: 'Wallpoet', sans-serif;
  position: absolute;
  top: 50px;
  left: 50%;
  transform: translateX(-50%) rotate(-30deg);
  color: #b91c1c;
  border: 2px solid #b91c1c;
  padding: 6px 12px;
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  opacity: 0.8;
  animation: stampPop 0.6s ease-out;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}
</style>
