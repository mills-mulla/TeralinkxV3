<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-cyan-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Data Quality Monitoring</h2>
      </div>
      <div class="text-right">
        <p class="text-xs text-slate-600 dark:text-slate-400">Overall Score</p>
        <p class="text-2xl font-bold" :class="getScoreColor(data.overall_score)">{{ data.overall_score }}%</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Total Checks</span>
        </div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ data.checks?.length || 0 }}</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Total Issues</span>
        </div>
        <p class="text-2xl font-bold text-red-600 dark:text-red-400">{{ data.total_issues || 0 }}</p>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
          </svg>
          <span class="text-xs text-slate-600 dark:text-slate-400">Last Check</span>
        </div>
        <p class="text-sm font-medium text-slate-900 dark:text-white">{{ formatTime(data.last_check) }}</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-slate-400">Loading...</div>

    <div v-else class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <h3 class="text-sm font-medium text-slate-900 dark:text-white mb-4">Quality Checks by Table</h3>
      <div class="space-y-3">
        <div
          v-for="check in data.checks"
          :key="check.table + check.check"
          class="p-4 rounded-lg border"
          :class="getCheckBorder(check.status)"
        >
          <div class="flex items-center justify-between mb-3">
            <div>
              <p class="text-sm font-medium text-slate-900 dark:text-white">{{ check.table }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ check.check }} Check</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-xs px-2 py-1 rounded-full" :class="getStatusBadge(check.status)">
                {{ check.status }}
              </span>
              <span class="text-lg font-bold" :class="getScoreColor(check.score)">{{ check.score }}%</span>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex-1 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden mr-3">
              <div
                class="h-full transition-all duration-500"
                :class="getScoreBar(check.score)"
                :style="{ width: check.score + '%' }"
              ></div>
            </div>
            <span class="text-xs text-slate-600 dark:text-slate-400">{{ check.issues }} issues</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataQuality',
  props: {
    data: {
      type: Object,
      default: () => ({ checks: [], overall_score: 0, total_issues: 0, last_check: null })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    getCheckBorder(status) {
      const borders = {
        'passed': 'border-emerald-200 dark:border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-500/5',
        'warning': 'border-amber-200 dark:border-amber-500/20 bg-amber-50/50 dark:bg-amber-500/5',
        'failed': 'border-red-200 dark:border-red-500/20 bg-red-50/50 dark:bg-red-500/5'
      }
      return borders[status] || 'border-slate-200 dark:border-slate-700'
    },
    getStatusBadge(status) {
      const badges = {
        'passed': 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400',
        'warning': 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400',
        'failed': 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400'
      }
      return badges[status] || 'bg-slate-100 dark:bg-slate-700'
    },
    getScoreColor(score) {
      if (score >= 95) return 'text-emerald-600 dark:text-emerald-400'
      if (score >= 85) return 'text-blue-600 dark:text-blue-400'
      if (score >= 70) return 'text-amber-600 dark:text-amber-400'
      return 'text-red-600 dark:text-red-400'
    },
    getScoreBar(score) {
      if (score >= 95) return 'bg-emerald-500'
      if (score >= 85) return 'bg-blue-500'
      if (score >= 70) return 'bg-amber-500'
      return 'bg-red-500'
    },
    formatTime(timestamp) {
      if (!timestamp) return 'Never'
      return new Date(timestamp).toLocaleString()
    }
  }
}
</script>
