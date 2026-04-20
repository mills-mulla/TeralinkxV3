<template>
  <div class="space-y-6">

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="s in statCards" :key="s.label" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <p class="text-xs text-slate-500 mb-1">{{ s.label }}</p>
        <p class="text-2xl font-bold" :class="s.color">{{ s.value }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg w-fit">
      <button v-for="t in ['History', 'Process Refund', 'Eligible Clients']" :key="t"
        @click="tab = t"
        :class="['px-4 py-1.5 rounded-md text-sm font-medium transition-colors',
          tab === t ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                    : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300']">
        {{ t }}
      </button>
    </div>

    <!-- ── History Tab ── -->
    <div v-if="tab === 'History'">
      <div class="flex items-center justify-between mb-3">
        <div class="flex gap-2">
          <select v-model="historyFilter" @change="loadHistory"
            class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
            <option value="">All Types</option>
            <option value="individual">Individual</option>
            <option value="batch">Batch</option>
            <option value="sla">SLA Credit</option>
          </select>
          <select v-model="historyStatus" @change="loadHistory"
            class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
            <option value="">All Status</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
          </select>
        </div>
        <button @click="loadHistory" class="px-3 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm hover:bg-slate-300">Refresh</button>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 dark:bg-slate-900">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Account</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount (KES)</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Downtime</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Type</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="r in history" :key="r.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                <td class="px-4 py-3 font-mono text-xs text-slate-600 dark:text-slate-400">{{ r.account }}</td>
                <td class="px-4 py-3 text-slate-700 dark:text-slate-300">{{ r.client_username || '—' }}</td>
                <td class="px-4 py-3 text-right font-medium text-emerald-600">{{ fmt(r.refund_amount) }}</td>
                <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">{{ r.downtime_minutes }}min</td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 rounded text-xs font-medium" :class="typeBadge(r.refund_type)">{{ r.refund_type }}</span>
                </td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 rounded text-xs font-medium" :class="r.status === 'completed' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'">
                    {{ r.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-xs text-slate-500">{{ fmtDate(r.created_at) }}</td>
              </tr>
              <tr v-if="!history.length">
                <td colspan="7" class="px-4 py-8 text-center text-slate-400">No refund history</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── Process Refund Tab ── -->
    <div v-if="tab === 'Process Refund'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- Individual Refund -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 space-y-4">
        <h3 class="font-semibold text-slate-900 dark:text-white">Individual Refund</h3>

        <div>
          <label class="text-xs text-slate-500 mb-1 block">Customer Account</label>
          <input v-model="individual.account" @blur="previewIndividual" placeholder="e.g. ACC-001"
            class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
        </div>
        <div>
          <label class="text-xs text-slate-500 mb-1 block">Downtime Minutes</label>
          <input v-model.number="individual.downtime_minutes" @blur="previewIndividual" type="number" min="1" placeholder="e.g. 60"
            class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
        </div>

        <!-- Preview result — calculated backend -->
        <div v-if="preview" class="rounded-lg p-4 space-y-2" :class="preview.eligible === false ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800' : 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800'">
          <div v-if="preview.eligible === false" class="text-sm text-red-600 dark:text-red-400">{{ preview.error }}</div>
          <template v-else>
            <div class="flex justify-between text-sm">
              <span class="text-slate-600 dark:text-slate-400">Customer</span>
              <span class="font-medium text-slate-900 dark:text-white">{{ preview.username }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-slate-600 dark:text-slate-400">Package</span>
              <span class="text-slate-700 dark:text-slate-300">{{ preview.duration }} @ KES {{ fmt(preview.package_price) }}</span>
            </div>
            <div class="flex justify-between text-sm font-semibold">
              <span class="text-slate-700 dark:text-slate-300">Calculated Refund</span>
              <span class="text-emerald-600 text-lg">KES {{ fmt(preview.refund_amount) }}</span>
            </div>
          </template>
        </div>

        <button @click="processIndividual" :disabled="!preview || preview.eligible === false || processing"
          class="w-full py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          {{ processing ? 'Processing...' : 'Confirm & Process Refund' }}
        </button>

        <div v-if="individualResult" class="text-sm text-center font-medium" :class="individualResult.success ? 'text-emerald-600' : 'text-red-500'">
          {{ individualResult.message }}
        </div>
      </div>

      <!-- Batch Refund -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 space-y-4">
        <h3 class="font-semibold text-slate-900 dark:text-white">Batch Refund — All Eligible</h3>
        <p class="text-xs text-slate-500">Applies refund to all currently eligible customers based on downtime minutes. Calculation is done server-side per customer package.</p>

        <div>
          <label class="text-xs text-slate-500 mb-1 block">Downtime Minutes (applies to all)</label>
          <input v-model.number="batch.downtime_minutes" type="number" min="1" placeholder="e.g. 120"
            class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" />
        </div>

        <div class="bg-slate-50 dark:bg-slate-900 rounded-lg p-3 text-sm space-y-1">
          <div class="flex justify-between"><span class="text-slate-500">Eligible customers</span><span class="font-medium text-slate-900 dark:text-white">{{ stats.eligible_clients || 0 }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Min downtime for refund</span><span class="font-medium text-slate-900 dark:text-white">10 min</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Extra bonus threshold</span><span class="font-medium text-slate-900 dark:text-white">&gt;15 min (+20%)</span></div>
        </div>

        <button @click="processBatch" :disabled="!batch.downtime_minutes || batchProcessing"
          class="w-full py-2.5 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          {{ batchProcessing ? 'Processing...' : `Batch Refund All ${stats.eligible_clients || ''} Customers` }}
        </button>

        <!-- Batch results -->
        <div v-if="batchResult" class="space-y-2">
          <div class="flex justify-between text-sm font-semibold">
            <span class="text-slate-700 dark:text-slate-300">Total Refunded</span>
            <span class="text-emerald-600">KES {{ fmt(batchResult.total_refunded) }}</span>
          </div>
          <div class="max-h-48 overflow-y-auto space-y-1">
            <div v-for="r in batchResult.results" :key="r.account"
              class="flex items-center justify-between text-xs px-2 py-1 rounded"
              :class="r.status.includes('✅') ? 'bg-emerald-50 dark:bg-emerald-900/20' : 'bg-slate-50 dark:bg-slate-900'">
              <span class="text-slate-600 dark:text-slate-400">{{ r.username || r.account }}</span>
              <span>{{ r.status }} <span v-if="r.refund_amount > 0" class="font-medium text-emerald-600">KES {{ fmt(r.refund_amount) }}</span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Eligible Clients Tab ── -->
    <div v-if="tab === 'Eligible Clients'">
      <div class="flex items-center justify-between mb-3">
        <p class="text-sm text-slate-500">{{ eligibleClients.length }} eligible customers</p>
        <button @click="loadEligible" class="px-3 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm hover:bg-slate-300">Refresh</button>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 dark:bg-slate-900">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Account</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Package</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Price</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Balance</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
              <tr v-for="c in eligibleClients" :key="c.dispatch_account" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                <td class="px-4 py-3 font-mono text-xs text-slate-600 dark:text-slate-400">{{ c.dispatch_account }}</td>
                <td class="px-4 py-3 text-slate-700 dark:text-slate-300">{{ c.username }}</td>
                <td class="px-4 py-3 text-xs text-slate-500">{{ c.dispatch_package_duration }}</td>
                <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{{ fmt(c.dispatch_price) }}</td>
                <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{{ fmt(c.current_balance) }}</td>
                <td class="px-4 py-3">
                  <span class="px-2 py-1 rounded text-xs" :class="c.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'">{{ c.status }}</span>
                </td>
                <td class="px-4 py-3">
                  <button @click="quickRefund(c)" class="text-xs text-blue-600 hover:underline">Refund</button>
                </td>
              </tr>
              <tr v-if="!eligibleClients.length">
                <td colspan="7" class="px-4 py-8 text-center text-slate-400">No eligible clients</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { useApi } from '../composables/useApi'
export default {
  name: 'Refunds',
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      tab: 'History',
      stats: {},
      history: [],
      historyFilter: '',
      historyStatus: '',
      eligibleClients: [],
      individual: { account: '', downtime_minutes: '' },
      preview: null,
      processing: false,
      individualResult: null,
      batch: { downtime_minutes: '' },
      batchProcessing: false,
      batchResult: null,
    }
  },
  computed: {
    statCards() {
      return [
        { label: 'Eligible Clients',  value: this.stats.eligible_clients || 0,                                    color: 'text-blue-600' },
        { label: 'Total Refunded',    value: 'KES ' + this.fmt(this.stats.total_refunded || 0),                   color: 'text-emerald-600' },
        { label: 'Pending',           value: this.stats.pending_refunds || 0,                                     color: 'text-amber-500' },
        { label: 'Avg Refund',        value: 'KES ' + this.fmt(this.stats.average_refund || 0),                   color: 'text-purple-600' },
      ]
    }
  },
  methods: {
    fmt(v) { return Number(v || 0).toLocaleString('en-KE', { minimumFractionDigits: 2 }) },
    fmtDate(d) { return d ? new Date(d).toLocaleString('en-KE', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—' },
    typeBadge(t) {
      return { individual: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               batch: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
               sla: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400' }[t] || 'bg-slate-100 text-slate-600'
    },
    async loadStats() {
      try { this.stats = await this.makeRequest('get', 'suapi/refunds/stats/', null, false) } catch (e) { console.error(e) }
    },
    async loadHistory() {
      try {
        let url = 'suapi/refunds/history/?limit=100'
        if (this.historyFilter) url += `&refund_type=${this.historyFilter}`
        if (this.historyStatus) url += `&status=${this.historyStatus}`
        const data = await this.makeRequest('get', url, null, false)
        this.history = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async loadEligible() {
      try {
        const data = await this.makeRequest('get', 'suapi/refunds/eligible_clients/', null, false)
        this.eligibleClients = Array.isArray(data) ? data : []
      } catch (e) { console.error(e) }
    },
    async previewIndividual() {
      if (!this.individual.account || !this.individual.downtime_minutes) { this.preview = null; return }
      try {
        this.preview = await this.makeRequest('post', 'suapi/refunds/preview/', this.individual, false)
      } catch (e) {
        this.preview = { eligible: false, error: e.response?.data?.error || 'Preview failed' }
      }
    },
    async processIndividual() {
      if (!this.preview || this.preview.eligible === false) return
      this.processing = true
      this.individualResult = null
      try {
        const res = await this.makeRequest('post', 'suapi/refunds/process_individual/', this.individual, false)
        this.individualResult = { success: true, message: res.message }
        this.individual = { account: '', downtime_minutes: '' }
        this.preview = null
        this.loadStats()
        this.loadHistory()
      } catch (e) {
        this.individualResult = { success: false, message: e.response?.data?.error || 'Failed' }
      } finally { this.processing = false }
    },
    async processBatch() {
      if (!this.batch.downtime_minutes) return
      this.batchProcessing = true
      this.batchResult = null
      try {
        this.batchResult = await this.makeRequest('post', 'suapi/refunds/batch_refund/', this.batch, false)
        this.loadStats()
        this.loadHistory()
      } catch (e) { console.error(e) }
      finally { this.batchProcessing = false }
    },
    quickRefund(client) {
      this.tab = 'Process Refund'
      this.individual.account = client.dispatch_account
    },
  },
  mounted() {
    this.loadStats()
    this.loadHistory()
  },
  watch: {
    tab(val) {
      if (val === 'Eligible Clients' && !this.eligibleClients.length) this.loadEligible()
    }
  }
}
</script>
