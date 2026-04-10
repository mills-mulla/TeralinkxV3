<template>
  <div class="space-y-6">
    <GuidePanel title="Board Reports" :terms="[
        { label: 'Financial Performance', color: 'blue', description: 'Revenue, expenses, net profit, and profit margin vs previous month.' },
        { label: 'Customer Metrics', color: 'emerald', description: 'Active customers, new acquisitions, churn count, churn rate, and ARPU.' },
        { label: 'Operational Metrics', color: 'purple', description: 'Transaction success rate, average transaction value, and network uptime.' },
        { label: 'Risk Register', color: 'red', description: 'High-risk customers, revenue at risk, budget overruns, and outstanding receivables.' },
        { label: 'Draft → Review → Approved', color: 'amber', description: 'Reports go through a workflow before distribution.' }
      ]" note="Reports are auto-generated from live data. Narrative sections are auto-drafted — review before distributing." />

    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Board Reports</h2>
      <button @click="generate" :disabled="generating"
        class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2 text-sm">
        <svg class="w-4 h-4" :class="{ 'animate-spin': generating }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        {{ generating ? 'Generating...' : 'Generate Report' }}
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Report History -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden h-fit">
        <div class="p-4 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-sm font-semibold text-slate-900 dark:text-white">History</h3>
        </div>
        <div class="divide-y divide-slate-200 dark:divide-slate-700">
          <div v-for="report in reports" :key="report.id"
            @click="selectReport(report.id)"
            class="px-4 py-3 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            :class="selected?.id === report.id ? 'bg-purple-50 dark:bg-purple-900/20 border-l-2 border-purple-500' : ''">
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ report.report_period }}</p>
            <p class="text-xs mt-0.5">
              <span :class="statusColor(report.status)">{{ report.status }}</span>
              <span class="text-slate-400"> · KES {{ fmt(report.revenue) }}</span>
            </p>
          </div>
          <div v-if="!reports.length" class="px-4 py-8 text-center text-slate-400 text-sm">
            No reports yet
          </div>
        </div>
      </div>

      <!-- Report Detail -->
      <div class="lg:col-span-2 space-y-4">
        <div v-if="!selected" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-12 text-center text-slate-400">
          <p class="text-sm">Select a report or generate a new one</p>
        </div>

        <template v-if="selected">
          <!-- Report Header -->
          <div class="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl p-5 text-white">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-purple-200 text-xs font-medium uppercase tracking-wide">Board Report</p>
                <h2 class="text-xl font-bold mt-0.5">{{ selected.report_period }}</h2>
                <p class="text-purple-200 text-xs mt-1">{{ formatDate(selected.generated_at) }}</p>
              </div>
              <div class="flex items-center gap-2">
                <span class="px-2 py-1 rounded-full text-xs font-bold bg-white/20">{{ selected.status?.toUpperCase() }}</span>
                <button v-if="selected.status === 'draft'" @click="approve(selected.id)"
                  class="px-3 py-1 bg-white text-purple-700 rounded-lg text-xs font-bold hover:bg-purple-50">
                  ✓ Approve
                </button>
              </div>
            </div>
            <div v-if="selected.executive_summary" class="mt-3 p-3 bg-white/10 rounded-lg">
              <p class="text-xs text-purple-200 uppercase mb-1">Executive Summary</p>
              <p class="text-sm whitespace-pre-line">{{ selected.executive_summary }}</p>
            </div>
          </div>

          <!-- Highlights & Challenges -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
              <p class="text-xs font-semibold text-emerald-600 uppercase mb-2">🏆 Highlights</p>
              <ul class="space-y-1">
                <li v-for="(h, i) in selected.key_highlights" :key="i" class="text-sm text-slate-700 dark:text-slate-300 flex gap-2">
                  <span class="text-emerald-500 flex-shrink-0">✓</span>{{ h }}
                </li>
                <li v-if="!selected.key_highlights?.length" class="text-sm text-slate-400">None recorded</li>
              </ul>
            </div>
            <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
              <p class="text-xs font-semibold text-red-600 uppercase mb-2">⚠️ Challenges</p>
              <ul class="space-y-1">
                <li v-for="(c, i) in selected.challenges" :key="i" class="text-sm text-slate-700 dark:text-slate-300 flex gap-2">
                  <span class="text-red-500 flex-shrink-0">!</span>{{ c }}
                </li>
                <li v-if="!selected.challenges?.length" class="text-sm text-slate-400">None recorded</li>
              </ul>
            </div>
          </div>

          <!-- Financial Performance (collapsible) -->
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
            <button @click="toggle('financial')" class="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <p class="text-sm font-semibold text-slate-900 dark:text-white">💰 Financial Performance</p>
              <svg class="w-4 h-4 text-slate-400 transition-transform" :class="open.financial ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <div v-show="open.financial" class="px-5 pb-5">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div class="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p class="text-xs text-blue-600 font-medium">Revenue</p>
                  <p class="text-base font-bold text-blue-700 dark:text-blue-300 mt-1">KES {{ fmt(fp.revenue?.current) }}</p>
                  <p class="text-xs mt-1" :class="fp.revenue?.growth_pct >= 0 ? 'text-emerald-600' : 'text-red-600'">
                    {{ fp.revenue?.growth_pct >= 0 ? '+' : '' }}{{ (fp.revenue?.growth_pct || 0).toFixed(1) }}% MoM
                  </p>
                </div>
                <div class="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <p class="text-xs text-red-600 font-medium">Expenses</p>
                  <p class="text-base font-bold text-red-700 dark:text-red-300 mt-1">KES {{ fmt(fp.expenses?.current) }}</p>
                  <p class="text-xs mt-1" :class="fp.expenses?.change_pct <= 0 ? 'text-emerald-600' : 'text-red-600'">
                    {{ fp.expenses?.change_pct >= 0 ? '+' : '' }}{{ (fp.expenses?.change_pct || 0).toFixed(1) }}% MoM
                  </p>
                </div>
                <div class="text-center p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
                  <p class="text-xs text-emerald-600 font-medium">Net Profit</p>
                  <p class="text-base font-bold mt-1" :class="fp.net_profit >= 0 ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-700 dark:text-red-300'">
                    KES {{ fmt(fp.net_profit) }}
                  </p>
                  <p class="text-xs text-slate-500 mt-1">{{ (fp.profit_margin_pct || 0).toFixed(1) }}% margin</p>
                </div>
                <div class="text-center p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                  <p class="text-xs text-slate-500 font-medium">Prev Revenue</p>
                  <p class="text-base font-bold text-slate-700 dark:text-slate-300 mt-1">KES {{ fmt(fp.revenue?.previous) }}</p>
                  <p class="text-xs text-slate-500 mt-1">Last month</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Customer Metrics (collapsible) -->
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
            <button @click="toggle('customers')" class="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <p class="text-sm font-semibold text-slate-900 dark:text-white">👥 Customer Metrics</p>
              <svg class="w-4 h-4 text-slate-400 transition-transform" :class="open.customers ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <div v-show="open.customers" class="px-5 pb-5">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div class="text-center p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
                  <p class="text-xs text-emerald-600 font-medium">Active</p>
                  <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">{{ cm.active_customers || 0 }}</p>
                  <p class="text-xs mt-1" :class="cm.customer_growth_pct >= 0 ? 'text-emerald-600' : 'text-red-600'">
                    {{ cm.customer_growth_pct >= 0 ? '+' : '' }}{{ (cm.customer_growth_pct || 0).toFixed(1) }}% MoM
                  </p>
                </div>
                <div class="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p class="text-xs text-blue-600 font-medium">New</p>
                  <p class="text-2xl font-bold text-blue-700 dark:text-blue-300 mt-1">{{ cm.new_customers || 0 }}</p>
                  <p class="text-xs text-slate-500 mt-1">this month</p>
                </div>
                <div class="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <p class="text-xs text-red-600 font-medium">Churned</p>
                  <p class="text-2xl font-bold text-red-700 dark:text-red-300 mt-1">{{ cm.churned_customers || 0 }}</p>
                  <p class="text-xs text-slate-500 mt-1">{{ (cm.churn_rate_pct || 0).toFixed(1) }}% rate</p>
                </div>
                <div class="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <p class="text-xs text-purple-600 font-medium">ARPU</p>
                  <p class="text-xl font-bold text-purple-700 dark:text-purple-300 mt-1">KES {{ fmt(cm.arpu) }}</p>
                  <p class="text-xs text-slate-500 mt-1">per customer</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Operational + Risk (collapsible, side by side) -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
              <button @click="toggle('operational')" class="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-slate-700/50">
                <p class="text-sm font-semibold text-slate-900 dark:text-white">⚙️ Operational</p>
                <svg class="w-4 h-4 text-slate-400 transition-transform" :class="open.operational ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              <div v-show="open.operational" class="px-5 pb-4 space-y-2">
                <div class="flex justify-between text-sm"><span class="text-slate-500">Transactions</span><span class="font-semibold text-slate-900 dark:text-white">{{ om.total_transactions || 0 }}</span></div>
                <div class="flex justify-between text-sm"><span class="text-slate-500">Success Rate</span><span class="font-semibold" :class="(om.success_rate_pct||0)>=95?'text-emerald-600':'text-amber-600'">{{ (om.success_rate_pct||0).toFixed(1) }}%</span></div>
                <div class="flex justify-between text-sm"><span class="text-slate-500">Avg Transaction</span><span class="font-semibold text-slate-900 dark:text-white">KES {{ fmt(om.avg_transaction_value) }}</span></div>
                <div class="flex justify-between text-sm"><span class="text-slate-500">Network Uptime</span><span class="font-semibold" :class="(om.network_uptime_pct||0)>=99?'text-emerald-600':'text-red-600'">{{ (om.network_uptime_pct||0).toFixed(1) }}%</span></div>
              </div>
            </div>
            <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
              <button @click="toggle('risk')" class="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-slate-700/50">
                <p class="text-sm font-semibold text-slate-900 dark:text-white">🚨 Risk Register</p>
                <svg class="w-4 h-4 text-slate-400 transition-transform" :class="open.risk ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              <div v-show="open.risk" class="px-5 pb-4 space-y-2">
                <div class="flex justify-between text-sm"><span class="text-slate-500">High Risk Customers</span><span class="font-semibold text-red-600">{{ rr.high_risk_customers || 0 }}</span></div>
                <div class="flex justify-between text-sm"><span class="text-slate-500">Revenue at Risk</span><span class="font-semibold text-amber-600">KES {{ fmt(rr.revenue_at_risk) }}</span></div>
                <div class="flex justify-between text-sm"><span class="text-slate-500">Budget Overruns</span><span class="font-semibold" :class="(rr.budget_overruns||0)>0?'text-red-600':'text-emerald-600'">{{ rr.budget_overruns || 0 }} depts</span></div>
                <div class="flex justify-between text-sm"><span class="text-slate-500">Receivables</span><span class="font-semibold text-slate-900 dark:text-white">KES {{ fmt(rr.outstanding_receivables) }}</span></div>
              </div>
            </div>
          </div>

          <!-- Cash Flow + Recommendations (collapsible) -->
          <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
            <button @click="toggle('forecast')" class="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <p class="text-sm font-semibold text-slate-900 dark:text-white">📈 Cash Flow Forecast & Recommendations</p>
              <svg class="w-4 h-4 text-slate-400 transition-transform" :class="open.forecast ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            <div v-show="open.forecast" class="px-5 pb-5 space-y-4">
              <div v-if="selected.cash_flow_forecast" class="grid grid-cols-3 gap-3 text-center">
                <div class="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
                  <p class="text-xs text-slate-500 font-medium">Scenario</p>
                  <p class="text-sm font-bold text-slate-900 dark:text-white mt-1 capitalize">{{ selected.cash_flow_forecast.scenario }}</p>
                </div>
                <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p class="text-xs text-blue-600 font-medium">30-Day Forecast</p>
                  <p class="text-sm font-bold text-blue-700 dark:text-blue-300 mt-1">KES {{ fmt(selected.cash_flow_forecast.next_30_days) }}</p>
                </div>
                <div class="p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
                  <p class="text-xs text-emerald-600 font-medium">Confidence</p>
                  <p class="text-sm font-bold text-emerald-700 dark:text-emerald-300 mt-1">{{ ((selected.cash_flow_forecast.confidence || 0) * 100).toFixed(0) }}%</p>
                </div>
              </div>
              <div v-if="selected.recommendations?.length" class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
                <p class="text-xs font-semibold text-amber-900 dark:text-amber-100 mb-2">💡 Recommendations</p>
                <ul class="space-y-1">
                  <li v-for="(r, i) in selected.recommendations" :key="i" class="text-sm text-amber-800 dark:text-amber-200 flex gap-2">
                    <span class="font-bold flex-shrink-0">{{ i + 1 }}.</span>{{ r }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'

export default {
  name: 'BoardReports',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      loading: false, generating: false, reports: [], selected: null,
      open: { financial: true, customers: true, operational: false, risk: false, forecast: false }
    }
  },
  computed: {
    fp() { return this.selected?.financial_performance || {} },
    cm() { return this.selected?.customer_metrics || {} },
    om() { return this.selected?.operational_metrics || {} },
    rr() { return this.selected?.risk_register || {} },
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    formatDate(d) { return d ? new Date(d).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' }) : '' },
    toggle(s) { this.open[s] = !this.open[s] },
    statusColor(s) {
      return { draft: 'text-amber-600', review: 'text-blue-600', approved: 'text-emerald-600', distributed: 'text-purple-600' }[s] || 'text-slate-600'
    },
    async generate() {
      this.generating = true
      try {
        await this.makeRequest('post', 'api/finance/api/board-report/generate/', {})
        await this.refresh()
        if (this.reports.length) this.selectReport(this.reports[0].id)
      } catch (e) { console.error('Generate report:', e) }
      finally { this.generating = false }
    },
    async selectReport(id) {
      try {
        this.selected = await this.makeRequest('get', `api/finance/api/board-report/${id}/`)
      } catch (e) { console.error('Load report:', e) }
    },
    async approve(id) {
      try {
        await this.makeRequest('post', `api/finance/api/board-report/${id}/approve/`, {})
        await this.selectReport(id)
        const r = this.reports.find(r => r.id === id)
        if (r) r.status = 'approved'
      } catch (e) { console.error('Approve:', e) }
    },
    async refresh() {
      try {
        const list = await this.makeRequest('get', 'api/finance/api/board-report/list/')
        this.reports = Array.isArray(list) ? list : (list.reports || list.results || [])
        if (!this.selected && this.reports.length) this.selectReport(this.reports[0].id)
      } catch (e) { console.error('Board reports fetch:', e) }
    }
  },
  mounted() { this.refresh() }
}
</script>
