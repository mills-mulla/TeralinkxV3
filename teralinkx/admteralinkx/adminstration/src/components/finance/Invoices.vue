<template>
  <div class="space-y-6">
    <GuidePanel title="Invoice Management" :terms="[
        { label: 'Tax Invoice', color: 'blue', description: 'KRA-compliant invoice auto-generated on every M-Pesa payment. Required for transactions above KES 1,000.' },
        { label: 'VAT (16%)', color: 'amber', description: 'Value Added Tax included in every invoice. Back-calculated from gross amount.', formula: 'VAT = Total × 16/116' },
        { label: 'Invoice Number', color: 'purple', description: 'Sequential number format INV-YYYY-NNNNN. Never reused or skipped.' },
        { label: 'Status: Paid', color: 'emerald', description: 'Invoice linked to a completed payment transaction.' },
        { label: 'Status: Issued', color: 'blue', description: 'Invoice generated but payment not yet confirmed.' },
      ]" note="Invoices are auto-generated on every successful M-Pesa callback. Manual invoices can be created for cash/bank payments." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Invoices</h2>
      <div class="flex gap-3">
        <select v-model="filters.status" @change="load"
          class="text-sm border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300">
          <option value="">All Status</option>
          <option value="issued">Issued</option>
          <option value="paid">Paid</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <button @click="load" :disabled="loading"
          class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm hover:bg-slate-300">
          Refresh
        </button>
        <button @click="showCreate=true"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          New Invoice
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Total Invoices</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white mt-1">{{ invoices.length }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Total Billed</p>
        <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">KES {{ fmt(totalBilled) }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Total VAT</p>
        <p class="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">KES {{ fmt(totalVAT) }}</p>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
        <p class="text-xs text-slate-500 font-medium">Paid</p>
        <p class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{{ paidCount }}</p>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Invoice #</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Customer</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Subtotal</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">VAT</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Total</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Date</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">PDF</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="inv in invoices" :key="inv.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-mono text-xs text-slate-700 dark:text-slate-300">{{ inv.invoice_number }}</td>
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ inv.customer?.account }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">KES {{ fmt(inv.subtotal) }}</td>
              <td class="px-4 py-3 text-right text-amber-600 dark:text-amber-400">KES {{ fmt(inv.vat_amount) }}</td>
              <td class="px-4 py-3 text-right font-semibold text-slate-900 dark:text-white">KES {{ fmt(inv.total) }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ fmtDate(inv.issue_date) }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(inv.status)">{{ inv.status }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <a :href="pdfUrl(inv.id)" target="_blank"
                  class="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs hover:bg-red-200">
                  📄 PDF
                </a>
              </td>
            </tr>
            <tr v-if="!invoices.length && !loading">
              <td colspan="8" class="px-4 py-8 text-center text-slate-400">No invoices found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showCreate=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-lg">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Create Manual Invoice</h3>
          <button @click="showCreate=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Customer Account *</label>
            <input v-model="form.customer_account" type="text" placeholder="e.g. CLI000001"
              class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Subtotal (KES) *</label>
              <input v-model="form.subtotal" type="number" step="0.01"
                class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Issue Date *</label>
              <input v-model="form.issue_date" type="date"
                class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
            <input v-model="form.description" type="text"
              class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <p v-if="createError" class="text-sm text-red-600">{{ createError }}</p>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showCreate=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="createInvoice" :disabled="creating" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
            {{ creating ? 'Creating...' : 'Create Invoice' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'

export default {
  name: 'Invoices',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      invoices: [], loading: false, filters: { status: '' },
      showCreate: false, creating: false, createError: '',
      form: { customer_account: '', subtotal: '', issue_date: new Date().toISOString().split('T')[0], description: '' }
    }
  },
  computed: {
    totalBilled() { return this.invoices.reduce((s, i) => s + parseFloat(i.total || 0), 0) },
    totalVAT()    { return this.invoices.reduce((s, i) => s + parseFloat(i.vat_amount || 0), 0) },
    paidCount()   { return this.invoices.filter(i => i.status === 'paid').length },
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' }) : '—' },
    pdfUrl(id) {
      const base = localStorage.getItem('api_base') || 'https://srv.teralinkxwaves.uk'
      const token = localStorage.getItem('access_token')
      return `${base}/api/finance/api/invoices/${id}/pdf/?token=${token}`
    },
    statusBadge(s) {
      return { issued: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
               cancelled: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
               credited: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400' }[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      this.loading = true
      try {
        const url = this.filters.status ? `api/finance/api/invoices/?status=${this.filters.status}` : 'api/finance/api/invoices/'
        const data = await this.makeRequest('get', url, null, false)
        this.invoices = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error('Invoices load:', e) }
      finally { this.loading = false }
    },
    async createInvoice() {
      if (!this.form.customer_account || !this.form.subtotal) {
        this.createError = 'Customer account and subtotal are required'; return
      }
      this.creating = true; this.createError = ''
      try {
        // Resolve customer_id from account
        const customers = await this.makeRequest('get', `api/finance/api/departments/`)
        // Use account as search — simplified: post with account field
        await this.makeRequest('post', 'api/finance/api/invoices/create/', {
          customer_account: this.form.customer_account,
          subtotal: parseFloat(this.form.subtotal),
          issue_date: this.form.issue_date,
          description: this.form.description,
        })
        this.showCreate = false
        await this.load()
      } catch (e) { this.createError = e.response?.data?.error || 'Failed to create invoice' }
      finally { this.creating = false }
    }
  },
  mounted() { this.load() }
}
</script>
