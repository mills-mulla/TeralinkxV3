// src/composables/useRewards.js
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from './useToast'

export function useRewards() {
  const authStore = useAuthStore()
  const { showSuccess, showError } = useToast()
  
  // State
  const loading = ref(false)
  const rewardSummary = ref(null)
  const availableRewards = ref([])
  const pointHistory = ref([])
  
  // Computed
  const currentPoints = computed(() => rewardSummary.value?.current_points || 0)
  const currentTier = computed(() => rewardSummary.value?.current_tier || 'bronze')
  const tierProgress = computed(() => rewardSummary.value?.tier_progress || 0)
  const nextTierPoints = computed(() => rewardSummary.value?.next_tier_points || 0)
  
  // Methods
  const fetchRewardSummary = async () => {
    try {
      loading.value = true
      const response = await fetch('/api/rewards/summary/', {
        headers: authStore.authHeaders
      })
      
      if (response.ok) {
        rewardSummary.value = await response.json()
      } else {
        throw new Error('Failed to fetch reward summary')
      }
    } catch (error) {
      showError('Failed to load rewards data')
    } finally {
      loading.value = false
    }
  }
  
  const fetchAvailableRewards = async () => {
    try {
      const response = await fetch('/api/rewards/available/', {
        headers: authStore.authHeaders
      })
      
      if (response.ok) {
        const data = await response.json()
        availableRewards.value = data.rewards
      }
    } catch (error) {
      // Failed to fetch available rewards
    }
  }
  
  const fetchPointHistory = async () => {
    try {
      const response = await fetch('/api/rewards/history/', {
        headers: authStore.authHeaders
      })
      
      if (response.ok) {
        const data = await response.json()
        pointHistory.value = data.transactions
      }
    } catch (error) {
      // Failed to fetch point history
    }
  }
  
  const redeemReward = async (pointsCost, discountPercentage) => {
    try {
      loading.value = true
      const response = await fetch('/api/rewards/redeem/', {
        method: 'POST',
        headers: {
          ...authStore.authHeaders,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          points_cost: pointsCost,
          discount_percentage: discountPercentage
        })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        showSuccess(`Redeemed ${discountPercentage}% discount! Code: ${data.coupon_code}`)
        await fetchRewardSummary() // Refresh data
        await fetchAvailableRewards()
        return { success: true, couponCode: data.coupon_code }
      } else {
        showError(data.error || 'Failed to redeem reward')
        return { success: false, error: data.error }
      }
    } catch (error) {
      showError('Failed to redeem reward')
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }
  
  const getTierColor = (tier) => {
    const colors = {
      bronze: 'text-orange-600 dark:text-orange-400',
      silver: 'text-gray-600 dark:text-gray-400', 
      gold: 'text-yellow-600 dark:text-yellow-400',
      platinum: 'text-purple-600 dark:text-purple-400'
    }
    return colors[tier] || colors.bronze
  }
  
  const getTierIcon = (tier) => {
    const icons = {
      bronze: '🥉',
      silver: '🥈',
      gold: '🥇',
      platinum: '💎'
    }
    return icons[tier] || icons.bronze
  }
  
  return {
    // State
    loading,
    rewardSummary,
    availableRewards,
    pointHistory,
    
    // Computed
    currentPoints,
    currentTier,
    tierProgress,
    nextTierPoints,
    
    // Methods
    fetchRewardSummary,
    fetchAvailableRewards,
    fetchPointHistory,
    redeemReward,
    getTierColor,
    getTierIcon
  }
}