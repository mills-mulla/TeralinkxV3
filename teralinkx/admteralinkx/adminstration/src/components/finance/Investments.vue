<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Investment Portfolio</h2>
      <div class="flex gap-3">
        <button @click="load" :disabled="loading"
          class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-300 text-sm flex items-center gap-2">
          <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          Refresh
        </button>
        <button @click="openAdd" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Add Investment
        </button>
      </div>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl p-5 text-white">
        <p class="text-indigo-100 text-xs font-medium">Total Invested</p>
        <p class="text-2xl font-bold mt-1">KES {{ fmt(totalInvested) }}</p>
      </div>
      <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-5 text-white">
        <p class="text-emerald-100 text-xs font-medium">Active</p>
        <p class="text-2xl font-bold mt-1">{{ activeCount }}</p>
      </div>
      <div class="bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-5 text-white">
        <p class="text-amber-100 text-xs font-medium">Avg Expected ROI</p>
        <p class="text-2xl font-bold mt-1">{{ avgROI }}%</p>
      </div>
      <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-5 text-white">
        <p class="text-purple-100 text-xs font-medium">Total Records</p>
        <p class="text-2xl font-bold mt-1">{{ investments.length }}</p>
      </div>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Investor</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Type</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Amount</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Interest</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">ROI</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Date</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Maturity</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="inv in investments" :key="inv.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3">
                <p class="font-medium text-slate-900 dark:text-white">{{ inv.investor_name }}</p>
                <p v-if="inv.contract_reference" class="text-xs text-slate-400">{{ inv.contract_reference }}</p>
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="typeBadge(inv.investment_type)">{{ inv.type_display }}</span>
              </td>
              <td class="px-4 py-3 text-right font-semibold text-slate-900 dark:text-white">KES {{ fmt(inv.amount) }}</td>
              <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-400">{{ inv.interest_rate }}%</td>
              <td class="px-4 py-3 text-right">
                <span v-if="inv.expected_roi" class="text-emerald-600 font-medium">{{ inv.expected_roi }}%</span>
                <span v-else class="text-slate-400">-</span>
              </td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ fmtDate(inv.investment_date) }}</td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-400">{{ inv.maturity_date ? fmtDate(inv.maturity_date) : '-' }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs font-medium" :class="statusBadge(inv.investment_status)">{{ inv.status_display }}</span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-2">
                  <button @click="openEdit(inv)" class="p-1.5 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded text-blue-600 dark:text-blue-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                  </button>
                  <button @click="openDelete(inv)" class="p-1.5 hover:bg-red-100 dark:hover:bg-red-900/30 rounded text-red-600 dark:text-red-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!investments.length && !loading">
              <td colspan="9" class="px-4 py-8 text-center text-slate-400">No investments found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showForm" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showForm=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-screen overflow-y-auto">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700 sticky top-0 bg-white dark:bg-slate-800 z-10">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">{{ editing ? 'Edit Investment' : 'Add Investment' }}</h3>
          <button @click="showForm=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Investor Name *</label>
            <input v-model="form.investor_name" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Type *</label>
              <select v-model="form.investment_type" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm">
                <option value="seed">Seed Funding</option>
                <option value="angel">Angel Investment</option>
                <option value="vc">Venture Capital</option>
                <option value="loan">Business Loan</option>
                <option value="personal">Personal Investment</option>
                <option value="equity">Equity Investment</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Status *</label>
              <select v-model="form.investment_status" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm">
                <option value="proposed">Proposed</option>
                <option value="approved">Approved</option>
                <option value="disbursed">Disbursed</option>
                <option value="active">Active</option>
                <option value="repaid">Repaid</option>
                <option value="converted">Converted</option>
                <option value="written_off">Written Off</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Amount (KES) *</label>
              <input v-model="form.amount" type="number" step="0.01" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Investment Date *</label>
              <input v-model="form.investment_date" type="date" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Interest Rate (%)</label>
              <input v-model="form.interest_rate" type="number" step="0.01" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Equity %</label>
              <input v-model="form.equity_percentage" type="number" step="0.01" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Expected ROI (%)</label>
              <input v-model="form.expected_roi" type="number" step="0.01" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Maturity Date</label>
              <input v-model="form.maturity_date" type="date" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Contract Reference</label>
            <input v-model="form.contract_reference" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <div class="flex items-center gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.is_recurring" type="checkbox" class="w-4 h-4 rounded"/>
              <span class="text-sm text-slate-700 dark:text-slate-300">Recurring</span>
            </label>
            <select v-if="form.is_recurring" v-model="form.recurrence_pattern" class="px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm">
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="annual">Annual</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Repayment Terms</label>
            <textarea v-model="form.repayment_terms" rows="2" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm resize-none"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
            <textarea v-model="form.description" rows="2" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm resize-none"></textarea>
          </div>
          <p v-if="formError" class="text-sm text-red-600 dark:text-red-400">{{ formError }}</p>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showForm=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="save" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">{{ saving ? 'Saving...' : 'Save' }}</button>
        </div>
      </div>
    </div>

    <div v-if="showDel" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showDel=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-md w-full p-6">
        <div class="flex items-center gap-4 mb-6">
          <div class="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Delete Investment</h3>
            <p class="text-sm text-slate-500 mt-1">Delete "{{ delTarget && delTarget.investor_name }}"? This cannot be undone.</p>
          </div>
        </div>
        <div class="flex justify-end gap-3">
          <button @click="showDel=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="confirmDelete" :disabled="deleting" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 disabled:opacity-50">{{ deleting ? 'Deleting...' : 'Delete' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'

export default {
  name: 'Investments',
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      investments: [], loading: false,
      showForm: false, editing: null, saving: false, formError: '',
      showDel: false, delTarget: null, deleting: false,
      form: {
        investor_name: '', investment_type: 'loan', investment_status: 'proposed',
        amount: '', investment_date: new Date().toISOString().split('T')[0],
        interest_rate: 0, equity_percentage: '', expected_roi: '', maturity_date: '',
        is_recurring: false, recurrence_pattern: 'monthly',
        contract_reference: '', repayment_terms: '', description: ''
      }
    }
  },
  computed: {
    totalInvested() { return this.investments.reduce((s, i) => s + parseFloat(i.amount || 0), 0) },
    activeCount() { return this.investments.filter(i => ['active','disbursed'].includes(i.investment_status)).length },
    avgROI() {
      const r = this.investments.filter(i => i.expected_roi)
      return r.length ? (r.reduce((s, i) => s + parseFloat(i.expected_roi), 0) / r.length).toFixed(1) : 0
    }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' }) : '-' },
    typeBadge(t) {
      const m = { seed: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
        angel: 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-400',
        vc: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400',
        loan: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
        personal: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        equity: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' }
      return m[t] || 'bg-slate-100 text-slate-800'
    },
    statusBadge(s) {
      const m = { proposed: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
        approved: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
        disbursed: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400',
        active: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
        repaid: 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-400',
        converted: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
        written_off: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' }
      return m[s] || 'bg-slate-100 text-slate-800'
    },
    async load() {
      this.loading = true
      try {
        const data = await this.makeRequest('get', 'api/finance/api/investments/', null, false)
        this.investments = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error('load:', e) }
      finally { this.loading = false }
    },
    openAdd() {
      this.editing = null
      this.form = { investor_name: '', investment_type: 'loan', investment_status: 'proposed',
        amount: '', investment_date: new Date().toISOString().split('T')[0],
        interest_rate: 0, equity_percentage: '', expected_roi: '', maturity_date: '',
        is_recurring: false, recurrence_pattern: 'monthly',
        contract_reference: '', repayment_terms: '', description: '' }
      this.formError = ''; this.showForm = true
    },
    openEdit(inv) {
      this.editing = inv
      this.form = { investor_name: inv.investor_name, investment_type: inv.investment_type,
        investment_status: inv.investment_status, amount: inv.amount,
        investment_date: inv.investment_date, interest_rate: inv.interest_rate,
        equity_percentage: inv.equity_percentage || '', expected_roi: inv.expected_roi || '',
        maturity_date: inv.maturity_date || '', is_recurring: inv.is_recurring,
        recurrence_pattern: inv.recurrence_pattern || 'monthly',
        contract_reference: inv.contract_reference || '',
        repayment_terms: inv.repayment_terms || '', description: inv.description || '' }
      this.formError = ''; this.showForm = true
    },
    async save() {
      if (!this.form.investor_name || !this.form.amount || !this.form.investment_date) {
        this.formError = 'Investor name, amount and date are required'; return
      }
      this.saving = true; this.formError = ''
      try {
        if (this.editing) {
          await this.makeRequest('put', 'api/finance/api/investments/' + this.editing.id + '/', this.form)
        } else {
          await this.makeRequest('post', 'api/finance/api/investments/', this.form)
        }
        this.showForm = false; await this.load()
      } catch (e) { this.formError = (e.response && e.response.data && e.response.data.error) || 'Failed to save' }
      finally { this.saving = false }
    },
    openDelete(inv) { this.delTarget = inv; this.showDel = true },
    async confirmDelete() {
      this.deleting = true
      try {
        await this.makeRequest('delete', 'api/finance/api/investments/' + this.delTarget.id + '/')
        this.showDel = false; await this.load()
      } catch (e) { console.error('delete:', e) }
      finally { this.deleting = false }
    }
  },
  mounted() { this.load() }
}
</script>
