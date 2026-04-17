<template>
  <div class="space-y-6">
    <GuidePanel title="Financial Year" :terms="[
        { label: 'Open', color: 'emerald', description: 'Current active year. Transactions can be posted.' },
        { label: 'Closed', color: 'slate', description: 'Year-end closing complete. No new transactions allowed for this period.' },
        { label: 'Opening Balance', color: 'blue', description: 'Cash balance carried forward from previous year closing.' },
      ]" note="Close the financial year after all December transactions are posted. This creates the next year automatically." />

    <h2 class="text-xl font-bold text-slate-900 dark:text-white">Financial Year Management</h2>

    <!-- Current Year -->
    <div v-if="data" class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white">
      <p class="text-blue-200 text-xs font-medium uppercase">Current Financial Year</p>
      <h3 class="text-2xl font-bold mt-1">FY {{ data.current_year?.year }}</h3>
      <div class="flex items-center gap-4 mt-2 text-sm text-blue-100">
        <span>{{ data.current_year?.start_date }} → {{ data.current_year?.end_date }}</span>
        <span class="px-2 py-0.5 bg-white/20 rounded-full text-xs font-medium">{{ data.current_year?.status?.toUpperCase() }}</span>
      </div>
      <p class="text-blue-200 text-xs mt-2">Opening Balance: KES {{ fmt(data.current_year?.opening_balance) }}</p>
    </div>

    <!-- Year History -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Year History</h3>
        <button v-if="data?.current_year?.status === 'open'" @click="showClose=true"
          class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700">
          Close FY {{ data?.current_year?.year }}
        </button>
      </div>
      <div class="divide-y divide-slate-200 dark:divide-slate-700">
        <div v-for="y in data?.all_years" :key="y.year" class="px-4 py-3 flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-slate-900 dark:text-white">FY {{ y.year }}</p>
            <p class="text-xs text-slate-500">{{ y.start_date }} → {{ y.end_date }}</p>
          </div>
          <div class="text-right">
            <span class="px-2 py-1 rounded-full text-xs font-medium" :class="y.status === 'open' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'">
              {{ y.status }}
            </span>
            <p v-if="y.closing_balance" class="text-xs text-slate-400 mt-1">Closing: KES {{ fmt(y.closing_balance) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Close Modal -->
    <div v-if="showClose" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showClose=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md p-6">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Close Financial Year {{ data?.current_year?.year }}</h3>
        <p class="text-sm text-slate-600 dark:text-slate-400 mb-4">This will lock all transactions for FY {{ data?.current_year?.year }} and create FY {{ (data?.current_year?.year || 0) + 1 }}.</p>
        <div class="mb-4">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Closing Balance (KES)</label>
          <input v-model="closingBalance" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white"/>
        </div>
        <div class="flex justify-end gap-3">
          <button @click="showClose=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="closeYear" :disabled="closing" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm disabled:opacity-50">{{ closing ? 'Closing...' : 'Close Year' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'FinancialYear',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { data: null, showClose: false, closing: false, closingBalance: 0 } },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    async load() {
      try { this.data = await this.makeRequest('get', 'api/finance/api/financial-year/', null, false) }
      catch (e) { console.error(e) }
    },
    async closeYear() {
      this.closing = true
      try {
        await this.makeRequest('post', 'api/finance/api/financial-year/', { action: 'close', year: this.data?.current_year?.year, closing_balance: this.closingBalance })
        this.showClose = false
        await this.load()
      } catch (e) { console.error(e) }
      finally { this.closing = false }
    }
  },
  mounted() { this.load() }
}
</script>
