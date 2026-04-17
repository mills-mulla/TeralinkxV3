<template>
  <div class="space-y-6">
    <GuidePanel title="Accounts Payable" :terms="[
        { label: 'AP Aging', color: 'blue', description: 'How long invoices have been outstanding. Older = higher risk of penalties.' },
        { label: 'WHT (6%)', color: 'amber', description: 'Withholding Tax deducted from vendor payments for services. Remitted to KRA.' },
        { label: 'Net Payable', color: 'emerald', description: 'Invoice total minus WHT. Actual amount paid to vendor.' },
        { label: 'Overdue', color: 'red', description: 'Invoice past due date. May attract late payment penalties from vendor.' },
      ]" note="WHT is automatically calculated on service invoices. Approve invoices before scheduling payment." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Accounts Payable</h2>
      <div class="flex gap-3">
        <select v-model="filters.status" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All</option>
          <option value="received">Received</option>
          <option value="approved">Approved</option>
          <option value="overdue">Overdue</option>
          <option value="paid">Paid</option>
        </select>
        <button @click="showAdd=true" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Add Invoice</button>
      </div>
    </div>

    <!-- Aging Summary -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-3" v-if="aging">
      <div v-for="(label, key) in { current: 'Current', '1_30': '1-30 Days', '31_60': '31-60 Days', '61_90': '61-90 Days', over_90: '90+ Days' }" :key="key"
        class="bg-white dark:bg-slate-800 rounded-xl p-4 border"
        :class="key === 'over_90' ? 'border-red-300 dark:border-red-700' : key === '61_90' ? 'border-amber-300 dark:border-amber-700' : 'border-slate-200 dark:border-slate-700'">
        <p class="text-xs font-medium" :class="key === 'over_90' ? 'text-red-600' : key === '61_90' ? 'text-amber-600' : 'text-slate-500'">{{ label }}</p>
        <p class="text-lg font-bold text-slate-900 dark:text-white mt-1">KES {{ fmt(aging.totals && aging.totals[key]) }}</p>
        <p class="text-xs text-slate-400">{{ aging.buckets && aging.buckets[key] }} invoices</p>
      </div>
    </div>

    <!-- Overdue Alert -->
    <div v-if="overdue.length" class="bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800 p-4">
      <p class="text-sm font-semibold text-red-900 dark:text-red-100 mb-2">⚠️ {{ overdue.length }} overdue invoices — KES {{ fmt(overdue.reduce((s,i) => s + i.net_payable, 0)) }} outstanding</p>
    </div>

    <!-- Invoices Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Vendor</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Invoice #</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Total</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">WHT</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Net Payable</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Due Date</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="inv in invoices" :key="inv.id"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50"
              :class="inv.is_overdue ? 'bg-red-50/30 dark:bg-red-900/10' : ''">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ inv.vendor_name }}</td>
              <td class="px-4 py-3 font-mono text-xs text-slate-600 dark:text-slate-400">{{ inv.invoice_number }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(inv.total) }}</td>
              <td class="px-4 py-3 text-right text-amber-600 dark:text-amber-400">{{ inv.wht_amount > 0 ? 'KES ' + fmt(inv.wht_amount) : '—' }}</td>
              <td class="px-4 py-3 text-right font-semibold text-slate-900 dark:text-white">KES {{ fmt(inv.net_payable) }}</td>
              <td class="px-4 py-3 text-xs" :class="inv.is_overdue ? 'text-red-600 font-semibold' : 'text-slate-600 dark:text-slate-400'">
                {{ inv.due_date }} {{ inv.is_overdue ? '(' + inv.days_overdue + 'd)' : '' }}
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(inv.status)">{{ inv.status_display }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button v-if="inv.status === 'received'" @click="doAction(inv.id,'approve')" class="px-2 py-1 bg-blue-600 text-white rounded text-xs">Approve</button>
                  <button v-if="['approved','overdue'].includes(inv.status)" @click="doAction(inv.id,'mark_paid')" class="px-2 py-1 bg-emerald-600 text-white rounded text-xs">Paid</button>
                  <button v-if="!['paid'].includes(inv.status)" @click="doAction(inv.id,'dispute')" class="px-2 py-1 bg-amber-600 text-white rounded text-xs">Dispute</button>
                </div>
              </td>
            </tr>
            <tr v-if="!invoices.length">
              <td colspan="8" class="px-4 py-8 text-center text-slate-400">No vendor invoices</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Invoice Modal -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showAdd=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-lg">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Add Vendor Invoice</h3>
          <button @click="showAdd=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Vendor Name *</label>
              <input v-model="form.vendor_name" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Invoice Number *</label>
              <input v-model="form.invoice_number" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Subtotal (KES) *</label>
              <input v-model="form.subtotal" type="number" step="0.01" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">VAT Amount (KES)</label>
              <input v-model="form.vat_amount" type="number" step="0.01" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Invoice Date *</label>
              <input v-model="form.invoice_date" type="date" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Due Date *</label>
              <input v-model="form.due_date" type="date" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input v-model="form.wht_applicable" type="checkbox" id="wht" class="w-4 h-4 rounded"/>
            <label for="wht" class="text-sm text-slate-700 dark:text-slate-300">Apply WHT (6% on services)</label>
          </div>
          <p v-if="err" class="text-sm text-red-600">{{ err }}</p>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showAdd=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="save" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">{{ saving ? 'Saving...' : 'Add Invoice' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'AccountsPayable',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    const today = new Date().toISOString().split('T')[0]
    const due = new Date(Date.now() + 30*86400000).toISOString().split('T')[0]
    return {
      invoices: [], aging: null, overdue: [], loading: false, filters: { status: '' },
      showAdd: false, saving: false, err: '',
      form: { vendor_name: '', invoice_number: '', subtotal: '', vat_amount: 0, invoice_date: today, due_date: due, wht_applicable: false }
    }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    statusBadge(s) {
      return { received: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
               approved: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               overdue: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
               paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               disputed: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400' }[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      try {
        const [list, agingData] = await Promise.allSettled([
          this.makeRequest('get', this.filters.status ? `api/finance/api/ap/?status=${this.filters.status}` : 'api/finance/api/ap/', null, false),
          this.makeRequest('get', 'api/finance/api/ap/aging/', null, false)
        ])
        if (list.status === 'fulfilled') {
          const d = list.value
          this.invoices = d.invoices || (Array.isArray(d) ? d : [])
        }
        if (agingData.status === 'fulfilled') {
          this.aging = agingData.value.aging
          this.overdue = agingData.value.overdue_invoices || []
        }
      } catch (e) { console.error(e) }
    },
    async doAction(id, act) {
      try { await this.makeRequest('patch', `api/finance/api/ap/${id}/`, { action: act }); await this.load() }
      catch (e) { console.error(e) }
    },
    async save() {
      if (!this.form.vendor_name || !this.form.invoice_number || !this.form.subtotal) { this.err = 'Vendor, invoice number and subtotal required'; return }
      this.saving = true; this.err = ''
      try { await this.makeRequest('post', 'api/finance/api/ap/', this.form); this.showAdd = false; await this.load() }
      catch (e) { this.err = e.response?.data?.error || 'Failed' }
      finally { this.saving = false }
    }
  },
  mounted() { this.load() }
}
</script>
