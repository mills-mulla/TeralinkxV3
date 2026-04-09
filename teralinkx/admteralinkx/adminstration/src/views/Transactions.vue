<template>
  <div class="space-y-4 animate-fade-in">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-slate-900 dark:text-white">Transactions</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">All transaction types</p>
      </div>
      <button @click="refreshData" class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" :class="{ 'animate-spin': loading }">
        <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
      </button>
    </div>

    <div v-if="error" class="bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-rose-600 dark:text-rose-400" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          <div>
            <h3 class="text-sm font-medium text-rose-800 dark:text-rose-400">Failed to load transactions</h3>
            <p class="text-xs text-rose-600 dark:text-rose-500 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="refreshData" class="px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm">Retry</button>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up">
      <ModernMetricCard title="Total Revenue" :value="formatCurrency(stats.total_revenue)" color="emerald">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Completed" :value="stats.completed_count" color="blue">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Pending" :value="stats.pending_count" color="amber">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm4.2 14.2L11 13V7h1.5v5.2l4.5 2.7-.8 1.3z"/></svg>
      </ModernMetricCard>
      <ModernMetricCard title="Failed" :value="stats.failed_count" color="rose">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
      </ModernMetricCard>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden animate-slide-up" style="animation-delay: 0.1s">
      <div class="border-b border-slate-200 dark:border-slate-700">
        <div class="flex overflow-x-auto">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" class="px-4 py-2.5 text-xs font-medium whitespace-nowrap transition-colors" :class="activeTab === tab.id ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'">
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="p-4 space-y-3">
        <div class="flex items-center gap-2">
          <input v-model="searchTerm" type="text" placeholder="Search transactions..." class="flex-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs" />
          <select v-if="activeTab === 'queue'" v-model="statusFilter" class="px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        <div v-if="activeTab === 'payments'" class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Transaction ID</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Amount</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Method</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="txn in filteredPayments" :key="txn.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-3 py-2 text-xs font-mono text-slate-900 dark:text-white">{{ txn.transaction_id?.substring(0, 12) }}...</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ txn.initiator }}</td>
                <td class="px-3 py-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400">{{ formatCurrency(txn.amount) }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400">{{ txn.payment_method }}</span></td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getStatusClass(txn.status)">{{ txn.status }}</span></td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatDate(txn.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeTab === 'balance'" class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Amount</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Balance Before</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Balance After</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Description</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="txn in filteredBalance" :key="txn.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ txn.user_account || txn.user }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400">{{ txn.transaction_type }}</span></td>
                <td class="px-3 py-2 text-xs font-semibold" :class="txn.credit > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'">{{ txn.credit > 0 ? '+' : '-' }}{{ formatCurrency(Math.abs(txn.credit || txn.debit)) }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatCurrency(txn.balance_before) }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatCurrency(txn.balance_after) }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.description }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatDate(txn.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeTab === 'queue'" class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Package</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Price</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Method</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Status</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Retries</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="txn in filteredQueue" :key="txn.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-indigo-100 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-400">{{ txn.queue_type }}</span></td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ txn.initiator }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.package }}</td>
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ formatCurrency(txn.price) }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.method }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full" :class="getQueueStatusClass(txn.status)">{{ txn.status }}</span></td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.retry_count }}/{{ txn.max_retries }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatDate(txn.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeTab === 'points'" class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">User</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Type</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Points</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Description</th>
                <th class="px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="txn in filteredPoints" :key="txn.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-3 py-2 text-xs text-slate-900 dark:text-white">{{ txn.user_account || txn.user }}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400">{{ txn.transaction_type }}</span></td>
                <td class="px-3 py-2 text-xs font-semibold" :class="txn.points > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'">{{ txn.points > 0 ? '+' : '' }}{{ txn.points }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ txn.description }}</td>
                <td class="px-3 py-2 text-xs text-slate-600 dark:text-slate-400">{{ formatDate(txn.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import ModernMetricCard from '../components/MetricCard.vue'

export default {
  name: 'Transactions',
  components: { ModernMetricCard },
  setup() {
    const { loading, error, makeRequest } = useApi()
    const activeTab = ref('payments')
    const searchTerm = ref('')
    const statusFilter = ref('')
    const stats = ref({})
    const payments = ref([])
    const balance = ref([])
    const queue = ref([])
    const points = ref([])

    const tabs = [
      { id: 'payments', label: 'Payment Transactions' },
      { id: 'balance', label: 'Balance Transactions' },
      { id: 'queue', label: 'Transaction Queue' },
      { id: 'points', label: 'Point Transactions' }
    ]

    const filteredPayments = computed(() => {
      let result = payments.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => 
          t.transaction_id?.toLowerCase().includes(term) || 
          t.initiator?.toLowerCase().includes(term)
        )
      }
      return result
    })

    const filteredBalance = computed(() => {
      let result = balance.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => 
          t.user_account?.toLowerCase().includes(term) || 
          t.description?.toLowerCase().includes(term)
        )
      }
      return result
    })

    const filteredQueue = computed(() => {
      let result = queue.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => 
          t.initiator?.toLowerCase().includes(term) || 
          t.package?.toLowerCase().includes(term)
        )
      }
      if (statusFilter.value) {
        result = result.filter(t => t.status === statusFilter.value)
      }
      return result
    })

    const filteredPoints = computed(() => {
      let result = points.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        result = result.filter(t => 
          t.user_account?.toLowerCase().includes(term) || 
          t.description?.toLowerCase().includes(term)
        )
      }
      return result
    })

    const fetchPayments = async () => {
      try {
        const data = await makeRequest('get', 'suapi/payment-transactions/')
        payments.value = data.results || data
      } catch (err) { console.error('Error:', err) }
    }

    const fetchBalance = async () => {
      try {
        const data = await makeRequest('get', 'suapi/balance-transactions/')
        balance.value = data.results || data
      } catch (err) { console.error('Error:', err) }
    }

    const fetchQueue = async () => {
      try {
        const data = await makeRequest('get', 'suapi/transaction-queue/')
        queue.value = data.results || data
      } catch (err) { console.error('Error:', err) }
    }

    const fetchPoints = async () => {
      try {
        const data = await makeRequest('get', 'suapi/point-transactions-txn/')
        points.value = data.results || data
      } catch (err) { console.error('Error:', err) }
    }

    const fetchStats = async () => {
      try {
        const data = await makeRequest('get', 'finance/api/transaction-stats/')
        stats.value = {
          total_revenue: data.queue.total_amount || 0,
          completed_count: data.queue.completed || 0,
          pending_count: data.queue.pending || 0,
          failed_count: data.queue.failed || 0
        }
      } catch (err) { 
        console.error('Error fetching stats:', err)
        stats.value = { total_revenue: 0, completed_count: 0, pending_count: 0, failed_count: 0 }
      }
    }

    const refreshData = async () => {
      await fetchStats()
      await Promise.all([fetchPayments(), fetchBalance(), fetchQueue(), fetchPoints()])
    }

    const formatCurrency = (amount) => {
      if (!amount) return 'KSh 0'
      return `KSh ${parseFloat(amount).toLocaleString()}`
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleString('en-US', { 
        month: 'short', day: 'numeric', year: 'numeric', 
        hour: '2-digit', minute: '2-digit' 
      })
    }

    const getStatusClass = (status) => {
      const classes = {
        completed: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        refunded: 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        partially_refunded: 'bg-orange-100 dark:bg-orange-500/20 text-orange-700 dark:text-orange-400'
      }
      return classes[status] || 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'
    }

    const getQueueStatusClass = (status) => {
      const classes = {
        pending: 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        processing: 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        completed: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        failed: 'bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-400',
        processed: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400'
      }
      return classes[status] || 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400'
    }

    onMounted(refreshData)

    return {
      loading, error, activeTab, searchTerm, statusFilter, stats, tabs,
      filteredPayments, filteredBalance, filteredQueue, filteredPoints,
      refreshData, formatCurrency, formatDate, getStatusClass, getQueueStatusClass
    }
  }
}
</script>

<style scoped>
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes slide-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 0.3s ease-out; }
.animate-slide-up { animation: slide-up 0.4s ease-out; }
</style>
