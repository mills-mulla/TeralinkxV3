<template>
  <div class="space-y-6">
    <GuidePanel title="VAT Management" :terms="[
        { label: 'Output VAT', color: 'blue', description: 'VAT collected from customers on sales invoices. You owe this to KRA.', formula: 'Sum of VAT on all issued invoices' },
        { label: 'Input VAT', color: 'emerald', description: 'VAT paid to suppliers on purchases/expenses. Deducted from output VAT.', formula: 'Sum of tax_amount on paid expenses' },
        { label: 'Net VAT Payable', color: 'amber', description: 'Amount owed to KRA. Negative = VAT credit (KRA owes you).', formula: 'Output VAT − Input VAT' },
        { label: 'Filing Deadline', color: 'red', description: '20th of the following month. Late filing attracts 5% penalty + 2% interest per month.' },
      ]" note="VAT returns are auto-calculated on the 1st of each month. Export CSV for KRA iTax upload." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">VAT Management</h2>
      <div class="flex gap-3">
        <select v-model="selectedYear" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
        <button @click="calculate" :disabled="calculating"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
          {{ calculating ? 'Calculating...' : 'Calculate Current Month' }}
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4" v-if="summary">
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-5 border border-blue-200 dark:border-blue-800">
        <p class="text-xs text-blue-600 font-medium">Total Output VAT</p>
        <p class="text-2xl font-bold text-blue-700 dark:text-blue-300 mt-1">KES {{ fmt(summary.total_output_vat) }}</p>
      </div>
      <div class="bg-emerald-50 dark:bg-emerald-900/20 rounded-xl p-5 border border-emerald-200 dark:border-emerald-800">
        <p class="text-xs text-emerald-600 font-medium">Total Input VAT</p>
        <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">KES {{ fmt(summary.total_input_vat) }}</p>
      </div>
      <div class="rounded-xl p-5 border" :class="summary.total_net_vat >= 0 ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800' : 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800'">
        <p class="text-xs font-medium" :class="summary.total_net_vat >= 0 ? 'text-amber-600' : 'text-emerald-600'">Net VAT {{ summary.total_net_vat >= 0 ? 'Payable' : 'Credit' }}</p>
        <p class="text-2xl font-bold mt-1" :class="summary.total_net_vat >= 0 ? 'text-amber-700 dark:text-amber-300' : 'text-emerald-700 dark:text-emerald-300'">KES {{ fmt(Math.abs(summary.total_net_vat)) }}</p>
      </div>
      <div class="bg-red-50 dark:bg-red-900/20 rounded-xl p-5 border border-red-200 dark:border-red-800">
        <p class="text-xs text-red-600 font-medium">Next Deadline</p>
        <p class="text-lg font-bold text-red-700 dark:text-red-300 mt-1">{{ summary.next_filing_deadline }}</p>
        <p class="text-xs text-red-500 mt-1">{{ summary.unfiled_count }} unfiled</p>
      </div>
    </div>

    <!-- Monthly Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Monthly Returns — {{ selectedYear }}</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Period</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Output VAT</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Input VAT</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Net Payable</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Deadline</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="r in months" :key="r.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ r.period }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(r.output_vat) }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(r.input_vat) }}</td>
              <td class="px-4 py-3 text-right font-semibold" :class="r.net_vat >= 0 ? 'text-amber-600' : 'text-emerald-600'">
                {{ r.net_vat >= 0 ? '' : '(' }}KES {{ fmt(Math.abs(r.net_vat)) }}{{ r.net_vat < 0 ? ' credit)' : '' }}
              </td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400 text-xs">{{ r.filing_deadline }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="vatStatusBadge(r.status)">{{ r.status_display }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button v-if="r.status === 'calculated'" @click="fileReturn(r.id)"
                    class="px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700">File</button>
                  <button v-if="r.status === 'filed'" @click="markPaid(r.id)"
                    class="px-2 py-1 bg-emerald-600 text-white rounded text-xs hover:bg-emerald-700">Paid</button>
                  <a :href="`api/finance/api/vat/${r.id}/export/`"
                    class="px-2 py-1 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded text-xs hover:bg-slate-300">CSV</a>
                </div>
              </td>
            </tr>
            <tr v-if="!months.length">
              <td colspan="7" class="px-4 py-8 text-center text-slate-400">No VAT returns for {{ selectedYear }}</td>
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
  name: 'VATDashboard',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    const year = new Date().getFullYear()
    return {
      loading: false, calculating: false,
      selectedYear: year,
      years: [year, year - 1, year - 2],
      summary: null, months: []
    }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    vatStatusBadge(s) {
      return { draft: 'bg-slate-100 text-slate-700', calculated: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               filed: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
               paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' }[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      this.loading = true
      try {
        const data = await this.makeRequest('get', `api/finance/api/vat/summary/?year=${this.selectedYear}`, null, false)
        this.summary = data
        this.months = data.months || []
      } catch (e) { console.error('VAT load:', e) }
      finally { this.loading = false }
    },
    async calculate() {
      this.calculating = true
      try {
        const now = new Date()
        await this.makeRequest('post', 'api/finance/api/vat/calculate/', { year: now.getFullYear(), month: now.getMonth() + 1 })
        await this.load()
      } catch (e) { console.error('VAT calculate:', e) }
      finally { this.calculating = false }
    },
    async fileReturn(id) {
      const ref = prompt('Enter KRA reference number (optional):') || ''
      try {
        await this.makeRequest('patch', `api/finance/api/vat/${id}/`, { action: 'file', kra_reference: ref })
        await this.load()
      } catch (e) { console.error('File VAT:', e) }
    },
    async markPaid(id) {
      try {
        await this.makeRequest('patch', `api/finance/api/vat/${id}/`, { action: 'mark_paid' })
        await this.load()
      } catch (e) { console.error('Mark paid:', e) }
    }
  },
  mounted() { this.load() }
}
</script>
