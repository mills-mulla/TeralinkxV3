<template>
  <div class="space-y-6">
    <GuidePanel title="Recurring Billing" :terms="[
        { label: 'Billing Day', color: 'blue', description: 'Day of month the customer is billed. System auto-deducts from balance.' },
        { label: 'Auto-Deduction', color: 'emerald', description: 'If customer has sufficient balance, payment is processed automatically.' },
        { label: 'Retry Logic', color: 'amber', description: 'Failed billings retry up to 3 times. After 3 failures, status becomes Failed.' },
        { label: 'Paused', color: 'slate', description: 'Billing temporarily stopped. Customer will not be charged until resumed.' },
      ]" note="Billing runs automatically at midnight daily. Only customers with active status and sufficient balance are charged." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Recurring Billing</h2>
      <div class="flex gap-3">
        <button @click="processBilling" :disabled="processing" class="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50">
          {{ processing ? 'Processing...' : '▶ Run Billing Now' }}
        </button>
        <button @click="showAdd=true" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Add Schedule</button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Active Schedules</p>
        <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{{ activeCount }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Paused</p>
        <p class="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">{{ pausedCount }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Failed</p>
        <p class="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">{{ failedCount }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Monthly Revenue</p>
        <p class="text-xl font-bold text-blue-600 dark:text-blue-400 mt-1">KES {{ fmt(monthlyRevenue) }}</p>
      </div>
    </div>

    <!-- Billing Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Package</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Next Billing</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="b in billings" :key="b.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ b.customer }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ b.package_name }}</td>
              <td class="px-4 py-3 text-right font-semibold text-slate-900 dark:text-white">KES {{ fmt(b.amount) }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400 text-xs">{{ b.next_billing_date }}</td>
              <td class="px-4 py-3">
                <div>
                  <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(b.status)">{{ b.status_display }}</span>
                  <p v-if="b.failure_reason" class="text-xs text-red-500 mt-0.5">{{ b.failure_reason }}</p>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button v-if="b.status === 'active'" @click="doAction(b.id,'pause')" class="px-2 py-1 bg-amber-600 text-white rounded text-xs">Pause</button>
                  <button v-if="b.status === 'paused'" @click="doAction(b.id,'resume')" class="px-2 py-1 bg-emerald-600 text-white rounded text-xs">Resume</button>
                  <button @click="doAction(b.id,'cancel')" class="px-2 py-1 bg-red-600 text-white rounded text-xs">Cancel</button>
                </div>
              </td>
            </tr>
            <tr v-if="!billings.length">
              <td colspan="6" class="px-4 py-8 text-center text-slate-400">No recurring billing schedules</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showAdd=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Add Billing Schedule</h3>
          <button @click="showAdd=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Customer ID *</label>
            <input v-model="form.customer_id" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Package Name *</label>
            <input v-model="form.package_name" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Amount (KES) *</label>
              <input v-model="form.amount" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Billing Day (1-28)</label>
              <input v-model="form.billing_day" type="number" min="1" max="28" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <p v-if="err" class="text-sm text-red-600">{{ err }}</p>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showAdd=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="save" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">{{ saving ? 'Saving...' : 'Add Schedule' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'RecurringBilling',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return { billings: [], loading: false, processing: false, showAdd: false, saving: false, err: '',
             form: { customer_id: '', package_name: '', amount: '', billing_day: 1 } }
  },
  computed: {
    activeCount() { return this.billings.filter(b => b.status === 'active').length },
    pausedCount() { return this.billings.filter(b => b.status === 'paused').length },
    failedCount() { return this.billings.filter(b => b.status === 'failed').length },
    monthlyRevenue() { return this.billings.filter(b => b.status === 'active').reduce((s, b) => s + parseFloat(b.amount || 0), 0) },
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    statusBadge(s) {
      return { active: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               paused: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
               failed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
               cancelled: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300' }[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      try { const data = await this.makeRequest('get', 'api/finance/api/recurring-billing/', null, false); this.billings = data.results || [] }
      catch (e) { console.error(e) }
    },
    async processBilling() {
      this.processing = true
      try {
        const r = await this.makeRequest('post', 'api/finance/api/recurring-billing/process/', {})
        alert(`Billing complete: ${r.success} success, ${r.failed} failed`)
        await this.load()
      } catch (e) { console.error(e) }
      finally { this.processing = false }
    },
    async doAction(id, act) {
      try { await this.makeRequest('patch', `api/finance/api/recurring-billing/${id}/`, { action: act }); await this.load() }
      catch (e) { console.error(e) }
    },
    async save() {
      if (!this.form.customer_id || !this.form.package_name || !this.form.amount) { this.err = 'All fields required'; return }
      this.saving = true; this.err = ''
      try { await this.makeRequest('post', 'api/finance/api/recurring-billing/', this.form); this.showAdd = false; await this.load() }
      catch (e) { this.err = e.response?.data?.error || 'Failed' }
      finally { this.saving = false }
    }
  },
  mounted() { this.load() }
}
</script>
