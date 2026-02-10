<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Advanced Analytics</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Deep insights into customer behavior and financial performance</p>
      </div>
      <div class="flex items-center gap-3">
        <DateRangePicker @change="handleDateChange" />
        <ExportButton :data="exportData" filename="advanced-analytics" />
        <button 
          @click="refreshData" 
          class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
          :class="{ 'animate-spin': loading }"
        >
          <svg class="w-5 h-5 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-2">
      <div class="flex gap-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="flex-1 px-4 py-2 text-sm rounded-lg transition-colors"
          :class="activeTab === tab.id ? 'bg-blue-500 text-white' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'"
        >
          {{ tab.name }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div v-if="activeTab === 'financial'">
      <FinancialAnalytics 
        :metrics="financialMetrics" 
        :packages="packagePerformance"
        :loading="loading"
      />
    </div>

    <div v-if="activeTab === 'customers'">
      <RFMSegmentation 
        :segments="rfmSegments" 
        :summary="rfmSummary"
        :loading="loading"
      />
    </div>

    <div v-if="activeTab === 'retention'">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CohortAnalysis :data="cohortData" :loading="loading" />
        <FunnelAnalysis :data="funnelData" :loading="loading" />
      </div>
    </div>

    <div v-if="activeTab === 'predictive'">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChurnPrediction :data="churnData" :loading="loading" />
        <RevenueForecast :data="forecastData" :loading="loading" />
      </div>
    </div>

    <div v-if="activeTab === 'network'">
      <NetworkAnalytics :data="networkData" :loading="loading" />
    </div>

    <div v-if="activeTab === 'builder'">
      <DashboardBuilder />
    </div>
  </div>
</template>

<script>
import { useApi } from '../composables/useApi'
import DateRangePicker from '../components/DateRangePicker.vue'
import ExportButton from '../components/ExportButton.vue'
import FinancialAnalytics from '../components/FinancialAnalytics.vue'
import RFMSegmentation from '../components/RFMSegmentation.vue'
import CohortAnalysis from '../components/CohortAnalysis.vue'
import FunnelAnalysis from '../components/FunnelAnalysis.vue'
import ChurnPrediction from '../components/ChurnPrediction.vue'
import RevenueForecast from '../components/RevenueForecast.vue'
import NetworkAnalytics from '../components/NetworkAnalytics.vue'
import DashboardBuilder from '../components/DashboardBuilder.vue'

export default {
  name: 'Analytics',
  components: {
    DateRangePicker,
    ExportButton,
    FinancialAnalytics,
    RFMSegmentation,
    CohortAnalysis,
    FunnelAnalysis,
    ChurnPrediction,
    RevenueForecast,
    NetworkAnalytics,
    DashboardBuilder
  },
  setup() {
    const { loading, makeRequest } = useApi()
    return { loading, makeRequest }
  },
  data() {
    return {
      activeTab: 'financial',
      tabs: [
        { id: 'financial', name: 'Financial' },
        { id: 'customers', name: 'Customers' },
        { id: 'retention', name: 'Retention' },
        { id: 'predictive', name: 'Predictive' },
        { id: 'network', name: 'Network' },
        { id: 'builder', name: 'Builder' }
      ],
      dateRange: {},
      financialMetrics: {},
      packagePerformance: [],
      rfmSegments: [],
      rfmSummary: {},
      cohortData: [],
      funnelData: {},
      churnData: {},
      forecastData: {},
      networkData: {}
    }
  },
  computed: {
    exportData() {
      return {
        financial: this.financialMetrics,
        packages: this.packagePerformance,
        rfm: { segments: this.rfmSegments, summary: this.rfmSummary },
        cohorts: this.cohortData,
        funnel: this.funnelData,
        churn: this.churnData,
        forecast: this.forecastData,
        network: this.networkData
      }
    }
  },
  async mounted() {
    await this.fetchAllData()
  },
  methods: {
    handleDateChange(range) {
      this.dateRange = range
      this.fetchAllData()
    },

    async fetchAllData() {
      await Promise.all([
        this.fetchFinancialAnalytics(),
        this.fetchRFMSegmentation(),
        this.fetchCohortAnalysis(),
        this.fetchFunnelAnalysis(),
        this.fetchChurnPrediction(),
        this.fetchRevenueForecast(),
        this.fetchNetworkAnalytics()
      ])
    },

    async fetchFinancialAnalytics() {
      try {
        const data = await this.makeRequest('get', 'suapi/dashboard-metrics/financial-analytics/')
        this.financialMetrics = {
          mrr: data.mrr,
          arr: data.arr,
          arpu: data.arpu,
          ltv: data.ltv,
          growth_rate: data.growth_rate
        }
        this.packagePerformance = data.package_performance || []
      } catch (error) {
        console.error('Error fetching financial analytics:', error)
      }
    },

    async fetchRFMSegmentation() {
      try {
        const data = await this.makeRequest('get', 'suapi/dashboard-metrics/rfm-segmentation/')
        this.rfmSegments = data.segments || []
        this.rfmSummary = data.summary || {}
      } catch (error) {
        console.error('Error fetching RFM segmentation:', error)
      }
    },

    async fetchCohortAnalysis() {
      try {
        const data = await this.makeRequest('get', 'suapi/dashboard-metrics/cohort-analysis/')
        this.cohortData = data.data || []
      } catch (error) {
        console.error('Error fetching cohort analysis:', error)
      }
    },

    async fetchFunnelAnalysis() {
      try {
        this.funnelData = await this.makeRequest('get', 'suapi/dashboard-metrics/funnel-analysis/')
      } catch (error) {
        console.error('Error fetching funnel analysis:', error)
      }
    },

    async fetchChurnPrediction() {
      try {
        this.churnData = await this.makeRequest('get', 'suapi/dashboard-metrics/churn-prediction/')
      } catch (error) {
        console.error('Error fetching churn prediction:', error)
      }
    },

    async fetchRevenueForecast() {
      try {
        this.forecastData = await this.makeRequest('get', 'suapi/dashboard-metrics/revenue-forecast/')
      } catch (error) {
        console.error('Error fetching revenue forecast:', error)
      }
    },

    async fetchNetworkAnalytics() {
      try {
        this.networkData = await this.makeRequest('get', 'suapi/dashboard-metrics/network-analytics/')
      } catch (error) {
        console.error('Error fetching network analytics:', error)
      }
    },

    refreshData() {
      this.fetchAllData()
    }
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>
