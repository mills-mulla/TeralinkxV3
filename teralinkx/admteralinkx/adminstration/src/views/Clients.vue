<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Clients</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage client accounts and profiles</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="showAddModal = true" class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Client
        </button>
        <button @click="refreshData" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
          <svg class="w-5 h-5 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load clients</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchClients" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Clients" :value="stats.total_clients" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Active" :value="stats.active_clients" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Premium" :value="stats.premium_clients" color="purple">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="New (7d)" :value="stats.new_clients_7d" color="cyan">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-3">
        <div class="flex-1">
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Search by username, phone, or account..."
            class="w-full px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
          />
        </div>
        <select v-model="statusFilter" class="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>
        <select v-model="tierFilter" class="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm">
          <option value="">All Tiers</option>
          <option value="basic">Basic</option>
          <option value="premium">Premium</option>
          <option value="business">Business</option>
          <option value="enterprise">Enterprise</option>
        </select>
      </div>

      <!-- Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-600 dark:text-slate-400">Client</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-600 dark:text-slate-400">Contact</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-600 dark:text-slate-400">Tier</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-600 dark:text-slate-400">Balance</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-600 dark:text-slate-400">Points</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-600 dark:text-slate-400">Joined</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="client in filteredClients" :key="client.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-4 py-3">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                      {{ getInitials(client.user_username) }}
                    </div>
                    <div>
                      <p class="text-sm font-medium text-slate-900 dark:text-white">{{ client.user_username }}</p>
                      <p class="text-xs text-slate-500 dark:text-slate-400">{{ client.account }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <p class="text-sm text-slate-900 dark:text-white">{{ client.phone_number || 'N/A' }}</p>
                  <p class="text-xs text-slate-500 dark:text-slate-400">{{ client.user_email || 'No email' }}</p>
                </td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getTierBadge(client.account_tier)">
                    {{ client.account_tier }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <p class="text-sm font-semibold text-slate-900 dark:text-white">KSh {{ formatNumber(client.balance) }}</p>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                    </svg>
                    <span class="text-sm text-slate-900 dark:text-white">{{ client.reward_points }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getStatusBadge(client.status)">
                    {{ client.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-slate-600 dark:text-slate-400">
                  {{ formatDate(client.created_at) }}
                </td>
                <td class="px-4 py-3 text-right">
                  <button @click="viewClient(client)" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-600 rounded transition-colors">
                    <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Client Detail Modal -->
    <ClientDetailModal :show="showDetailModal" :client="selectedClient" @close="showDetailModal = false" @refresh="refreshData" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import ClientDetailModal from '../components/ClientDetailModal.vue'

export default {
  name: 'Clients',
  components: { ModernMetricCard, ClientDetailModal },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const clients = ref([])
    const stats = ref({ total_clients: 0, active_clients: 0, premium_clients: 0, new_clients_7d: 0 })
    const searchTerm = ref('')
    const statusFilter = ref('')
    const tierFilter = ref('')
    const showAddModal = ref(false)
    const showDetailModal = ref(false)
    const selectedClient = ref(null)

    const filteredClients = computed(() => {
      let result = clients.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(c => 
          c.user_username?.toLowerCase().includes(term) || 
          c.phone_number?.includes(term) ||
          c.account?.toLowerCase().includes(term)
        )
      }
      if (statusFilter.value) {
        result = result.filter(c => c.status === statusFilter.value)
      }
      if (tierFilter.value) {
        result = result.filter(c => c.account_tier === tierFilter.value)
      }
      return result
    })

    const fetchClients = async () => {
      try {
        const data = await makeRequest('get', 'suapi/clients/')
        clients.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        const data = await makeRequest('get', 'suapi/clients/stats/')
        stats.value = data || stats.value
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchClients(), fetchStats()])
    
    const viewClient = (client) => {
      selectedClient.value = client
      showDetailModal.value = true
    }
    
    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
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

    const formatNumber = (num) => {
      return new Intl.NumberFormat().format(num || 0)
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString()
    }

    onMounted(refreshData)

    return {
      loading, error, clients, stats, searchTerm, statusFilter, tierFilter,
      filteredClients, fetchClients, refreshData, showAddModal,
      showDetailModal, selectedClient, viewClient,
      getInitials, getTierBadge, getStatusBadge, formatNumber, formatDate
    }
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.4s ease-out;
}
</style>
