<template>
  <div class="space-y-4">
    <!-- User Guide Section -->
    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800 p-4">
      <button 
        @click="showGuide = !showGuide"
        class="flex items-center justify-between w-full text-left"
      >
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
          <span class="text-sm font-medium text-blue-900 dark:text-blue-100">Financial Metrics Guide</span>
        </div>
        <svg 
          class="w-4 h-4 text-blue-600 dark:text-blue-400 transition-transform"
          :class="showGuide ? 'rotate-180' : ''"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>

      <div v-show="showGuide" class="mt-4 space-y-3 text-xs">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="bg-white dark:bg-slate-800 rounded-lg p-3 border border-blue-100 dark:border-blue-900">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2 h-2 rounded-full bg-blue-500"></div>
              <span class="font-semibold text-blue-900 dark:text-blue-100">MRR (Monthly Recurring Revenue)</span>
            </div>
            <p class="text-slate-600 dark:text-slate-400 mb-2">Total revenue from completed M-Pesa transactions in the current month.</p>
            <div class="bg-slate-50 dark:bg-slate-900 rounded p-2 font-mono text-[10px] text-slate-700 dark:text-slate-300">
              Sum of TransactionQueue.price<br/>
              WHERE method='mpesa'<br/>
              AND status IN ['completed', 'processed']<br/>
              AND created_at >= current_month_start
            </div>
          </div>

          <div class="bg-white dark:bg-slate-800 rounded-lg p-3 border border-emerald-100 dark:border-emerald-900">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
              <span class="font-semibold text-emerald-900 dark:text-emerald-100">ARR (Annual Recurring Revenue)</span>
            </div>
            <p class="text-slate-600 dark:text-slate-400 mb-2">Total revenue from completed M-Pesa transactions in the current year.</p>
            <div class="bg-slate-50 dark:bg-slate-900 rounded p-2 font-mono text-[10px] text-slate-700 dark:text-slate-300">
              Sum of TransactionQueue.price<br/>
              WHERE method='mpesa'<br/>
              AND status IN ['completed', 'processed']<br/>
              AND created_at >= current_year_start
            </div>
          </div>

          <div class="bg-white dark:bg-slate-800 rounded-lg p-3 border border-purple-100 dark:border-purple-900">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2 h-2 rounded-full bg-purple-500"></div>
              <span class="font-semibold text-purple-900 dark:text-purple-100">ARPU (Average Revenue Per User)</span>
            </div>
            <p class="text-slate-600 dark:text-slate-400 mb-2">Average monthly revenue generated per active user.</p>
            <div class="bg-slate-50 dark:bg-slate-900 rounded p-2 font-mono text-[10px] text-slate-700 dark:text-slate-300">
              ARPU = MRR / Active Users<br/><br/>
              Active Users = Count of users with<br/>
              active vouchers (status='active'<br/>
              AND expires_at > now)
            </div>
          </div>

          <div class="bg-white dark:bg-slate-800 rounded-lg p-3 border border-amber-100 dark:border-amber-900">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2 h-2 rounded-full bg-amber-500"></div>
              <span class="font-semibold text-amber-900 dark:text-amber-100">LTV (Lifetime Value)</span>
            </div>
            <p class="text-slate-600 dark:text-slate-400 mb-2">Estimated total revenue from a customer over their lifetime (12 months).</p>
            <div class="bg-slate-50 dark:bg-slate-900 rounded p-2 font-mono text-[10px] text-slate-700 dark:text-slate-300">
              LTV = ARPU × 12 months<br/><br/>
              Represents expected revenue<br/>
              from a customer over one year<br/>
              based on current monthly average
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-200 dark:border-slate-700">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-slate-600 dark:text-slate-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
            </svg>
            <span class="font-semibold text-slate-900 dark:text-slate-100">Growth Rate Calculation</span>
          </div>
          <p class="text-slate-600 dark:text-slate-400">Growth rate compares current month MRR vs previous month MRR: <span class="font-mono bg-slate-100 dark:bg-slate-900 px-2 py-1 rounded">((Current MRR - Previous MRR) / Previous MRR) × 100</span></p>
        </div>

        <div class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3 border border-amber-200 dark:border-amber-800">
          <div class="flex items-start gap-2">
            <svg class="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
            </svg>
            <div>
              <span class="font-semibold text-amber-900 dark:text-amber-100 text-xs">Data Source:</span>
              <p class="text-amber-800 dark:text-amber-200 text-xs mt-1">All financial metrics are calculated from the <span class="font-mono bg-amber-100 dark:bg-amber-900 px-1 rounded">TransactionQueue</span> table, filtering only completed and processed M-Pesa transactions to ensure accuracy and prevent duplicate counting.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Financial Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">MRR</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(metrics.mrr) }}</p>
        <p class="text-xs text-emerald-600 dark:text-emerald-400 mt-1">+{{ metrics.growth_rate }}% growth</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">ARR</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(metrics.arr) }}</p>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Annual recurring</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-purple-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">ARPU</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(metrics.arpu) }}</p>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Per user/month</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">LTV</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(metrics.ltv) }}</p>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Lifetime value</p>
      </div>
    </div>

    <!-- Package Performance -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Package Revenue Bar Chart -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <h3 class="text-sm font-medium text-slate-900 dark:text-white mb-3">Package Revenue</h3>
        <div v-if="packages.length" class="h-48">
          <apexchart type="bar" height="100%" :options="barOptions" :series="barSeries" />
        </div>
        <div v-else class="h-48 flex items-center justify-center text-slate-400 text-sm">No package data</div>
      </div>

      <!-- Revenue vs Profit Donut -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <h3 class="text-sm font-medium text-slate-900 dark:text-white mb-3">Revenue Split by Package</h3>
        <div v-if="packages.length" class="h-48">
          <apexchart type="donut" height="100%" :options="donutOptions" :series="donutSeries" />
        </div>
        <div v-else class="h-48 flex items-center justify-center text-slate-400 text-sm">No package data</div>
      </div>
    </div>

    <!-- Package Performance Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="flex items-center gap-2 mb-4">
        <svg class="w-5 h-5 text-cyan-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Package Performance & Margins</h3>
      </div>

      <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead class="border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th class="text-left p-2 text-slate-600 dark:text-slate-400">Package</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Sales</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Revenue</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Profit</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Margin</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="pkg in packages" 
              :key="pkg.name"
              class="border-b border-slate-200 dark:border-slate-700"
            >
              <td class="p-2 font-medium text-slate-900 dark:text-white">{{ pkg.name }}</td>
              <td class="p-2 text-center text-slate-900 dark:text-white">{{ pkg.sales }}</td>
              <td class="p-2 text-center text-slate-900 dark:text-white">KSh {{ formatNumber(pkg.revenue) }}</td>
              <td class="p-2 text-center text-slate-900 dark:text-white">KSh {{ formatNumber(pkg.profit) }}</td>
              <td class="p-2 text-center">
                <span 
                  class="px-2 py-1 rounded-full font-medium"
                  :class="pkg.margin >= 50 ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : pkg.margin >= 30 ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400' : 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400'"
                >
                  {{ pkg.margin }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import VueApexCharts from 'vue3-apexcharts'
export default {
  name: 'FinancialAnalytics',
  components: { apexchart: VueApexCharts },
  data() { return { showGuide: false } },
  props: {
    metrics: {
      type: Object,
      default: () => ({
        mrr: 0,
        arr: 0,
        arpu: 0,
        ltv: 0,
        growth_rate: 0
      })
    },
    packages: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    barSeries() {
      return [{ name: 'Revenue', data: this.packages.map(p => Math.round(p.revenue)) }]
    },
    barOptions() {
      return {
        chart: { type: 'bar', toolbar: { show: false }, background: 'transparent' },
        colors: ['#3b82f6'],
        plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
        dataLabels: { enabled: false },
        xaxis: { categories: this.packages.map(p => p.name), labels: { style: { colors: '#94a3b8', fontSize: '10px' } }, axisBorder: { show: false } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '10px' }, formatter: v => 'KES ' + new Intl.NumberFormat('en-KE', { notation: 'compact' }).format(v) } },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        tooltip: { y: { formatter: v => 'KES ' + new Intl.NumberFormat('en-KE').format(v) } }
      }
    },
    donutSeries() { return this.packages.map(p => Math.round(p.revenue)) },
    donutOptions() {
      return {
        chart: { type: 'donut', background: 'transparent' },
        labels: this.packages.map(p => p.name),
        colors: ['#3b82f6','#10b981','#8b5cf6','#f59e0b','#ef4444','#06b6d4'],
        dataLabels: { enabled: false },
        legend: { position: 'bottom', fontSize: '10px', labels: { colors: '#94a3b8' } },
        plotOptions: { pie: { donut: { size: '65%', labels: { show: true, total: { show: true, label: 'Total', color: '#94a3b8', fontSize: '11px', formatter: w => 'KES ' + new Intl.NumberFormat('en-KE', { notation: 'compact' }).format(w.globals.seriesTotals.reduce((a,b) => a+b, 0)) } } } } },
        tooltip: { y: { formatter: v => 'KES ' + new Intl.NumberFormat('en-KE').format(v) } }
      }
    }
  },
  methods: {
    formatNumber(num) { return new Intl.NumberFormat().format(num) }
  }
}
</script>
