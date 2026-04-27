<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Point Transactions</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Track reward points activity</p>
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
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load transactions</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="fetchTransactions" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <!-- Metrics -->
    <div class="flex items-center gap-2 flex-wrap">
      <div class="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-xl">
        <span class="text-[10px] text-blue-600 dark:text-blue-400 font-medium">🏆 Transactions</span>
        <span class="text-sm font-bold text-blue-700 dark:text-blue-300">{{ stats.total_transactions || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-xl">
        <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">➕ Earned</span>
        <span class="text-sm font-bold text-emerald-700 dark:text-emerald-300">{{ stats.total_earned || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-xl">
        <span class="text-[10px] text-rose-600 dark:text-rose-400 font-medium">➖ Redeemed</span>
        <span class="text-sm font-bold text-rose-700 dark:text-rose-300">{{ stats.total_redeemed || 0 }}</span>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20 rounded-xl">
        <span class="text-[10px] text-purple-600 dark:text-purple-400 font-medium">💰 Net Balance</span>
        <span class="text-sm font-bold text-purple-700 dark:text-purple-300">{{ stats.net_balance || 0 }}</span>
      </div>
    </div>

    <!-- Search & Table -->
    <div class="space-y-4 animate-slide-up" style="animation-delay: 0.1s">
      <SearchBar
        v-model="searchTerm"
        placeholder="Search transactions..."
        :filters="filters"
        @filter-change="handleFilterChange"
        @clear="clearFilters"
        :show-add-button="false"
      />

      <DataTable
        title="Transaction Records"
        :data="filteredTransactions"
        :columns="columns"
        :actions="[]"
      >
        <template #cell-transaction_type="{ value }">
          <span :class="value === 'earn' ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-400'" class="px-2 py-0.5 text-xs font-medium rounded-full">
            {{ value === 'earn' ? '➕ Earned' : '➖ Redeemed' }}
          </span>
        </template>
        <template #cell-points="{ value, item }">
          <span :class="item.transaction_type === 'earn' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'" class="font-medium">
            {{ item.transaction_type === 'earn' ? '+' : '-' }}{{ value }}
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
  name: 'PointTransactions',
  components: { ModernMetricCard, SearchBar, DataTable, ArrowPathIcon, ExclamationTriangleIcon },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const transactions = ref([])
    const stats = ref({})
    const searchTerm = ref('')
    const activeFilters = ref({})

    const columns = [
      { key: 'id', label: 'ID', sortable: true },
      { key: 'user_username', label: 'User', sortable: true },
      { key: 'transaction_type', label: 'Type', sortable: true },
      { key: 'points', label: 'Points', sortable: true },
      { key: 'description', label: 'Description', sortable: true },
      { key: 'created_at', label: 'Date', sortable: true, format: (v) => new Date(v).toLocaleDateString() }
    ]

    const filters = [
      { key: 'transaction_type', label: 'Type', options: [{ value: 'earn', label: 'Earned' }, { value: 'redeem', label: 'Redeemed' }] }
    ]

    const filteredTransactions = computed(() => {
      let result = transactions.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => t.user_username?.toLowerCase().includes(term) || t.description?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(t => t[key] === value)
      })
      return result
    })

    const fetchTransactions = async () => {
      try {
        const data = await makeRequest('get', 'suapi/point-transactions/')
        transactions.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/point-transactions/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchTransactions(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }

    onMounted(refreshData)

    return {
      loading, error, transactions, stats, searchTerm, columns, filters, filteredTransactions,
      fetchTransactions, refreshData, handleFilterChange, clearFilters
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
