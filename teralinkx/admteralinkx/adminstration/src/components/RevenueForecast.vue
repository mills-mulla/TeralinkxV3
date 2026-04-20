<template>
  <div class="space-y-4">

    <!-- Header + Period Selector -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h3 class="text-base font-semibold text-slate-900 dark:text-white">Revenue Intelligence</h3>
        <p class="text-xs text-slate-500 mt-0.5">Period-over-period comparison with forecast</p>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex border border-slate-200 dark:border-slate-600 rounded-lg overflow-hidden">
          <button v-for="p in periods" :key="p.id" @click="setPeriod(p.id)"
            class="px-3 py-1.5 text-xs font-medium transition-colors"
            :class="period === p.id ? 'bg-blue-600 text-white' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50'">
            {{ p.label }}
          </button>
        </div>
        <button @click="loadAll" class="p-1.5 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700">
          <svg class="w-4 h-4 text-slate-500" :class="loading ? 'animate-spin' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Comparison Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3" v-if="comparison">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <p class="text-xs text-slate-500">{{ currentLabel }} Revenue</p>
        <p class="text-xl font-bold text-slate-900 dark:text-white mt-1">KES {{ fmt(comparison.current.revenue) }}</p>
        <div class="flex items-center gap-1 mt-1">
          <span class="text-xs font-medium px-1.5 py-0.5 rounded-full"
            :class="comparison.change.direction === 'up' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'">
            {{ comparison.change.direction === 'up' ? '↑' : '↓' }} {{ Math.abs(comparison.change.revenue_pct) }}%
          </span>
          <span class="text-xs text-slate-400">vs {{ previousLabel }}</span>
        </div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <p class="text-xs text-slate-500">{{ previousLabel }} Revenue</p>
        <p class="text-xl font-bold text-slate-500 dark:text-slate-400 mt-1">KES {{ fmt(comparison.previous.revenue) }}</p>
        <p class="text-xs text-slate-400 mt-1">{{ comparison.previous.transactions }} transactions</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <p class="text-xs text-slate-500">Transactions</p>
        <p class="text-xl font-bold text-slate-900 dark:text-white mt-1">{{ comparison.current.transactions }}</p>
        <div class="flex items-center gap-1 mt-1">
          <span class="text-xs font-medium px-1.5 py-0.5 rounded-full"
            :class="comparison.change.transactions_pct >= 0 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'">
            {{ comparison.change.transactions_pct >= 0 ? '↑' : '↓' }} {{ Math.abs(comparison.change.transactions_pct) }}%
          </span>
        </div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <p class="text-xs text-slate-500">Avg Transaction</p>
        <p class="text-xl font-bold text-slate-900 dark:text-white mt-1">KES {{ fmt(comparison.current.avg_transaction) }}</p>
        <p class="text-xs text-slate-400 mt-1">vs KES {{ fmt(comparison.previous.avg_transaction) }}</p>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

      <!-- Trend Chart — 8 periods -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <h4 class="text-sm font-medium text-slate-900 dark:text-white mb-3">{{ periodLabel }} Revenue Trend</h4>
        <div v-if="trendSeries[0].data.length" class="h-48">
          <apexchart type="bar" height="100%" :options="trendOptions" :series="trendSeries" />
        </div>
        <div v-else class="h-48 flex items-center justify-center text-slate-400 text-sm">Loading...</div>
      </div>

      <!-- Current vs Previous Overlay -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <h4 class="text-sm font-medium text-slate-900 dark:text-white mb-3">{{ currentLabel }} vs {{ previousLabel }}</h4>
        <div v-if="comparison && (comparison.current.daily.length || comparison.previous.daily.length)" class="h-48">
          <apexchart type="area" height="100%" :options="compareOptions" :series="compareSeries" />
        </div>
        <div v-else class="h-48 flex items-center justify-center text-slate-400 text-sm">No daily data for this period</div>
      </div>
    </div>

    <!-- Forecast Chart -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="flex items-center justify-between mb-3">
        <div>
          <h4 class="text-sm font-medium text-slate-900 dark:text-white">30-Day Revenue Forecast</h4>
          <p class="text-xs text-slate-500 mt-0.5" v-if="forecast.model_accuracy">
            Prophet model · {{ (forecast.model_accuracy * 100).toFixed(0) }}% accuracy · {{ (forecast.confidence_interval * 100).toFixed(0) }}% confidence
          </p>
        </div>
        <div class="flex border border-slate-200 dark:border-slate-600 rounded-lg overflow-hidden">
          <button v-for="s in scenarios" :key="s.id" @click="setScenario(s.id)"
            class="px-3 py-1 text-xs font-medium transition-colors"
            :class="scenario === s.id ? 'bg-blue-600 text-white' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50'">
            {{ s.label }}
          </button>
        </div>
      </div>
      <div class="grid grid-cols-3 gap-3 mb-4">
        <div class="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
          <p class="text-xs text-slate-500">30-Day Total</p>
          <p class="text-lg font-bold text-slate-900 dark:text-white">KES {{ fmtCompact(forecast.total_forecasted) }}</p>
        </div>
        <div class="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
          <p class="text-xs text-slate-500">Daily Average</p>
          <p class="text-lg font-bold text-slate-900 dark:text-white">KES {{ fmtCompact(forecast.average_daily) }}</p>
        </div>
        <div class="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
          <p class="text-xs text-slate-500">Seasonality</p>
          <p class="text-sm font-medium text-slate-700 dark:text-slate-300 mt-0.5">
            {{ [forecast.has_weekly_seasonality && 'Weekly', forecast.has_monthly_seasonality && 'Monthly'].filter(Boolean).join(' + ') || 'None detected' }}
          </p>
        </div>
      </div>
      <div v-if="forecastSeries[0].data.length" class="h-52">
        <apexchart type="area" height="100%" :options="forecastOptions" :series="forecastSeries" />
      </div>
      <div v-else class="h-52 flex items-center justify-center text-slate-400 text-sm">Loading forecast...</div>
    </div>

    <!-- AI Insights -->
    <div v-if="comparison && comparison.insights.length" class="bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800 p-4">
      <p class="text-xs font-semibold text-blue-900 dark:text-blue-100 mb-2">💡 Insights</p>
      <ul class="space-y-1">
        <li v-for="(insight, i) in comparison.insights" :key="i" class="text-sm text-blue-800 dark:text-blue-200 flex items-start gap-2">
          <span class="text-blue-400 mt-0.5">•</span>{{ insight }}
        </li>
      </ul>
    </div>

  </div>
</template>

<script>
import VueApexCharts from 'vue3-apexcharts'
import { useApi } from '../composables/useApi'

export default {
  name: 'RevenueForecast',
  components: { apexchart: VueApexCharts },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      period: 'week',
      scenario: 'optimistic',
      loading: false,
      comparison: null,
      forecast: {},
      periods: [
        { id: 'week', label: 'Week' },
        { id: 'month', label: 'Month' },
        { id: 'quarter', label: 'Quarter' },
        { id: 'year', label: 'Year' },
      ],
      scenarios: [
        { id: 'optimistic', label: 'Optimistic' },
        { id: 'base', label: 'Base' },
        { id: 'conservative', label: 'Conservative' },
      ],
    }
  },
  computed: {
    periodLabel() {
      return { week: 'Weekly', month: 'Monthly', quarter: 'Quarterly', year: 'Yearly' }[this.period]
    },
    currentLabel() {
      return { week: 'This Week', month: 'This Month', quarter: 'This Quarter', year: 'This Year' }[this.period]
    },
    previousLabel() {
      return { week: 'Last Week', month: 'Last Month', quarter: 'Last Quarter', year: 'Last Year' }[this.period]
    },
    trendSeries() {
      if (!this.comparison) return [{ name: 'Revenue', data: [] }]
      return [{
        name: 'Revenue',
        data: this.comparison.trend.map(t => ({ x: t.label, y: Math.round(t.revenue) }))
      }]
    },
    trendOptions() {
      return {
        chart: { type: 'bar', toolbar: { show: false }, background: 'transparent' },
        colors: ['#3b82f6'],
        plotOptions: { bar: { borderRadius: 3, columnWidth: '60%' } },
        dataLabels: { enabled: false },
        xaxis: { labels: { style: { colors: '#94a3b8', fontSize: '9px' }, rotate: -30 }, axisBorder: { show: false } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '9px' }, formatter: v => 'KES ' + new Intl.NumberFormat('en-KE', { notation: 'compact' }).format(v) } },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        tooltip: { y: { formatter: v => 'KES ' + new Intl.NumberFormat('en-KE').format(v) } }
      }
    },
    compareSeries() {
      if (!this.comparison) return []
      return [
        { name: this.currentLabel, data: this.comparison.current.daily.map(d => ({ x: d.date, y: Math.round(d.revenue) })) },
        { name: this.previousLabel, data: this.comparison.previous.daily.map(d => ({ x: d.date, y: Math.round(d.revenue) })) },
      ]
    },
    compareOptions() {
      return {
        chart: { type: 'area', toolbar: { show: false }, background: 'transparent' },
        colors: ['#3b82f6', '#94a3b8'],
        fill: { type: 'gradient', gradient: { opacityFrom: 0.3, opacityTo: 0.05 } },
        stroke: { width: [2, 1], dashArray: [0, 4], curve: 'smooth' },
        dataLabels: { enabled: false },
        xaxis: { type: 'datetime', labels: { style: { colors: '#94a3b8', fontSize: '9px' } }, axisBorder: { show: false } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '9px' }, formatter: v => 'KES ' + new Intl.NumberFormat('en-KE', { notation: 'compact' }).format(v) } },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        legend: { position: 'top', fontSize: '10px', labels: { colors: '#94a3b8' } },
        tooltip: { x: { format: 'dd MMM' }, y: { formatter: v => 'KES ' + new Intl.NumberFormat('en-KE').format(v) } }
      }
    },
    forecastSeries() {
      const data = this.forecast.forecast_data || []
      return [
        { name: 'Forecast', data: data.map(d => ({ x: d.date, y: Math.round(d.value) })) },
        { name: 'Upper', data: data.map(d => ({ x: d.date, y: Math.round(d.upper_bound) })) },
        { name: 'Lower', data: data.map(d => ({ x: d.date, y: Math.round(d.lower_bound) })) },
      ]
    },
    forecastOptions() {
      return {
        chart: { type: 'area', toolbar: { show: false }, background: 'transparent' },
        colors: ['#3b82f6', '#10b981', '#f59e0b'],
        fill: { type: ['gradient', 'solid', 'solid'], opacity: [0.25, 0.08, 0.08] },
        stroke: { width: [2, 1, 1], dashArray: [0, 4, 4], curve: 'smooth' },
        dataLabels: { enabled: false },
        xaxis: { type: 'datetime', labels: { style: { colors: '#94a3b8', fontSize: '9px' }, datetimeFormatter: { day: 'dd MMM' } }, axisBorder: { show: false } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '9px' }, formatter: v => 'KES ' + new Intl.NumberFormat('en-KE', { notation: 'compact' }).format(v) } },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        legend: { position: 'top', fontSize: '10px', labels: { colors: '#94a3b8' } },
        tooltip: { x: { format: 'dd MMM yyyy' }, y: { formatter: v => 'KES ' + new Intl.NumberFormat('en-KE').format(v) } }
      }
    }
  },
  methods: {
    fmt(v) { return new Intl.NumberFormat('en-KE', { minimumFractionDigits: 0 }).format(Math.round(v || 0)) },
    fmtCompact(v) { return new Intl.NumberFormat('en-KE', { notation: 'compact', maximumFractionDigits: 1 }).format(v || 0) },
    setPeriod(p) { this.period = p; this.loadComparison() },
    setScenario(s) { this.scenario = s; this.loadForecast() },
    async loadComparison() {
      try {
        this.comparison = await this.makeRequest('get', `api/finance/api/kpi/revenue-comparison/?period=${this.period}`, null, false)
      } catch (e) { console.error('comparison:', e) }
    },
    async loadForecast() {
      try {
        this.forecast = await this.makeRequest('get', `api/finance/api/kpi/cash-flow/forecast/?scenario=${this.scenario}`, null, false) || {}
      } catch (e) { console.error('forecast:', e) }
    },
    async loadAll() {
      this.loading = true
      await Promise.all([this.loadComparison(), this.loadForecast()])
      this.loading = false
    }
  },
  mounted() { this.loadAll() }
}
</script>
