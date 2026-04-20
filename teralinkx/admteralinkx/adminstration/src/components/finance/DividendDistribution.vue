<template>
  <div class="space-y-6">
    <GuidePanel title="Dividend Distribution" :terms="[
      { label: 'Declaration', color: 'blue', description: 'Board resolution to distribute profits to shareholders. Sets total amount and per-share rate.' },
      { label: 'WHT', color: 'amber', description: 'Withholding Tax deducted at source on dividends. Kenya rate: 5% (residents) / 10% (non-residents).' },
    ]" note="Declare and track dividend distributions. WHT is auto-calculated and filed with KRA." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Dividend Declarations</h2>
      <button @click="showForm = !showForm" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ Declare Dividend</button>
    </div>

    <div v-if="showForm" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 space-y-3">
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-xs text-slate-500">Financial Year</label>
          <input v-model="form.financial_year" placeholder="e.g. 2024" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Total Amount (KES)</label>
          <input type="number" v-model="form.total_amount" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Per Share (KES)</label>
          <input type="number" v-model="form.per_share_amount" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Declaration Date</label>
          <input type="date" v-model="form.declaration_date" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
        <div><label class="text-xs text-slate-500">Payment Date</label>
          <input type="date" v-model="form.payment_date" class="w-full text-sm border border-slate-200 dark:border-slate-600 rounded px-3 py-2 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300" /></div>
      </div>
      <button @click="save" class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">Save Declaration</button>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 dark:bg-slate-900">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Year</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Total (KES)</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Per Share</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">WHT</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Declared</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Payment Date</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="d in dividends" :key="d.id" class="hover:bg-slate-50 dark:hover:bg-slate-700/50">
              <td class="px-4 py-3 font-medium text-slate-900 dark:text-white">{{ d.financial_year }}</td>
              <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{{ fmt(d.total_amount) }}</td>
              <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{{ fmt(d.per_share_amount) }}</td>
              <td class="px-4 py-3 text-right text-red-500">{{ fmt(d.wht_amount) }}</td>
              <td class="px-4 py-3 text-xs text-slate-500">{{ fmtDate(d.declaration_date) }}</td>
              <td class="px-4 py-3 text-xs text-slate-500">{{ fmtDate(d.payment_date) }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="statusClass(d.status)">{{ d.status }}</span>
              </td>
              <td class="px-4 py-3">
                <button v-if="d.status === 'declared'" @click="approve(d.id)" class="text-xs text-blue-600 hover:underline">Approve</button>
                <button v-if="d.status === 'approved'" @click="pay(d.id)" class="text-xs text-emerald-600 hover:underline">Mark Paid</button>
              </td>
            </tr>
            <tr v-if="!dividends.length">
              <td colspan="8" class="px-4 py-8 text-center text-slate-400">No dividend declarations found</td>
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
  name: 'DividendDistribution',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return {
      dividends: [], showForm: false,
      form: { financial_year: '', total_amount: '', per_share_amount: '', declaration_date: '', payment_date: '' }
    }
  },
  methods: {
    fmt(v) { return Number(v || 0).toLocaleString('en-KE', { minimumFractionDigits: 2 }) },
    fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', year: 'numeric' }) : '—' },
    statusClass(s) {
      return { declared: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
               approved: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
               paid: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400' }[s] || 'bg-slate-100 text-slate-600'
    },
    async load() {
      try {
        const data = await this.makeRequest('get', 'api/finance/api/dividends/', null, false)
        this.dividends = Array.isArray(data) ? data : (data.results || [])
      } catch (e) { console.error(e) }
    },
    async save() {
      try {
        await this.makeRequest('post', 'api/finance/api/dividends/', this.form, false)
        this.showForm = false
        this.form = { financial_year: '', total_amount: '', per_share_amount: '', declaration_date: '', payment_date: '' }
        this.load()
      } catch (e) { console.error(e) }
    },
    async approve(id) {
      try { await this.makeRequest('post', `api/finance/api/dividends/${id}/`, { action: 'approve' }, false); this.load() } catch (e) { console.error(e) }
    },
    async pay(id) {
      try { await this.makeRequest('post', `api/finance/api/dividends/${id}/`, { action: 'pay' }, false); this.load() } catch (e) { console.error(e) }
    }
  },
  mounted() { this.load() }
}
</script>
