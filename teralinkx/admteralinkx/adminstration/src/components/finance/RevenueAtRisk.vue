<template>
  <div class="space-y-6">
    <GuidePanel title="Revenue at Risk" :terms="[
        { label: 'Total Revenue at Risk', color: 'red', description: 'Sum of MRR × churn probability for all high and critical risk customers. This is the maximum potential monthly revenue loss.' },
        { label: 'Retention Rate', color: 'emerald', description: 'Percentage of at-risk customers who resumed service after a retention offer was sent.', formula: 'Retained ÷ (Retained + Churned) × 100' },
        { label: 'Automated Offers Sent', color: 'blue', description: 'Count of automated retention actions taken (discounts applied, SMS sent) in the last 30 days.' },
        { label: 'Relocated', color: 'indigo', description: 'Customers who moved outside coverage area. Excluded from churn calculations — not actionable.' },
        { label: 'Retained', color: 'emerald', description: 'Customer made a payment within 14 days of receiving a retention offer.' },
        { label: 'Churned', color: 'red', description: 'No session activity for 60+ days after retention offer. Marked as lost.' }
      ]" note="Revenue at risk updates automatically when churn predictions are regenerated. Top accounts are sorted by MRR × churn probability." />
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Revenue at Risk</h2>
      <button @click="refresh" :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">
        Refresh
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-5">
        <p class="text-xs font-medium text-red-600 dark:text-red-400">Total Revenue at Risk</p>
        <p class="text-2xl font-bold text-red-700 dark:text-red-300 mt-1">KES {{ fmt(summary.total_revenue_at_risk) }}</p>
      </div>
      <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-5">
        <p class="text-xs font-medium text-amber-600 dark:text-amber-400">At-Risk Customers</p>
        <p class="text-2xl font-bold text-amber-700 dark:text-amber-300 mt-1">{{ summary.at_risk_customer_count || 0 }}</p>
      </div>
      <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-5">
        <p class="text-xs font-medium text-blue-600 dark:text-blue-400">Automated Offers Sent</p>
        <p class="text-2xl font-bold text-blue-700 dark:text-blue-300 mt-1">{{ offers.total_offers_sent || 0 }}</p>
      </div>
      <div class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-xl p-5">
        <p class="text-xs font-medium text-emerald-600 dark:text-emerald-400">Retention Rate</p>
        <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">{{ effectiveness.retention_rate || 0 }}%</p>
      </div>
    </div>

    <!-- Top At-Risk Accounts -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Top At-Risk Accounts</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Risk</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">MRR</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Revenue at Risk</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Top Factor</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="acc in topAccounts" :key="acc.customer_id"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">
                {{ acc.customer_username || acc.customer_id }}
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-bold"
                  :class="riskBadge(acc.risk_level)">
                  {{ acc.risk_level }}
                </span>
              </td>
              <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">
                KES {{ fmt(acc.monthly_recurring_revenue) }}
              </td>
              <td class="px-4 py-3 text-right font-semibold text-red-600 dark:text-red-400">
                KES {{ fmt(acc.revenue_at_risk) }}
              </td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400 text-xs">
                {{ firstFactor(acc.top_factors) }}
              </td>
            </tr>
            <tr v-if="!topAccounts.length">
              <td colspan="5" class="px-4 py-8 text-center text-slate-400 text-sm">No at-risk accounts</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Effectiveness Stats -->
    <div v-if="effectiveness.outcome_breakdown" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-4">Retention Effectiveness</h3>
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <p class="text-2xl font-bold text-emerald-600">{{ effectiveness.outcome_breakdown.retained || 0 }}</p>
          <p class="text-xs text-slate-500 mt-1">Retained</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-red-600">{{ effectiveness.outcome_breakdown.churned || 0 }}</p>
          <p class="text-xs text-slate-500 mt-1">Churned</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-blue-600">{{ effectiveness.outcome_breakdown.relocated || 0 }}</p>
          <p class="text-xs text-slate-500 mt-1">Relocated</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'

export default {
  components: { GuidePanel, },
  name: 'RevenueAtRisk',
  setup() {
    const { makeRequest } = useApi()
    return { makeRequest }
  },
  data() {
    return { loading: false, summary: {}, topAccounts: [], effectiveness: {}, offers: {} }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    riskBadge(level) {
      return {
        critical: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
        high:     'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
        medium:   'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
        low:      'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      }[level] || 'bg-slate-100 text-slate-800'
    },
    firstFactor(factors) {
      if (!factors?.length) return '—'
      const f = factors[0]
      return typeof f === 'object' ? f.factor : f
    },
    async refresh() {
      this.loading = true
      try {
        const [summary, top, effectiveness, offers] = await Promise.allSettled([
          this.makeRequest('get', 'api/finance/api/revenue-at-risk/'),
          this.makeRequest('get', 'api/finance/api/revenue-at-risk/top-accounts/'),
          this.makeRequest('get', 'api/finance/api/revenue-at-risk/effectiveness/'),
          this.makeRequest('get', 'api/finance/api/revenue-at-risk/offers/')
        ])
        this.summary       = summary.status === 'fulfilled' ? summary.value : {}
        const t = top.status === 'fulfilled' ? top.value : []
        this.topAccounts   = Array.isArray(t) ? t : (t.results || t.top_at_risk_accounts || [])
        this.effectiveness = effectiveness.status === 'fulfilled' ? effectiveness.value : {}
        this.offers        = offers.status === 'fulfilled' ? offers.value : {}
      } catch (e) {
        console.error('RevenueAtRisk fetch:', e)
      } finally {
        this.loading = false
      }
    }
  },
  mounted() { this.refresh() }
}
</script>
