<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Revenue Forecast</h3>
      </div>
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4" :class="data.trend === 'upward' ? 'text-emerald-500' : 'text-red-500'" fill="currentColor" viewBox="0 0 24 24">
          <path v-if="data.trend === 'upward'" d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
          <path v-else d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"/>
        </svg>
        <span class="text-xs font-medium" :class="data.trend === 'upward' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
          {{ data.trend === 'upward' ? 'Growing' : 'Declining' }}
        </span>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

    <div v-else>
      <!-- Chart -->
      <div v-if="chartData.length > 0" class="h-64 mb-4">
        <apexchart
          type="line"
          height="100%"
          :options="chartOptions"
          :series="chartSeries"
        />
      </div>

      <!-- Forecast Table -->
      <div class="mt-4">
        <h4 class="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2">6-Month Forecast</h4>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
          <div 
            v-for="item in data.forecast" 
            :key="item.month"
            class="p-3 rounded-lg bg-slate-50 dark:bg-slate-700/50"
          >
            <p class="text-xs text-slate-600 dark:text-slate-400">{{ item.month }}</p>
            <p class="text-lg font-bold text-slate-900 dark:text-white">KSh {{ formatNumber(item.predicted_revenue) }}</p>
            <div class="flex items-center gap-1 mt-1">
              <div class="flex-1 h-1 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500" :style="{ width: item.confidence + '%' }"></div>
              </div>
              <span class="text-xs text-slate-500 dark:text-slate-400">{{ item.confidence }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Growth Rate -->
      <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-lg">
        <div class="flex items-center justify-between">
          <span class="text-xs text-blue-600 dark:text-blue-400">Avg Monthly Growth</span>
          <span class="text-sm font-bold text-blue-700 dark:text-blue-300">KSh {{ formatNumber(data.avg_monthly_growth) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VueApexCharts from 'vue3-apexcharts'

export default {
  name: 'RevenueForecast',
  components: {
    apexchart: VueApexCharts
  },
  props: {
    data: {
      type: Object,
      default: () => ({
        historical: [],
        forecast: [],
        avg_monthly_growth: 0,
        trend: 'upward'
      })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    chartData() {
      return [...(this.data.historical || []), ...(this.data.forecast || [])]
    },
    chartSeries() {
      return [
        {
          name: 'Historical',
          data: (this.data.historical || []).map(item => ({
            x: item.month,
            y: item.revenue
          }))
        },
        {
          name: 'Forecast',
          data: (this.data.forecast || []).map(item => ({
            x: item.month,
            y: item.predicted_revenue
          }))
        }
      ]
    },
    chartOptions() {
      return {
        chart: { type: 'line', toolbar: { show: false }, zoom: { enabled: false } },
        colors: ['#3b82f6', '#10b981'],
        stroke: { width: [3, 3], dashArray: [0, 5] },
        dataLabels: { enabled: false },
        xaxis: { 
          type: 'category',
          labels: { style: { colors: '#94a3b8', fontSize: '10px' } }
        },
        yaxis: { 
          labels: { 
            style: { colors: '#94a3b8', fontSize: '10px' },
            formatter: (v) => `${this.formatNumber(v)}`
          }
        },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        tooltip: { theme: 'dark' },
        legend: { position: 'top', fontSize: '11px' }
      }
    }
  },
  methods: {
    formatNumber(num) {
      return new Intl.NumberFormat().format(Math.round(num))
    }
  }
}
</script>
