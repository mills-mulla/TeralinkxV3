<template>
  <div class="space-y-6">
    <GuidePanel title="Budget Intelligence" :terms="[
        { label: 'Utilization Rate', color: 'blue', description: 'Percentage of the monthly budget already spent. Context matters — 80% spent with 60% of month elapsed is on track.', formula: 'Spent ÷ Budget × 100' },
        { label: 'Expected Utilization', color: 'emerald', description: 'Where utilization should be based on days elapsed in the month.', formula: 'Days Elapsed ÷ Days in Month × 100' },
        { label: 'Variance', color: 'amber', description: 'Difference between budgeted and actual spend. Positive = underspent (good). Negative = overspent (review needed).', formula: 'Budget − Actual Spend' },
        { label: 'Status: On Track', color: 'emerald', description: 'Utilization is within 10% of expected utilization for the current date.' },
        { label: 'Status: At Risk', color: 'red', description: 'Utilization exceeds expected utilization by more than 10%. Spending faster than planned.' },
        { label: 'Critical Alert (90%+)', color: 'red', description: 'Department has used over 90% of its monthly budget. Immediate review required.' }
      ]" note="Budget periods reset on the 1st of each month. Expenses must be marked as Approved or Paid to count against budget." />
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Budget Intelligence</h2>
      <button @click="refresh" :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">
        Refresh
      </button>
    </div>

    <!-- Alerts -->
    <div v-if="alerts.length" class="space-y-2">
      <div v-for="alert in alerts" :key="alert.category"
        class="flex items-center gap-3 p-3 rounded-lg border"
        :class="(alert.utilization || alert.utilization_rate || 0) >= 90 ? 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800' : 'bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800'">
        <span class="text-lg">{{ (alert.utilization || alert.utilization_rate || 0) >= 90 ? '🚨' : '⚠️' }}</span>
        <div class="flex-1 text-sm">
          <span class="font-semibold text-slate-900 dark:text-white">{{ alert.department || alert.category }}</span>
          <span class="text-slate-600 dark:text-slate-400"> — {{ (alert.utilization || alert.utilization_rate || 0).toFixed(1) }}% used</span>
        </div>
        <span class="text-xs text-slate-500">KES {{ fmt(alert.spent) }} / {{ fmt(alert.budget || alert.planned) }}</span>
      </div>
    </div>

    <!-- Utilization Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="item in utilization" :key="item.category"
        class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <div class="flex justify-between items-start mb-3">
          <div>
            <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ item.category }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">{{ item.department || 'All' }}</p>
          </div>
          <span class="text-sm font-bold" :class="utilizationColor(item.utilization_rate)">
            {{ item.utilization_rate }}%
          </span>
        </div>
        <div class="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden mb-2">
          <div class="h-full rounded-full transition-all"
            :class="utilizationBg(item.utilization_rate)"
            :style="{ width: Math.min(item.utilization_rate, 100) + '%' }">
          </div>
        </div>
        <div class="flex justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>Spent: KES {{ fmt(item.spent) }}</span>
          <span>Budget: KES {{ fmt(item.planned) }}</span>
        </div>
      </div>
    </div>

    <!-- Variance Table -->
    <div v-if="variance.length" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Variance Analysis</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Category</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Budget</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Actual</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Variance</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="row in variance" :key="row.category" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ row.category }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(row.planned) }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(row.spent) }}</td>
              <td class="px-4 py-3 text-right font-semibold"
                :class="row.variance >= 0 ? 'text-emerald-600' : 'text-red-600'">
                {{ row.variance >= 0 ? '+' : '' }}KES {{ fmt(Math.abs(row.variance)) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'

export default {
  components: { GuidePanel, },
  name: 'BudgetDashboard',
  setup() {
    const { makeRequest } = useApi()
    return { makeRequest }
  },
  data() {
    return { loading: false, utilization: [], alerts: [], variance: [] }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    utilizationColor(r) {
      if (r >= 90) return 'text-red-600 dark:text-red-400'
      if (r >= 75) return 'text-amber-600 dark:text-amber-400'
      return 'text-emerald-600 dark:text-emerald-400'
    },
    utilizationBg(r) {
      if (r >= 90) return 'bg-red-500'
      if (r >= 75) return 'bg-amber-500'
      return 'bg-emerald-500'
    },
    async refresh() {
      this.loading = true
      try {
        const [util, alerts, variance] = await Promise.allSettled([
          this.makeRequest('get', 'api/finance/api/budget/utilization/'),
          this.makeRequest('get', 'api/finance/api/budget/alerts/'),
          this.makeRequest('get', 'api/finance/api/budget/variance/')
        ])
        const u = util.status === 'fulfilled' ? util.value : []
        const a = alerts.status === 'fulfilled' ? alerts.value : []
        const v = variance.status === 'fulfilled' ? variance.value : []
        this.utilization = Array.isArray(u) ? u : (u.results || u.data || [])
        this.alerts      = Array.isArray(a) ? a : (a.results || a.data || [])
        this.variance    = Array.isArray(v) ? v : (v.results || v.data || [])
      } catch (e) {
        console.error('Budget fetch:', e)
      } finally {
        this.loading = false
      }
    }
  },
  mounted() { this.refresh() }
}
</script>
