<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Pricing Intelligence</h2>
      <button @click="refresh" :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">Refresh</button>
    </div>

    <!-- Recommendations -->
    <div v-if="recommendations.length" class="space-y-3">
      <h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300">💡 Recommendations</h3>
      <div v-for="rec in recommendations" :key="rec.package_name"
        class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex items-start gap-3">
        <span class="text-blue-500 text-lg mt-0.5">→</span>
        <div>
          <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ rec.package_name }}</p>
          <p class="text-sm text-slate-600 dark:text-slate-400 mt-0.5">{{ rec.recommendation }}</p>
          <p class="text-xs text-blue-600 dark:text-blue-400 mt-1">
            Current: KES {{ fmt(rec.current_price) }} · Suggested: KES {{ fmt(rec.suggested_price) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Package Performance Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Package Performance</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Package</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Sales</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Revenue</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">ARPU</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Churn Rate</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="pkg in packages" :key="pkg.package_name"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ pkg.package_name }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">{{ pkg.sales || pkg.transaction_count || 0 }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(pkg.revenue || pkg.total_revenue) }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(pkg.arpu) }}</td>
              <td class="px-4 py-3 text-right" :class="(pkg.churn_rate || 0) > 5 ? 'text-red-600' : 'text-emerald-600'">
                {{ (pkg.churn_rate || 0).toFixed(1) }}%
              </td>
            </tr>
            <tr v-if="!packages.length">
              <td colspan="5" class="px-4 py-8 text-center text-slate-400 text-sm">No data</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Upgrade/Downgrade Stats -->
    <div v-if="upgradeStats" class="grid grid-cols-2 gap-4">
      <div class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-xl p-5">
        <p class="text-xs font-medium text-emerald-600">Upgrades (30d)</p>
        <p class="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">{{ upgradeStats.upgrades || 0 }}</p>
      </div>
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-5">
        <p class="text-xs font-medium text-red-600">Downgrades (30d)</p>
        <p class="text-3xl font-bold text-red-700 dark:text-red-300 mt-1">{{ upgradeStats.downgrades || 0 }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
export default {
  name: 'PricingIntelligence',
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { loading: false, packages: [], recommendations: [], upgradeStats: null } },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    async refresh() {
      this.loading = true
      try {
        const [pkgs, recs, upgrades] = await Promise.all([
          this.makeRequest('get', 'api/finance/api/pricing/package-performance/'),
          this.makeRequest('get', 'api/finance/api/pricing/recommendations/'),
          this.makeRequest('get', 'api/finance/api/pricing/upgrade-downgrade/')
        ])
        this.packages        = Array.isArray(pkgs) ? pkgs : (pkgs.results || pkgs.packages || [])
        this.recommendations = Array.isArray(recs) ? recs : (recs.results || recs.recommendations || [])
        this.upgradeStats    = upgrades
      } catch (e) { console.error('Pricing fetch:', e) }
      finally { this.loading = false }
    }
  },
  mounted() { this.refresh() }
}
</script>
