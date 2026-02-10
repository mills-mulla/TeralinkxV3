<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Customer Health Scores</h2>
      <div class="text-right">
        <p class="text-xs text-slate-600 dark:text-slate-400">Avg Health Score</p>
        <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ data.summary?.avg_health_score || 0 }}</p>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div class="p-3 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20">
        <p class="text-xs text-emerald-600 dark:text-emerald-400 mb-1">Low Risk</p>
        <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300">{{ data.summary?.low_risk || 0 }}</p>
      </div>
      <div class="p-3 rounded-lg bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20">
        <p class="text-xs text-blue-600 dark:text-blue-400 mb-1">Medium Risk</p>
        <p class="text-2xl font-bold text-blue-700 dark:text-blue-300">{{ data.summary?.medium_risk || 0 }}</p>
      </div>
      <div class="p-3 rounded-lg bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20">
        <p class="text-xs text-amber-600 dark:text-amber-400 mb-1">High Risk</p>
        <p class="text-2xl font-bold text-amber-700 dark:text-amber-300">{{ data.summary?.high_risk || 0 }}</p>
      </div>
      <div class="p-3 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20">
        <p class="text-xs text-red-600 dark:text-red-400 mb-1">Critical</p>
        <p class="text-2xl font-bold text-red-700 dark:text-red-300">{{ data.summary?.critical_risk || 0 }}</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

    <div v-else class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <h3 class="text-sm font-medium text-slate-900 dark:text-white mb-4">Customer Health Details</h3>
      <div class="space-y-3">
        <div
          v-for="customer in topCustomers"
          :key="customer.user_id"
          class="p-4 rounded-lg border"
          :class="getRiskBorder(customer.risk_level)"
        >
          <div class="flex items-center justify-between mb-3">
            <div>
              <p class="text-sm font-medium text-slate-900 dark:text-white">{{ customer.username }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Last activity: {{ formatDate(customer.last_activity) }}</p>
            </div>
            <div class="text-right">
              <p class="text-2xl font-bold" :class="getScoreColor(customer.health_score)">{{ customer.health_score }}</p>
              <span class="text-xs px-2 py-1 rounded-full" :class="getRiskBadge(customer.risk_level)">
                {{ customer.risk_level }}
              </span>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div>
              <p class="text-xs text-slate-600 dark:text-slate-400">Engagement</p>
              <div class="flex items-center gap-2 mt-1">
                <div class="flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div class="h-full bg-blue-500" :style="{ width: customer.engagement_score + '%' }"></div>
                </div>
                <span class="text-xs font-medium text-slate-900 dark:text-white">{{ customer.engagement_score }}</span>
              </div>
            </div>
            <div>
              <p class="text-xs text-slate-600 dark:text-slate-400">Usage</p>
              <div class="flex items-center gap-2 mt-1">
                <div class="flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div class="h-full bg-purple-500" :style="{ width: customer.usage_score + '%' }"></div>
                </div>
                <span class="text-xs font-medium text-slate-900 dark:text-white">{{ customer.usage_score }}</span>
              </div>
            </div>
            <div>
              <p class="text-xs text-slate-600 dark:text-slate-400">Payment</p>
              <div class="flex items-center gap-2 mt-1">
                <div class="flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div class="h-full bg-emerald-500" :style="{ width: customer.payment_score + '%' }"></div>
                </div>
                <span class="text-xs font-medium text-slate-900 dark:text-white">{{ customer.payment_score }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CustomerHealth',
  props: {
    data: {
      type: Object,
      default: () => ({ health_scores: [], summary: {} })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    topCustomers() {
      return this.data.health_scores?.slice(0, 10) || []
    }
  },
  methods: {
    getRiskBorder(risk) {
      const borders = {
        'low': 'border-emerald-200 dark:border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-500/5',
        'medium': 'border-blue-200 dark:border-blue-500/20 bg-blue-50/50 dark:bg-blue-500/5',
        'high': 'border-amber-200 dark:border-amber-500/20 bg-amber-50/50 dark:bg-amber-500/5',
        'critical': 'border-red-200 dark:border-red-500/20 bg-red-50/50 dark:bg-red-500/5'
      }
      return borders[risk] || 'border-slate-200 dark:border-slate-700'
    },
    getRiskBadge(risk) {
      const badges = {
        'low': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'medium': 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400',
        'high': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'critical': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
      }
      return badges[risk] || 'bg-slate-100 dark:bg-slate-700'
    },
    getScoreColor(score) {
      if (score >= 75) return 'text-emerald-600 dark:text-emerald-400'
      if (score >= 50) return 'text-blue-600 dark:text-blue-400'
      if (score >= 25) return 'text-amber-600 dark:text-amber-400'
      return 'text-red-600 dark:text-red-400'
    },
    formatDate(date) {
      if (!date) return 'Never'
      return new Date(date).toLocaleDateString()
    }
  }
}
</script>
