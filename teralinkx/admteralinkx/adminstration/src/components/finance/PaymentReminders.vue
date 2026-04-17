<template>
  <div class="space-y-6">
    <GuidePanel title="Payment Reminders" :terms="[
        { label: '3 Days Before', color: 'blue', description: 'First reminder sent 3 days before package expiry.' },
        { label: 'Expiry Day', color: 'amber', description: 'Reminder sent on the day the package expires.' },
        { label: '3 Days Overdue', color: 'orange', description: 'Follow-up sent 3 days after expiry.' },
        { label: '7 Days Overdue', color: 'red', description: 'Final warning before service suspension.' },
      ]" note="Reminders fire automatically daily at 8am via Celery. SMS integration requires Africa's Talking or Twilio configuration." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Payment Reminders</h2>
      <button @click="load" :disabled="loading" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm hover:bg-slate-300">Refresh</button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4" v-if="stats">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Total Sent (30d)</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">{{ stats.last_30_days?.total || 0 }}</p>
      </div>
      <div class="bg-emerald-50 dark:bg-emerald-900/20 rounded-xl p-5 border border-emerald-200 dark:border-emerald-800">
        <p class="text-xs text-emerald-600 font-medium">Delivered</p>
        <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">{{ stats.last_30_days?.sent || 0 }}</p>
      </div>
      <div class="bg-red-50 dark:bg-red-900/20 rounded-xl p-5 border border-red-200 dark:border-red-800">
        <p class="text-xs text-red-600 font-medium">Failed</p>
        <p class="text-2xl font-bold text-red-700 dark:text-red-300 mt-1">{{ stats.last_30_days?.failed || 0 }}</p>
      </div>
      <div class="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-5 border border-amber-200 dark:border-amber-800">
        <p class="text-xs text-amber-600 font-medium">Pending</p>
        <p class="text-2xl font-bold text-amber-700 dark:text-amber-300 mt-1">{{ stats.last_30_days?.pending || 0 }}</p>
      </div>
    </div>

    <!-- Reminder History -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-slate-900 dark:text-white">Reminder History</h3>
        <select v-model="filters.status" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All</option>
          <option value="sent">Sent</option>
          <option value="failed">Failed</option>
          <option value="pending">Pending</option>
        </select>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Type</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Phone</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Scheduled</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="r in reminders" :key="r.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ r.customer }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ r.reminder_type_display }}</td>
              <td class="px-4 py-3 font-mono text-xs text-slate-500">{{ r.phone_number }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400 text-xs">{{ fmtDate(r.scheduled_at) }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(r.status)">{{ r.status }}</span>
              </td>
            </tr>
            <tr v-if="!reminders.length">
              <td colspan="5" class="px-4 py-8 text-center text-slate-400">No reminders sent yet — reminders fire when customers have expiring packages</td>
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
  name: 'PaymentReminders',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() { return { reminders: [], stats: null, loading: false, filters: { status: '' } } },
  methods: {
    fmtDate(d) { return d ? new Date(d).toLocaleString('en-KE', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—' },
    statusBadge(s) {
      return { sent: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               failed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
               pending: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
               skipped: 'bg-slate-100 text-slate-700' }[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      this.loading = true
      try {
        const [remData, statsData] = await Promise.allSettled([
          this.makeRequest('get', this.filters.status ? `api/finance/api/reminders/?status=${this.filters.status}` : 'api/finance/api/reminders/', null, false),
          this.makeRequest('get', 'api/finance/api/reminders/stats/', null, false)
        ])
        if (remData.status === 'fulfilled') this.reminders = Array.isArray(remData.value) ? remData.value : (remData.value.results || [])
        if (statsData.status === 'fulfilled') this.stats = statsData.value
      } catch (e) { console.error(e) }
      finally { this.loading = false }
    }
  },
  mounted() { this.load() }
}
</script>
