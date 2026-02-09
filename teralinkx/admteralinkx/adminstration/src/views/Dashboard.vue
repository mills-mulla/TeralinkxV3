<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Dashboard</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Welcome back, here's your overview</p>
      </div>
      <button 
        @click="refreshData" 
        class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
        :class="{ 'animate-spin': loading }"
      >
        <ArrowPathIcon class="w-5 h-5 text-slate-600 dark:text-slate-400" />
      </button>
    </div>

    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      <ModernMetricCard
        title="Total Clients"
        :value="metrics.totalClients || 0"
        trend="up"
        trendValue="12.5%"
        icon="👥"
        color="blue"
      />
      <ModernMetricCard
        title="New (7d)"
        :value="metrics.newClients7d || 0"
        trend="up"
        trendValue="8.2%"
        icon="🚀"
        color="emerald"
      />
      <ModernMetricCard
        title="Active Users"
        :value="metrics.activeUsers || 0"
        trend="stable"
        trendValue="2.1%"
        icon="✅"
        color="green"
      />
      <ModernMetricCard
        title="Revenue"
        :value="`KSh ${formatNumber(metrics.totalRevenue || 0)}`"
        trend="up"
        trendValue="18.7%"
        icon="💰"
        color="amber"
        :formatted="false"
      />
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up" style="animation-delay: 0.1s">
      <!-- Revenue Chart -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 transition-colors duration-300">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-medium text-slate-900 dark:text-white">Revenue Analytics</h3>
          <select 
            v-model="revenuePeriod" 
            @change="fetchRevenueAnalytics"
            class="text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 text-slate-900 dark:text-white"
          >
            <option value="7d">7 days</option>
            <option value="30d">30 days</option>
          </select>
        </div>
        <div v-if="revenueData.length > 0" class="h-64">
          <apexchart
            type="area"
            height="100%"
            :options="revenueChartOptions"
            :series="revenueChartSeries"
          />
        </div>
        <div v-else class="h-64 flex items-center justify-center text-slate-400 dark:text-slate-500 text-sm">
          Loading...
        </div>
      </div>

      <!-- Growth Chart -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 transition-colors duration-300">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-medium text-slate-900 dark:text-white">Client Growth</h3>
          <select 
            v-model="growthPeriod" 
            @change="fetchClientGrowth"
            class="text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 text-slate-900 dark:text-white"
          >
            <option value="7d">7 days</option>
            <option value="30d">30 days</option>
          </select>
        </div>
        <div v-if="clientGrowthData.length > 0" class="h-64">
          <apexchart
            type="bar"
            height="100%"
            :options="growthChartOptions"
            :series="growthChartSeries"
          />
        </div>
        <div v-else class="h-64 flex items-center justify-center text-slate-400 dark:text-slate-500 text-sm">
          Loading...
        </div>
      </div>
    </div>

    <!-- System Status -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 transition-colors duration-300 animate-slide-up" style="animation-delay: 0.2s">
      <h3 class="text-sm font-medium text-slate-900 dark:text-white mb-4">System Status</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="stat in systemStats" :key="stat.name" class="flex items-center gap-3">
          <div :class="`w-2 h-2 rounded-full ${stat.statusColor}`"></div>
          <div>
            <p class="text-xs text-slate-500 dark:text-slate-400">{{ stat.name }}</p>
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ stat.value }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ModernMetricCard from '../components/MetricCard.vue'
import VueApexCharts from 'vue3-apexcharts'
import { useApi } from '../composables/useApi'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'Dashboard',
  components: {
    ModernMetricCard,
    apexchart: VueApexCharts,
    ArrowPathIcon
  },
  setup() {
    const { loading, makeRequest } = useApi()
    return { loading, makeRequest }
  },
  data() {
    return {
      revenuePeriod: '7d',
      growthPeriod: '30d',
      metrics: {},
      revenueData: [],
      clientGrowthData: [],
      systemStats: [],
      
      revenueChartOptions: {
        chart: { type: 'area', toolbar: { show: false }, zoom: { enabled: false } },
        colors: ['#10B981'],
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 2 },
        fill: { type: 'gradient', gradient: { opacityFrom: 0.4, opacityTo: 0.1 } },
        xaxis: { type: 'datetime', labels: { style: { colors: '#94a3b8', fontSize: '11px' } } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '11px' }, formatter: (v) => `${this.formatNumber(v)}` } },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        tooltip: { theme: 'dark' }
      },
      revenueChartSeries: [{ name: 'Revenue', data: [] }],

      growthChartOptions: {
        chart: { type: 'bar', toolbar: { show: false } },
        colors: ['#8B5CF6'],
        plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
        dataLabels: { enabled: false },
        xaxis: { type: 'datetime', labels: { style: { colors: '#94a3b8', fontSize: '11px' } } },
        yaxis: { labels: { style: { colors: '#94a3b8', fontSize: '11px' } } },
        grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
        tooltip: { theme: 'dark' }
      },
      growthChartSeries: [{ name: 'Signups', data: [] }]
    }
  },
  async mounted() {
    await this.fetchAllData()
  },
  methods: {
    async fetchAllData() {
      await Promise.all([
        this.fetchDashboardMetrics(),
        this.fetchRevenueAnalytics(),
        this.fetchClientGrowth(),
        this.fetchSystemStatus()
      ])
    },

    async fetchDashboardMetrics() {
      try {
        this.metrics = await this.makeRequest('get', 'suapi/dashboard-metrics/')
      } catch (error) {
        console.error('Error fetching metrics:', error)
      }
    },

    async fetchRevenueAnalytics() {
      try {
        const data = await this.makeRequest('get', `suapi/dashboard-metrics/revenue-analytics/?period=${this.revenuePeriod}`)
        this.revenueData = data.data
        this.revenueChartSeries = [{
          name: 'Revenue',
          data: this.revenueData.map(item => ({ x: new Date(item.date).getTime(), y: item.revenue }))
        }]
      } catch (error) {
        console.error('Error fetching revenue:', error)
      }
    },

    async fetchClientGrowth() {
      try {
        const data = await this.makeRequest('get', `suapi/dashboard-metrics/client-growth/?period=${this.growthPeriod}`)
        this.clientGrowthData = data.data
        this.growthChartSeries = [{
          name: 'Signups',
          data: this.clientGrowthData.map(item => ({ x: new Date(item.date).getTime(), y: item.signups }))
        }]
      } catch (error) {
        console.error('Error fetching growth:', error)
      }
    },

    async fetchSystemStatus() {
      try {
        const data = await this.makeRequest('get', 'suapi/system-status/')
        this.systemStats = [
          { name: 'Response', value: data.apiResponseTime, statusColor: 'bg-emerald-500' },
          { name: 'Uptime', value: data.uptime, statusColor: 'bg-emerald-500' },
          { name: 'Sessions', value: data.activeSessions, statusColor: 'bg-blue-500' },
          { name: 'Errors', value: `${data.errorRate}%`, statusColor: 'bg-amber-500' }
        ]
      } catch (error) {
        console.error('Error fetching status:', error)
      }
    },

    refreshData() {
      this.fetchAllData()
    },

    formatNumber(num) {
      return new Intl.NumberFormat().format(num)
    }
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.4s ease-out;
}
</style>
