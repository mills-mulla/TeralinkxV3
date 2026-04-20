<template>
  <div class="space-y-6">
    <GuidePanel title="CLV Cohort Analysis" :terms="[
      { label: 'CLV', color: 'blue', description: 'Customer Lifetime Value — total revenue generated per customer since acquisition.' },
      { label: 'Cohort', color: 'purple', description: 'Group of customers acquired in the same month. Tracks how their revenue and retention evolves over time.' },
      { label: 'Retention Rate', color: 'emerald', description: 'Percentage of cohort still active and paying. Drops over time — higher is better.' },
      { label: 'Churn Rate', color: 'red', description: '100% minus retention rate. How many customers from this cohort have stopped paying.' },
    ]" note="Cohorts auto-calculate on load. Click Recalculate to refresh with latest transaction data." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">CLV Cohort Analysis</h2>
      <div class="flex gap-2">
        <button @click="recalculate" :disabled="recalculating"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50">
          {{ recalculating ? 'Recalculating...' : '🔄 Recalculate All' }}
        </button>
        <button @click="load" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm hover:bg-slate-300">Refresh</button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <p class="text-xs text-slate-500 mb-1">Total Cohorts</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ cohorts.length }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <p class="text-xs text-slate-500 mb-1">Avg CLV</p>
        <p class="text-2xl font-bold text-blue-600">KES {{ fmt(avgClv) }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <p class="text-xs text-slate-500 mb-1">Total Revenue</p>
        <p class="text-2xl font-bold text-emerald-600">KES {{ fmtCompact(totalRevenue) }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <p class="text-xs text-slate-500 mb-1">Avg Retention</p>
        <p class="text-2xl font-bold text-purple-600">{{ avgRetention }}%</p>
      </div>
    </div>

    <!-- Cohort Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Cohort</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Customers</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Avg CLV (KES)</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Total Revenue</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Retention</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Churn</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">CLV Bar</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Detail</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <template v-for="c in cohorts" :key="c.id">
              <tr class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ c.cohort_name }}</td>
                <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{{ c.customer_count }}</td>
                <td class="px-4 py-3 text-right font-medium text-blue-600">{{ fmt(c.avg_clv) }}</td>
                <td class="px-4 py-3 text-right text-emerald-600 font-medium">{{ fmt(c.total_revenue) }}</td>
                <td class="px-4 py-3 text-right">
                  <span class="font-medium" :class="c.retention_rate >= 70 ? 'text-emerald-600' : c.retention_rate >= 40 ? 'text-amber-600' : 'text-red-500'">
                    {{ c.retention_rate }}%
                  </span>
                </td>
                <td class="px-4 py-3 text-right text-red-500">{{ c.churn_rate }}%</td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div class="h-full bg-blue-500 rounded-full transition-all"
                        :style="{ width: bestClv > 0 ? Math.min((c.avg_clv / bestClv) * 100, 100) + '%' : '0%' }">
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3 text-center">
                  <button @click="toggleDetail(c.id)" class="text-xs text-blue-600 hover:underline">
                    {{ expandedId === c.id ? 'Hide' : 'Monthly' }}
                  </button>
                </td>
              </tr>
              <!-- Monthly breakdown row -->
              <tr v-if="expandedId === c.id" class="bg-slate-50 dark:bg-slate-900/50">
                <td colspan="8" class="px-4 py-3">
                  <div class="overflow-x-auto">
                    <table class="w-full text-xs">
                      <thead>
                        <tr class="text-slate-400">
                          <th class="text-left py-1 pr-4">Month</th>
                          <th class="text-right pr-4">Active</th>
                          <th class="text-right pr-4">Retention</th>
                          <th class="text-right pr-4">Revenue</th>
                          <th class="text-right pr-4">Avg/Customer</th>
                          <th class="text-right">Cumulative CLV</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
                        <tr v-for="m in c.monthly_breakdown" :key="m.month_offset"
                          :class="m.revenue > 0 ? '' : 'opacity-40'">
                          <td class="py-1 pr-4 text-slate-600 dark:text-slate-400">Month {{ m.month_offset + 1 }}</td>
                          <td class="text-right pr-4 text-slate-700 dark:text-slate-300">{{ m.active_customers }}</td>
                          <td class="text-right pr-4" :class="m.retention_rate >= 50 ? 'text-emerald-600' : 'text-red-500'">{{ m.retention_rate }}%</td>
                          <td class="text-right pr-4 text-emerald-600">{{ m.revenue > 0 ? 'KES ' + fmt(m.revenue) : '—' }}</td>
                          <td class="text-right pr-4 text-slate-600 dark:text-slate-400">{{ m.avg_revenue_per_customer > 0 ? 'KES ' + fmt(m.avg_revenue_per_customer) : '—' }}</td>
                          <td class="text-right font-medium text-blue-600">{{ m.cumulative_clv > 0 ? 'KES ' + fmt(m.cumulative_clv) : '—' }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </td>
              </tr>
            </template>
            <tr v-if="!cohorts.length">
              <td colspan="8" class="px-4 py-8 text-center text-slate-400">
                No cohort data. Click "Recalculate All" to generate cohorts from existing customers.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Retention Chart -->
    <div v-if="cohorts.length" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-3">Retention by Cohort Month</h3>
      <div class="h-48">
        <apexchart type="bar" height="100%" :options="retentionChartOptions" :series="retentionSeries" />
      </div>
    </div>

  </div>
</template>

<script>
import VueApexCharts from 'vue3-apexcharts'
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'CLVCohorts',
  components: { GuidePanel, apexchart: VueApexCharts },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { cohorts: [], recalculating: false, expandedId: null } },
  computed: {
    avgClv() { return this.cohorts.length ? this.cohorts.reduce((s, c) => s + Number(c.avg_clv || 0), 0) / this.cohorts.length : 0 },
    bestClv() { return this.cohorts.length ? Math.max(...this.cohorts.map(c => Number(c.avg_clv || 0))) : 1 },
    totalRevenue() { return this.cohorts.reduce((s, c) => s + Number(c.total_revenue || 0), 0) },
    avgRetention() { return this.cohorts.length ? (this.cohorts.reduce((s, c) => s + Number(c.retention_rate || 0), 0) / this.cohorts.length).toFixed(1) : 0 },
    retentionSeries() {
      return [
        { name: 'Retention %', data: this.cohorts.map(c => ({ x: c.cohort_name, y: c.retention_rate })) },
        { name: 'Churn %', data: this.cohorts.map(c => ({ x: c.cohort_name, y: c.churn_rate })) },
      ]
    },
    retentionChartOptions() {
      return {
        chart: { type: 'bar', stacked: true, toolbar: { show: false }, background: 'transparent' },
        colors: ['#10b981', '#ef4444'],
        plotOptions: { bar: { borderRadius: 3, columnWidth: '50%' } },
        dataLabels: { enabled: false },
        xaxis: { labels: { style: { colors: '#94a3b8', fontSize: '10px' } }, axisBorder: { show: false } },
        yaxis: { max: 100, labels: { style: { colors: '#94a3b8', fontSize: '10px' }, formatter: v => v + '%' } },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        legend: { position: 'top', fontSize: '11px', labels: { colors: '#94a3b8' } },
        tooltip: { y: { formatter: v => v + '%' } }
      }
    }
  },
  methods: {
    fmt(v) { return Number(v || 0).toLocaleString('en-KE', { minimumFractionDigits: 0 }) },
    fmtCompact(v) { return new Intl.NumberFormat('en-KE', { notation: 'compact', maximumFractionDigits: 1 }).format(v || 0) },
    toggleDetail(id) { this.expandedId = this.expandedId === id ? null : id },
    async load() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/clv/cohorts/', null, false)
        this.cohorts = Array.isArray(data) ? data : []
      } catch (e) { console.error(e) }
    },
    async recalculate() {
      this.recalculating = true
      try {
        await this.makeRequest('post', 'api/finance/api/clv/cohorts/', { action: 'recalculate_all' }, false)
        await this.load()
      } catch (e) { console.error(e) }
      finally { this.recalculating = false }
    }
  },
  mounted() { this.load() }
}
</script>
