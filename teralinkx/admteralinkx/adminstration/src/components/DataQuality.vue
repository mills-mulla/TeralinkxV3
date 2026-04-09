<template>
  <div class="space-y-6">
    <!-- Overall Score Card -->
    <div class="bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-cyan-100 text-sm font-medium mb-2">Overall Data Quality Score</p>
          <div class="flex items-baseline gap-3">
            <p class="text-5xl font-bold">{{ data.overall_score || 0 }}%</p>
            <span class="text-lg" :class="getTrendIcon(data.trend)">
              {{ data.trend > 0 ? '↑' : data.trend < 0 ? '↓' : '→' }} {{ Math.abs(data.trend || 0) }}%
            </span>
          </div>
          <p class="text-cyan-100 text-xs mt-2">Last checked: {{ formatTime(data.last_check) }}</p>
        </div>
        <div class="text-right">
          <div class="w-32 h-32 relative">
            <svg class="transform -rotate-90" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="12"/>
              <circle
                cx="60" cy="60" r="54" fill="none"
                stroke="white"
                stroke-width="12"
                stroke-dasharray="339.292"
                :stroke-dashoffset="339.292 - (339.292 * (data.overall_score || 0) / 100)"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <svg class="w-12 h-12" fill="white" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <div class="flex items-center gap-2 mb-2">
          <div class="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-500/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <div>
            <p class="text-xs text-slate-600 dark:text-slate-400">Passed</p>
            <p class="text-xl font-bold text-slate-900 dark:text-white">{{ passedChecks }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <div class="flex items-center gap-2 mb-2">
          <div class="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-500/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-amber-600 dark:text-amber-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
            </svg>
          </div>
          <div>
            <p class="text-xs text-slate-600 dark:text-slate-400">Warnings</p>
            <p class="text-xl font-bold text-slate-900 dark:text-white">{{ warningChecks }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <div class="flex items-center gap-2 mb-2">
          <div class="w-10 h-10 rounded-lg bg-red-100 dark:bg-red-500/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
          </div>
          <div>
            <p class="text-xs text-slate-600 dark:text-slate-400">Failed</p>
            <p class="text-xl font-bold text-slate-900 dark:text-white">{{ failedChecks }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <div class="flex items-center gap-2 mb-2">
          <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M11 15h2v2h-2zm0-8h2v6h-2zm.99-5C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
            </svg>
          </div>
          <div>
            <p class="text-xs text-slate-600 dark:text-slate-400">Total Issues</p>
            <p class="text-xl font-bold text-slate-900 dark:text-white">{{ data.total_issues || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quality Checks Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Data Quality Checks</h3>
        <button @click="runChecks" :disabled="loading" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors flex items-center gap-2" :class="{ 'opacity-50': loading }">
          <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ loading ? 'Running...' : 'Run Checks' }}
        </button>
      </div>

      <div v-if="loading" class="p-12 text-center">
        <svg class="animate-spin h-10 w-10 mx-auto mb-4 text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-slate-600 dark:text-slate-400">Running quality checks...</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Table</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Check Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Score</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Issues</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr
              v-for="check in data.checks"
              :key="check.table + check.check"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-slate-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
                  </svg>
                  <span class="text-sm font-medium text-slate-900 dark:text-white">{{ check.table }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-slate-600 dark:text-slate-400">{{ check.check }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                  <div class="flex-1 w-24 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      class="h-full transition-all"
                      :class="getScoreBar(check.score)"
                      :style="{ width: check.score + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm font-bold" :class="getScoreColor(check.score)">{{ check.score }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-semibold text-slate-900 dark:text-white">{{ check.issues }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-3 py-1 text-xs font-medium rounded-full" :class="getStatusBadge(check.status)">
                  {{ check.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <button @click="showDetails(check)" class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors">
                  View Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-if="recommendations.length > 0" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        Recommendations
      </h3>
      <div class="space-y-3">
        <div
          v-for="(rec, index) in recommendations"
          :key="index"
          class="p-4 bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-500/20 rounded-lg"
        >
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
            </svg>
            <div class="flex-1">
              <p class="text-sm font-medium text-slate-900 dark:text-white">{{ rec.title }}</p>
              <p class="text-xs text-slate-600 dark:text-slate-400 mt-1">{{ rec.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="selectedCheck" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="selectedCheck = null">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full">
        <div class="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Quality Check Details</h2>
          <button @click="selectedCheck = null" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Table</label>
              <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ selectedCheck.table }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Check Type</label>
              <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ selectedCheck.check }}</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Score</label>
              <p class="text-2xl font-bold" :class="getScoreColor(selectedCheck.score)">{{ selectedCheck.score }}%</p>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Status</label>
              <span class="px-3 py-1 text-xs font-medium rounded-full" :class="getStatusBadge(selectedCheck.status)">
                {{ selectedCheck.status }}
              </span>
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">Issues Found</label>
            <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
              <p class="text-3xl font-bold text-slate-900 dark:text-white">{{ selectedCheck.issues }}</p>
              <p class="text-xs text-slate-600 dark:text-slate-400 mt-1">records with data quality issues</p>
            </div>
          </div>
          <div class="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-500/30 rounded-lg">
            <p class="text-sm font-medium text-blue-900 dark:text-blue-400 mb-2">💡 Recommendation</p>
            <p class="text-xs text-blue-700 dark:text-blue-300">{{ getRecommendation(selectedCheck) }}</p>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700">
          <button @click="selectedCheck = null" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg">Close</button>
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
      default: () => ({ checks: [], overall_score: 0, total_issues: 0, last_check: null, trend: 0 })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  data() {
    return {
      selectedCheck: null
    }
  },
  computed: {
    passedChecks() {
      return (this.data.checks || []).filter(c => c.status === 'passed').length
    },
    warningChecks() {
      return (this.data.checks || []).filter(c => c.status === 'warning').length
    },
    failedChecks() {
      return (this.data.checks || []).filter(c => c.status === 'failed').length
    },
    recommendations() {
      const recs = []
      const checks = this.data.checks || []
      
      checks.forEach(check => {
        if (check.status === 'failed' || check.status === 'warning') {
          recs.push({
            title: `Improve ${check.table} ${check.check}`,
            description: this.getRecommendation(check)
          })
        }
      })
      
      return recs.slice(0, 5)
    }
  },
  methods: {
    runChecks() {
      this.$emit('refresh')
    },
    showDetails(check) {
      this.selectedCheck = check
    },
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
    getTrendIcon(trend) {
      if (trend > 0) return 'text-emerald-300'
      if (trend < 0) return 'text-red-300'
      return 'text-cyan-300'
    },
    formatTime(timestamp) {
      if (!timestamp) return 'Never'
      const date = new Date(timestamp)
      const now = new Date()
      const diff = Math.floor((now - date) / 1000)
      
      if (diff < 60) return 'Just now'
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
      return date.toLocaleDateString()
    },
    getRecommendation(check) {
      const recommendations = {
        'Completeness': `Review and fill in missing ${check.table} data. Implement validation rules to prevent incomplete records.`,
        'Accuracy': `Verify ${check.table} data accuracy. Cross-reference with source systems and correct discrepancies.`,
        'Consistency': `Standardize ${check.table} data formats. Implement data normalization procedures.`,
        'Timeliness': `Update ${check.table} records more frequently. Set up automated data refresh schedules.`,
        'Validity': `Validate ${check.table} data against business rules. Remove or correct invalid entries.`
      }
      return recommendations[check.check] || `Review and improve ${check.table} data quality.`
    }
  }
}
</script>
