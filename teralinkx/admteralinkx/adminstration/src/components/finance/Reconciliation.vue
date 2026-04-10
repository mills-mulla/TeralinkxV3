<template>
  <div class="space-y-6">
    <GuidePanel title="Automated Reconciliation" :terms="[
        { label: 'Confidence Score', color: 'blue', description: 'How certain the system is that a bank entry matches a payment transaction. Based on amount, customer, date, and phone number matching.', formula: 'Amount(50) + Customer(30) + Date(15) + Phone(5) = max 100' },
        { label: 'Auto-Matched (85%+)', color: 'emerald', description: 'System is confident enough to match automatically. No human review needed.' },
        { label: 'Review Queue (60–84%)', color: 'amber', description: 'Likely match but needs human confirmation. Sorted by payment amount (largest first).' },
        { label: 'Manual Queue (<60%)', color: 'red', description: 'Low confidence. System shows top 3 candidates — human must select the correct match.' },
        { label: 'Auto-Match Rate', color: 'teal', description: 'Percentage of entries matched automatically. Target: 85%+. Higher means less manual work.' }
      ]" note="Bank statement entries are matched against PaymentTransaction records. Upload a new bank statement via the Create Job button to start reconciliation." />
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Reconciliation</h2>
      <button @click="refresh" :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">Refresh</button>
    </div>

    <!-- Stats -->
    <div v-if="stats" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 text-center">
        <p class="text-2xl font-bold text-blue-600">{{ stats.total_jobs || 0 }}</p>
        <p class="text-xs text-slate-500 mt-1">Total Jobs</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 text-center">
        <p class="text-2xl font-bold text-emerald-600">{{ stats.avg_auto_match_rate || 0 }}%</p>
        <p class="text-xs text-slate-500 mt-1">Auto-Match Rate</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 text-center">
        <p class="text-2xl font-bold text-amber-600">{{ stats.pending_review || 0 }}</p>
        <p class="text-xs text-slate-500 mt-1">Pending Review</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 text-center">
        <p class="text-2xl font-bold text-slate-700 dark:text-slate-300">{{ stats.avg_confidence || 0 }}%</p>
        <p class="text-xs text-slate-500 mt-1">Avg Confidence</p>
      </div>
    </div>

    <!-- Review Queue -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Review Queue</h3>
        <span class="text-xs text-slate-500">{{ reviewQueue.length }} items</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Reference</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Date</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Confidence</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="item in reviewQueue" :key="item.id"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-mono text-xs text-slate-700 dark:text-slate-300">{{ item.source_reference }}</td>
              <td class="px-4 py-3 text-right font-semibold text-slate-900 dark:text-white">KES {{ fmt(item.source_amount) }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ item.source_date }}</td>
              <td class="px-4 py-3 text-right">
                <span class="px-2 py-1 rounded-full text-xs font-bold"
                  :class="item.confidence_score >= 0.8 ? 'bg-emerald-100 text-emerald-800' : item.confidence_score >= 0.5 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'">
                  {{ (item.confidence_score * 100).toFixed(0) }}%
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-2">
                  <button @click="approve(item.id)"
                    class="px-2 py-1 bg-emerald-600 text-white rounded text-xs hover:bg-emerald-700">Approve</button>
                  <button @click="reject(item.id)"
                    class="px-2 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700">Reject</button>
                </div>
              </td>
            </tr>
            <tr v-if="!reviewQueue.length">
              <td colspan="5" class="px-4 py-8 text-center text-slate-400 text-sm">No items pending review</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Job History -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Job History</h3>
      </div>
      <div class="divide-y divide-slate-200 dark:divide-slate-700">
        <div v-for="job in jobs" :key="job.job_id"
          class="px-4 py-3 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-slate-900 dark:text-white font-mono">{{ job.job_id }}</p>
            <p class="text-xs text-slate-500">{{ job.period_start }} → {{ job.period_end }}</p>
          </div>
          <div class="text-right">
            <p class="text-sm font-semibold" :class="job.status === 'completed' ? 'text-emerald-600' : 'text-amber-600'">
              {{ job.status }}
            </p>
            <p class="text-xs text-slate-500">{{ job.auto_match_rate }}% matched</p>
          </div>
        </div>
        <div v-if="!jobs.length" class="px-4 py-8 text-center text-slate-400 text-sm">No jobs yet</div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  components: { GuidePanel, },
  name: 'Reconciliation',
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { loading: false, stats: null, reviewQueue: [], jobs: [] } },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    async approve(id) {
      try {
        await this.makeRequest('post', `api/finance/api/reconciliation/matches/${id}/approve/`, {})
        this.reviewQueue = this.reviewQueue.filter(i => i.id !== id)
      } catch (e) { console.error('Approve:', e) }
    },
    async reject(id) {
      try {
        await this.makeRequest('post', `api/finance/api/reconciliation/matches/${id}/reject/`, {})
        this.reviewQueue = this.reviewQueue.filter(i => i.id !== id)
      } catch (e) { console.error('Reject:', e) }
    },
    async refresh() {
      this.loading = true
      try {
        const [stats, queue, jobs] = await Promise.allSettled([
          this.makeRequest('get', 'api/finance/api/reconciliation/stats/'),
          this.makeRequest('get', 'api/finance/api/reconciliation/review-queue/'),
          this.makeRequest('get', 'api/finance/api/reconciliation/jobs/')
        ])
        this.stats       = stats.status === 'fulfilled' ? stats.value : null
        const q = queue.status === 'fulfilled' ? queue.value : []
        const j = jobs.status === 'fulfilled' ? jobs.value : []
        this.reviewQueue = Array.isArray(q) ? q : (q.results || [])
        this.jobs        = Array.isArray(j) ? j : (j.results || [])
      } catch (e) { console.error('Reconciliation fetch:', e) }
      finally { this.loading = false }
    }
  },
  mounted() { this.refresh() }
}
</script>
