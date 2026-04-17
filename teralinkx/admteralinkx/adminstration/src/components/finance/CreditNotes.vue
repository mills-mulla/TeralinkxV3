<template>
  <div class="space-y-6">
    <GuidePanel title="Credit Notes" :terms="[
        { label: 'Credit Note', color: 'blue', description: 'Formal document reducing a customer balance. Required for KRA audit.' },
        { label: 'SLA Breach', color: 'red', description: 'Service was unavailable — customer entitled to credit per SLA policy.' },
        { label: 'Apply to Account', color: 'emerald', description: 'Credits the customer balance directly for next renewal.' },
      ]" note="Credit notes must be approved before applying. Once applied they cannot be voided." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Credit Notes</h2>
      <div class="flex gap-3">
        <select v-model="filters.status" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All</option>
          <option value="draft">Draft</option>
          <option value="approved">Approved</option>
          <option value="applied">Applied</option>
        </select>
        <button @click="showCreate=true" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ New</button>
      </div>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">CN #</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Reason</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="cn in notes" :key="cn.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-mono text-xs text-slate-700 dark:text-slate-300">{{ cn.credit_note_number }}</td>
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ cn.customer && cn.customer.account }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ cn.reason_display }}</td>
              <td class="px-4 py-3 text-right font-semibold text-slate-900 dark:text-white">KES {{ fmt(cn.total) }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(cn.status)">{{ cn.status_display }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button v-if="cn.status === 'draft'" @click="doAction(cn.id,'approve')" class="px-2 py-1 bg-blue-600 text-white rounded text-xs">Approve</button>
                  <button v-if="cn.status === 'approved'" @click="doAction(cn.id,'apply')" class="px-2 py-1 bg-emerald-600 text-white rounded text-xs">Apply</button>
                  <button v-if="cn.status !== 'applied'" @click="doAction(cn.id,'void')" class="px-2 py-1 bg-red-600 text-white rounded text-xs">Void</button>
                </div>
              </td>
            </tr>
            <tr v-if="!notes.length">
              <td colspan="6" class="px-4 py-8 text-center text-slate-400">No credit notes</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showCreate" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showCreate=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">New Credit Note</h3>
          <button @click="showCreate=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Customer ID *</label>
            <input v-model="form.customer_id" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Amount (KES) *</label>
              <input v-model="form.amount" type="number" step="0.01" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Reason *</label>
              <select v-model="form.reason" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm">
                <option value="overcharge">Overcharge</option>
                <option value="sla_breach">SLA Breach</option>
                <option value="duplicate">Duplicate Payment</option>
                <option value="cancellation">Cancellation</option>
                <option value="goodwill">Goodwill</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description *</label>
            <textarea v-model="form.description" rows="2" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm resize-none"></textarea>
          </div>
          <p v-if="err" class="text-sm text-red-600">{{ err }}</p>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showCreate=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="create" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">{{ saving ? 'Saving...' : 'Create' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'CreditNotes',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return { notes: [], loading: false, filters: { status: '' }, showCreate: false, saving: false, err: '',
             form: { customer_id: '', amount: '', reason: 'overcharge', description: '' } }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    statusBadge(s) {
      return { draft: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
               approved: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               applied: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               voided: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      try {
        const url = this.filters.status ? `api/finance/api/credit-notes/?status=${this.filters.status}` : 'api/finance/api/credit-notes/'
        const data = await this.makeRequest('get', url, null, false)
        this.notes = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async doAction(id, act) {
      try { await this.makeRequest('patch', `api/finance/api/credit-notes/${id}/`, { action: act }); await this.load() }
      catch (e) { console.error(e) }
    },
    async create() {
      if (!this.form.customer_id || !this.form.amount || !this.form.description) { this.err = 'All fields required'; return }
      this.saving = true; this.err = ''
      try { await this.makeRequest('post', 'api/finance/api/credit-notes/', this.form); this.showCreate = false; await this.load() }
      catch (e) { this.err = e.response?.data?.error || 'Failed' }
      finally { this.saving = false }
    }
  },
  mounted() { this.load() }
}
</script>
