<template>
  <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-lg font-bold">
            {{ getInitials(client.user_username) }}
          </div>
          <div>
            <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ client.user_username }}</h2>
            <p class="text-xs text-slate-500 dark:text-slate-400">{{ client.account }}</p>
          </div>
        </div>
        <button @click="$emit('close')" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
          <svg class="w-4 h-4 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Tabs -->
      <div class="border-b border-slate-200 dark:border-slate-700 px-4">
        <div class="flex gap-3">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" class="px-3 py-2 text-xs font-medium border-b-2 transition-colors" :class="activeTab === tab.id ? 'border-blue-500 text-blue-600 dark:text-blue-400' : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'">
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-4 overflow-y-auto max-h-[calc(80vh-140px)]">
        <!-- General Tab -->
        <div v-if="activeTab === 'general'" class="space-y-3">
          <!-- Profile Image & Key Metrics -->
          <div class="flex items-start gap-3 mb-3">
            <div v-if="client.profile_image" class="w-16 h-16 rounded-lg overflow-hidden">
              <img :src="client.profile_image" alt="Profile" class="w-full h-full object-cover" @error="$event.target.parentElement.innerHTML = getUserIcon()" />
            </div>
            <div v-else class="w-16 h-16 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center" v-html="getUserIcon()">
            </div>
            <div class="flex-1 grid grid-cols-3 gap-2">
              <div class="p-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
                <p class="text-[10px] text-blue-600 dark:text-blue-400">Balance</p>
                <p class="text-sm font-bold text-blue-700 dark:text-blue-300">KSh {{ formatNumber(client.balance) }}</p>
              </div>
              <div class="p-2 bg-purple-50 dark:bg-purple-500/10 rounded-lg">
                <p class="text-[10px] text-purple-600 dark:text-purple-400">Points</p>
                <p class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ client.reward_points }}</p>
              </div>
              <div class="p-2 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg">
                <p class="text-[10px] text-emerald-600 dark:text-emerald-400">Spent</p>
                <p class="text-sm font-bold text-emerald-700 dark:text-emerald-300">KSh {{ formatNumber(client.total_spent) }}</p>
              </div>
            </div>
          </div>

          <!-- All Client Fields -->
          <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
            <div><span class="text-slate-500 dark:text-slate-400">Account:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.account }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Phone:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.phone_number }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Email:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.user_email || 'N/A' }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Display Name:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.display_name || 'N/A' }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Tier:</span> <span class="px-2 py-0.5 text-xs rounded-full ml-2" :class="getTierBadge(client.account_tier)">{{ client.account_tier }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Status:</span> <span class="px-2 py-0.5 text-xs rounded-full ml-2" :class="getStatusBadge(client.status)">{{ client.status }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Reward Tier:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.reward_tier }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Credit Limit:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">KSh {{ formatNumber(client.credit_limit) }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Data Used:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ formatBytes(client.lifetime_data_used) }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Joined:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ formatDate(client.created_at) }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">Last Login:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ formatDate(client.last_login) }}</span></div>
            <div><span class="text-slate-500 dark:text-slate-400">2FA:</span> <span class="font-medium text-slate-900 dark:text-white ml-2">{{ client.two_factor_enabled ? 'Enabled' : 'Disabled' }}</span></div>
          </div>

          <!-- Quick Stats -->
          <div class="grid grid-cols-4 gap-2 pt-2 border-t border-slate-200 dark:border-slate-700">
            <div class="text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded">
              <p class="text-[10px] text-slate-500 dark:text-slate-400">Devices</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ profile.stats?.total_devices || 0 }}</p>
            </div>
            <div class="text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded">
              <p class="text-[10px] text-slate-500 dark:text-slate-400">Sessions</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ profile.stats?.active_sessions || 0 }}</p>
            </div>
            <div class="text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded">
              <p class="text-[10px] text-slate-500 dark:text-slate-400">Vouchers</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ profile.stats?.total_vouchers || 0 }}</p>
            </div>
            <div class="text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded">
              <p class="text-[10px] text-slate-500 dark:text-slate-400">Points Earned</p>
              <p class="text-sm font-bold text-slate-900 dark:text-white">{{ client.total_points_earned || 0 }}</p>
            </div>
          </div>
        </div>

        <!-- Advanced Tab -->
        <div v-if="activeTab === 'advanced'" class="space-y-3">
          <!-- Analytics -->
          <div>
            <h4 class="text-xs font-semibold text-slate-900 dark:text-white mb-2">Analytics & Insights</h4>
            <div class="grid grid-cols-2 gap-2">
              <div class="p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                <p class="text-[10px] text-slate-600 dark:text-slate-400 mb-0.5">Lifetime Value</p>
                <p class="text-base font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(analytics.ltv) }}</p>
              </div>
              <div class="p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                <p class="text-[10px] text-slate-600 dark:text-slate-400 mb-0.5">Engagement Score</p>
                <p class="text-base font-bold text-slate-900 dark:text-white">{{ analytics.engagement_score }}%</p>
              </div>
              <div class="p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                <p class="text-[10px] text-slate-600 dark:text-slate-400 mb-0.5">Churn Risk</p>
                <p class="text-base font-bold" :class="analytics.churn_risk === 'low' ? 'text-emerald-600' : 'text-red-600'">{{ analytics.churn_risk }}</p>
              </div>
              <div class="p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                <p class="text-[10px] text-slate-600 dark:text-slate-400 mb-0.5">Avg Transaction</p>
                <p class="text-base font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(analytics.avg_transaction) }}</p>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div>
            <h4 class="text-xs font-semibold text-slate-900 dark:text-white mb-2">Quick Actions</h4>
            <div class="grid grid-cols-2 gap-2">
              <button @click="showBalanceModal = true" class="p-2.5 bg-blue-50 dark:bg-blue-500/10 hover:bg-blue-100 dark:hover:bg-blue-500/20 rounded-lg text-left transition-colors">
                <p class="text-xs font-medium text-blue-700 dark:text-blue-400">Adjust Balance</p>
                <p class="text-[10px] text-blue-600 dark:text-blue-500 mt-0.5">Add or deduct balance</p>
              </button>
              <button @click="showPointsModal = true" class="p-2.5 bg-purple-50 dark:bg-purple-500/10 hover:bg-purple-100 dark:hover:bg-purple-500/20 rounded-lg text-left transition-colors">
                <p class="text-xs font-medium text-purple-700 dark:text-purple-400">Award Points</p>
                <p class="text-[10px] text-purple-600 dark:text-purple-500 mt-0.5">Give reward points</p>
              </button>
              <button @click="toggleSuspend" class="p-2.5 bg-amber-50 dark:bg-amber-500/10 hover:bg-amber-100 dark:hover:bg-amber-500/20 rounded-lg text-left transition-colors">
                <p class="text-xs font-medium text-amber-700 dark:text-amber-400">{{ client.status === 'suspended' ? 'Activate' : 'Suspend' }}</p>
                <p class="text-[10px] text-amber-600 dark:text-amber-500 mt-0.5">{{ client.status === 'suspended' ? 'Reactivate account' : 'Temporarily disable' }}</p>
              </button>
              <button @click="forceLogout" class="p-2.5 bg-red-50 dark:bg-red-500/10 hover:bg-red-100 dark:hover:bg-red-500/20 rounded-lg text-left transition-colors">
                <p class="text-xs font-medium text-red-700 dark:text-red-400">Force Logout</p>
                <p class="text-[10px] text-red-600 dark:text-red-500 mt-0.5">End all sessions</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Balance Modal -->
    <div v-if="showBalanceModal" class="fixed inset-0 bg-black/60 z-60 flex items-center justify-center p-4" @click.self="showBalanceModal = false">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Adjust Balance</h3>
        <input v-model="balanceAmount" type="number" placeholder="Amount (+ or -)" class="w-full px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white mb-3" />
        <input v-model="balanceReason" type="text" placeholder="Reason" class="w-full px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white mb-4" />
        <div class="flex gap-2">
          <button @click="adjustBalance" class="flex-1 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg">Confirm</button>
          <button @click="showBalanceModal = false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Points Modal -->
    <div v-if="showPointsModal" class="fixed inset-0 bg-black/60 z-60 flex items-center justify-center p-4" @click.self="showPointsModal = false">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Award Points</h3>
        <input v-model="pointsAmount" type="number" placeholder="Points" class="w-full px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white mb-3" />
        <input v-model="pointsReason" type="text" placeholder="Description" class="w-full px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white mb-4" />
        <div class="flex gap-2">
          <button @click="awardPoints" class="flex-1 px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg">Award</button>
          <button @click="showPointsModal = false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useApi } from '../composables/useApi'

export default {
  name: 'ClientDetailModal',
  props: {
    show: Boolean,
    client: Object
  },
  emits: ['close', 'refresh'],
  setup(props, { emit }) {
    const { makeRequest } = useApi()
    const activeTab = ref('general')
    const profile = ref({ devices: [], sessions: [], transactions: [], vouchers: [], stats: {} })
    const analytics = ref({})
    const showBalanceModal = ref(false)
    const showPointsModal = ref(false)
    const balanceAmount = ref(0)
    const balanceReason = ref('')
    const pointsAmount = ref(0)
    const pointsReason = ref('')

    const tabs = [
      { id: 'general', label: 'General' },
      { id: 'advanced', label: 'Advanced' }
    ]

    const fetchProfile = async () => {
      if (!props.client?.id) return
      try {
        profile.value = await makeRequest('get', `suapi/clients/${props.client.id}/profile/`)
        analytics.value = await makeRequest('get', `suapi/clients/${props.client.id}/analytics/`)
      } catch (error) {
        console.error('Error fetching profile:', error)
      }
    }

    const adjustBalance = async () => {
      try {
        await makeRequest('post', `suapi/clients/${props.client.id}/adjust_balance/`, {
          amount: balanceAmount.value,
          reason: balanceReason.value
        })
        showBalanceModal.value = false
        emit('refresh')
        fetchProfile()
      } catch (error) {
        console.error('Error adjusting balance:', error)
      }
    }

    const awardPoints = async () => {
      try {
        await makeRequest('post', `suapi/clients/${props.client.id}/award_points/`, {
          points: pointsAmount.value,
          description: pointsReason.value
        })
        showPointsModal.value = false
        emit('refresh')
        fetchProfile()
      } catch (error) {
        console.error('Error awarding points:', error)
      }
    }

    const toggleSuspend = async () => {
      const action = props.client.status === 'suspended' ? 'activate' : 'suspend'
      if (!confirm(`${action === 'suspend' ? 'Suspend' : 'Activate'} this client?`)) return
      try {
        await makeRequest('post', `suapi/clients/${props.client.id}/${action}/`, { reason: 'Admin action' })
        emit('refresh')
        emit('close')
      } catch (error) {
        console.error(`Error ${action}ing client:`, error)
      }
    }

    const forceLogout = async () => {
      if (!confirm('Force logout all sessions?')) return
      try {
        await makeRequest('post', `suapi/clients/${props.client.id}/force_logout/`, { reason: 'Admin action' })
        fetchProfile()
      } catch (error) {
        console.error('Error forcing logout:', error)
      }
    }

    const getUserIcon = () => {
      return `<svg class="w-10 h-10 text-slate-400 dark:text-slate-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>`
    }

    const formatNumber = (num) => new Intl.NumberFormat().format(num || 0)
    const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'N/A'
    const formatBytes = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    const getTierBadge = (tier) => {
      const badges = {
        'basic': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300',
        'premium': 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400',
        'business': 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        'enterprise': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400'
      }
      return badges[tier] || badges.basic
    }

    const getStatusBadge = (status) => {
      const badges = {
        'active': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'inactive': 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400',
        'suspended': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400',
        'banned': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
      }
      return badges[status] || badges.inactive
    }

    watch(() => props.show, (newVal) => {
      if (newVal) fetchProfile()
    })

    return {
      activeTab, tabs, profile, analytics,
      showBalanceModal, showPointsModal,
      balanceAmount, balanceReason, pointsAmount, pointsReason,
      adjustBalance, awardPoints, toggleSuspend, forceLogout,
      getUserIcon, formatNumber, formatDate, formatBytes, getTierBadge, getStatusBadge
    }
  }
}
</script>
