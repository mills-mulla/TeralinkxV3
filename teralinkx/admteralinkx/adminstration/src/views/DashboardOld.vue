<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2">
            📊 Analytics Dashboard
          </h1>
          <p class="text-slate-600 font-light">Real-time insights and performance metrics</p>
        </div>
        <div class="flex items-center space-x-3">
          <div class="relative">
            <div class="w-3 h-3 bg-emerald-500 rounded-full animate-ping absolute -top-1 -right-1"></div>
            <div class="w-2 h-2 bg-emerald-500 rounded-full absolute -top-0.5 -right-0.5"></div>
            <button @click="refreshData" class="p-2 hover:bg-white/50 rounded-xl transition-all duration-300 backdrop-blur-sm" title="Refresh data">
              <ArrowPathIcon class="w-6 h-6 text-slate-600" />
            </button>
          </div>
          <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
            <span class="text-white font-semibold text-sm">NG</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-rose-50 border border-rose-200 rounded-2xl p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <ExclamationTriangleIcon class="w-6 h-6 text-rose-600" />
          <div>
            <h3 class="text-rose-800 font-semibold">Failed to load dashboard data</h3>
            <p class="text-rose-600 text-sm">{{ error }}</p>
          </div>
        </div>
        <button 
          @click="fetchAllData"
          class="px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700 transition-colors duration-200 flex items-center space-x-2"
        >
          <ArrowPathIcon class="w-4 h-4" />
          <span>Retry</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !error" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-blue-200 rounded-full"></div>
          <div class="w-16 h-16 border-4 border-transparent border-t-blue-500 rounded-full animate-spin absolute top-0 left-0"></div>
        </div>
        <p class="mt-4 text-slate-500 font-light">Loading dashboard data...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="!loading" class="space-y-8">
      <!-- Client Insights Section -->
      <section>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-slate-800 flex items-center">
            <div class="w-2 h-8 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full mr-3"></div>
            Client Insights
          </h2>
          <div class="text-sm text-slate-500 bg-white/50 px-3 py-1 rounded-full backdrop-blur-sm">
            Updated just now
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <ModernMetricCard
            title="Total Clients"
            :value="metrics.totalClients || 0"
            trend="up"
            trendValue="12.5%"
            icon="👥"
            color="blue"
            :formatted="true"
          />
          
          <ModernMetricCard
            title="New Clients (7d)"
            :value="metrics.newClients7d || 0"
            trend="up"
            trendValue="8.2%"
            icon="🚀"
            color="emerald"
            :formatted="true"
          />
          
          <ModernMetricCard
            title="Active Users"
            :value="metrics.activeUsers || 0"
            trend="stable"
            trendValue="2.1%"
            icon="🟢"
            color="green"
            :formatted="true"
          />
          
          <ModernMetricCard
            title="New Today"
            :value="metrics.newClientsToday || 0"
            trend="up"
            trendValue="15.3%"
            icon="🎯"
            color="purple"
            :formatted="true"
          />
        </div>
      </section>

      <!-- Business Performance Section -->
      <section>
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-slate-800 flex items-center">
            <div class="w-2 h-8 bg-gradient-to-b from-amber-500 to-orange-600 rounded-full mr-3"></div>
            Business Performance
          </h2>
          <button class="text-sm text-blue-600 bg-blue-50 hover:bg-blue-100 px-4 py-2 rounded-xl transition-colors duration-300 flex items-center space-x-2">
            <span>View Report</span>
            <ArrowRightIcon class="w-4 h-4" />
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <ModernMetricCard
            title="Total Revenue"
            :value="`KSh ${formatNumber(metrics.totalRevenue || 0)}`"
            trend="up"
            trendValue="18.7%"
            icon="💰"
            color="amber"
            :formatted="false"
          />
          
          <ModernMetricCard
            title="Processed Orders"
            :value="metrics.totalProcessedOrders || 0"
            trend="up"
            trendValue="5.3%"
            icon="✅"
            color="indigo"
            :formatted="true"
          />
          
          <ModernMetricCard
            title="Packages Sold"
            :value="metrics.totalPackagesSold || 0"
            trend="up"
            trendValue="12.9%"
            icon="📦"
            color="cyan"
            :formatted="true"
          />
          
          <ModernMetricCard
            title="Active Ratio"
            :value="`${(metrics.activeRatio || 0).toFixed(1)}%`"
            trend="down"
            trendValue="1.2%"
            icon="📊"
            color="rose"
            :formatted="false"
          />
        </div>
      </section>

      <!-- Charts Grid -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <!-- Revenue Chart -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="font-semibold text-slate-800 flex items-center">
              <ChartBarIcon class="w-5 h-5 text-emerald-500 mr-2" />
              Revenue Analytics
            </h3>
            <select 
              v-model="revenuePeriod" 
              @change="fetchRevenueAnalytics"
              class="text-sm border-0 bg-slate-50 rounded-lg px-3 py-1 focus:ring-2 focus:ring-blue-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>
          <div v-if="revenueData.length > 0" class="h-80">
            <apexchart
              type="area"
              height="100%"
              :options="revenueChartOptions"
              :series="revenueChartSeries"
            />
          </div>
          <div v-else class="h-80 flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50/50 rounded-xl">
            <div class="text-center">
              <div class="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                <ChartBarIcon class="w-8 h-8 text-white" />
              </div>
              <p class="text-slate-600 font-light">Loading revenue data...</p>
            </div>
          </div>
        </div>

        <!-- Client Growth Chart -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="font-semibold text-slate-800 flex items-center">
              <UserGroupIcon class="w-5 h-5 text-blue-500 mr-2" />
              Client Growth
            </h3>
            <select 
              v-model="growthPeriod" 
              @change="fetchClientGrowth"
              class="text-sm border-0 bg-slate-50 rounded-lg px-3 py-1 focus:ring-2 focus:ring-blue-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>
          <div v-if="clientGrowthData.length > 0" class="h-80">
            <apexchart
              type="bar"
              height="100%"
              :options="growthChartOptions"
              :series="growthChartSeries"
            />
          </div>
          <div v-else class="h-80 flex items-center justify-center bg-gradient-to-br from-slate-50 to-purple-50/50 rounded-xl">
            <div class="text-center">
              <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                <UserGroupIcon class="w-8 h-8 text-white" />
              </div>
              <p class="text-slate-600 font-light">Loading growth data...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Charts -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <!-- Package Distribution -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
          <h3 class="font-semibold text-slate-800 mb-6 flex items-center">
            <ShoppingBagIcon class="w-5 h-5 text-amber-500 mr-2" />
            Package Distribution
          </h3>
          <div class="h-80">
            <apexchart
              type="donut"
              height="100%"
              :options="packageChartOptions"
              :series="packageChartSeries"
            />
          </div>
        </div>

        <!-- System Performance -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
          <h3 class="font-semibold text-slate-800 mb-6 flex items-center">
            <Cog6ToothIcon class="w-5 h-5 text-slate-600 mr-2" />
            System Performance
          </h3>
          <div class="h-80">
            <apexchart
              type="radialBar"
              height="100%"
              :options="performanceChartOptions"
              :series="performanceChartSeries"
            />
          </div>
        </div>
      </div>

      <!-- Quick Stats & Activity -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- System Status -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
          <h3 class="font-semibold text-slate-800 mb-4 flex items-center">
            <Cog6ToothIcon class="w-5 h-5 text-slate-600 mr-2" />
            System Status
          </h3>
          <div class="space-y-4">
            <div v-for="stat in systemStats" :key="stat.name" class="flex items-center justify-between p-3 hover:bg-slate-50 rounded-xl transition-colors duration-200">
              <div class="flex items-center space-x-3">
                <div :class="`w-3 h-3 rounded-full ${stat.statusColor}`"></div>
                <span class="text-slate-700 font-medium">{{ stat.name }}</span>
              </div>
              <span class="text-slate-500 text-sm">{{ stat.value }}</span>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
          <h3 class="font-semibold text-slate-800 mb-4 flex items-center">
            <ClockIcon class="w-5 h-5 text-slate-600 mr-2" />
            Recent Activity
          </h3>
          <div class="space-y-4">
            <div v-for="activity in recentActivities" :key="activity.id" class="flex items-center space-x-3 p-3 hover:bg-slate-50 rounded-xl transition-colors duration-200">
              <div :class="`w-10 h-10 rounded-xl flex items-center justify-center ${activity.bgColor}`">
                <component :is="activity.icon" class="w-5 h-5 text-white" />
              </div>
              <div class="flex-1">
                <p class="text-slate-800 font-medium text-sm">{{ activity.title }}</p>
                <p class="text-slate-500 text-xs">{{ activity.time }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Metrics -->
        <div class="bg-gradient-to-br from-blue-600 to-purple-700 rounded-2xl shadow-lg p-6 text-white">
          <h3 class="font-semibold mb-4">Performance Score</h3>
          <div class="text-center mb-6">
            <div class="relative inline-block">
              <div class="w-32 h-32 rounded-full border-4 border-white/20 flex items-center justify-center">
                <div class="text-center">
                  <div class="text-3xl font-bold">{{ performanceScore }}%</div>
                  <div class="text-blue-200 text-sm">{{ performanceStatus }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="space-y-3">
            <div v-for="metric in performanceMetrics" :key="metric.name" class="flex items-center justify-between">
              <span class="text-blue-200 text-sm">{{ metric.name }}</span>
              <span class="font-semibold">{{ metric.value }}</span>
            </div>
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

import { 
  BellIcon,
  ArrowRightIcon,
  ChartBarIcon,
  UserGroupIcon,
  EyeIcon,
  ArrowUpTrayIcon,
  Cog6ToothIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  ShoppingBagIcon
} from '@heroicons/vue/24/outline'

import { 
  UserPlusIcon,
  CurrencyDollarIcon,
  CogIcon,
} from '@heroicons/vue/24/solid'

export default {
  name: 'Dashboard',
  components: {
    ModernMetricCard,
    apexchart: VueApexCharts,
    BellIcon,
    ArrowRightIcon,
    ChartBarIcon,
    UserGroupIcon,
    EyeIcon,
    ArrowUpTrayIcon,
    Cog6ToothIcon,
    ClockIcon,
    ExclamationTriangleIcon,
    ArrowPathIcon,
    ShoppingBagIcon,
    UserPlusIcon,
    CurrencyDollarIcon,
    CogIcon,
  },
  setup() {
    const { loading, error, makeRequest } = useApi()
    return { loading, error, makeRequest }
  },
  data() {
    return {
      revenuePeriod: '7d',
      growthPeriod: '30d',
      metrics: {
        totalClients: 0,
        newClients7d: 0,
        newClientsToday: 0,
        activeUsers: 0,
        totalRevenue: 0,
        totalProcessedOrders: 0,
        totalPackagesSold: 0,
        activeRatio: 0,
      },
      revenueData: [],
      clientGrowthData: [],
      systemStats: [],
      recentActivities: [],
      performanceScore: 0,
      performanceStatus: 'Excellent',
      
      // Chart options and series
      revenueChartOptions: {
        chart: {
          type: 'area',
          height: '100%',
          toolbar: { show: false },
          zoom: { enabled: false }
        },
        colors: ['#10B981'],
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 3 },
        fill: {
          type: 'gradient',
          gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.7,
            opacityTo: 0.1,
            stops: [0, 90, 100]
          }
        },
        xaxis: {
          type: 'datetime',
          labels: {
            style: { colors: '#6B7280', fontSize: '12px' }
          }
        },
        yaxis: {
          labels: {
            style: { colors: '#6B7280', fontSize: '12px' },
            formatter: (value) => `KSh ${this.formatNumber(value)}`
          }
        },
        tooltip: {
          x: { format: 'dd MMM yyyy' },
          y: {
            formatter: (value) => `KSh ${this.formatNumber(value)}`
          }
        },
        grid: {
          borderColor: '#F3F4F6',
          strokeDashArray: 4,
        }
      },
      revenueChartSeries: [{ name: 'Revenue', data: [] }],

      growthChartOptions: {
        chart: {
          type: 'bar',
          height: '100%',
          toolbar: { show: false }
        },
        colors: ['#8B5CF6'],
        plotOptions: {
          bar: {
            borderRadius: 4,
            columnWidth: '60%',
          }
        },
        dataLabels: { enabled: false },
        xaxis: {
          type: 'datetime',
          labels: {
            style: { colors: '#6B7280', fontSize: '12px' }
          }
        },
        yaxis: {
          labels: {
            style: { colors: '#6B7280', fontSize: '12px' }
          }
        },
        grid: {
          borderColor: '#F3F4F6',
          strokeDashArray: 4,
        }
      },
      growthChartSeries: [{ name: 'New Signups', data: [] }],

      packageChartOptions: {
        chart: {
          type: 'donut',
          height: '100%'
        },
        colors: ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'],
        labels: ['Basic', 'Standard', 'Premium', 'Enterprise', 'Custom'],
        legend: {
          position: 'bottom',
          fontSize: '12px',
          labels: { colors: '#6B7280' }
        },
        plotOptions: {
          pie: {
            donut: {
              size: '65%',
              labels: {
                show: true,
                total: {
                  show: true,
                  label: 'Total Packages',
                  color: '#6B7280',
                  formatter: () => this.formatNumber(this.metrics.totalPackagesSold || 0)
                }
              }
            }
          }
        },
        dataLabels: { enabled: false }
      },
      packageChartSeries: [35, 25, 20, 15, 5],

      performanceChartOptions: {
        chart: {
          type: 'radialBar',
          height: '100%'
        },
        colors: ['#10B981'],
        plotOptions: {
          radialBar: {
            hollow: { size: '60%' },
            dataLabels: {
              name: { fontSize: '16px', color: '#6B7280' },
              value: { 
                fontSize: '24px', 
                color: '#1F2937',
                formatter: (val) => `${val}%`
              }
            }
          }
        },
        labels: ['System Uptime'],
      },
      performanceChartSeries: [99.9],

      performanceMetrics: [
        { name: 'Response Time', value: '124ms' },
        { name: 'Success Rate', value: '99.8%' },
        { name: 'Peak Load', value: '2.4k' },
        { name: 'Avg. Session', value: '8.2m' }
      ]
    }
  },
  async mounted() {
    await this.fetchAllData();
  },
  methods: {
    async fetchAllData() {
      try {
        this.error = null;
        
        await Promise.all([
          this.fetchDashboardMetrics(),
          this.fetchRevenueAnalytics(),
          this.fetchClientGrowth(),
          this.fetchSystemStatus()
        ]);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        this.error = error.response?.data?.error || 'Failed to load dashboard data';
      }
    },

    async fetchDashboardMetrics() {
      try {
        const data = await this.makeRequest('get', 'suapi/dashboard-metrics/');
        this.metrics = data;
      } catch (error) {
        console.error('Error fetching dashboard metrics:', error);
        throw error;
      }
    },

    async fetchRevenueAnalytics() {
      try {
        const data = await this.makeRequest('get', `suapi/dashboard-metrics/revenue-analytics/?period=${this.revenuePeriod}`);
        this.revenueData = data.data;
        
        // Update chart series
        this.revenueChartSeries = [{
          name: 'Revenue',
          data: this.revenueData.map(item => ({
            x: new Date(item.date).getTime(),
            y: item.revenue
          }))
        }];
      } catch (error) {
        console.error('Error fetching revenue analytics:', error);
      }
    },

    async fetchClientGrowth() {
      try {
        const data = await this.makeRequest('get', `suapi/dashboard-metrics/client-growth/?period=${this.growthPeriod}`);
        this.clientGrowthData = data.data;
        
        // Update chart series
        this.growthChartSeries = [{
          name: 'New Signups',
          data: this.clientGrowthData.map(item => ({
            x: new Date(item.date).getTime(),
            y: item.signups
          }))
        }];
      } catch (error) {
        console.error('Error fetching client growth:', error);
      }
    },

    async fetchSystemStatus() {
      try {
        const data = await this.makeRequest('get', 'suapi/system-status/');
        
        this.systemStats = [
          { name: 'API Response', value: data.apiResponseTime, statusColor: 'bg-emerald-500' },
          { name: 'Uptime', value: data.uptime, statusColor: 'bg-emerald-500' },
          { name: 'Active Sessions', value: data.activeSessions, statusColor: 'bg-blue-500' },
          { name: 'Error Rate', value: `${data.errorRate}%`, statusColor: data.errorRate > 5 ? 'bg-rose-500' : 'bg-amber-500' }
        ];

        this.performanceScore = data.uptime.replace('%', '');
        this.performanceStatus = this.performanceScore >= 99 ? 'Excellent' : 
                                this.performanceScore >= 95 ? 'Good' : 'Needs Attention';

        // Update performance chart
        this.performanceChartSeries = [parseFloat(this.performanceScore)];

      } catch (error) {
        console.error('Error fetching system status:', error);
      }
    },

    refreshData() {
      this.fetchAllData();
    },

    formatNumber(num) {
      return new Intl.NumberFormat().format(num);
    },

    calculateTotalRevenue() {
      return this.revenueData.reduce((sum, item) => sum + item.revenue, 0);
    }
  }
}
</script>

<style scoped>
/* Custom styles for better chart integration */
:deep(.apexcharts-tooltip) {
  background: #1F2937 !important;
  border: 1px solid #374151 !important;
  border-radius: 8px !important;
}

:deep(.apexcharts-tooltip-title) {
  background: #111827 !important;
  border-bottom: 1px solid #374151 !important;
  color: #F9FAFB !important;
}

:deep(.apexcharts-tooltip-text) {
  color: #F9FAFB !important;
}

:deep(.apexcharts-legend-text) {
  color: #6B7280 !important;
  font-size: 12px !important;
}
</style>