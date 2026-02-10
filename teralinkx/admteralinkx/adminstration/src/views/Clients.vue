<template>
  <div class="space-y-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Clients</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage client accounts</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="showAddModal = true" class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Client
        </button>
        <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
          <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 animate-slide-up">
      <ModernMetricCard title="Total Clients" :value="stats.total_clients" color="blue" :trend="stats.total_clients_trend?.direction" :trendValue="stats.total_clients_trend?.value">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Total Balance" :value="'KSh ' + formatNumber(stats.total_balance)" color="emerald" trend="stable" trendValue="0%">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Active" :value="stats.active_clients" color="cyan" :trend="stats.active_clients_trend?.direction" :trendValue="stats.active_clients_trend?.value" class="col-span-2 md:col-span-1">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="Premium" :value="stats.premium_clients" color="purple" :trend="stats.premium_clients_trend?.direction" :trendValue="stats.premium_clients_trend?.value">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      </ModernMetricCard>
      <ModernMetricCard title="New (7d)" :value="stats.new_clients_7d" color="amber" :trend="stats.new_clients_7d_trend?.direction" :trendValue="stats.new_clients_7d_trend?.value">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </ModernMetricCard>
    </div>

    <!-- Search & Filters -->
    <div class="space-y-3 animate-slide-up" style="animation-delay: 0.1s">
      <div class="flex items-center gap-2">
        <div class="flex-1">
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Search by username, phone, or account..."
            class="w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
          />
        </div>
        <select v-model="statusFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>
        <select v-model="tierFilter" class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
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
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Client</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Contact</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Tier</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Balance</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Points</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Joined</th>
                <th class="px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="client in filteredClients" :key="client.id" @click="viewClient(client)" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer">
                <td class="px-3 py-2">
                  <div class="flex items-center gap-2">
                    <div v-if="client.profile_image" class="w-7 h-7 rounded-full overflow-hidden flex-shrink-0">
                      <img :src="client.profile_image" alt="Profile" class="w-full h-full object-cover" @error="handleImageError" />
                    </div>
                    <div v-else class="w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center flex-shrink-0">
                      <svg class="w-4 h-4 text-slate-400 dark:text-slate-500" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                      </svg>
                    </div>
                    <div>
                      <p class="text-xs font-medium text-slate-900 dark:text-white">{{ client.user_username }}</p>
                      <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ client.account }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-3 py-2">
                  <p class="text-xs text-slate-900 dark:text-white">{{ client.phone_number || 'N/A' }}</p>
                  <p class="text-[10px] text-slate-500 dark:text-slate-400">{{ client.user_email || 'No email' }}</p>
                </td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getTierBadge(client.account_tier)">
                    {{ client.account_tier }}
                  </span>
                </td>
                <td class="px-3 py-2">
                  <p class="text-xs font-semibold text-slate-900 dark:text-white">KSh {{ formatNumber(client.balance) }}</p>
                </td>
                <td class="px-3 py-2">
                  <div class="flex items-center gap-1">
                    <svg class="w-3 h-3 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                    </svg>
                    <span class="text-xs text-slate-900 dark:text-white">{{ client.reward_points }}</span>
                  </div>
                </td>
                <td class="px-3 py-2">
                  <span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getStatusBadge(client.status)">
                    {{ client.status }}
                  </span>
                </td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">
                  {{ formatDate(client.created_at) }}
                </td>
                <td class="px-3 py-2 text-right">
                  <div class="flex items-center justify-end gap-0.5">
                    <button @click.stop="viewClient(client)" class="p-1 hover:bg-slate-100 dark:hover:bg-slate-600 rounded transition-colors" title="View">
                      <svg class="w-3.5 h-3.5 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button @click.stop="editClient(client)" class="p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors" title="Edit">
                      <svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button @click.stop="deleteClient(client)" class="p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors" title="Delete">
                      <svg class="w-3.5 h-3.5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Client Detail Modal -->
    <ClientDetailModal :show="showDetailModal" :client="selectedClient" @close="showDetailModal = false" @refresh="refreshData" />

    <!-- Add/Edit Client Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeFormModal">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-xl font-semibold text-slate-900 dark:text-white">{{ showEditModal ? 'Edit Client' : 'Add New Client' }}</h2>
          <button @click="closeFormModal" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Username</label>
              <input v-model="formData.username" type="text" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" :disabled="showEditModal" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Email</label>
              <input v-model="formData.email" type="email" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Phone Number</label>
              <input v-model="formData.phone_number" type="text" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Display Name</label>
              <input v-model="formData.display_name" type="text" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Account Tier</label>
              <select v-model="formData.account_tier" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm">
                <option value="basic">Basic</option>
                <option value="premium">Premium</option>
                <option value="business">Business</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Status</label>
              <select v-model="formData.status" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Balance</label>
              <input v-model="formData.balance" type="number" step="0.01" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Credit Limit</label>
              <input v-model="formData.credit_limit" type="number" step="0.01" class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm" />
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-2 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="closeFormModal" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm">Cancel</button>
          <button @click="saveClient" class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm">{{ showEditModal ? 'Update' : 'Create' }}</button>
        </div>
      </div>
    </div>
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
    const stats = ref({ total_clients: 0, active_clients: 0, premium_clients: 0, new_clients_7d: 0, total_balance: 0 })
    const searchTerm = ref('')
    const statusFilter = ref('')
    const tierFilter = ref('')
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const showDetailModal = ref(false)
    const selectedClient = ref(null)
    const formData = ref({
      username: '',
      email: '',
      phone_number: '',
      display_name: '',
      account_tier: 'basic',
      status: 'active',
      balance: 0,
      credit_limit: 0
    })

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

    const editClient = (client) => {
      selectedClient.value = client
      formData.value = {
        username: client.user_username,
        email: client.user_email || '',
        phone_number: client.phone_number || '',
        display_name: client.display_name || '',
        account_tier: client.account_tier,
        status: client.status,
        balance: client.balance,
        credit_limit: client.credit_limit
      }
      showEditModal.value = true
    }

    const deleteClient = async (client) => {
      if (!confirm(`Delete client ${client.user_username}? This action cannot be undone.`)) return
      try {
        await makeRequest('delete', `suapi/clients/${client.id}/`)
        await refreshData()
      } catch (err) {
        console.error('Error deleting client:', err)
        alert('Failed to delete client')
      }
    }

    const saveClient = async () => {
      try {
        if (showEditModal.value) {
          await makeRequest('patch', `suapi/clients/${selectedClient.value.id}/`, formData.value)
        } else {
          await makeRequest('post', 'suapi/clients/', formData.value)
        }
        closeFormModal()
        await refreshData()
      } catch (err) {
        console.error('Error saving client:', err)
        alert('Failed to save client')
      }
    }

    const closeFormModal = () => {
      showAddModal.value = false
      showEditModal.value = false
      formData.value = {
        username: '',
        email: '',
        phone_number: '',
        display_name: '',
        account_tier: 'basic',
        status: 'active',
        balance: 0,
        credit_limit: 0
      }
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

    const handleImageError = (event) => {
      event.target.parentElement.innerHTML = `
        <svg class="w-4 h-4 text-slate-400 dark:text-slate-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
      `
    }

    onMounted(refreshData)

    return {
      loading, error, clients, stats, searchTerm, statusFilter, tierFilter,
      filteredClients, fetchClients, refreshData, 
      showAddModal, showEditModal, showDetailModal, selectedClient, formData,
      viewClient, editClient, deleteClient, saveClient, closeFormModal,
      getInitials, getTierBadge, getStatusBadge, formatNumber, formatDate, handleImageError
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
