<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Transactions</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Payment transaction history</p>
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
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard title="Total Transactions" :value="stats.total_transactions" icon="💳" color="blue" />
      <ModernMetricCard title="Successful" :value="stats.successful_transactions" icon="✅" color="emerald" />
      <ModernMetricCard title="Failed" :value="stats.failed_transactions" icon="❌" color="rose" />
      <ModernMetricCard title="Total Amount" :value="`KSh ${formatNumber(stats.total_amount || 0)}`" icon="💰" color="purple" :formatted="false" />
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
        <template #cell-status="{ value }">
          <span :class="value === 'completed' ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : value === 'failed' ? 'bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-400' : 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400'" class="px-2 py-0.5 text-xs font-medium rounded-full">
            {{ value }}
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
  name: 'Transactions',
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
      { key: 'amount', label: 'Amount', sortable: true, format: (v) => `KSh ${v}` },
      { key: 'payment_method', label: 'Method', sortable: true },
      { key: 'status', label: 'Status', sortable: true },
      { key: 'created_at', label: 'Date', sortable: true, format: (v) => new Date(v).toLocaleDateString() }
    ]

    const filters = [
      { key: 'status', label: 'Status', options: [{ value: 'completed', label: 'Completed' }, { value: 'pending', label: 'Pending' }, { value: 'failed', label: 'Failed' }] },
      { key: 'payment_method', label: 'Method', options: [{ value: 'mpesa', label: 'M-Pesa' }, { value: 'card', label: 'Card' }, { value: 'cash', label: 'Cash' }] }
    ]

    const filteredTransactions = computed(() => {
      let result = transactions.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => t.user_username?.toLowerCase().includes(term) || t.transaction_id?.toLowerCase().includes(term))
      }
      Object.keys(activeFilters.value).forEach(key => {
        const value = activeFilters.value[key]
        if (value) result = result.filter(t => t[key] === value)
      })
      return result
    })

    const fetchTransactions = async () => {
      try {
        const data = await makeRequest('get', 'suapi/transactions/')
        transactions.value = data.results || data
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const fetchStats = async () => {
      try {
        stats.value = await makeRequest('get', 'suapi/transactions/stats/')
      } catch (err) {
        console.error('Error:', err)
      }
    }

    const refreshData = () => Promise.all([fetchTransactions(), fetchStats()])
    const handleFilterChange = ({ all }) => { activeFilters.value = all }
    const clearFilters = () => { searchTerm.value = ''; activeFilters.value = {} }
    const formatNumber = (num) => new Intl.NumberFormat().format(num)

    onMounted(refreshData)

    return {
      loading, error, transactions, stats, searchTerm, columns, filters, filteredTransactions,
      fetchTransactions, refreshData, handleFilterChange, clearFilters, formatNumber
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
