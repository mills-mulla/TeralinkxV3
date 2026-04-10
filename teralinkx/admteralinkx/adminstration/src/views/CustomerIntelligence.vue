<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white">Customer Intelligence</h1>
        <p class="text-slate-600 dark:text-slate-400 mt-1">Churn prediction, retention workflow, and revenue at risk</p>
      </div>
      <button @click="refreshAll"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
        Refresh
      </button>
    </div>

    <!-- Tabs -->
    <div class="border-b border-slate-200 dark:border-slate-700 overflow-x-auto">
      <nav class="-mb-px flex space-x-6 min-w-max">
        <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors whitespace-nowrap',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-slate-400 dark:hover:text-slate-300'
          ]">
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div>
      <div v-if="activeTab === 'churn'"><ChurnDashboard ref="churnRef" /></div>
      <div v-if="activeTab === 'retention'"><RetentionDashboard ref="retentionRef" /></div>
      <div v-if="activeTab === 'revenue-at-risk'"><RevenueAtRisk /></div>
    </div>
  </div>
</template>

<script>
import ChurnDashboard from '../components/finance/ChurnDashboard.vue'
import RetentionDashboard from '../components/finance/RetentionDashboard.vue'
import RevenueAtRisk from '../components/finance/RevenueAtRisk.vue'

export default {
  name: 'CustomerIntelligence',
  components: { ChurnDashboard, RetentionDashboard, RevenueAtRisk },
  data() {
    return {
      activeTab: 'churn',
      tabs: [
        { id: 'churn',          name: '🔮 Churn Prediction' },
        { id: 'retention',      name: '🎯 Retention Tasks' },
        { id: 'revenue-at-risk', name: '⚠️ Revenue at Risk' },
      ]
    }
  },
  methods: {
    refreshAll() {
      this.$refs.churnRef?.loadPredictions?.()
      this.$refs.retentionRef?.loadTasks?.()
    }
  }
}
</script>
