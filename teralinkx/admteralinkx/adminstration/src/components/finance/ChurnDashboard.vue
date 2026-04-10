<template>
  <div class="space-y-6">
    <GuidePanel title="Churn Prediction" :terms="[
        { label: 'Churn Score', color: 'red', description: 'Probability (0–1) that a customer will stop using the service.', formula: 'Score = weighted sum of risk factors (0.0 = no risk, 1.0 = certain churn)' },
        { label: 'Critical Risk (75%+)', color: 'red', description: 'Very likely to churn. Automated 20% discount applied for high-value customers.' },
        { label: 'High Risk (55–74%)', color: 'orange', description: 'Elevated probability. SMS with 10% discount offer sent automatically.' },
        { label: 'Medium Risk (30–54%)', color: 'amber', description: 'Moderate risk. Re-engagement SMS sent.' },
        { label: 'Low Risk (0–29%)', color: 'blue', description: 'Customer is stable. No action required.' },
        { label: 'Revenue at Risk', color: 'purple', description: 'Estimated 6-month revenue loss if customer churns.', formula: 'MRR × 6 months' }
      ]" note="ML model requires 50+ labelled samples — rule-based model used until then." />

    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Churn Prediction</h2>
      <div class="flex items-center gap-3">
        <select v-model="filters.risk_level" @change="loadPredictions"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All Risk Levels</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <button @click="generatePredictions" :disabled="generating"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm flex items-center gap-2">
          <svg class="w-4 h-4" :class="{ 'animate-spin': generating }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          {{ generating ? 'Generating...' : 'Refresh Predictions' }}
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border-l-4 border-red-500 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Critical Risk</p>
        <p class="text-3xl font-bold text-red-600 dark:text-red-400 mt-1">{{ stats.critical }}</p>
        <p class="text-xs text-slate-500 mt-1">customers</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border-l-4 border-orange-500 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">High Risk</p>
        <p class="text-3xl font-bold text-orange-600 dark:text-orange-400 mt-1">{{ stats.high }}</p>
        <p class="text-xs text-slate-500 mt-1">customers</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border-l-4 border-amber-500 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Medium Risk</p>
        <p class="text-3xl font-bold text-amber-600 dark:text-amber-400 mt-1">{{ stats.medium }}</p>
        <p class="text-xs text-slate-500 mt-1">customers</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border-l-4 border-purple-500 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 dark:text-slate-400 font-medium">Revenue at Risk</p>
        <p class="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">KES {{ fmt(stats.revenue_at_risk) }}</p>
        <p class="text-xs text-slate-500 mt-1">6-month estimate</p>
      </div>
    </div>

    <!-- Predictions Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Predictions</h3>
        <span class="text-xs text-slate-500">{{ predictions.length }} customers</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Risk</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Score</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">MRR</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Top Factors</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="pred in predictions" :key="pred.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">
                {{ pred.customer?.account || pred.customer?.id }}
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-bold" :class="riskBadge(pred.risk_level)">
                  {{ pred.risk_level }}
                </span>
              </td>
              <td class="px-4 py-3 text-right font-semibold" :class="scoreColor(pred.churn_score)">
                {{ (pred.churn_score * 100).toFixed(1) }}%
              </td>
              <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">
                KES {{ fmt(pred.monthly_recurring_revenue) }}
              </td>
              <td class="px-4 py-3">
                <div class="flex flex-wrap gap-1">
                  <span v-for="(f, i) in pred.top_factors?.slice(0, 2)" :key="i"
                    class="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded">
                    {{ typeof f === 'object' ? f.factor : f }}
                  </span>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <button @click="createRetentionTask(pred)" :disabled="taskCreating === pred.id"
                  class="px-3 py-1 rounded text-xs font-medium transition-colors"
                  :class="taskCreated === pred.id
                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                    : 'bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50'">
                  {{ taskCreated === pred.id ? '✓ Created' : taskCreating === pred.id ? '...' : '+ Task' }}
                </button>
              </td>
            </tr>
            <tr v-if="!predictions.length">
              <td colspan="6" class="px-4 py-8 text-center text-slate-400 text-sm">No predictions yet</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import GuidePanel from './GuidePanel.vue'
import { useApi } from '../../composables/useApi'

export default {
  name: 'ChurnDashboard',
  components: { GuidePanel },
  setup() {
    const { makeRequest } = useApi()
    const predictions = ref([])
    const filters = ref({ risk_level: '' })
    const generating = ref(false)
    const stats = ref({ critical: 0, high: 0, medium: 0, revenue_at_risk: 0 })

    const fmt = (n) => new Intl.NumberFormat('en-KE').format(Math.round(n || 0))

    const riskBadge = (level) => ({
      critical: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      high:     'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
      medium:   'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
      low:      'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    }[level] || 'bg-slate-100 text-slate-800')

    const scoreColor = (score) => {
      if (score >= 0.75) return 'text-red-600 dark:text-red-400'
      if (score >= 0.55) return 'text-orange-600 dark:text-orange-400'
      if (score >= 0.30) return 'text-amber-600 dark:text-amber-400'
      return 'text-blue-600 dark:text-blue-400'
    }

    const loadPredictions = async () => {
      try {
        const url = filters.value.risk_level
          ? `api/finance/api/churn-predictions/?risk_level=${filters.value.risk_level}`
          : 'api/finance/api/churn-predictions/'
        const data = await makeRequest('get', url)
        const raw = Array.isArray(data) ? data : (data.results || [])
        predictions.value = raw
        stats.value = {
          critical: raw.filter(p => p.risk_level === 'critical').length,
          high:     raw.filter(p => p.risk_level === 'high').length,
          medium:   raw.filter(p => p.risk_level === 'medium').length,
          revenue_at_risk: raw.reduce((sum, p) => sum + (parseFloat(p.monthly_recurring_revenue) || 0) * 6, 0)
        }
      } catch (e) { console.error('Failed to load predictions:', e) }
    }

    const generatePredictions = async () => {
      generating.value = true
      try {
        await makeRequest('post', 'api/finance/api/churn-predictions/generate/', { method: 'ml_model' })
        await loadPredictions()
      } catch (e) { console.error('Failed to generate predictions:', e) }
      finally { generating.value = false }
    }

    const taskCreating = ref(null)
    const taskCreated = ref(null)

    const createRetentionTask = async (prediction) => {
      taskCreating.value = prediction.id
      try {
        await makeRequest('post', 'api/finance/api/retention-tasks/', {
          customer_id: prediction.customer?.id || prediction.id,
          churn_prediction_id: prediction.id
        })
        taskCreated.value = prediction.id
        setTimeout(() => { taskCreated.value = null }, 3000)
      } catch (e) { console.error('Failed to create task:', e) }
      finally { taskCreating.value = null }
    }

    onMounted(() => { loadPredictions() })
    return { predictions, filters, stats, generating, taskCreating, taskCreated, fmt, riskBadge, scoreColor, loadPredictions, generatePredictions, createRetentionTask }
  }
}
</script>
