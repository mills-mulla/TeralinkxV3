<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
        <h3 class="text-sm font-medium text-slate-900 dark:text-white">Churn Prediction</h3>
      </div>
      <div class="text-right">
        <p class="text-xs text-slate-600 dark:text-slate-400">Churn Rate</p>
        <p class="text-lg font-bold text-red-600 dark:text-red-400">{{ data.churn_rate }}%</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

    <div v-else>
      <!-- Risk Summary -->
      <div class="grid grid-cols-3 gap-3 mb-4">
        <div class="p-3 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20">
          <p class="text-xs text-red-600 dark:text-red-400 mb-1">High Risk</p>
          <p class="text-2xl font-bold text-red-700 dark:text-red-300">{{ data.summary?.high_risk || 0 }}</p>
        </div>
        <div class="p-3 rounded-lg bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20">
          <p class="text-xs text-amber-600 dark:text-amber-400 mb-1">Medium Risk</p>
          <p class="text-2xl font-bold text-amber-700 dark:text-amber-300">{{ data.summary?.medium_risk || 0 }}</p>
        </div>
        <div class="p-3 rounded-lg bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/20">
          <p class="text-xs text-yellow-600 dark:text-yellow-400 mb-1">Low Risk</p>
          <p class="text-2xl font-bold text-yellow-700 dark:text-yellow-300">{{ data.summary?.low_risk || 0 }}</p>
        </div>
      </div>

      <!-- At-Risk Users Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead class="border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th class="text-left p-2 text-slate-600 dark:text-slate-400">User</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Inactive Days</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Purchases</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Risk</th>
              <th class="text-center p-2 text-slate-600 dark:text-slate-400">Probability</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="user in topAtRisk" 
              :key="user.user_id"
              class="border-b border-slate-200 dark:border-slate-700"
            >
              <td class="p-2 text-slate-900 dark:text-white">{{ user.username }}</td>
              <td class="p-2 text-center text-slate-900 dark:text-white">{{ user.days_inactive }}</td>
              <td class="p-2 text-center text-slate-900 dark:text-white">{{ user.total_purchases }}</td>
              <td class="p-2 text-center">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="getRiskBadge(user.risk_level)">
                  {{ user.risk_level }}
                </span>
              </td>
              <td class="p-2 text-center">
                <span class="font-bold" :class="getRiskColor(user.churn_probability)">
                  {{ user.churn_probability }}%
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
export default {
  name: 'ChurnPrediction',
  props: {
    data: {
      type: Object,
      default: () => ({
        at_risk_users: [],
        summary: {},
        churn_rate: 0
      })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    topAtRisk() {
      return this.data.at_risk_users?.slice(0, 10) || []
    }
  },
  methods: {
    getRiskBadge(risk) {
      const badges = {
        'high': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400',
        'medium': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'low': 'bg-yellow-100 dark:bg-yellow-500/20 text-yellow-700 dark:text-yellow-400'
      }
      return badges[risk] || 'bg-slate-100 dark:bg-slate-700'
    },
    getRiskColor(probability) {
      if (probability >= 70) return 'text-red-600 dark:text-red-400'
      if (probability >= 50) return 'text-amber-600 dark:text-amber-400'
      return 'text-yellow-600 dark:text-yellow-400'
    }
  }
}
</script>
