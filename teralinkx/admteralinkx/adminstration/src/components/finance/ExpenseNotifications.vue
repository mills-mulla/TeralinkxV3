<template>
  <div class="space-y-6">
    <GuidePanel title="Expense Notifications" :terms="[
        { label: 'Pending Approvals', color: 'amber', description: 'Expenses submitted but not yet approved. Approvers are notified via SMS/email.' },
        { label: 'Overdue (48h+)', color: 'red', description: 'Expenses waiting more than 48 hours for approval. Escalation alert sent.' },
      ]" note="Notifications fire automatically. Configure your preferences below to control which alerts you receive." />

    <h2 class="text-xl font-bold text-slate-900 dark:text-white">Expense Notifications</h2>

    <!-- Pending Badge -->
    <div v-if="pending" class="grid grid-cols-2 gap-4">
      <div class="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-5 border border-amber-200 dark:border-amber-800">
        <p class="text-xs text-amber-600 font-medium">Pending Approvals</p>
        <p class="text-3xl font-bold text-amber-700 dark:text-amber-300 mt-1">{{ pending.pending }}</p>
        <p class="text-xs text-amber-500 mt-1">awaiting review</p>
      </div>
      <div class="bg-red-50 dark:bg-red-900/20 rounded-xl p-5 border border-red-200 dark:border-red-800">
        <p class="text-xs text-red-600 font-medium">Overdue (48h+)</p>
        <p class="text-3xl font-bold text-red-700 dark:text-red-300 mt-1">{{ pending.overdue_48h }}</p>
        <p class="text-xs text-red-500 mt-1">need immediate attention</p>
      </div>
    </div>

    <!-- Preferences -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" v-if="prefs">
      <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-4">My Notification Preferences</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label v-for="(label, key) in prefLabels" :key="key" class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg cursor-pointer">
          <span class="text-sm text-slate-700 dark:text-slate-300">{{ label }}</span>
          <input type="checkbox" v-model="prefs[key]" @change="savePrefs" class="w-4 h-4 rounded"/>
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'ExpenseNotifications',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      pending: null, prefs: null,
      prefLabels: {
        expense_submitted_sms: 'SMS when expense submitted',
        expense_submitted_email: 'Email when expense submitted',
        expense_approved_sms: 'SMS when expense approved/rejected',
        expense_approved_email: 'Email when expense approved/rejected',
        budget_alert_sms: 'SMS for budget alerts',
        budget_alert_email: 'Email for budget alerts',
        tax_deadline_sms: 'SMS for tax deadlines',
        tax_deadline_email: 'Email for tax deadlines',
      }
    }
  },
  methods: {
    async load() {
      const [p, pr] = await Promise.allSettled([
        this.makeRequest('get', 'api/finance/api/notifications/pending/', null, false),
        this.makeRequest('get', 'api/finance/api/notifications/prefs/', null, false)
      ])
      if (p.status === 'fulfilled') this.pending = p.value
      if (pr.status === 'fulfilled') this.prefs = pr.value
    },
    async savePrefs() {
      try { await this.makeRequest('patch', 'api/finance/api/notifications/prefs/', this.prefs) }
      catch (e) { console.error(e) }
    }
  },
  mounted() { this.load() }
}
</script>
