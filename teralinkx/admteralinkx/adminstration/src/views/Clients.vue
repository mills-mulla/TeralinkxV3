<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Clients</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage client accounts</p>
      </div>
      <button @click="refreshData" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
        <ArrowPathIcon class="w-5 h-5 text-slate-600 dark:text-slate-400" />
      </button>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <ExclamationTriangleIcon class="w-5 h-5 text-rose-600 dark:text-rose-400" />
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
      <ModernMetricCard title="Total Clients" :value="stats.total_clients" icon="👥" color="blue" />
      <ModernMetricCard title="Active" :value="stats.active_clients" icon="✅" color="emerald" />
      <ModernMetricCard title="Premium" :value="stats.premium_clients" icon="⭐" color="purple" />
      <ModernMetricCard title="New (7d)" :value="stats.new_clients_7d" icon="🚀" color="cyan" />
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search clients..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        :show-add-button="false"
      />

      <DataTable
        title="Client Records"
        :data="filteredClients"
        :columns="columns"
        :actions="[]"
      >
        <template #cell-is_active="{ value }">
          <span :class="value ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'" class="px-2 py-0.5 text-xs font-medium rounded-full">
            {{ value ? 'Active' : 'Inactive' }}
          </span>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'
import SearchBar from '../components/SearchBar.vue'
import DataTable from '../components/DataTable.vue'
import { ArrowPathIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'Clients',
  components: { ModernMetricCard, SearchBar, DataTable, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const clients = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'user_username', label: 'Username', sortable: true },
      { key: 'phone_number', label: 'Phone', sortable: true },
      { key: 'current_balance', label: 'Balance', sortable: true, format: (v) => `KSh ${v}` },
      { key: 'reward_points', label: 'Points', sortable: true },
      { key: 'is_active', label: 'Status', sortable: true },
      { key: 'created_at', label: 'Joined', sortable: true, format: (v) => new Date(v).toLocaleDateString() }
    ]

    const filters = [
      { key: 'is_active', label: 'Status', options: [{ value: 'true', label: 'Active' }, { value: 'false', label: 'Inactive' }] }
    ]

    const filteredClients = computed(() => {
      let result = clients.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(c => c.user_username?.toLowerCase().includes(term) || c.phone_number?.includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(c => c[key] === (value === 'true'))
      })
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
        stats.value = await makeRequest('get', 'suapi/clients/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchClients(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }

    onMounted(refreshData)

    return {
      loading, error, clients, stats, searchTerm, columns, filters, filteredClients,
      fetchClients, refreshData, handleFilterChange, clearFilters
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
