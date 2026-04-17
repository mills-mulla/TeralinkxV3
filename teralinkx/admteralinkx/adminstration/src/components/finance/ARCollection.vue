<template>
  <div class="space-y-6">
    <GuidePanel title="AR Collection" :terms="[
        { label: 'AR Aging', color: 'blue', description: 'How long customer invoices have been outstanding. Older = higher bad debt risk.' },
        { label: 'Collection Queue', color: 'red', description: 'Sorted by amount × days overdue. Highest priority at top.' },
        { label: 'Escalation', color: 'amber', description: 'Reminder → Warning → Suspension → Legal. Auto-set based on days overdue.' },
        { label: 'Write-Off', color: 'slate', description: 'Formally record uncollectable debt. Requires approval. Affects P&L.' },
      ]" note="Collection cases are auto-created daily for overdue invoices. Escalation levels set automatically based on days overdue." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">AR Collection</h2>
      <div class="flex gap-3">
        <button @click="refresh" :disabled="refreshing" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm hover:bg-slate-300 disabled:opacity-50">
          {{ refreshing ? 'Updating...' : 'Update Cases' }}
        </button>
        <button @click="load" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">Refresh</button>
      </div>
    </div>

    <!-- Aging Summary -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-3" v-if="aging">
      <div v-for="(label, key) in { current: 'Current', '31_60': '31-60d', '61_90': '61-90d', over_90: '90d+' }" :key="key"
        class="bg-white dark:bg-slate-800 rounded-xl p-4 border"
        :class="key === 'over_90' ? 'border-red-300 dark:border-red-700' : 'border-slate-200 dark:border-slate-700'">
        <p class="text-xs font-medium" :class="key === 'over_90' ? 'text-red-600' : 'text-slate-500'">{{ label }}</p>
        <p class="text-lg font-bold text-slate-900 dark:text-white mt-1">KES {{ fmt(aging.totals && aging.totals[key]) }}</p>
        <p class="text-xs text-slate-400">{{ aging.buckets && aging.buckets[key] }} customers</p>
      </div>
      <div class="bg-slate-50 dark:bg-slate-700/50 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Open Cases</p>
        <p class="text-lg font-bold text-slate-900 dark:text-white mt-1">{{ aging.open_cases || 0 }}</p>
        <p class="text-xs text-slate-400">active</p>
      </div>
    </div>

    <!-- Collection Queue -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Collection Queue — sorted by priority</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount Overdue</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Days</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Escalation</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="c in cases" :key="c.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ c.customer?.account }}</td>
              <td class="px-4 py-3 text-right font-semibold text-red-600 dark:text-red-400">KES {{ fmt(c.amount_overdue) }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">{{ c.days_overdue }}d</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="escalationBadge(c.escalation_level)">{{ c.escalation_display }}</span>
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(c.status)">{{ c.status_display }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button @click="doAction(c.id,'escalate')" class="px-2 py-1 bg-amber-600 text-white rounded text-xs hover:bg-amber-700">Escalate</button>
                  <button @click="doAction(c.id,'resolve')" class="px-2 py-1 bg-emerald-600 text-white rounded text-xs hover:bg-emerald-700">Resolve</button>
                  <button @click="doAction(c.id,'write_off')" class="px-2 py-1 bg-slate-600 text-white rounded text-xs hover:bg-slate-700">Write Off</button>
                </div>
              </td>
            </tr>
            <tr v-if="!cases.length">
              <td colspan="6" class="px-4 py-8 text-center text-slate-400">No open collection cases — all customers are current</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'ARCollection',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { cases: [], aging: null, loading: false, refreshing: false } },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    escalationBadge(e) {
      return { reminder: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
               suspension: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
               legal: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }[e] || 'bg-slate-100 text-slate-800'
    },
    statusBadge(s) {
      return { open: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
               in_progress: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               resolved: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               written_off: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      this.loading = true
      try {
        const [queue, agingData] = await Promise.allSettled([
          this.makeRequest('get', 'api/finance/api/ar/collection/', null, false),
          this.makeRequest('get', 'api/finance/api/ar/aging/', null, false)
        ])
        if (queue.status === 'fulfilled') this.cases = queue.value.results || []
        if (agingData.status === 'fulfilled') this.aging = agingData.value
      } catch (e) { console.error(e) }
      finally { this.loading = false }
    },
    async refresh() {
      this.refreshing = true
      try { await this.makeRequest('post', 'api/finance/api/ar/collection/refresh/', {}); await this.load() }
      catch (e) { console.error(e) }
      finally { this.refreshing = false }
    },
    async doAction(id, act) {
      if (act === 'write_off' && !confirm('Write off this debt? This cannot be undone.')) return
      try { await this.makeRequest('patch', `api/finance/api/ar/collection/${id}/`, { action: act }); await this.load() }
      catch (e) { console.error(e) }
    }
  },
  mounted() { this.load() }
}
</script>
