<template>
  <div class="space-y-6">
    <GuidePanel title="KRA Tax Calendar" :terms="[
        { label: 'PAYE', color: 'blue', description: 'Pay As You Earn — employee income tax. Due 9th of following month.' },
        { label: 'VAT', color: 'amber', description: 'Value Added Tax (16%). Due 20th of following month.' },
        { label: 'WHT', color: 'purple', description: 'Withholding Tax (6% on services). Due 20th of following month.' },
        { label: 'NHIF/NSSF', color: 'emerald', description: 'Statutory deductions from payroll. Due 9th of following month.' },
        { label: 'Income Tax', color: 'red', description: 'Corporate income tax. Due 30 June following year.' },
      ]" note="Tax calendar auto-generates all filing deadlines. Mark returns as filed after submitting on KRA iTax portal." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">KRA Tax Calendar</h2>
      <div class="flex gap-3">
        <select v-model="selectedYear" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
        <select v-model="filterType" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All Types</option>
          <option value="vat">VAT</option>
          <option value="paye">PAYE</option>
          <option value="wht">WHT</option>
          <option value="nhif">NHIF</option>
          <option value="nssf">NSSF</option>
          <option value="income_tax">Income Tax</option>
        </select>
      </div>
    </div>

    <!-- Summary -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4" v-if="summary">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Total Returns</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">{{ summary.total }}</p>
      </div>
      <div class="bg-emerald-50 dark:bg-emerald-900/20 rounded-xl p-5 border border-emerald-200 dark:border-emerald-800">
        <p class="text-xs text-emerald-600 font-medium">Filed/Paid</p>
        <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">{{ (summary.filed || 0) + (summary.paid || 0) }}</p>
      </div>
      <div class="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-5 border border-amber-200 dark:border-amber-800">
        <p class="text-xs text-amber-600 font-medium">Pending</p>
        <p class="text-2xl font-bold text-amber-700 dark:text-amber-300 mt-1">{{ summary.pending || 0 }}</p>
      </div>
      <div class="bg-red-50 dark:bg-red-900/20 rounded-xl p-5 border border-red-200 dark:border-red-800">
        <p class="text-xs text-red-600 font-medium">Overdue</p>
        <p class="text-2xl font-bold text-red-700 dark:text-red-300 mt-1">{{ summary.overdue || 0 }}</p>
      </div>
    </div>

    <!-- Upcoming Deadlines -->
    <div v-if="upcoming.length" class="bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-200 dark:border-amber-800 p-4">
      <p class="text-sm font-semibold text-amber-900 dark:text-amber-100 mb-3">⏰ Due in next 30 days</p>
      <div class="flex flex-wrap gap-2">
        <span v-for="r in upcoming" :key="r.id"
          class="px-3 py-1.5 bg-white dark:bg-slate-800 rounded-lg text-xs border border-amber-200 dark:border-amber-700">
          <span class="font-semibold text-slate-900 dark:text-white">{{ r.tax_type_display }}</span>
          <span class="text-slate-500 ml-1">{{ r.period_label }}</span>
          <span class="text-amber-600 ml-1">— {{ r.days_until_due }}d</span>
        </span>
      </div>
    </div>

    <!-- Returns Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Tax Type</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Period</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Due Date</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">KRA Ref</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="r in returns" :key="r.id"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50"
              :class="r.is_overdue ? 'bg-red-50/50 dark:bg-red-900/10' : ''">
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="typeBadge(r.tax_type)">{{ r.tax_type_display }}</span>
              </td>
              <td class="px-4 py-3 text-slate-700 dark:text-slate-300">{{ r.period_label }}</td>
              <td class="px-4 py-3 text-right font-semibold text-slate-900 dark:text-white">
                {{ r.tax_amount > 0 ? 'KES ' + fmt(r.tax_amount) : '—' }}
              </td>
              <td class="px-4 py-3 text-xs" :class="r.is_overdue ? 'text-red-600 font-semibold' : 'text-slate-600 dark:text-slate-400'">
                {{ r.due_date }} {{ r.is_overdue ? '⚠️' : '' }}
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(r.status)">{{ r.status_display }}</span>
              </td>
              <td class="px-4 py-3 text-xs text-slate-500">{{ r.kra_reference || '—' }}</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button v-if="['pending','calculated'].includes(r.status)" @click="fileReturn(r)"
                    class="px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700">File</button>
                  <button v-if="r.status === 'filed'" @click="markPaid(r.id)"
                    class="px-2 py-1 bg-emerald-600 text-white rounded text-xs hover:bg-emerald-700">Paid</button>
                </div>
              </td>
            </tr>
            <tr v-if="!returns.length">
              <td colspan="7" class="px-4 py-8 text-center text-slate-400">No tax returns found</td>
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
  name: 'TaxCalendar',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    const year = new Date().getFullYear()
    return { loading: false, selectedYear: year, filterType: '', years: [year, year-1], summary: null, returns: [], upcoming: [] }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    typeBadge(t) {
      return { vat: 'bg-amber-100 text-amber-800', paye: 'bg-blue-100 text-blue-800', wht: 'bg-purple-100 text-purple-800',
               nhif: 'bg-emerald-100 text-emerald-800', nssf: 'bg-teal-100 text-teal-800', income_tax: 'bg-red-100 text-red-800' }[t] || 'bg-slate-100 text-slate-800'
    },
    statusBadge(s) {
      return { pending: 'bg-slate-100 text-slate-700', calculated: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               filed: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
               paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               overdue: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      this.loading = true
      try {
        const [cal, upcomingData] = await Promise.allSettled([
          this.makeRequest('get', `api/finance/api/tax/calendar/?year=${this.selectedYear}`, null, false),
          this.makeRequest('get', 'api/finance/api/tax/upcoming/?days=30', null, false)
        ])
        if (cal.status === 'fulfilled') {
          this.summary = cal.value.summary
          const allReturns = Object.values(cal.value.calendar || {}).flat()
          this.returns = this.filterType ? allReturns.filter(r => r.tax_type === this.filterType) : allReturns
        }
        if (upcomingData.status === 'fulfilled') {
          this.upcoming = upcomingData.value.upcoming || []
        }
      } catch (e) { console.error('Tax calendar load:', e) }
      finally { this.loading = false }
    },
    async fileReturn(r) {
      const ref = prompt(`KRA reference for ${r.tax_type_display} ${r.period_label}:`) || ''
      try {
        await this.makeRequest('patch', `api/finance/api/tax/${r.id}/`, { action: 'file', kra_reference: ref })
        await this.load()
      } catch (e) { console.error('File tax:', e) }
    },
    async markPaid(id) {
      try {
        await this.makeRequest('patch', `api/finance/api/tax/${id}/`, { action: 'mark_paid' })
        await this.load()
      } catch (e) { console.error('Mark paid:', e) }
    }
  },
  mounted() { this.load() }
}
</script>
