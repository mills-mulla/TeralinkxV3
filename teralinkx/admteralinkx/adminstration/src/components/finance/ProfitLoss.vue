<template>
  <div class="space-y-6">
    <GuidePanel title="Profit & Loss" :terms="[
        { label: 'Gross Revenue', color: 'blue', description: 'Total revenue including VAT collected from customers.' },
        { label: 'Net Revenue', color: 'emerald', description: 'Revenue after deducting VAT. This is your actual earned income.', formula: 'Gross Revenue − VAT Collected' },
        { label: 'Gross Profit', color: 'purple', description: 'Net revenue minus all operating expenses.', formula: 'Net Revenue − Total Expenses' },
        { label: 'Forex Gain/Loss', color: 'amber', description: 'Impact of exchange rate changes on USD-denominated expenses (bandwidth costs).' },
        { label: 'Net Profit', color: 'teal', description: 'Final profit after all expenses and forex adjustments.', formula: 'Gross Profit + Forex Gain/Loss' },
      ]" note="P&L is auto-generated on 2nd of each month. Select period type and month/quarter/year to view." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Profit & Loss</h2>
      <div class="flex gap-3">
        <select v-model="params.period_type" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="monthly">Monthly</option>
          <option value="quarterly">Quarterly</option>
          <option value="annual">Annual</option>
        </select>
        <select v-if="params.period_type === 'monthly'" v-model="params.month" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option v-for="m in 12" :key="m" :value="m">{{ monthName(m) }}</option>
        </select>
        <select v-if="params.period_type === 'quarterly'" v-model="params.quarter" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="1">Q1</option><option value="2">Q2</option><option value="3">Q3</option><option value="4">Q4</option>
        </select>
        <select v-model="params.year" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>

    <div v-if="pl" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Income Statement -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-4">Income Statement — {{ pl.period_label }}</h3>
        <div class="space-y-2">
          <div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-700">
            <span class="text-sm text-slate-600 dark:text-slate-400">Gross Revenue</span>
            <span class="font-semibold text-blue-600 dark:text-blue-400">KES {{ fmt(pl.gross_revenue) }}</span>
          </div>
          <div class="flex justify-between py-1 text-sm">
            <span class="text-slate-500 pl-4">Less: VAT Collected</span>
            <span class="text-red-500">- KES {{ fmt(pl.vat_collected) }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-slate-200 dark:border-slate-700 font-medium">
            <span class="text-slate-700 dark:text-slate-300">Net Revenue</span>
            <span class="text-emerald-600 dark:text-emerald-400">KES {{ fmt(pl.net_revenue) }}</span>
          </div>
          <div class="flex justify-between py-1 text-sm">
            <span class="text-slate-500 pl-4">Less: Operating Expenses</span>
            <span class="text-red-500">- KES {{ fmt(pl.total_expenses) }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-slate-200 dark:border-slate-700 font-medium">
            <span class="text-slate-700 dark:text-slate-300">Gross Profit</span>
            <span :class="pl.gross_profit >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
              KES {{ fmt(pl.gross_profit) }}
            </span>
          </div>
          <div v-if="pl.forex_gain_loss !== 0" class="flex justify-between py-1 text-sm">
            <span class="text-slate-500 pl-4">{{ pl.forex_gain_loss >= 0 ? 'Add:' : 'Less:' }} Forex {{ pl.forex_gain_loss >= 0 ? 'Gain' : 'Loss' }}</span>
            <span :class="pl.forex_gain_loss >= 0 ? 'text-emerald-500' : 'text-red-500'">
              {{ pl.forex_gain_loss >= 0 ? '+' : '-' }} KES {{ fmt(Math.abs(pl.forex_gain_loss)) }}
            </span>
          </div>
          <div class="flex justify-between py-3 border-t-2 border-slate-300 dark:border-slate-600 font-bold text-lg">
            <span class="text-slate-900 dark:text-white">Net Profit</span>
            <span :class="pl.net_profit >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
              KES {{ fmt(pl.net_profit) }}
            </span>
          </div>
          <div class="flex justify-between py-1 text-xs text-slate-400">
            <span>Profit Margin</span>
            <span :class="pl.profit_margin >= 0 ? 'text-emerald-500' : 'text-red-500'">{{ pl.profit_margin }}%</span>
          </div>
        </div>
      </div>

      <!-- Expense Breakdown -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-4">Expense Breakdown</h3>
        <div class="space-y-2">
          <div v-for="(amount, cat) in pl.expense_breakdown" :key="cat" class="flex items-center gap-3">
            <div class="flex-1">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-slate-600 dark:text-slate-400 capitalize">{{ cat.replace('_', ' ') }}</span>
                <span class="font-medium text-slate-900 dark:text-white">KES {{ fmt(amount) }}</span>
              </div>
              <div class="h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 rounded-full" :style="{ width: pct(amount, pl.total_expenses) + '%' }"></div>
              </div>
            </div>
          </div>
          <div v-if="!Object.keys(pl.expense_breakdown || {}).length" class="text-sm text-slate-400 text-center py-4">No expenses this period</div>
        </div>
      </div>
    </div>

    <div v-if="!pl && !loading" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-12 text-center text-slate-400">
      Select a period to view P&L statement
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'ProfitLoss',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    const year = new Date().getFullYear()
    return {
      pl: null, loading: false,
      params: { period_type: 'monthly', month: new Date().getMonth() + 1, quarter: 1, year },
      years: [year, year - 1, year - 2]
    }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    pct(val, total) { return total > 0 ? Math.min(100, Math.round(val / total * 100)) : 0 },
    monthName(m) { return new Date(2000, m - 1, 1).toLocaleString('en', { month: 'long' }) },
    async load() {
      this.loading = true
      try {
        const p = this.params
        let url = `api/finance/api/pl/?period_type=${p.period_type}&year=${p.year}`
        if (p.period_type === 'monthly') url += `&month=${p.month}`
        if (p.period_type === 'quarterly') url += `&quarter=${p.quarter}`
        this.pl = await this.makeRequest('get', url, null, false)
      } catch (e) { console.error(e) }
      finally { this.loading = false }
    }
  },
  mounted() { this.load() }
}
</script>
