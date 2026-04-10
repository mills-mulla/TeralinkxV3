<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Vendor Intelligence</h2>
      <button @click="refresh" :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm">Refresh</button>
    </div>

    <!-- Invoice Alerts -->
    <div v-if="invoiceAlerts.length" class="space-y-2">
      <h3 class="text-sm font-semibold text-red-600 dark:text-red-400">🚨 Invoice Alerts</h3>
      <div v-for="alert in invoiceAlerts" :key="alert.vendor"
        class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 flex justify-between items-center">
        <div>
          <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ alert.vendor }}</p>
          <p class="text-xs text-slate-600 dark:text-slate-400">{{ alert.message }}</p>
        </div>
        <span class="text-sm font-bold text-red-600">KES {{ fmt(alert.amount) }}</span>
      </div>
    </div>

    <!-- Bandwidth Costs -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Bandwidth Costs by Provider</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Vendor</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Monthly Cost</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Cost/GB</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Trend</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="v in bandwidthCosts" :key="v.vendor"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ v.vendor }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(v.monthly_cost) }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(v.cost_per_gb) }}</td>
              <td class="px-4 py-3 text-right" :class="(v.trend || 0) > 0 ? 'text-red-600' : 'text-emerald-600'">
                {{ (v.trend || 0) > 0 ? '↑' : '↓' }} {{ Math.abs(v.trend || 0).toFixed(1) }}%
              </td>
            </tr>
            <tr v-if="!bandwidthCosts.length">
              <td colspan="4" class="px-4 py-8 text-center text-slate-400 text-sm">No vendor data</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Contract Calendar -->
    <div v-if="contracts.length" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-4">📅 Contract Renewals</h3>
      <div class="space-y-2">
        <div v-for="c in contracts" :key="c.vendor"
          class="flex items-center justify-between p-3 rounded-lg"
          :class="c.days_until_renewal <= 30 ? 'bg-red-50 dark:bg-red-900/20' : 'bg-slate-50 dark:bg-slate-700/50'">
          <div>
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ c.vendor }}</p>
            <p class="text-xs text-slate-500">Renews: {{ c.renewal_date }}</p>
          </div>
          <span class="text-sm font-bold"
            :class="c.days_until_renewal <= 30 ? 'text-red-600' : 'text-slate-600 dark:text-slate-400'">
            {{ c.days_until_renewal }}d
          </span>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-if="vendorRecs.length" class="space-y-2">
      <h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300">💡 Recommendations</h3>
      <div v-for="rec in vendorRecs" :key="rec.vendor"
        class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
        <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ rec.vendor }}</p>
        <p class="text-sm text-slate-600 dark:text-slate-400">{{ rec.recommendation }}</p>
        <p class="text-xs text-blue-600 mt-1">Potential saving: KES {{ fmt(rec.potential_saving) }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
export default {
  name: 'VendorIntelligence',
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { loading: false, bandwidthCosts: [], invoiceAlerts: [], contracts: [], vendorRecs: [] } },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    async refresh() {
      this.loading = true
      try {
        const [bw, alerts, cal, recs] = await Promise.all([
          this.makeRequest('get', 'api/finance/api/vendors/bandwidth-costs/'),
          this.makeRequest('get', 'api/finance/api/vendors/invoice-alerts/'),
          this.makeRequest('get', 'api/finance/api/vendors/contract-calendar/'),
          this.makeRequest('get', 'api/finance/api/vendors/recommendations/')
        ])
        this.bandwidthCosts = Array.isArray(bw)     ? bw     : (bw.results     || bw.data     || [])
        this.invoiceAlerts  = Array.isArray(alerts) ? alerts : (alerts.results || alerts.alerts || [])
        this.contracts      = Array.isArray(cal)    ? cal    : (cal.results    || cal.contracts || [])
        this.vendorRecs     = Array.isArray(recs)   ? recs   : (recs.results   || recs.recommendations || [])
      } catch (e) { console.error('Vendor fetch:', e) }
      finally { this.loading = false }
    }
  },
  mounted() { this.refresh() }
}
</script>
