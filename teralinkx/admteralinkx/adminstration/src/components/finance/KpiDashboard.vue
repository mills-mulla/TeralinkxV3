<template>
  <div class="space-y-6">
    <GuidePanel title="KPI Command Centre" :terms="[
        { label: 'MRR (Monthly Recurring Revenue)', color: 'blue', description: 'Total revenue from completed transactions in the current month. The primary health metric for the business.', formula: 'SUM(TransactionQueue.price) WHERE status=completed AND month=current' },
        { label: 'Active Customers', color: 'emerald', description: 'Customers with active status. Tracks your subscriber base size month over month.' },
        { label: 'Churn Rate (30d)', color: 'amber', description: 'Percentage of customers who became inactive in the last 30 days. Target: keep below 5%.', formula: 'Churned Customers / Total Customers × 100' },
        { label: 'Cash Position', color: 'purple', description: 'Total revenue minus total paid expenses. Negative means expenses exceed revenue collected to date.' },
        { label: 'Revenue at Risk', color: 'red', description: 'Combined MRR of customers flagged as high or critical churn risk. Actionable via Retention Tasks.' },
        { label: 'Network Uptime', color: 'teal', description: '7-day average network availability. Target: 99.5%+. Sourced from HIDS monitoring.' },
        { label: 'Receivables', color: 'indigo', description: 'Outstanding payments not yet collected, grouped by age (current, 30-60d, 60-90d, 90d+).' },
        { label: 'ARR (Annual Recurring Revenue)', color: 'slate', description: 'MRR target × 12. Represents the annualised revenue goal based on current month target.' }
      ]" note="All values are pre-computed every 5 minutes. Click Refresh to force an immediate update." />
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-slate-900 dark:text-white">KPI Command Centre</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
          Last updated: {{ lastUpdated }} · Auto-refreshes every 5 min
        </p>
      </div>
      <button @click="refresh" :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 text-sm">
        <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        Refresh
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="card in kpiCards" :key="card.label"
        class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">{{ card.label }}</p>
        <p class="text-2xl font-bold mt-1" :class="card.color">{{ card.value }}</p>
        <p class="text-xs mt-1" :class="card.trendColor">{{ card.trend }}</p>
      </div>
    </div>

    <!-- Weekly Summary -->
    <div v-if="weekly" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-4">Weekly Summary</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <p class="text-xs font-medium text-emerald-600 dark:text-emerald-400 mb-2">🏆 Top Wins</p>
          <ul class="space-y-1">
            <li v-for="(win, i) in weekly.top_wins" :key="i"
              class="text-sm text-slate-700 dark:text-slate-300 flex items-start gap-2">
              <span class="text-emerald-500 mt-0.5">✓</span>{{ win }}
            </li>
          </ul>
        </div>
        <div>
          <p class="text-xs font-medium text-red-600 dark:text-red-400 mb-2">⚠️ Top Risks</p>
          <ul class="space-y-1">
            <li v-for="(risk, i) in weekly.top_risks" :key="i"
              class="text-sm text-slate-700 dark:text-slate-300 flex items-start gap-2">
              <span class="text-red-500 mt-0.5">!</span>{{ risk }}
            </li>
          </ul>
        </div>
        <div>
          <p class="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2">📊 Churn Risk</p>
          <div class="space-y-1 text-sm text-slate-700 dark:text-slate-300">
            <div class="flex justify-between">
              <span>High risk customers</span>
              <span class="font-semibold text-red-600">{{ weekly.churn_risk_summary?.high_risk || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span>Revenue at risk</span>
              <span class="font-semibold text-amber-600">KES {{ fmt(weekly.churn_risk_summary?.revenue_at_risk || 0) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'

export default {
  components: { GuidePanel, },
  name: 'KpiDashboard',
  setup() {
    const { makeRequest } = useApi()
    return { makeRequest }
  },
  data() {
    return {
      loading: false,
      kpi: null,
      weekly: null,
      lastUpdated: '—',
      timer: null
    }
  },
  computed: {
    kpiCards() {
      const k = this.kpi || {}
      const growth = parseFloat(k.mrr_growth_pct || 0)
      return [
        { label: 'MRR',              value: `KES ${this.fmt(k.mrr_current || 0)}`,        color: 'text-blue-600 dark:text-blue-400',    trend: `${growth >= 0 ? '+' : ''}${growth.toFixed(1)}% vs last month`, trendColor: growth >= 0 ? 'text-emerald-600' : 'text-red-600' },
        { label: 'Active Customers', value: k.active_customers || 0,                       color: 'text-emerald-600 dark:text-emerald-400', trend: `${k.new_customers_30d || 0} new this month`,                   trendColor: 'text-slate-500' },
        { label: 'Churn Rate (30d)', value: `${k.churn_rate_30d || 0}%`,                  color: 'text-amber-600 dark:text-amber-400',   trend: 'Monthly churn rate',                                           trendColor: 'text-slate-500' },
        { label: 'Cash Position',    value: `KES ${this.fmt(k.cash_position || 0)}`,       color: 'text-purple-600 dark:text-purple-400', trend: `Revenue at risk: KES ${this.fmt(k.revenue_at_risk || 0)}`,      trendColor: 'text-slate-500' },
        { label: 'Network Uptime',   value: `${k.network_uptime_7d || 0}%`,               color: 'text-teal-600 dark:text-teal-400',    trend: '7-day average',                                                trendColor: 'text-slate-500' },
        { label: 'High Risk Customers', value: k.high_risk_customers || 0,                color: 'text-red-600 dark:text-red-400',       trend: 'Churn risk flagged',                                           trendColor: 'text-red-500' },
        { label: 'Receivables',      value: `KES ${this.fmt(k.total_receivables || 0)}`,  color: 'text-indigo-600 dark:text-indigo-400', trend: `Outstanding: KES ${this.fmt(this.outstandingTotal(k))}`,        trendColor: 'text-slate-500' },
        { label: 'ARR',              value: `KES ${this.fmt(k.mrr_target ? k.mrr_target * 12 : 0)}`, color: 'text-slate-700 dark:text-slate-300', trend: 'Annual target', trendColor: 'text-slate-500' },
      ]
    }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n)) },
    outstandingTotal(k) {
      const o = k.outstanding_receivables || {}
      return (o['0_30'] || 0) + (o['31_60'] || 0) + (o['60_plus'] || 0)
    },
    async refresh() {
      this.loading = true
      try {
        this.kpi = await this.makeRequest('get', 'api/finance/api/kpi/summary/')
        this.lastUpdated = new Date().toLocaleTimeString()
      } catch (e) {
        console.error('KPI fetch:', e)
      } finally {
        this.loading = false
      }
      try {
        const weekly = await this.makeRequest('get', 'api/finance/api/kpi/weekly-summary/')
        this.weekly = Array.isArray(weekly) ? weekly[0] : (weekly.results?.[0] || weekly)
      } catch (e) { /* weekly summary optional */ }
    }
  },
  mounted() {
    this.refresh()
    this.timer = setInterval(this.refresh, 300000) // 5 min
  },
  beforeUnmount() {
    clearInterval(this.timer)
  }
}
</script>
