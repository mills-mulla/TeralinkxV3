<template>
  <div class="space-y-6">
    <GuidePanel title="Petty Cash" :terms="[
        { label: 'Float Amount', color: 'blue', description: 'Total amount allocated to the petty cash fund.' },
        { label: 'Current Balance', color: 'emerald', description: 'Remaining cash after expenses. Replenish when low.' },
        { label: 'Replenishment', color: 'amber', description: 'Top up the fund back to float amount. Creates a credit transaction.' },
      ]" note="All petty cash transactions are logged with receipt numbers for audit purposes." />

    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Petty Cash</h2>
      <button @click="showAdd=true" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">+ New Fund</button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="fund in funds" :key="fund.id"
        class="bg-white dark:bg-slate-800 rounded-xl border p-5 cursor-pointer hover:border-blue-300"
        :class="fund.is_low ? 'border-red-300 dark:border-red-700' : 'border-slate-200 dark:border-slate-700'"
        @click="selectedFund = selectedFund?.id === fund.id ? null : fund; if(selectedFund) loadTxns(fund.id)">
        <div class="flex items-start justify-between">
          <div>
            <p class="font-semibold text-slate-900 dark:text-white">{{ fund.name }}</p>
            <p class="text-xs text-slate-500 mt-0.5">{{ fund.department || 'No department' }} · Custodian: {{ fund.custodian }}</p>
          </div>
          <span v-if="fund.is_low" class="px-2 py-1 bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 rounded text-xs font-medium">Low Balance</span>
        </div>
        <div class="mt-3 flex items-end justify-between">
          <div>
            <p class="text-xs text-slate-500">Balance</p>
            <p class="text-2xl font-bold" :class="fund.is_low ? 'text-red-600 dark:text-red-400' : 'text-emerald-600 dark:text-emerald-400'">KES {{ fmt(fund.current_balance) }}</p>
          </div>
          <p class="text-xs text-slate-400">Float: KES {{ fmt(fund.float_amount) }}</p>
        </div>

        <!-- Transactions -->
        <div v-if="selectedFund?.id === fund.id && txns[fund.id]" class="mt-4 border-t border-slate-200 dark:border-slate-700 pt-4 space-y-2">
          <div class="flex justify-between mb-2">
            <p class="text-xs font-medium text-slate-500 uppercase">Recent Transactions</p>
            <button @click.stop="showTxn=fund.id" class="text-xs text-blue-600 hover:underline">+ Add</button>
          </div>
          <div v-for="t in txns[fund.id]?.slice(0,5)" :key="t.id" class="flex justify-between text-sm">
            <span class="text-slate-600 dark:text-slate-400">{{ t.description }}</span>
            <span :class="t.type === 'expense' ? 'text-red-600' : 'text-emerald-600'">
              {{ t.type === 'expense' ? '-' : '+' }} KES {{ fmt(t.amount) }}
            </span>
          </div>
        </div>
      </div>
      <div v-if="!funds.length" class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-8 text-center text-slate-400">No petty cash funds</div>
    </div>

    <!-- Add Transaction Modal -->
    <div v-if="showTxn" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showTxn=null">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Add Transaction</h3>
          <button @click="showTxn=null" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Type</label>
              <select v-model="txnForm.transaction_type" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm">
                <option value="expense">Expense</option>
                <option value="replenishment">Replenishment</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Amount (KES) *</label>
              <input v-model="txnForm.amount" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description *</label>
            <input v-model="txnForm.description" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Receipt Number</label>
            <input v-model="txnForm.receipt_number" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showTxn=null" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="addTxn" :disabled="savingTxn" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">{{ savingTxn ? 'Saving...' : 'Add' }}</button>
        </div>
      </div>
    </div>

    <!-- Add Fund Modal -->
    <div v-if="showAdd" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="showAdd=false">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md">
        <div class="flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">New Petty Cash Fund</h3>
          <button @click="showAdd=false" class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg">
            <svg class="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Fund Name *</label>
            <input v-model="fundForm.name" type="text" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Float Amount (KES) *</label>
              <input v-model="fundForm.float_amount" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Low Balance Alert</label>
              <input v-model="fundForm.low_balance_threshold" type="number" class="w-full px-3 py-2 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white text-sm"/>
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-3 p-5 border-t border-slate-200 dark:border-slate-700">
          <button @click="showAdd=false" class="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm">Cancel</button>
          <button @click="createFund" :disabled="savingFund" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">{{ savingFund ? 'Creating...' : 'Create Fund' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useApi } from '../../composables/useApi'
import GuidePanel from './GuidePanel.vue'
export default {
  name: 'PettyCash',
  components: { GuidePanel },
  setup() { const { makeRequest } = useApi(); return { makeRequest } },
  data() {
    return { funds: [], txns: {}, selectedFund: null, showAdd: false, showTxn: null, savingFund: false, savingTxn: false,
             fundForm: { name: '', float_amount: '', low_balance_threshold: 1000 },
             txnForm: { transaction_type: 'expense', amount: '', description: '', receipt_number: '' } }
  },
  methods: {
    fmt(n) { return new Intl.NumberFormat('en-KE').format(Math.round(n || 0)) },
    async load() {
      try { const d = await this.makeRequest('get', 'api/finance/api/petty-cash/', null, false); this.funds = d.funds || [] }
      catch (e) { console.error(e) }
    },
    async loadTxns(id) {
      try { const d = await this.makeRequest('get', `api/finance/api/petty-cash/${id}/transactions/`, null, false); this.txns = { ...this.txns, [id]: d.transactions || [] } }
      catch (e) { console.error(e) }
    },
    async createFund() {
      this.savingFund = true
      try { await this.makeRequest('post', 'api/finance/api/petty-cash/', this.fundForm); this.showAdd = false; await this.load() }
      catch (e) { console.error(e) }
      finally { this.savingFund = false }
    },
    async addTxn() {
      this.savingTxn = true
      try { await this.makeRequest('post', `api/finance/api/petty-cash/${this.showTxn}/transactions/`, this.txnForm); this.showTxn = null; await this.load(); if (this.selectedFund) await this.loadTxns(this.selectedFund.id) }
      catch (e) { console.error(e) }
      finally { this.savingTxn = false }
    }
  },
  mounted() { this.load() }
}
</script>
