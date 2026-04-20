<template>
  <div class="space-y-6">
    <GuidePanel title="Loan Repayment Schedule" :terms="[
      { label: 'Repayment Schedule', color: 'blue', description: 'Amortization table showing principal + interest breakdown for each installment.' },
      { label: 'Outstanding', color: 'amber', description: 'Remaining balance after all payments made to date.' },
    ]" note="Select an investment/loan to view its full repayment schedule." />

    <div class="flex items-center gap-4">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Loan Repayment</h2>
      <select v-model="selectedId" @change="load" class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
        <option value="">Select Loan / Investment</option>
        <option v-for="inv in investments" :key="inv.id" :value="inv.id">{{ inv.name }} (KES {{ fmt(inv.amount) }})</option>
      </select>
    </div>

    <div v-if="schedule.length" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">#</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Due Date</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Principal</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Interest</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Total</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Balance</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="r in schedule" :key="r.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 text-slate-500 text-xs">{{ r.installment_number }}</td>
              <td class="px-4 py-3 text-xs text-slate-600 dark:text-slate-400">{{ fmtDate(r.due_date) }}</td>
              <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{{ fmt(r.principal_amount) }}</td>
              <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{{ fmt(r.interest_amount) }}</td>
              <td class="px-4 py-3 text-right font-medium text-slate-900 dark:text-white">{{ fmt(r.total_payment) }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">{{ fmt(r.outstanding_balance) }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="statusClass(r.status)">{{ r.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else-if="selectedId" class="text-center py-12 text-slate-400">No schedule found for this loan.</div>
    <div v-else class="text-center py-12 text-slate-400">Select a loan to view its repayment schedule.</div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'LoanRepayment',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { investments: [], schedule: [], selectedId: '' } },
  methods: {
    fmt(v) { return Number(v || 0).toLocaleString('en-KE', { minimumFractionDigits: 2 }) },
    fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' }) : '—' },
    statusClass(s) {
      return { paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               pending: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
               overdue: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }[s] || 'bg-slate-100 text-slate-600'
    },
    async loadInvestments() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/investments/', null, false)
        this.investments = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async load() {
      if (!this.selectedId) return
      try {
        const data = await this.makeRequest('get', `api/finance/api/investments/${this.selectedId}/repayment/`, null, false)
        this.schedule = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    }
  },
  mounted() { this.loadInvestments() }
}
</script>
