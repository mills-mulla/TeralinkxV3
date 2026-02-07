<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-800 pt-16">
    <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
    
    <div class="sm:max-w-md md:max-w-lg lg:max-w-4xl mx-auto px-4 mt-4 mb-8">
      <!-- Page Header -->
      <header class="mb-8 transform transition-all duration-500 animate-fade-in">
        <div class="flex items-center space-x-3 mb-2">
          <div class="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg transition-all duration-300 hover:scale-110 hover:rotate-3">
            <svg class="w-6 h-6 text-white transition-transform duration-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8Z"/>
            </svg>
          </div>
          <div class="transition-all duration-300 hover:translate-x-1">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Rewards</h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">Earn points and redeem exclusive rewards</p>
          </div>
        </div>
      </header>

      <!-- Loading State -->
      <div v-if="loading && !rewardSummary" class="flex justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>

      <!-- Rewards Content -->
      <div v-else class="space-y-6">
        <!-- Points Overview -->
        <div class="bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl p-6 text-white animate-fade-in">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-2xl font-bold">{{ currentPoints.toLocaleString() }}</h2>
              <p class="text-purple-100">Reward Points</p>
            </div>
            <div class="text-right">
              <div class="flex items-center space-x-2 mb-1">
                <span class="text-2xl">{{ getTierIcon(currentTier) }}</span>
                <span class="text-lg font-semibold capitalize">{{ currentTier }}</span>
              </div>
              <p class="text-purple-100 text-sm">Current Tier</p>
            </div>
          </div>
          
          <!-- Tier Progress -->
          <div v-if="currentTier !== 'platinum'" class="space-y-2">
            <div class="flex justify-between text-sm">
              <span>Progress to {{ getNextTier(currentTier) }}</span>
              <span>{{ nextTierPoints }} points to go</span>
            </div>
            <div class="w-full bg-purple-400 rounded-full h-2">
              <div 
                class="bg-white rounded-full h-2 transition-all duration-500"
                :style="{ width: `${tierProgress}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Available Coupons -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">My Coupons</h3>
          
          <div v-if="userCoupons.length > 0" class="space-y-3">
            <div
              v-for="coupon in userCoupons"
              :key="coupon.code"
              class="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800"
            >
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M11,16.5L18,9.5L16.59,8.09L11,13.67L7.91,10.59L6.5,12L11,16.5Z"/>
                  </svg>
                </div>
                <div>
                  <p class="font-medium text-green-800 dark:text-green-200">{{ coupon.name }}</p>
                  <p class="text-sm text-green-600 dark:text-green-300">Code: {{ coupon.code }}</p>
                  <p class="text-xs text-green-500 dark:text-green-400">Expires: {{ formatDate(coupon.valid_until) }}</p>
                </div>
              </div>
              
              <button
                @click="copyCouponCode(coupon.code)"
                class="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm font-medium transition-colors"
              >
                Copy Code
              </button>
            </div>
          </div>
          
          <div v-else class="text-center py-6 text-gray-500 dark:text-gray-400">
            <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.023.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.99 1.99 0 013 12V7a4 4 0 014-4z"></path>
            </svg>
            <p>No coupons available</p>
            <p class="text-sm">Redeem points to get discount coupons</p>
          </div>
        </div>

        <!-- Available Rewards -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Available Rewards</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="reward in availableRewards"
              :key="reward.points"
              class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 transition-all duration-300 hover:shadow-lg"
              :class="reward.can_redeem ? 'hover:border-purple-400' : 'opacity-60'"
            >
              <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium text-gray-900 dark:text-white">{{ reward.name }}</h4>
                <span class="text-lg font-bold text-purple-600">{{ reward.discount }}%</span>
              </div>
              
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ reward.points }} points</span>
                
                <button
                  v-if="reward.can_redeem"
                  @click="handleRedeem(reward)"
                  :disabled="loading"
                  class="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-all duration-300 hover:scale-105 disabled:opacity-50"
                >
                  Redeem
                </button>
                
                <span v-else class="text-xs text-gray-500 dark:text-gray-400">
                  {{ reward.reason }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Transactions -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-fade-in">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h3>
          
          <div class="space-y-3">
            <div
              v-for="transaction in recentTransactions"
              :key="transaction.id"
              class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
            >
              <div class="flex items-center space-x-3">
                <div 
                  class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                  :class="transaction.points > 0 ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'"
                >
                  {{ transaction.points > 0 ? '+' : '' }}{{ transaction.points }}
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">{{ transaction.description }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatDate(transaction.date) }}</p>
                </div>
              </div>
              
              <div v-if="transaction.coupon_code" class="text-right">
                <p class="text-xs text-purple-600 dark:text-purple-400 font-medium">{{ transaction.coupon_code }}</p>
              </div>
            </div>
            
            <div v-if="!recentTransactions.length" class="text-center py-4 text-gray-500 dark:text-gray-400">
              No transactions yet. Start earning points by purchasing packages!
            </div>
          </div>
        </div>

        <!-- How to Earn Points -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800 animate-fade-in">
          <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-4">How to Earn Points</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="text-center">
              <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-2">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4Z"/>
                </svg>
              </div>
              <h4 class="font-medium text-blue-900 dark:text-blue-200">Purchase Packages</h4>
              <p class="text-sm text-blue-700 dark:text-blue-300">1 point per KSh spent</p>
            </div>
            
            <div class="text-center">
              <div class="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-2">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,5.5A3.5,3.5 0 0,1 15.5,9A3.5,3.5 0 0,1 12,12.5A3.5,3.5 0 0,1 8.5,9A3.5,3.5 0 0,1 12,5.5M5,8C5.56,8 6.08,8.15 6.53,8.42C6.38,9.85 6.8,11.27 7.66,12.38C7.16,13.34 6.16,14 5,14A3,3 0 0,1 2,11A3,3 0 0,1 5,8M19,8A3,3 0 0,1 22,11A3,3 0 0,1 19,14C17.84,14 16.84,13.34 16.34,12.38C17.2,11.27 17.62,9.85 17.47,8.42C17.92,8.15 18.44,8 19,8M5.5,18.25C5.5,16.18 8.41,14.5 12,14.5C15.59,14.5 18.5,16.18 18.5,18.25V20H5.5V18.25Z"/>
                </svg>
              </div>
              <h4 class="font-medium text-blue-900 dark:text-blue-200">Refer Friends</h4>
              <p class="text-sm text-blue-700 dark:text-blue-300">500 points per referral</p>
            </div>
            
            <div class="text-center">
              <div class="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-2">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M11,16.5L18,9.5L16.59,8.09L11,13.67L7.91,10.59L6.5,12L11,16.5Z"/>
                </svg>
              </div>
              <h4 class="font-medium text-blue-900 dark:text-blue-200">Tier Upgrades</h4>
              <p class="text-sm text-blue-700 dark:text-blue-300">Bonus points + multipliers</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRewards } from '@/composables/useRewards'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import NavBar from '@/components/NavBar.vue'

const {
  loading,
  rewardSummary,
  availableRewards,
  currentPoints,
  currentTier,
  tierProgress,
  nextTierPoints,
  fetchRewardSummary,
  fetchAvailableRewards,
  redeemReward,
  getTierIcon
} = useRewards()

const { showSuccess } = useToast()
const authStore = useAuthStore()

// State
const userCoupons = ref([])

// Computed
const recentTransactions = computed(() => {
  return rewardSummary.value?.recent_transactions?.slice(0, 5) || []
})

// Methods
const getNextTier = (tier) => {
  const tiers = { bronze: 'Silver', silver: 'Gold', gold: 'Platinum' }
  return tiers[tier] || 'Platinum'
}

const handleRedeem = async (reward) => {
  const result = await redeemReward(reward.points, reward.discount)
  if (result.success) {
    await Promise.all([
      fetchRewardSummary(),
      fetchAvailableRewards(),
      fetchUserCoupons()
    ])
  }
}

const fetchUserCoupons = async () => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/rewards/coupons/`, {
      headers: authStore.authHeaders
    })
    
    if (response.ok) {
      const data = await response.json()
      userCoupons.value = data.coupons || []
      console.log('Fetched coupons:', data.coupons) // Debug log
    } else {
      console.error('Failed to fetch coupons:', response.status)
    }
  } catch (error) {
    console.error('Failed to fetch user coupons:', error)
  }
}

const copyCouponCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code)
    showSuccess(`Coupon code ${code} copied to clipboard!`)
  } catch (error) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = code
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    showSuccess(`Coupon code ${code} copied!`)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    fetchRewardSummary(),
    fetchAvailableRewards(),
    fetchUserCoupons()
  ])
})
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
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