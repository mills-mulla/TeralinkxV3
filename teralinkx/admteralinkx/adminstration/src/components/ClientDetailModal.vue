<template>
  <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
            {{ getInitials(client.user_username) }}
          </div>
          <div>
            <h2 class="text-xl font-semibold text-slate-900 dark:text-white">{{ client.user_username }}</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ client.account }}</p>
          </div>
        </div>
        <button @click="$emit('close')" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Tabs -->
      <div class="border-b border-slate-200 dark:border-slate-700 px-6">
        <div class="flex gap-4 overflow-x-auto">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" class="px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap" :class="activeTab === tab.id ? 'border-blue-500 text-blue-600 dark:text-blue-400' : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'">
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="p-4 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
              <p class="text-xs text-blue-600 dark:text-blue-400 mb-1">Balance</p>
              <p class="text-2xl font-bold text-blue-700 dark:text-blue-300">KSh {{ formatNumber(client.balance) }}</p>
            </div>
            <div class="p-4 bg-purple-50 dark:bg-purple-500/10 rounded-lg">
              <p class="text-xs text-purple-600 dark:text-purple-400 mb-1">Reward Points</p>
              <p class="text-2xl font-bold text-purple-700 dark:text-purple-300">{{ client.reward_points }}</p>
            </div>
            <div class="p-4 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg">
              <p class="text-xs text-emerald-600 dark:text-emerald-400 mb-1">Total Spent</p>
              <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300">KSh {{ formatNumber(profile.stats?.total_spent) }}</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 text-sm">
            <div><span class="text-slate-600 dark:text-slate-400">Phone:</span> <span class="font-medium text-slate-900 dark:text-white">{{ client.phone_number }}</span></div>
            <div><span class="text-slate-600 dark:text-slate-400">Tier:</span> <span class="font-medium text-slate-900 dark:text-white">{{ client.account_tier }}</span></div>
            <div><span class="text-slate-600 dark:text-slate-400">Status:</span> <span class="font-medium text-slate-900 dark:text-white">{{ client.status }}</span></div>
            <div><span class="text-slate-600 dark:text-slate-400">Joined:</span> <span class="font-medium text-slate-900 dark:text-white">{{ formatDate(client.created_at) }}</span></div>
          </div>
        </div>

        <!-- Devices Tab -->
        <div v-if="activeTab === 'devices'" class="space-y-3">
          <div v-for="device in profile.devices" :key="device.id" class="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">{{ device.name }}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400">{{ device.mac }} • {{ device.type }}</p>
              </div>
              <span class="text-xs text-slate-600 dark:text-slate-400">{{ formatDate(device.last_seen) }}</span>
            </div>
          </div>
        </div>

        <!-- Sessions Tab -->
        <div v-if="activeTab === 'sessions'" class="space-y-3">
          <div v-for="session in profile.sessions" :key="session.id" class="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">{{ session.device }}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400">{{ session.ip }}</p>
              </div>
              <span :class="session.is_active ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700'" class="px-2 py-1 text-xs rounded-full">
                {{ session.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Transactions Tab -->
        <div v-if="activeTab === 'transactions'" class="space-y-3">
          <div v-for="txn in profile.transactions" :key="txn.id" class="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg flex items-center justify-between">
            <div>
              <p class="font-medium text-slate-900 dark:text-white">KSh {{ formatNumber(txn.amount) }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400">{{ formatDate(txn.transaction_time) }}</p>
            </div>
            <span :class="txn.result_code === 0 ? 'text-emerald-600' : 'text-red-600'" class="text-sm font-medium">
              {{ txn.result_code === 0 ? 'Success' : 'Failed' }}
            </span>
          </div>
        </div>

        <!-- Analytics Tab -->
        <div v-if="activeTab === 'analytics'" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
              <p class="text-xs text-slate-600 dark:text-slate-400 mb-1">Lifetime Value</p>
              <p class="text-xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(analytics.ltv) }}</p>
            </div>
            <div class="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
              <p class="text-xs text-slate-600 dark:text-slate-400 mb-1">Engagement Score</p>
              <p class="text-xl font-bold text-slate-900 dark:text-white">{{ analytics.engagement_score }}%</p>
            </div>
            <div class="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
              <p class="text-xs text-slate-600 dark:text-slate-400 mb-1">Churn Risk</p>
              <p class="text-xl font-bold" :class="analytics.churn_risk === 'low' ? 'text-emerald-600' : 'text-red-600'">{{ analytics.churn_risk }}</p>
            </div>
            <div class="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
              <p class="text-xs text-slate-600 dark:text-slate-400 mb-1">Avg Transaction</p>
              <p class="text-xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(analytics.avg_transaction) }}</p>
            </div>
          </div>
        </div>

        <!-- Actions Tab -->
        <div v-if="activeTab === 'actions'" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <button @click="showBalanceModal = true" class="p-4 bg-blue-50 dark:bg-blue-500/10 hover:bg-blue-100 dark:hover:bg-blue-500/20 rounded-lg text-left transition-colors">
              <p class="font-medium text-blue-700 dark:text-blue-400">Adjust Balance</p>
              <p class="text-xs text-blue-600 dark:text-blue-500 mt-1">Add or deduct balance</p>
            </button>
            <button @click="showPointsModal = true" class="p-4 bg-purple-50 dark:bg-purple-500/10 hover:bg-purple-100 dark:hover:bg-purple-500/20 rounded-lg text-left transition-colors">
              <p class="font-medium text-purple-700 dark:text-purple-400">Award Points</p>
              <p class="text-xs text-purple-600 dark:text-purple-500 mt-1">Give reward points</p>
            </button>
            <button @click="suspendClient" class="p-4 bg-amber-50 dark:bg-amber-500/10 hover:bg-amber-100 dark:hover:bg-amber-500/20 rounded-lg text-left transition-colors">
              <p class="font-medium text-amber-700 dark:text-amber-400">Suspend Account</p>
              <p class="text-xs text-amber-600 dark:text-amber-500 mt-1">Temporarily disable</p>
            </button>
            <button @click="forceLogout" class="p-4 bg-red-50 dark:bg-red-500/10 hover:bg-red-100 dark:hover:bg-red-500/20 rounded-lg text-left transition-colors">
              <p class="font-medium text-red-700 dark:text-red-400">Force Logout</p>
              <p class="text-xs text-red-600 dark:text-red-500 mt-1">End all sessions</p>
            </button>
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
    const activeTab = ref('overview')
    const profile = ref({ devices: [], sessions: [], transactions: [], vouchers: [], stats: {} })
    const analytics = ref({})
    const showBalanceModal = ref(false)
    const showPointsModal = ref(false)
    const balanceAmount = ref(0)
    const balanceReason = ref('')
    const pointsAmount = ref(0)
    const pointsReason = ref('')

    const tabs = [
      { id: 'overview', label: 'Overview' },
      { id: 'devices', label: 'Devices' },
      { id: 'sessions', label: 'Sessions' },
      { id: 'transactions', label: 'Transactions' },
      { id: 'analytics', label: 'Analytics' },
      { id: 'actions', label: 'Actions' }
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

    const suspendClient = async () => {
      if (!confirm('Suspend this client?')) return
      try {
        await makeRequest('post', `suapi/clients/${props.client.id}/suspend/`, { reason: 'Admin action' })
        emit('refresh')
        emit('close')
      } catch (error) {
        console.error('Error suspending client:', error)
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

    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    }

    const formatNumber = (num) => new Intl.NumberFormat().format(num || 0)
    const formatDate = (date) => date ? new Date(date).toLocaleDateString() : 'N/A'

    watch(() => props.show, (newVal) => {
      if (newVal) fetchProfile()
    })

    return {
      activeTab, tabs, profile, analytics,
      showBalanceModal, showPointsModal,
      balanceAmount, balanceReason, pointsAmount, pointsReason,
      adjustBalance, awardPoints, suspendClient, forceLogout,
      getInitials, formatNumber, formatDate
    }
  }
}
</script>
